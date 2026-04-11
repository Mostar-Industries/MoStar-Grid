// ╔══════════════════════════════════════════════════════╗
// ║         MOSTAR GRID — PM2 ECOSYSTEM CONFIG           ║
// ║         The Grid's permanent breath on this machine  ║
// ╚══════════════════════════════════════════════════════╝

const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const LOGS = path.join(ROOT, "logs");
const CONFIG_ENV_FILE = path.join(ROOT, "config", ".env");
const PYTHON_BIN = fs.existsSync(path.join(ROOT, ".venv-wsl", "bin", "python"))
  ? path.join(ROOT, ".venv-wsl", "bin", "python")
  : "/usr/bin/python3";

function parseEnv(filePath) {
  if (!fs.existsSync(filePath)) {
    return {};
  }

  return fs
    .readFileSync(filePath, "utf8")
    .split(/\r?\n/)
    .reduce((acc, line) => {
      const trimmed = line.trim();

      if (!trimmed || trimmed.startsWith("#")) {
        return acc;
      }

      const separatorIndex = trimmed.indexOf("=");

      if (separatorIndex === -1) {
        return acc;
      }

      const key = trimmed.slice(0, separatorIndex).trim();
      let value = trimmed.slice(separatorIndex + 1).trim();

      if (
        (value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))
      ) {
        value = value.slice(1, -1);
      }

      acc[key] = value;
      return acc;
    }, {});
}

// Ensure PM2 sets PYTHONPATH so modules resolve instantly without bash wrappers.
const backendEnv = {
  ...parseEnv(CONFIG_ENV_FILE),
  PYTHONPATH: `${ROOT}:${path.join(ROOT, "core", "grid-orchestrator")}:${path.join(ROOT, "core", "cognition")}:${path.join(ROOT, "engines", "idim-ikang")}:${path.join(ROOT, "memory", "neo4j-mindgraph")}`,
  PYTHONUNBUFFERED: "1",
  PYTHONUTF8: "1",
  PYTHONIOENCODING: "utf-8",
  OLLAMA_HOST: "http://127.0.0.1:11434",
  NEO4J_URI: "bolt://127.0.0.1:7687",
  NEO4J_USER: "neo4j",
  REDIS_URL: "redis://127.0.0.1:6379",
};

const frontendEnv = {
  GRID_API_BASE: "http://127.0.0.1:8001",
  CONSCIOUSNESS_API_BASE: "http://127.0.0.1:8001",
  NEXT_PUBLIC_API_URL: "http://127.0.0.1:8001",
  NEO4J_URI: "bolt://127.0.0.1:7687",
  NEO4J_USER: "neo4j",
  NEO4J_PASSWORD: backendEnv.NEO4J_PASSWORD || "",
  OLLAMA_API_URL: "http://127.0.0.1:11434",
  HOSTNAME: "0.0.0.0",
  PORT: "3000",
};

const cloudflaredEnv = {
  CLOUDFLARED_BIN: "/mnt/c/Users/idona/Desktop/cloudflared-windows-amd64.exe",
  CLOUDFLARED_CONFIG: path.join(ROOT, "cloudflared", "config-direct.yml"),
  ...(process.env.CLOUDFLARED_TOKEN ? { CLOUDFLARED_TOKEN: process.env.CLOUDFLARED_TOKEN } : {}),
};

const ollamaEnv = {
  OLLAMA_HOST: "127.0.0.1:11434",
  OLLAMA_HOME: path.join(ROOT, ".ollama"),
  OLLAMA_MODELS: path.join(ROOT, ".ollama", "models"),
};

module.exports = {
  apps: [
    {
      name: "mostar-ollama",
      script: "/bin/bash",
      args: path.join(ROOT, "scripts", "run-ollama.sh"),
      cwd: ROOT,
      interpreter: "none",
      watch: false,
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      env: ollamaEnv,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      out_file: path.join(LOGS, "ollama.out.log"),
      error_file: path.join(LOGS, "ollama.err.log"),
    },
    {
      name: "mostar-api-ingress",
      script: PYTHON_BIN,
      args: path.join(ROOT, "core", "mostar-api", "main.py"),
      cwd: ROOT,
      interpreter: "none",
      watch: false,
      autorestart: true,
      restart_delay: 3000,
      max_restarts: 10,
      env: backendEnv,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      out_file: path.join(LOGS, "api-ingress.out.log"),
      error_file: path.join(LOGS, "api-ingress.err.log"),
    },
    {
      name: "mostar-orchestrator",
      script: PYTHON_BIN,
      args: path.join(ROOT, "core", "grid-orchestrator", "mo_executor.py"),
      cwd: ROOT,
      interpreter: "none",
      watch: false,
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      env: backendEnv,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      out_file: path.join(LOGS, "executor.out.log"),
      error_file: path.join(LOGS, "executor.err.log"),
    },
    {
      name: "mostar-frontend",
      script: "/bin/bash",
      args: path.join(ROOT, "scripts", "run-frontend.sh"),
      cwd: path.join(ROOT, "frontend"),
      interpreter: "none",
      watch: false,
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      env: frontendEnv,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      out_file: path.join(LOGS, "frontend.out.log"),
      error_file: path.join(LOGS, "frontend.err.log"),
    },
    {
      name: "mostar-cloudflared",
      script: "/bin/bash",
      args: path.join(ROOT, "scripts", "run-cloudflared.sh"),
      cwd: ROOT,
      interpreter: "none",
      watch: false,
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      env: cloudflaredEnv,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      out_file: path.join(LOGS, "cloudflared.out.log"),
      error_file: path.join(LOGS, "cloudflared.err.log"),
    },
  ],
};
