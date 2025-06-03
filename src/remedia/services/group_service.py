from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from itertools import combinations
import os

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
            matched = []
            for other in media_list:
                if anchor == other:
                    continue
                sim = (embeddings[anchor] @ embeddings[other].T).item()
                if sim >= threshold:
                    matched.append(other)

            candidate_group = [anchor] + matched
            if len(candidate_group) <= 1:
                continue

            if self.is_fully_similar_group(candidate_group, threshold):
                if not any(set(candidate_group).issubset(set(g)) for g in groups):
                    groups.append(candidate_group)

        return groups

    def compare_pairs_parallel(self, media_list):
        def compare(i, j):
            a, b = media_list[i], media_list[j]
            if self.engine.are_similar(a, b):
                return (a, b)
            return None

        total = len(media_list)
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(compare, i, j): (i, j)
                for i in range(total) for j in range(i + 1, total)
            }

            for future in tqdm(as_completed(futures), total=len(futures), desc="Comparing media pairs"):
                result = future.result()
                if result:
                    results.append(result)

        return results

    def is_fully_similar_group(self, group, threshold):
        embeddings = self.engine.embeddings
        return all((embeddings[a] @ embeddings[b].T).item() >= threshold for a, b in combinations(group, 2))
