from PIL import Image
import imagehash
from remedia.domain.media_object import MediaObject

class ImageObject(MediaObject):
    def __init__(self, path):
        super().__init__(path)
        self.dhash = None
        self.phash = None

    def compute_hashes(self):
        try:
            with Image.open(self.path) as img:
                self.dhash = imagehash.dhash(img)
                self.phash = imagehash.phash(img)
        except Exception as e:
            print(f"Failed to compute hashes for {self.path.name}: {e}")

    def total_difference(self, other: "ImageObject") -> int:
        if self.dhash is None or self.phash is None:
            self.compute_hashes()
        if other.dhash is None or other.phash is None:
            other.compute_hashes()
        diff_d = self.dhash - other.dhash
        diff_p = self.phash - other.phash
        return diff_d + diff_p
