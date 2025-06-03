import logging
from pathlib import Path

def find_project_root(marker="pyproject.toml") -> Path:
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / marker).exists():
            return current
        current = current.parent
    raise RuntimeError(f"Project root with {marker} not found.")

PROJECT_ROOT = find_project_root()
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "remedia.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_logger(name="ReMedia"):
    return logging.getLogger(name)
