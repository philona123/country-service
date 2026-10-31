import logging
import sys
def configure_logging(level: str = "INFO") -> None:
    log_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)
    
    for name in (
        "httpx",
        "httpcore",
        "pymongo",
        "uvicorn.access",
        "apscheduler",
        "watchfiles",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)