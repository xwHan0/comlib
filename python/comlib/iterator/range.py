from comlib.iterator.iter import XIterator

class range(XIterator):
    def __init__(self, 
        begin :'迭代起始值' = 0, 
        end :'迭代结束值' = None, 
        step :'递增/减步长' = 1, 
        mode :'模式选择' = 'unlimmitted'
    ):
        self.begin, self.end, self.step = begin, end, step
        
        self.mode = 'unlimmitted' if end==None else mode
        
        if self.mode == 'roundrobin':
            if self.step > 0 and begin > end:
                self.begin, self.end = end, begin
            elif self.step < 0 and begin < end:
                self.begin, self.end = end, begin
        
    def __iter__(self):
        self._nxt_ = self.begin
        return self
        
    def __next__(self):
        
        rst = self._nxt_
        if self.end == None:
            pass
        elif self.mode == 'unlimmitted':
            if self.end > self.begin:
                if self._nxt_ >= self.end: raise StopIteration()
            else:
                if self._nxt_ <= self.end: raise StopIteration()
        elif self.mode == 'roundrobin':
            if self.step > 0:
                if self._nxt_ >= self.end: self._nxt_ = self.begin
            else:
                if self._nxt_ <= self.end: self._nxt_ = self.begin
        
        self._nxt_ += self.step
        
        return rst
