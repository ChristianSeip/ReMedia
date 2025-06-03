from utils.logger import get_logger

logger = get_logger(__name__)

def print_group_summary(groups: list):
    print(f"{len(groups)} duplicate group{'s' if len(groups) != 1 else ''} detected.")
    for i, group in enumerate(groups, start=1):
        print(f"\nGroup {i}:")
        for media in group:
            print(f" - {media.path.name}")

def print_start_info(media_count: int):
    print(f"{media_count} valid media found.")

def print_welcome():
    print("=" * 60)
    print("ReMedia v0.2.0 - Duplicate detection for media files")
    print("Created by Christian Seip • https://www.seip.io")
    print("=" * 60 + "\n")

def print_no_duplicates():
    print("No duplicates detected.")
