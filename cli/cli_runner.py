from cli.input_handler import get_media_dir, get_tolerance
from cli.output_handler import (
    print_start_info,
    print_group_summary,
    print_welcome,
    print_no_duplicates,
)
from services.group_service import GroupService
from services.move_service import MoveService
from engines.hash_engine import HashEngine
from utils.loader import load_valid_images
from utils.logger import get_logger

logger = get_logger(__name__)

def run_cli():
    print_welcome()

    media_dir = get_media_dir()
    if not media_dir:
        return

    tolerance = get_tolerance()
    media_files = load_valid_images(media_dir)
    print_start_info(len(media_files))
    engine = HashEngine(tolerance)
    engine.compute_hashes(media_files)
    groups = GroupService(engine).find_duplicates(media_files)

    if groups:
        print_group_summary(groups)
        MoveService(media_dir).move_all(groups)
        logger.info("All groups have been moved.")
    else:
        print_no_duplicates()
        logger.info("No duplicates to move.")