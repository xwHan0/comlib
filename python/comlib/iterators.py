class CommonIterator:
    def __iter__(self): return self
    def sub(self): return self


class Counter(CommonIterator):
    def __init__(self):
        CommonIterator.__init__(self)
        self.cnt = -1
        
    def __next__(self):
        self.cnt += 1
        return self.cnt
        

class Index(CommonIterator):
    def __init__(self, prefix=[], root=True):
        CommonIterator.__init__(self)
        self.curr = -1
        self.prefix = prefix
        self.root = root
        
    def __next__(self):
        self.curr += 1
        return self

    def idx(self): return self.prefix if self.root else self.prefix + [self.curr]
    def lvl(self): return len(self.prefix)
    def sub(self): return Index( self.prefix, False ) if self.root else Index(self.prefix + [self.curr], False)


class IndexSub(CommonIterator):
    def __init__(self, prefix):
        CommonIterator.__init__(self)
        self.curr = -1
        self.prefix = prefix
        
    def __next__(self):
        self.curr += 1
        return self

    def idx(self): return self.prefix + [self.curr]
    def lvl(self): return len(self.prefix)
    def sub(self): return IndexSub(self.prefix + [self.curr])