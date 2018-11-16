
class Index:
    def __init__(self, prefix=[]):
        self.curr = 0
        self.sub = []
        self.prefix = prefix
        
    def __iter__(self):
        return self
        
    def __next__(self):
        rst = self.prefix + [self.curr]
        self.curr += 1
        self.sub.append(Index(rst))
        return rst