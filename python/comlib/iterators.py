class CommonIterator:
    def __iter__(self): return self
    def sub(self): return self


class Counter(CommonIterator):
    """返回迭代遍历过的节点个数迭代器"""
    def __init__(self):
        CommonIterator.__init__(self)
        self.cnt = -1
        
    def __next__(self):
        self.cnt += 1
        return self.cnt
        

class Index(CommonIterator):
    """返回节点序号迭代器"""
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
    

class LinkList:
    """返回node.nxt做指针的迭代器"""
    def __init__(self, node, nxt):
        """返回node.nxt做指针的迭代器"""
        self.node = node
        self.nxt = nxt
        
    def __iter__(self): return self
    
    def __next__(self):
        try:
            nxt = getattr(self.node, self.nxt)
            self.node = nxt
            return nxt
        except Exception:
            raise StopIteration()
            
