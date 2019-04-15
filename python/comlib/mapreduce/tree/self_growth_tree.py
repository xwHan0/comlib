
from comlib.mapreduce import Child

class SelfGrowthTree(Child): pass


class ContentTree(SelfGrowthTree):
    def __init__(self, val=None):
        self.val = val
        self.subs = [] #子节点列表

        self.has_new = False

    def sub(self, *node): 
        self.has_new = True
        return self

    def next_val(self):
        return None
        
    def __getitem__(self, idx):
        return self.subs[idx]

    def __iter__(self):
        return self

    def __next__(self):
        new_val = self.next_val()

        if self.has_new:
            self.has_new = False

        self.subs.append(SelfGrowthTree(new_val))
        return self.subs[-1]


