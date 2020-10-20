from comlib.iterator.iter import XIterator
from comlib.iterator.iter import RtnNone, RtnList, Rtn, _RtnNone_


class acc(XIterator):

    def __init__(self, action, iter, init=None):
        """
        * action: {(init,ele)=>ele} -- 迭代函数
        * iter: {iterator} -- 迭代对象
        * init: {} -- 初始值
        """
        self.action = action
        self.iter = iter
        self.init = init
        self.rtn_list_iter = None

    def __iter__(self):
        self._nxt_ = iter(self.iter)
        self.rtn_list_iter = None
        return self

    def __next__(self):

        if self.rtn_list_iter:
            try:
                ele = next(self.rtn_list_iter)
                self.init = ele
                return ele
            except StopIteration:
                self.rtn_list_iter = None
                return self.__next__()

        ele = next(self._nxt_)
        ret = self.action( self.init, ele )

        if isinstance( ret, Rtn ):
            if isinstance( ret, _RtnNone_ ):
                return self.__next__()
            elif isinstance( ret, RtnList ):
                self.rtn_list_iter = iter( ret.rtn )
                return self.__next__()
        else:
            self.init = ret
            return ret
    
