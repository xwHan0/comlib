def deq(it, n=1): return [next(it) for i in range(n)]

           
class intetpose:
    """在集合node迭代内容之间插入pos，返回迭代器"""
    def __init__(self, node, pos):
        """在集合node迭代内容之间插入pos"""
        self.it = iter(node)
        self.pos = pos
        self.isPos = False
        self.status = 0  # IDLE
        
    def __iter__(self): return self
    
    def __next__(self):
        if self.status == 0:  # FIRST
            rst = next(self.it)
            self.status == 1
            return rst
        elif self.status == 1:  # POS
            self.data = next(it)
            self.status = 2
            return self.pos
        elif self.status == 2:  # NEXT
            self.status == 1
            return self.data