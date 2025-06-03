from pathlib import Path
from PIL import Image
from remedia.domain.image_object import ImageObject
from tqdm import tqdm

def load_valid_images(directory: Path):
    media_list = []
    for file in tqdm(sorted(directory.glob("*")), desc="Scanning media"):
        if not file.is_file():
            continue
        try:
            with Image.open(file) as img:
                img.verify()
            media_list.append(ImageObject(file))
        except Exception:
            continue
    return media_list