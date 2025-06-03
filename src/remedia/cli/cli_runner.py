from remedia.core.constants import ACCURACY_STEPS, DEFAULT_TOLERANCE, ACCURACY_TO_RELATED_THRESHOLD
from remedia.cli.input_handler import get_detection_engine, get_media_dir, get_tolerance
from remedia.cli.output_handler import (
    print_start_info,
    print_group_summary,
    print_welcome,
    print_no_duplicates,
)
from remedia.services.group_service import GroupService
from remedia.services.move_service import MoveService
from remedia.utils.loader import load_valid_images

logger = None

def run_cli():
    print_welcome()

    global logger
    if logger is None:
        from remedia.utils.logger import get_logger
        logger = get_logger(__name__)

    media_dir = get_media_dir()
    if not media_dir:
        return

    tolerance = get_tolerance()
    engine_choice = get_detection_engine()

    hash_tolerance = ACCURACY_STEPS.get(tolerance, DEFAULT_TOLERANCE)
    related_threshold = ACCURACY_TO_RELATED_THRESHOLD.get(tolerance, 0.90)

    if engine_choice == 2:
        from remedia.engines.related_engine import RelatedEngine
        engine = RelatedEngine(threshold=related_threshold)
    else:
        from remedia.engines.hash_engine import HashEngine
        engine = HashEngine(tolerance=hash_tolerance)

    media_files = load_valid_images(media_dir)
    print_start_info(len(media_files))

    engine.compute_features(media_files)
    groups = GroupService(engine, strict_mode=engine_choice==2).find_duplicates(media_files)

    if groups:
        print_group_summary(groups)
        MoveService(media_dir).move_all(groups)
        logger.info("All groups have been moved.")
    else:
        print_no_duplicates()
        logger.info("No duplicates to move.")
