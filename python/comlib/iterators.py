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
    

class LinkList:
    def __init__(self, node, nxt):
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
            
           
class intetpose:
    def __init__(self, node, pos):
        self.it = iter(node)
        self.pos = pos
        self.isPos = False
        self.status = 0  # IDLE
        
    def __iter__(): return self
    
    def __next__():
        if self.status == 0:  # FIRST
            rst = next(it)
            self.status == 1
            return rst
        elif self.status == 1:  # POS
            self.data = next(it)
            self.status = 2
            return self.pos
        elif self.status == 2:  # NEXT
            self.status == 1
            return self.data