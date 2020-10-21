from comlib.iterator.iter import XIterator


class acc(XIterator):

    def __init__(self, action, iter=None, init=None):
        """
        * action: {(init,ele)=>ele} -- 迭代函数
        * iter: {iterator} -- 迭代对象
        * init: {} -- 初始值
        """
        self.action = action
        self.iter = iter
        self.init = init

    def __iter__(self):
        self._nxt_ = iter(self.iter)
        return self

    def __next__(self):

        ele = next(self._nxt_)
        ret = self.action( self.init, ele )

        self.init = ret
        return ret

    def __call__(self, iter, init=None):
        self.iter = iter
        if init:
            self.init = init
        return self
    
