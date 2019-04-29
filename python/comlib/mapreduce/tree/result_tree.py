
from comlib.mapreduce.tree import SelfGrowthTree

class ResultTree(SelfGrowthTree):
    def __init__(self):
        self.subs = []

    def sub(self, *node): return self
        
    def __getitem__(self, idx):
        return self.subs[idx]

    def __iter__(self):
        return self

    def __next__(self):
        self.subs.append(ResultTree())
        return self.subs[-1]
