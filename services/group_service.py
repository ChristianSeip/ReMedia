from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
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
    def __init__(self, engine, max_workers=None):
        self.engine = engine
        self.max_workers = max_workers or os.cpu_count()

    def find_duplicates(self, media_list):
        uf = UnionFind()
        total = len(media_list)

        def compare(i, j):
            a, b = media_list[i], media_list[j]
            if self.engine.are_similar(a, b):
                return (a, b)
            return None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(compare, i, j): (i, j)
                for i in range(total) for j in range(i + 1, total)
            }

            for future in tqdm(as_completed(futures), total=len(futures), desc="Comparing media pairs"):
                result = future.result()
                if result:
                    a, b = result
                    uf.union(a, b)

        return [group for group in uf.groups() if len(group) > 1]