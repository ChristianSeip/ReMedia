from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from itertools import combinations
from multiprocessing import Pool, cpu_count
import os

def compare_pair(pair):
    a, b, threshold, embeddings = pair
    if a not in embeddings or b not in embeddings:
        return None
    sim = (embeddings[a] @ embeddings[b].T).item()
    if sim >= threshold:
        return (a, b)
    return None

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
        if self.strict_mode:
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

        for anchor in tqdm(media_list, desc="Finding strict groups"):
            candidates = [
                (anchor, other, threshold, embeddings)
                for other in media_list if anchor != other
            ]

            with Pool(processes=self.max_workers or cpu_count()) as pool:
                matches = pool.map(compare_pair, candidates)

            matched = [b for result in matches if result for b in result if b != anchor]
            candidate_group = [anchor] + matched

            if len(candidate_group) <= 1:
                continue

            if self.is_fully_similar_group(candidate_group, threshold):
                if not any(set(candidate_group).issubset(set(g)) for g in groups):
                    groups.append(candidate_group)

        return groups

    def compare_pairs_parallel(self, media_list):
        embeddings = self.engine.embeddings
        threshold = self.engine.threshold
        all_pairs = [
            (media_list[i], media_list[j], threshold, embeddings)
            for i in range(len(media_list))
            for j in range(i + 1, len(media_list))
        ]
        
        results = []
        with Pool(processes=self.max_workers or cpu_count()) as pool:
            with tqdm(total=len(all_pairs), desc="Comparing media pairs") as pbar:
                for result in pool.imap_unordered(compare_pair, all_pairs, chunksize=32):
                    if result:
                        results.append(result)
                    pbar.update(1)

        return results

    def is_fully_similar_group(self, group, threshold):
        embeddings = self.engine.embeddings
        return all((embeddings[a] @ embeddings[b].T).item() >= threshold for a, b in combinations(group, 2))
