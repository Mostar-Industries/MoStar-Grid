import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from neo4j import GraphDatabase

try:
    import yaml
except ImportError:
    yaml = None

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
DEFAULT_SYMBOLIC_YAML_URI = os.getenv(
    "MOSTAR_SYMBOLIC_YAML_URI", "file:///data/scripts/symbolic-logic.yaml"
)
DEFAULT_SYMBOLIC_YAML_PATH = (
    Path(__file__).resolve().parent.parent
    / "neo4j-mostar-industries"
    / "import"
    / "data"
    / "scripts"
    / "symbolic-logic.yaml"
)

CONSTRAINT_STATEMENTS = [
    "CREATE CONSTRAINT symbolic_module_id IF NOT EXISTS FOR (n:SymbolicModule) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT symbolic_mode_id IF NOT EXISTS FOR (n:SymbolicMode) REQUIRE n.id IS UNIQUE",
    "CREATE CONSTRAINT symbolic_fact_raw IF NOT EXISTS FOR (n:SymbolicFact) REQUIRE n.raw_text IS UNIQUE",
    "CREATE CONSTRAINT symbolic_rule_raw IF NOT EXISTS FOR (n:SymbolicRule) REQUIRE n.raw_text IS UNIQUE",
    "CREATE CONSTRAINT lisp_function_code IF NOT EXISTS FOR (n:LispFunction) REQUIRE n.code IS UNIQUE",
    "CREATE CONSTRAINT symbolic_entry_input IF NOT EXISTS FOR (n:SymbolicEntryPoint) REQUIRE n.input IS UNIQUE",
]


class Symbol(str):
    pass


@dataclass
class Fact:
    predicate: str
    args: list[str]
    raw_text: str


@dataclass
class Rule:
    head_predicate: str
    head_args: list[str]
    body: list[tuple[str, list[str]]]
    raw_text: str


