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
            

class LinkNext:
    """返回node.nxt做指针的迭代器。从第二个元素开始"""
    def __init__(self, node, nxt):
        """返回node.nxt做指针的迭代器"""
        self.node = node.nxt
        self.nxt = nxt
        
    def __iter__(self): return self
    
    def __next__(self):
        try:
            nxt = getattr(self.node, self.nxt)
            self.node = nxt
            return nxt
        except Exception:
            raise StopIteration()


class LinkArray:
    def __init__(self, nxt):
        self.nxt = nxt
        
    def next(self, node):
        return getattr(node, self.nxt)

           
class interpose(CommonIterator):
    """在集合node迭代内容之间插入pos，返回迭代器"""
    def __init__(self, node, pos):
        """在集合node迭代内容之间插入pos"""
        CommonIterator.__init__(self)
        self.it = iter(node)
        self.pos = pos
        #self.isPos = False
        
        
    def __iter__(self): 
        self.status = 0  # IDLE
        return self
    
    def __next__(self):
        if self.status == 0:  # FIRST
            rst = next(self.it)
            self.status = 1
            return rst
        elif self.status == 1:  # POS
            self.data = next(self.it)
            self.status = 2
            return self.pos
        elif self.status == 2:  # NEXT
            self.status = 1
            return self.data