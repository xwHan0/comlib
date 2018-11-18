
class Index:
    def __init__(self, prefix=[], root=True):
        self.curr = -1
        self.prefix = prefix
        self.root = root

    def __iter__(self): return self
        
    def __next__(self):
        self.curr += 1
        return self

    def idx(self): return self.prefix if self.root else self.prefix + [self.curr]
    def sub(self): return Index( self.prefix, False ) if self.root else Index(self.prefix + [self.curr], False)


class IndexSub:
    def __init__(self, prefix):
        self.curr = -1
        self.prefix = prefix

    def __iter__(self): return self
        
    def __next__(self):
        self.curr += 1
        return self

    def idx(self): return self.prefix + [self.curr]
    def sub(self): return IndexSub(self.prefix + [self.curr])