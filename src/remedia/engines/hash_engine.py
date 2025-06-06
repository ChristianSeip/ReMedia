from tqdm import tqdm
from .similarity_engine import SimilarityEngine

class HashEngine(SimilarityEngine):
    def __init__(self, tolerance: int):
        self.tolerance = tolerance

    def are_similar(self, a, b) -> bool:
        if hasattr(a, "total_difference") and hasattr(b, "total_difference"):
            return a.total_difference(b) <= self.tolerance
        return False

    def compute_hashes(self, media_list: list):
        for media in tqdm(media_list, desc="Calculating media hashes"):
            try:
                if hasattr(media, "compute_hashes"):
                    media.compute_hashes()
            except Exception as e:
                print(f"Failed to hash {media.path.name}: {e}")
    
    def compute_features(self, media_list):
        for media in media_list:
            if hasattr(media, "compute_hashes"):
                media.compute_hashes()