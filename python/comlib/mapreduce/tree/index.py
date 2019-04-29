"""
Common iterators
"""

from comlib.mapreduce.tree import SelfGrowthTree

class Index(SelfGrowthTree):
    """返回节点序号迭代器"""
    def __init__(self, prefix=[], root=True):
        super().__init__()
        self.curr = -1
        self.prefix = prefix
        self.root = root
       
    def __iter__(self): return self

    def __next__(self):
        self.curr += 1
        return self

    def idx(self): return self.prefix if self.root else self.prefix + [self.curr]
    def lvl(self): return len(self.prefix)
    def sub(self,*node): return Index( self.prefix, False ) if self.root else Index(self.prefix + [self.curr], False)


