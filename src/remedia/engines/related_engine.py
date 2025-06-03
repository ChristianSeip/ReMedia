import torch
import open_clip
import os
from PIL import Image
from torchvision import transforms
from .similarity_engine import SimilarityEngine
from tqdm import tqdm

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

class RelatedEngine(SimilarityEngine):
    def __init__(self, model_name="ViT-B-32", device=None, threshold=0.90):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(f"{model_name}-quickgelu", pretrained="openai")
        self.model.eval().to(self.device)
        self.threshold = threshold
        self.embeddings = {}

    def compute_features(self, media_list):
        for media in tqdm(media_list, desc="Computing AI features", unit="media"):
            try:
                image = Image.open(media.path).convert("RGB")
                image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    embedding = self.model.encode_image(image_tensor)
                    embedding = embedding / embedding.norm(dim=-1, keepdim=True)
                    self.embeddings[media] = embedding
            except Exception as e:
                print(f"Failed to compute embedding for {media.path.name}: {e}")

    def are_similar(self, a, b) -> bool:
        emb_a = self.embeddings.get(a)
        emb_b = self.embeddings.get(b)
        if emb_a is None or emb_b is None:
            return False
        similarity = (emb_a @ emb_b.T).item()
        return similarity >= self.threshold
