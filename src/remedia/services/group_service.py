from tqdm import tqdm
from multiprocessing import Pool
from itertools import combinations
from collections import defaultdict
import os

_global_embeddings = None
_global_threshold = None

def init_worker(embeddings, threshold):
    global _global_embeddings, _global_threshold
    _global_embeddings = embeddings
    _global_threshold = threshold

def compare_pair(pair):
    a, b = pair
    if a not in _global_embeddings or b not in _global_embeddings:
        return None
    sim = (_global_embeddings[a] @ _global_embeddings[b].T).item()
    if sim >= _global_threshold:
        return (a, b)
    return None

def compare_pair_hash(pair):
    a, b, engine = pair
    return (a, b) if engine.are_similar(a, b) else None


class GroupService:
    def __init__(self, engine, max_workers=None, strict_mode=False):
        self.engine = engine
        self.max_workers = max_workers or os.cpu_count()
        self.strict_mode = strict_mode

    def find_duplicates(self, media_list):
        return self._find_disjoint_groups(media_list)

    def _find_disjoint_groups(self, media_list, min_match_ratio=0.80):
        unassigned = set(media_list)
        groups = []

        while unassigned:
            anchor = unassigned.pop()
            group = [anchor]
            candidates = list(unassigned)
            to_remove = set()

            for candidate in candidates:
                match_count = sum(
                    1 for member in group if self.engine.are_similar(candidate, member)
                )
                required_matches = int(len(group) * min_match_ratio)

                if match_count >= required_matches:
                    group.append(candidate)
                    to_remove.add(candidate)

            unassigned -= to_remove

            if len(group) > 1:
                groups.append(group)

        return groups


    def compare_pairs_parallel(self, media_list):
        if self.engine.__class__.__name__ == "RelatedEngine":
            return self._compare_ai_pairs_parallel(media_list)
        else:
            return self._compare_hash_pairs_parallel(media_list)

    def _compare_ai_pairs_parallel(self, media_list):
        embeddings = self.engine.embeddings
        threshold = self.engine.threshold
        all_pairs = [
            (media_list[i], media_list[j])
            for i in range(len(media_list))
            for j in range(i + 1, len(media_list))
        ]

        results = []
        with Pool(
            processes=self.max_workers,
            initializer=init_worker,
            initargs=(embeddings, threshold)
        ) as pool:
            with tqdm(total=len(all_pairs), desc="Comparing media pairs") as pbar:
                for result in pool.imap_unordered(compare_pair, all_pairs, chunksize=32):
                    if result:
                        results.append(result)
                    pbar.update(1)

        return results

    def _compare_hash_pairs_parallel(self, media_list):
        all_pairs = [
            (media_list[i], media_list[j], self.engine)
            for i in range(len(media_list))
            for j in range(i + 1, len(media_list))
        ]

        results = []
        with Pool(processes=self.max_workers) as pool:
            with tqdm(total=len(all_pairs), desc="Comparing hash pairs") as pbar:
                for result in pool.imap_unordered(compare_pair_hash, all_pairs, chunksize=32):
                    if result:
                        results.append(result)
                    pbar.update(1)

        return results
