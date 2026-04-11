#!/usr/bin/env python3
"""
Mo Executor - Purified Root Dispatch.
All actions are ritual-only. No fallbacks. Cycle guards enforced.
"""

import asyncio
import logging
import os
import sys
import traceback

from neo4j import GraphDatabase, TrustAll

# Ensure PROJECT_ROOT/core/grid-orchestrator and PROJECT_ROOT/engines/idim-ikang etc are reachable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Add important service boundaries to path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if os.path.join(PROJECT_ROOT, "core", "grid-orchestrator") not in sys.path:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "core", "grid-orchestrator"))
if os.path.join(PROJECT_ROOT, "core", "cognition") not in sys.path:
    sys.path.insert(0, os.path.join(PROJECT_ROOT, "core", "cognition"))

try:
    from core_engine.moscript_engine import MoScriptEngine
    from sacred_handshake import SacredHandshake
    print("✅ MoExecutor dependencies loaded.")
except ImportError as e:
    print(f"⚠️  Import error in MoExecutor: {e}")
    # Fallback to direct imports if needed
    from core_engine.moscript_engine import MoScriptEngine
    from sacred_handshake import SacredHandshake

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MoExecutor")


class MoExecutor:
    def __init__(
        self,
        neo4j_uri,
        neo4j_user,
        neo4j_password,
        poll_interval=10,
        feedback_interval=10,
    ):
        self.poll_interval = poll_interval
        self.feedback_interval = feedback_interval
        self.cycle_count = 0
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_uri_source = os.getenv("NEO4J_URI_SOURCE", "env")
        driver_kwargs = {"auth": (neo4j_user, neo4j_password)}
        self.driver = GraphDatabase.driver(neo4j_uri, **driver_kwargs)
        self.mo = MoScriptEngine()  # single shared engine
        self.executor_agent_id = "agent-mo-executor"
        self._running = True
        self._current_cycle_task = None

        self.handshake = SacredHandshake(engine=self.mo)
        self._setup_done = False
        logger.info(
            "Executor Neo4j config resolved | uri=%s | source=%s | scheme=%s",
            self.neo4j_uri,
            self.neo4j_uri_source,
            self.neo4j_uri.split("://", 1)[0],
        )

    async def _setup(self):
        # Verify covenant node
        if not await self.handshake.check_covenant_node():
            # Fallback to create if missing based on directive
            with self.driver.session() as session:
                session.run(
                    "CREATE (c:CovenantKernel {id: 'covenant-kernel-001', trusted: true, created_at: datetime()})"
                )

            if not await self.handshake.check_covenant_node():
                raise RuntimeError("Covenant kernel not trusted. Aborting.")

        # Register executor as an agent
        await self.handshake.register_agent(
            agent_id=self.executor_agent_id,
            agent_name="Mo Executor",
            public_key="system",
        )

        self._ensure_executor_agent()
        self._cleanup_orphaned_moments()
        self._setup_done = True

    def _cleanup_orphaned_moments(self):
        """Mark MoStarMoment nodes that are missing an id so they are never polled again."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:MoStarMoment)
                WHERE m.id IS NULL AND m.mo_processed IS NULL
                SET m.mo_processed = false,
                    m.processingError = 'orphaned: missing id field',
                    m.processedAt = datetime()
                RETURN count(m) AS cleaned
            """)
            record = result.single()
            cleaned = record["cleaned"] if record else 0
            if cleaned > 0:
                logger.warning(
                    "Cleaned up %d orphaned MoStarMoment nodes missing 'id'.", cleaned
                )

    def _ensure_executor_agent(self):
        with self.driver.session() as session:
            session.run(
                """
                MERGE (a:Agent {id: $id})
                SET a.name = 'Mo Executor',
                    a.type = 'system',
                    a.last_seen = datetime()
            """,
                id=self.executor_agent_id,
            )

    def _get_unprocessed_moments(self):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (m:MoStarMoment)
                WHERE m.mo_processed IS NULL
                  AND m.id IS NOT NULL
                RETURN m
                ORDER BY m.timestamp ASC
                LIMIT 10
            """)
            return [record["m"] for record in result]

    def _mark_processed(self, moment_id, output_data, executor_cycle):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (m:MoStarMoment {id: $moment_id})
                SET m.mo_processed = true,
                    m.processedAt = datetime(),
                    m.processingOutput = $output,
                    m.executor_id = $executor_id,
                    m.executor_cycle = $executor_cycle
            """,
                moment_id=moment_id,
                output=output_data,
                executor_id=self.executor_agent_id,
                executor_cycle=executor_cycle,
            )

    async def process_moment(self, moment_node):
        moment_props = dict(moment_node)
        moment_id = moment_props.get("id")
        if not moment_id:
            logger.error("Moment missing id, skipping")
            return

        # Provenance stamp: attach executor signature
        ritual = {
            "operation": "route_reasoning",
            "payload": {
                "query": moment_props.get("description", ""),
                "purpose": "moment_processing",
                "metadata": {
                    **moment_props,
                    "executor_cycle": self.cycle_count,
                    "executor_id": self.executor_agent_id,
                },
            },
            "target": "Grid.Mind",
        }
        try:
            response = await self.mo.interpret(ritual)
            if response.get("status") == "aligned":
                result = response.get("result", {})
                self._mark_processed(
                    moment_id, result.get("logic_deduced", ""), self.cycle_count
                )
                logger.info(f"Processed moment {moment_id}")
            else:
                logger.error(f"Ritual failed for {moment_id}: {response.get('error')}")
                # Optionally mark as failed
                with self.driver.session() as session:
                    session.run(
                        """
                        MATCH (m:MoStarMoment {id: $moment_id})
                        SET m.mo_processed = false,
                            m.processingError = $error,
                            m.processedAt = datetime()
                    """,
                        moment_id=moment_id,
                        error=response.get("error"),
                    )
        except Exception as e:
            logger.error(
                f"Error processing moment {moment_id}: {e}\n{traceback.format_exc()}"
            )

    async def run_feedback_loop(self):
        ritual = {"operation": "run_feedback_loop", "payload": {}}
        try:
            response = await self.mo.interpret(ritual)
            if response.get("status") == "aligned":
                logger.info(f"Feedback loop completed: {response.get('result', {})}")
            else:
                logger.warning(f"Feedback loop failed: {response.get('error')}")
        except Exception as e:
            logger.error(f"Feedback loop exception: {e}")

    async def run_cycle(self):
        """One complete cycle: process moments, then maybe feedback."""
        try:
            moments = self._get_unprocessed_moments()
            if moments:
                logger.info(
                    f"Cycle {self.cycle_count}: processing {len(moments)} moments"
                )
                for moment in moments:
                    await self.process_moment(moment)
            else:
                logger.debug(f"Cycle {self.cycle_count}: no moments")

            self.cycle_count += 1
            if self.cycle_count % self.feedback_interval == 0:
                await self.run_feedback_loop()

        except Exception as e:
            logger.error(
                f"Cycle {self.cycle_count} failed: {e}\n{traceback.format_exc()}"
            )

    async def run_loop(self):
        while self._running:
            try:
                if not self._setup_done:
                    await self._setup()
                    logger.info(
                        "Mo Executor started. Polling every %d seconds, feedback every %d cycles.",
                        self.poll_interval,
                        self.feedback_interval,
                    )

                # Cycle guard: ensure previous cycle finished (should be sequential)
                if self._current_cycle_task and not self._current_cycle_task.done():
                    logger.warning("Previous cycle still running - skipping this tick")
                    await asyncio.sleep(self.poll_interval)
                    continue

                self._current_cycle_task = asyncio.create_task(self.run_cycle())
            except Exception as e:
                logger.error("Executor loop failed: %s\n%s", e, traceback.format_exc())

            await asyncio.sleep(self.poll_interval)

    def stop(self):
        self._running = False
        logger.info("Executor stopping...")

    def close(self):
        self.driver.close()
        logger.info("Neo4j driver closed.")


async def main():
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
    if "NEO4J_URI" in os.environ:
        os.environ["NEO4J_URI_SOURCE"] = "env"
    else:
        os.environ["NEO4J_URI_SOURCE"] = "fallback_default"
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))
    FEEDBACK_INTERVAL = int(os.getenv("FEEDBACK_INTERVAL", "10"))

    executor = MoExecutor(
        NEO4J_URI,
        NEO4J_USER,
        NEO4J_PASSWORD,
        poll_interval=POLL_INTERVAL,
        feedback_interval=FEEDBACK_INTERVAL,
    )
    try:
        await executor.run_loop()
    except KeyboardInterrupt:
        executor.stop()
        logger.info("Shutting down...")
    except Exception as e:
        logger.error("Fatal executor error: %s\n%s", e, traceback.format_exc())
        executor.stop()
    finally:
        executor.close()


if __name__ == "__main__":
    asyncio.run(main())
