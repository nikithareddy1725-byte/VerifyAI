import logging
import sys
from datetime import datetime

class AgentLogger:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"VerifyAI.{agent_name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str, exc: Exception = None):
        if exc:
            self.logger.error(f"{message} - Exception: {exc}", exc_info=True)
        else:
            self.logger.error(message)

    def agent_start(self, task_id: str):
        self.info(f"[{self.agent_name}] started for task={task_id}")

    def agent_complete(self, task_id: str, summary: str = ""):
        self.info(f"[{self.agent_name}] completed for task={task_id}: {summary}")

    def agent_fail(self, task_id: str, error: str = ""):
        self.error(f"[{self.agent_name}] failed for task={task_id}: {error}")
