// ╔══════════════════════════════════════════════════════╗
// ║         MOSTAR GRID — PM2 ECOSYSTEM CONFIG           ║
// ║         The Grid's permanent breath on this machine  ║
// ╚══════════════════════════════════════════════════════╝

const ROOT = "C:\\Users\\idona\\OneDrive - World Health Organization\\Documents\\Dev\\MoStar-Grid";

module.exports = {
  apps: [
    {
      name: "mostar-backend",
      script: "C:\\Users\\idona\\OneDrive - World Health Organization\\Documents\\Dev\\MoStar-Grid\\.venv\\Scripts\\python.exe",
      args: "-m uvicorn main:app --host 0.0.0.0 --port 7001",
      cwd: "C:\\Users\\idona\\OneDrive - World Health Organization\\Documents\\Dev\\MoStar-Grid\\backend",
      watch: false,
      autorestart: true,
      restart_delay: 3000,
      max_restarts: 10,
      env: {
        PYTHONPATH: ROOT,
        PYTHONUNBUFFERED: "1",
        PYTHONUTF8: "1",
        PYTHONIOENCODING: "utf-8"
      },
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      out_file: `${ROOT}\\logs\\backend.out.log`,
      error_file: `${ROOT}\\logs\\backend.err.log`,
    },
    {
      name: "mostar-executor",
      script: "C:\\Users\\idona\\OneDrive - World Health Organization\\Documents\\Dev\\MoStar-Grid\\.venv\\Scripts\\python.exe",
      args: "mo_executor.py",
      cwd: "C:\\Users\\idona\\OneDrive - World Health Organization\\Documents\\Dev\\MoStar-Grid\\backend",
      watch: false,
      autorestart: true,
      restart_delay: 5000,
      max_restarts: 10,
      env: {
        PYTHONPATH: ROOT,
        PYTHONUNBUFFERED: "1",
        PYTHONUTF8: "1",
        PYTHONIOENCODING: "utf-8"
      },
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      out_file: `${ROOT}\\logs\\executor.out.log`,
      error_file: `${ROOT}\\logs\\executor.err.log`,
    }
  ]
};
