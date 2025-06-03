import logging
from pathlib import Path
from functools import lru_cache

@lru_cache(maxsize=1)
def get_logger(name="ReMedia"):
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            project_root = current
            break
        current = current.parent
    else:
        raise RuntimeError("Project root with pyproject.toml not found.")

    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "remedia.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(name)
