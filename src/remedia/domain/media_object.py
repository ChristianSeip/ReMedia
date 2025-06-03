from pathlib import Path

class MediaObject:
    def __init__(self, path: Path):
        self.path = path

    def __repr__(self):
        return f"<MediaObject path={self.path.name}>"

    def __eq__(self, other):
        return isinstance(other, MediaObject) and self.path.resolve() == other.path.resolve()

    def __hash__(self):
        return hash(self.path.resolve())

    def compute_hashes(self):
        """To be implemented by subclasses."""
        pass
