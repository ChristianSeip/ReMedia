from collections import defaultdict
from tqdm import tqdm
from itertools import combinations
from multiprocessing import Pool, cpu_count
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

class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if self.parent.get(x) != x:
            self.parent[x] = self.find(self.parent.get(x, x))
        return self.parent.get(x, x)

    def union(self, x, y):
        self.parent.setdefault(x, x)
        self.parent.setdefault(y, y)
        self.parent[self.find(y)] = self.find(x)

    def groups(self):
        result = defaultdict(list)
        for item in self.parent:
            root = self.find(item)
            result[root].append(item)
        return list(result.values())

class GroupService:
    def __init__(self, engine, max_workers=None, strict_mode=False):
        self.engine = engine
        self.max_workers = max_workers or os.cpu_count()
        self.strict_mode = strict_mode

    def find_duplicates(self, media_list):
        if self.strict_mode and self.engine.__class__.__name__ == "RelatedEngine":
            return self._find_strict_groups(media_list)

        uf = UnionFind()
        matches = self.compare_pairs_parallel(media_list)
        for a, b in matches:
            uf.union(a, b)

        return [group for group in uf.groups() if len(group) > 1]

    def _find_strict_groups(self, media_list):
        embeddings = self.engine.embeddings
        threshold = self.engine.threshold
        groups = []
        already_grouped = set()

        all_pairs = [
            (media_list[i], media_list[j])
            for i in range(len(media_list))
            for j in range(i + 1, len(media_list))
        ]

        similarity_map = defaultdict(list)
        with Pool(
            processes=self.max_workers,
            initializer=init_worker,
            initargs=(embeddings, threshold)
        ) as pool:
            with tqdm(total=len(all_pairs), desc="Comparing all pairs") as pbar:
                for result in pool.imap_unordered(compare_pair, all_pairs, chunksize=32):
                    if result:
                        a, b = result
                        similarity_map[a].append(b)
                        similarity_map[b].append(a)
                    pbar.update(1)

        for anchor in tqdm(media_list, desc="Building groups"):
            if anchor in already_grouped:
                continue

            matched = similarity_map.get(anchor, [])
            candidate_group = [anchor] + matched

            if len(candidate_group) <= 1:
                continue

            if self.is_fully_similar_group(candidate_group, threshold):
                if not any(set(candidate_group).issubset(set(g)) for g in groups):
                    groups.append(candidate_group)
                    already_grouped.update(candidate_group)

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

    def is_fully_similar_group(self, group, threshold):
        embeddings = self.engine.embeddings
        return all(
            (embeddings[a] @ embeddings[b].T).item() >= threshold
            for a, b in combinations(group, 2)
        )
