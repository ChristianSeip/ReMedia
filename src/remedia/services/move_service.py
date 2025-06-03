from pathlib import Path
import shutil
from tqdm import tqdm
from remedia.core.constants import DEFAULT_MEDIA_DIR
from remedia.utils.logger import get_logger

logger = get_logger(__name__)

class MoveService:
    def __init__(self, source_dir: Path):
        self.source_dir = source_dir.resolve()
        self.default_dir = DEFAULT_MEDIA_DIR.resolve()
        self.duplicates_base = (
            Path("duplicates") if self.source_dir == self.default_dir
            else self.source_dir.parent / "duplicates"
        )
        self.duplicates_base.mkdir(exist_ok=True)

    def move_all(self, groups: list[list]):
        for index, group in enumerate(tqdm(groups, desc="Moving duplicate media")):
            self.move_group(group, index)

    def move_group(self, group: list, index: int):
        if not group:
            return

        base_name = f"group_{index:04d}"
        target_dir = self.duplicates_base / base_name
        target_dir.mkdir(exist_ok=True)

        for media in group:
            try:
                target = target_dir / media.path.name
                if media.path.exists():
                    shutil.move(str(media.path), str(target))
                    logger.info(f"Moved {media.path.name} → {target}")
            except Exception as e:
                logger.warning(f"Failed to move {media.path.name}: {e}")