class SymbolicLogicRuntime:
    def __init__(self) -> None:
        self._driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
        )
        self._rule_counter = 0

    def close(self) -> None:
        self._driver.close()

    def _read(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        with self._driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]

    def _write(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        with self._driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]

    def bootstrap(self, yaml_uri: str = DEFAULT_SYMBOLIC_YAML_URI) -> dict[str, Any]:
        summary: list[dict[str, Any]] = []
        for statement in CONSTRAINT_STATEMENTS:
            rows = self._write(statement)
            summary.append({"statement": statement, "rows": rows})
        source = self._load_symbolic_source(yaml_uri)
        config = source["symbolic_logic"]
        self._write(
            """
            MERGE (module:SymbolicModule:GridCore {id: 'symbolic_logic'})
            SET module.version = $version,
                module.description = $description,
                module.source_file = $yaml_uri,
                module.source_path = $yaml_path,
                module.subgraph = 'grid_core',
                module.domain = 'mostar_grid'
            """,
            {
                "version": str(config.get("version", "1.0.0")),
                "description": config.get("description", ""),
                "yaml_uri": yaml_uri,
                "yaml_path": str(source["path"]),
            },
        )
        for mode_data in config.get("modes", []):
            mode_id = f"symbolic_mode_{str(mode_data['name']).lower()}"
            self._write(
                """
                MATCH (module:SymbolicModule:GridCore {id: 'symbolic_logic'})
                MERGE (mode:SymbolicMode:GridCore {id: $mode_id})
                SET mode.name = $name,
                    mode.engine = $engine,
                    mode.source_file = $yaml_uri,
                    mode.subgraph = 'grid_core',
                    mode.domain = 'mostar_grid'
                MERGE (module)-[:HAS_MODE]->(mode)
                """,
                {
                    "mode_id": mode_id,
                    "name": mode_data.get("name"),
                    "engine": mode_data.get("engine"),
                    "yaml_uri": yaml_uri,
                },
            )
            for rule_entry in mode_data.get("rules", []):
                if "fact" in rule_entry:
                    self._write(
                        """
                        MATCH (mode:SymbolicMode:GridCore {id: $mode_id})
                        MERGE (fact:SymbolicFact:GridCore {raw_text: $raw_text})
                        SET fact.mode = 'Prolog',
                            fact.source_file = $yaml_uri,
                            fact.subgraph = 'grid_core',
                            fact.domain = 'mostar_grid'
                        MERGE (mode)-[:HAS_FACT]->(fact)
                        """,
                        {
                            "mode_id": mode_id,
                            "raw_text": rule_entry["fact"],
                            "yaml_uri": yaml_uri,
                        },
                    )
                if "rule" in rule_entry:
                    self._write(
                        """
                        MATCH (mode:SymbolicMode:GridCore {id: $mode_id})
                        MERGE (rule:SymbolicRule:GridCore {raw_text: $raw_text})
                        SET rule.mode = 'Prolog',
                            rule.source_file = $yaml_uri,
                            rule.subgraph = 'grid_core',
                            rule.domain = 'mostar_grid'
                        MERGE (mode)-[:HAS_RULE]->(rule)
                        """,
                        {
                            "mode_id": mode_id,
                            "raw_text": rule_entry["rule"],
                            "yaml_uri": yaml_uri,
                        },
                    )
            for expression_entry in mode_data.get("expressions", []):
                if "function" not in expression_entry:
                    continue
                self._write(
                    """
                    MATCH (mode:SymbolicMode:GridCore {id: $mode_id})
                    MERGE (fn:LispFunction:GridCore {code: $code})
                    SET fn.mode = 'Lisp',
                        fn.source_file = $yaml_uri,
                        fn.subgraph = 'grid_core',
                        fn.domain = 'mostar_grid'
                    MERGE (mode)-[:HAS_FUNCTION]->(fn)
                    """,
                    {
                        "mode_id": mode_id,
                        "code": expression_entry["function"],
                        "yaml_uri": yaml_uri,
                    },
                )
        for entry_group in config.get("entry_points", []):
            for example in entry_group.get("examples", []):
                self._write(
                    """
                    MATCH (module:SymbolicModule:GridCore {id: 'symbolic_logic'})
                    MERGE (ep:SymbolicEntryPoint:GridCore {input: $input})
                    SET ep.type = $entry_type,
                        ep.output = $output,
                        ep.source_file = $yaml_uri,
                        ep.subgraph = 'grid_core',
                        ep.domain = 'mostar_grid'
                    MERGE (module)-[:HAS_ENTRY_POINT]->(ep)
                    """,
                    {
                        "input": example.get("input"),
                        "output": example.get("output"),
                        "entry_type": entry_group.get("type"),
                        "yaml_uri": yaml_uri,
                    },
                )
        counts = self.status()
        return {"yaml_uri": yaml_uri, "counts": counts, "steps": summary}

    def _load_symbolic_source(self, yaml_uri: str) -> dict[str, Any]:
        yaml_path = self._resolve_yaml_path(yaml_uri)
        text = yaml_path.read_text(encoding="utf-8")
        if yaml is not None:
            parsed = yaml.safe_load(text)
            if isinstance(parsed, dict) and "symbolic_logic" in parsed:
                return {"symbolic_logic": parsed["symbolic_logic"], "path": yaml_path}
        return {
            "symbolic_logic": self._manual_parse_symbolic_yaml(text),
            "path": yaml_path,
        }

    def _resolve_yaml_path(self, yaml_uri: str) -> Path:
        candidate = yaml_uri.strip()
        if candidate.startswith("file:///"):
            filename = Path(candidate.replace("file:///", "")).name
            local_candidate = DEFAULT_SYMBOLIC_YAML_PATH.parent / filename
            if local_candidate.exists():
                return local_candidate
        direct = Path(candidate)
        if direct.exists():
            return direct
        return DEFAULT_SYMBOLIC_YAML_PATH

    def _manual_parse_symbolic_yaml(self, text: str) -> dict[str, Any]:
        version_match = re.search(r"version:\s*([^\n]+)", text)
        description_match = re.search(r"description:\s*(.*?)\n\s*modes:", text, re.S)
        prolog_match = re.search(
            r"-\s*name:\s*Prolog(.*?)\n\s*-\s*name:\s*Lisp", text, re.S
        )
        lisp_match = re.search(r"-\s*name:\s*Lisp(.*?)\n\s*entry_points:", text, re.S)
        entry_match = re.search(r"entry_points:\s*(.*)$", text, re.S)
        version = version_match.group(1).strip() if version_match else "1.0.0"
        description = " ".join(
            line.strip()
            for line in (
                description_match.group(1) if description_match else ""
            ).splitlines()
        ).strip()
        prolog_rules: list[dict[str, str]] = []
        for match in re.finditer(
            r"-\s+(fact|rule):\s*(.+)", prolog_match.group(1) if prolog_match else ""
        ):
            prolog_rules.append({match.group(1): match.group(2).strip()})
        lisp_functions: list[dict[str, str]] = []
        for match in re.finditer(
            r'-\s+function:\s+"((?:[^"\\]|\\.|\n)*?)"',
            lisp_match.group(1) if lisp_match else "",
            re.S,
        ):
            code = bytes(match.group(1), "utf-8").decode("unicode_escape")
            lisp_functions.append({"function": code})
        examples: list[dict[str, str]] = []
        for match in re.finditer(
            r"-\s+input:\s*(.+?)\n\s+output:\s*'([^']*)'",
            entry_match.group(1) if entry_match else "",
            re.S,
        ):
            examples.append({"input": match.group(1).strip(), "output": match.group(2)})
        return {
            "version": version,
            "description": description,
            "modes": [
                {"name": "Prolog", "engine": "rule-based", "rules": prolog_rules},
                {
                    "name": "Lisp",
                    "engine": "symbolic-recursion",
                    "expressions": lisp_functions,
                },
            ],
            "entry_points": [{"type": "query", "examples": examples}],
        }

    def status(self) -> dict[str, Any]:
        counts = self._read(
            """
            CALL {
              MATCH (n:SymbolicModule)
              RETURN count(n) AS symbolic_modules
            }
            CALL {
              MATCH (n:SymbolicMode)
              RETURN count(n) AS symbolic_modes
            }
            CALL {
              MATCH (n:SymbolicFact)
              RETURN count(n) AS symbolic_facts
            }
            CALL {
              MATCH (n:SymbolicRule)
              RETURN count(n) AS symbolic_rules
            }
            CALL {
              MATCH (n:LispFunction)
              RETURN count(n) AS lisp_functions
            }
            CALL {
              MATCH (n:SymbolicEntryPoint)
              RETURN count(n) AS symbolic_entry_points
            }
            RETURN symbolic_modules,
                   symbolic_modes,
                   symbolic_facts,
                   symbolic_rules,
                   lisp_functions,
                   symbolic_entry_points
             """
        )
        return counts[0] if counts else {}

    def _load_facts(self) -> list[Fact]:
        rows = self._read(
            "MATCH (n:SymbolicFact) RETURN n.raw_text AS raw_text ORDER BY raw_text"
        )
        facts: list[Fact] = []
        for row in rows:
            parsed = self._parse_fact(row["raw_text"])
            if parsed is not None:
                facts.append(parsed)
        facts.extend(self._dynamic_trust_facts())
        return facts

    def _load_rules(self) -> list[Rule]:
        rows = self._read(
            "MATCH (n:SymbolicRule) RETURN n.raw_text AS raw_text ORDER BY raw_text"
        )
        rules: list[Rule] = []
        for row in rows:
            parsed = self._parse_rule(row["raw_text"])
            if parsed is not None:
                rules.append(parsed)
        return rules

    def _load_lisp_functions(self) -> list[str]:
        rows = self._read(
            "MATCH (n:LispFunction) WHERE n.code IS NOT NULL RETURN DISTINCT n.code AS code ORDER BY n.code"
        )
        return [row["code"] for row in rows if row.get("code")]

    def _dynamic_trust_facts(self) -> list[Fact]:
        rows = self._read(
            """
            MATCH (a)-[r:TRUSTS]->(b)
            RETURN coalesce(a.id, a.name, toString(id(a))) AS source,
                   coalesce(b.id, b.name, toString(id(b))) AS target
            """
        )
        return [
            Fact(
                predicate="trust",
                args=[row["source"], row["target"]],
                raw_text=f"trust({row['source']}, {row['target']}).",
            )
            for row in rows
        ]

    def prove(self, query: str) -> dict[str, Any]:
        goal = self._parse_query(query)
        query_variables = [arg for arg in goal[1] if self._is_variable(arg)]
        facts = self._load_facts()
        rules = self._load_rules()
        proofs = list(self._prove_goal(goal, {}, facts, rules, depth=0, max_depth=25))
        formatted = []
        for bindings, proof in proofs:
            result_bindings = {
                var: self._resolve_value(var, bindings) for var in query_variables
            }
            formatted.append({"bindings": result_bindings, "proof": proof})
        return {"query": query, "results": formatted, "count": len(formatted)}

    def eval_lisp(self, program: str) -> dict[str, Any]:
        evaluator = LispEvaluator(self._read)
        for function_code in self._load_lisp_functions():
            evaluator.eval_string(function_code)
        result = evaluator.eval_string(program)
        return {"query": program, "result": result}

    def _parse_fact(self, raw_text: str) -> Fact | None:
        text = raw_text.strip()
        if text.endswith("."):
            text = text[:-1]
        match = re.fullmatch(r"([a-zA-Z_][\w-]*)\((.*)\)", text)
        if not match:
            return None
        predicate = match.group(1)
        args = [part.strip() for part in self._split_arguments(match.group(2))]
        return Fact(predicate=predicate, args=args, raw_text=raw_text)

    def _parse_rule(self, raw_text: str) -> Rule | None:
        text = raw_text.strip()
        if text.endswith("."):
            text = text[:-1]
        if ":-" not in text:
            return None
        head_text, body_text = [part.strip() for part in text.split(":-", 1)]
        head_fact = self._parse_fact(head_text + ".")
        if head_fact is None:
            return None
        body_goals: list[tuple[str, list[str]]] = []
        for chunk in self._split_top_level(body_text):
            piece = chunk.strip()
            if "\\=" in piece:
                left, right = [side.strip() for side in piece.split("\\=", 1)]
                body_goals.append(("neq", [left, right]))
                continue
            parsed = self._parse_fact(piece + ".")
            if parsed is None:
                continue
            body_goals.append((parsed.predicate, parsed.args))
        return Rule(
            head_predicate=head_fact.predicate,
            head_args=head_fact.args,
            body=body_goals,
            raw_text=raw_text,
        )

    def _parse_query(self, query: str) -> tuple[str, list[str]]:
        text = query.strip()
        if text.startswith("?-"):
            text = text[2:].strip()
        if text.endswith("."):
            text = text[:-1]
        parsed = self._parse_fact(text + ".")
        if parsed is None:
            raise ValueError(f"Invalid Prolog query: {query}")
        return parsed.predicate, parsed.args

    def _split_arguments(self, value: str) -> list[str]:
        return [part.strip() for part in self._split_top_level(value)] if value else []

    def _split_top_level(self, value: str) -> list[str]:
        parts: list[str] = []
        buffer: list[str] = []
        depth = 0
        for char in value:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            if char == "," and depth == 0:
                parts.append("".join(buffer).strip())
                buffer = []
                continue
            buffer.append(char)
        if buffer:
            parts.append("".join(buffer).strip())
        return parts

    def _is_variable(self, term: str) -> bool:
        return bool(term) and (term[0].isupper() or term.startswith("_"))

    def _resolve_value(self, term: str, bindings: dict[str, str]) -> str:
        current = term
        seen: set[str] = set()
        while (
            self._is_variable(current) and current in bindings and current not in seen
        ):
            seen.add(current)
            current = bindings[current]
        return current

    def _unify_term(
        self, left: str, right: str, bindings: dict[str, str]
    ) -> dict[str, str] | None:
        left_value = self._resolve_value(left, bindings)
        right_value = self._resolve_value(right, bindings)
        if left_value == right_value:
            return bindings
        if self._is_variable(left_value):
            bindings[left_value] = right_value
            return bindings
        if self._is_variable(right_value):
            bindings[right_value] = left_value
            return bindings
        return None

    def _unify_goals(
        self,
        left_predicate: str,
        left_args: list[str],
        right_predicate: str,
        right_args: list[str],
        bindings: dict[str, str],
    ) -> dict[str, str] | None:
        if left_predicate != right_predicate or len(left_args) != len(right_args):
            return None
        working = dict(bindings)
        for left_arg, right_arg in zip(left_args, right_args):
            updated = self._unify_term(left_arg, right_arg, working)
            if updated is None:
                return None
            working = updated
        return working

    def _standardize_rule(self, rule: Rule) -> Rule:
        self._rule_counter += 1
        suffix = f"__{self._rule_counter}"
        mapping: dict[str, str] = {}

        def rename(term: str) -> str:
            if not self._is_variable(term):
                return term
            if term not in mapping:
                mapping[term] = f"{term}{suffix}"
            return mapping[term]

        return Rule(
            head_predicate=rule.head_predicate,
            head_args=[rename(arg) for arg in rule.head_args],
            body=[
                (predicate, [rename(arg) for arg in args])
                for predicate, args in rule.body
            ],
            raw_text=rule.raw_text,
        )

    def _prove_goal(
        self,
        goal: tuple[str, list[str]],
        bindings: dict[str, str],
        facts: list[Fact],
        rules: list[Rule],
        depth: int,
        max_depth: int,
    ):
        if depth > max_depth:
            return
        predicate, args = goal
        resolved_args = [self._resolve_value(arg, bindings) for arg in args]
        if predicate == "neq":
            if len(resolved_args) == 2 and resolved_args[0] != resolved_args[1]:
                yield (
                    dict(bindings),
                    {"type": "builtin", "predicate": "neq", "args": resolved_args},
                )
            return
        for fact in facts:
            unified = self._unify_goals(
                predicate, resolved_args, fact.predicate, fact.args, bindings
            )
            if unified is not None:
                yield (
                    unified,
                    {
                        "type": "fact",
                        "predicate": fact.predicate,
                        "args": fact.args,
                        "raw_text": fact.raw_text,
                    },
                )
        for rule in rules:
            standardized = self._standardize_rule(rule)
            unified = self._unify_goals(
                predicate,
                resolved_args,
                standardized.head_predicate,
                standardized.head_args,
                bindings,
            )
            if unified is None:
                continue
            for final_bindings, steps in self._prove_body(
                standardized.body,
                unified,
                facts,
                rules,
                depth + 1,
                max_depth,
            ):
                yield (
                    final_bindings,
                    {
                        "type": "rule",
                        "head": {
                            "predicate": standardized.head_predicate,
                            "args": standardized.head_args,
                            "raw_text": standardized.raw_text,
                        },
                        "steps": steps,
                    },
                )

    def _prove_body(
        self,
        goals: list[tuple[str, list[str]]],
        bindings: dict[str, str],
        facts: list[Fact],
        rules: list[Rule],
        depth: int,
        max_depth: int,
    ):
        if not goals:
            yield dict(bindings), []
            return
        first, rest = goals[0], goals[1:]
        for next_bindings, proof in self._prove_goal(
            first, dict(bindings), facts, rules, depth, max_depth
        ):
            for final_bindings, rest_proofs in self._prove_body(
                rest, next_bindings, facts, rules, depth, max_depth
            ):
                yield final_bindings, [proof, *rest_proofs]


