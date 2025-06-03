from pathlib import Path
from core.constants import DEFAULT_MEDIA_DIR, ACCURACY_STEPS, DEFAULT_TOLERANCE

def get_media_dir() -> Path:
    user_input = input("Path to media folder [Enter for 'images']: ").strip()
    path = Path(user_input) if user_input else DEFAULT_MEDIA_DIR

    if not path.exists() or not path.is_dir():
        print(f"Folder not found: {path.resolve()}")
        return None
    return path

def get_tolerance() -> int:
    try:
        choice = int(input("Search accuracy (1=very strict, 5=generous): ").strip())
        return ACCURACY_STEPS.get(choice, DEFAULT_TOLERANCE)
    except Exception:
        print("Invalid input - using default accuracy level 3.")
        return DEFAULT_TOLERANCE

def get_detection_engine():
    print("\nChoose detection engine:")
    print("1 - Find duplicats")
    print("2 - Find related images")

    try:
        choice = int(input("Selection [1]: ").strip())
    except Exception:
        choice = 1

    return choice