from core.config import PROJECT_ROOT

DEFAULT_MEDIA_DIR = PROJECT_ROOT / "images"

DUPLICATE_OUTPUT_DIR = PROJECT_ROOT / "duplicate_found"

# Levels of tolerance (1 = very strict, 5 = generous)
ACCURACY_STEPS = {
    1: 12,
    2: 16,
    3: 20,
    4: 26,
    5: 32,
}

DEFAULT_ACCURACY = 3
DEFAULT_TOLERANCE = ACCURACY_STEPS[DEFAULT_ACCURACY]

ACCURACY_TO_RELATED_THRESHOLD = {
    1: 0.99,
    2: 0.95,
    3: 0.90,
    4: 0.85,
    5: 0.80 
}