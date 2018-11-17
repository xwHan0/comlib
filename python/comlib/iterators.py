
class Index:
    def idx(self): return []
    def sub(self): return IndexSub([])


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