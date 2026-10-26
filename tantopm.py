"""
TANTO Process Manager (TPM)
Monitors BF2142_w32ded.exe and restarts it if it crashes.
Fully standalone - does not require TCD.
"""
import asyncio
import subprocess
import time
import yaml
from collections import deque
from pathlib import Path
import psutil
from loguru import logger

# --- Default Settings ---
DEFAULT_EXE = r"C:\Path\To\BF2142_w32ded.exe"
DEFAULT_WORK = r"C:\Path\To\BF2142"
DEFAULT_ARGS = ["+config", "mods/bf2142/settings/serversettings.con", "+maplist", "mods/bf2142/settings/maplist.con", "+dedicated"]


def load_config(config_path: str = "config.yaml"):
    """Reads configuration from config.yaml."""
    path = Path(config_path)
    if not path.exists():
        logger.warning(f"Config not found at {config_path}. Using defaults.")
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to parse config.yaml: {e}")
        return {}


class ProcessManager:
    def __init__(self, process_cfg):
        self.enabled = process_cfg.get("enabled", True)
        self.exe_path = process_cfg.get("exe_path", DEFAULT_EXE)
        self.work_dir = process_cfg.get("work_dir", DEFAULT_WORK)
        self.args = process_cfg.get("args", DEFAULT_ARGS)
        self.check_interval = process_cfg.get("check_interval_sec", 10)
        self.restart_delay = process_cfg.get("restart_delay_sec", 15)
        self.max_restarts = process_cfg.get("max_restarts_per_hour", 5)
        self.stdout_log = process_cfg.get("stdout_log", "logs/bf2142_stdout.log")
        
        self.proc = None
        self._restarts = deque()
        self._stdout_file = None

    def _is_alive(self) -> bool:
        """Checks if the server process is running."""
        exe_name = Path(self.exe_path).name.lower()
        for p in psutil.process_iter(["name"]):
            try:
                if p.info["name"] and p.info["name"].lower() == exe_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def _can_restart(self) -> bool:
        """Checks the hourly restart limit."""
        now = time.time()
        while self._restarts and now - self._restarts[0] > 3600:
            self._restarts.popleft()
        return len(self._restarts) < self.max_restarts

    def _start_process(self) -> bool:
        """Launches the server executable."""
        exe = Path(self.exe_path)
        work = Path(self.work_dir) if self.work_dir else exe.parent

        if not exe.exists():
            logger.error(f"Executable not found at: {exe}")
            return False

        log_path = Path(self.stdout_log)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self._stdout_file = log_path.open("a", encoding="utf-8", errors="ignore")

        try:
            self.proc = subprocess.Popen(
                [str(exe), *self.args],
                cwd=str(work),
                stdout=self._stdout_file,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            logger.info(f"Server started (PID: {self.proc.pid})")
            self._restarts.append(time.time())
            return True
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False

    async def monitor_loop(self):
        """Main loop for monitoring and restarting."""
        if not self.enabled:
            logger.info("Process Manager is disabled in config. Exiting.")
            return

        logger.info(f"TPM started. Watching {Path(self.exe_path).name} every {self.check_interval}s.")
        
        while True:
            await asyncio.sleep(self.check_interval)

            if self._is_alive():
                continue

            logger.warning("Game server is down!")
            
            if not self._can_restart():
                logger.error(f"Restart limit reached ({self.max_restarts}/hour). Waiting 1 hour...")
                await asyncio.sleep(3600)
                self._restarts.clear()
                continue

            logger.info(f"Waiting {self.restart_delay}s before restarting...")
            await asyncio.sleep(self.restart_delay)

            if self._is_alive():
                logger.info("Server was started manually. Skipping auto-restart.")
                continue

            if self._start_process():
                logger.info("Server restarted successfully.")


async def main():
    cfg = load_config("config.yaml")
    
    # Setup logging from config
    log_cfg = cfg.get("logging", {})
    log_level = log_cfg.get("level", "INFO")
    log_file = log_cfg.get("file", "logs/tpm.log")
    
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger.add(log_file, level=log_level, rotation="10 MB", retention="5 days")
    
    # Start PM
    process_cfg = cfg.get("process", {})
    pm = ProcessManager(process_cfg)
    await pm.monitor_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("TPM stopped by user.")