class LispEvaluator:
    def __init__(
        self, read_query: Callable[[str, dict[str, Any] | None], list[dict[str, Any]]]
    ) -> None:
        self._read_query = read_query
        self._functions: dict[str, tuple[list[str], Any]] = {}
        self._base_env = {
            "+": lambda *values: sum(values),
            "-": self._subtract,
            "*": self._multiply,
            "/": self._divide,
            "<=": lambda left, right: left <= right,
            "<": lambda left, right: left < right,
            ">=": lambda left, right: left >= right,
            ">": lambda left, right: left > right,
            "equal": lambda left, right: left == right,
            "and": lambda *values: all(values),
            "list": lambda *values: list(values),
            "car": lambda values: values[0],
            "cdr": lambda values: values[1:],
            "cons": lambda head, tail: [head, *tail],
            "graph-query": self._graph_query,
        }

    def eval_string(self, program: str) -> Any:
        expression = self._parse(program)
        return self._eval(expression, dict(self._base_env))

    def _graph_query(self, query: str) -> list[dict[str, Any]]:
        return self._read_query(query, None)

    def _subtract(self, first: float, *rest: float) -> float:
        if not rest:
            return -first
        current = first
        for value in rest:
            current -= value
        return current

    def _multiply(self, *values: float) -> float:
        result = 1
        for value in values:
            result *= value
        return result

    def _divide(self, first: float, *rest: float) -> float:
        current = first
        for value in rest:
            current /= value
        return current

    def _tokenize(self, program: str) -> list[Any]:
        tokens: list[Any] = []
        i = 0
        while i < len(program):
            char = program[i]
            if char.isspace():
                i += 1
                continue
            if char in "()'":
                tokens.append(char)
                i += 1
                continue
            if char == '"':
                j = i + 1
                buffer: list[str] = []
                while j < len(program):
                    current = program[j]
                    if current == '"' and program[j - 1] != "\\":
                        break
                    buffer.append(current)
                    j += 1
                if j >= len(program):
                    raise ValueError("Unterminated string literal")
                tokens.append("".join(buffer))
                i = j + 1
                continue
            j = i
            while (
                j < len(program)
                and not program[j].isspace()
                and program[j] not in "()'"
            ):
                j += 1
            token = program[i:j]
            if re.fullmatch(r"-?\d+", token):
                tokens.append(int(token))
            elif re.fullmatch(r"-?\d+\.\d+", token):
                tokens.append(float(token))
            else:
                tokens.append(Symbol(token))
            i = j
        return tokens

    def _parse(self, program: str) -> Any:
        tokens = self._tokenize(program)

        def read_at(position: int) -> tuple[Any, int]:
            if position >= len(tokens):
                raise ValueError("Unexpected end of input")
            token = tokens[position]
            if token == "'":
                value, next_position = read_at(position + 1)
                return [Symbol("quote"), value], next_position
            if token == "(":
                values: list[Any] = []
                index = position + 1
                while index < len(tokens) and tokens[index] != ")":
                    value, index = read_at(index)
                    values.append(value)
                if index >= len(tokens):
                    raise ValueError("Missing closing parenthesis")
                return values, index + 1
            if token == ")":
                raise ValueError("Unexpected closing parenthesis")
            return token, position + 1

        expression, final_position = read_at(0)
        if final_position != len(tokens):
            raise ValueError("Unexpected trailing tokens")
        return expression

    def _quote(self, expression: Any) -> Any:
        if isinstance(expression, Symbol):
            return str(expression)
        if isinstance(expression, list):
            return [self._quote(item) for item in expression]
        return expression

    def _eval(self, expression: Any, env: dict[str, Any]) -> Any:
        if isinstance(expression, Symbol):
            if expression in env:
                return env[expression]
            if expression in self._functions:
                return expression
            return str(expression)
        if not isinstance(expression, list):
            return expression
        if not expression:
            return []
        operator = expression[0]
        if operator == Symbol("quote"):
            return self._quote(expression[1])
        if operator == Symbol("if"):
            condition, yes_branch, no_branch = (
                expression[1],
                expression[2],
                expression[3],
            )
            return (
                self._eval(yes_branch, env)
                if self._eval(condition, env)
                else self._eval(no_branch, env)
            )
        if operator == Symbol("cond"):
            for clause in expression[1:]:
                test = clause[0]
                body = clause[1]
                if test == Symbol("t") or self._eval(test, env):
                    return self._eval(body, env)
            return None
        if operator == Symbol("defun"):
            name = str(expression[1])
            params = [str(param) for param in expression[2]]
            body = expression[3]
            self._functions[name] = (params, body)
            return name
        evaluated_operator = self._eval(operator, env)
        evaluated_args = [self._eval(arg, env) for arg in expression[1:]]
        if (
            isinstance(evaluated_operator, Symbol)
            and evaluated_operator in self._functions
        ):
            params, body = self._functions[str(evaluated_operator)]
            child_env = dict(env)
            for param, arg in zip(params, evaluated_args):
                child_env[param] = arg
            return self._eval(body, child_env)
        if (
            isinstance(evaluated_operator, str)
            and evaluated_operator in self._functions
        ):
            params, body = self._functions[evaluated_operator]
            child_env = dict(env)
            for param, arg in zip(params, evaluated_args):
                child_env[param] = arg
            return self._eval(body, child_env)
        if callable(evaluated_operator):
            return evaluated_operator(*evaluated_args)
        raise ValueError(f"Cannot call operator: {evaluated_operator}")
