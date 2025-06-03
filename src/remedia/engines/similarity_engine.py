from abc import ABC, abstractmethod
from remedia.domain.media_object import MediaObject

class SimilarityEngine(ABC):
    @abstractmethod
    def compute_features(self, media_list: list[MediaObject]) -> None:
        """Precompute hashes or embeddings for all media."""
        pass

    @abstractmethod
    def are_similar(self, a: MediaObject, b: MediaObject) -> bool:
        """Return True if media objects are considered similar."""
        pass
