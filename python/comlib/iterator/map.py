
from comlib.iterator.iter import XIterator

class map(XIterator):
    def __init__(self, action, *iters, **kargs):
        """
        返回一个xmap迭代器。

        Argument:
        * action: {Action} -- 对每个元素的处理函数。
          * Action格式定义参见'high order function.html'
          * 每个action函数的格式为: 
            * proc(ele) -> value
            * proc(ele, **args) -> value
            * proc(*eles, **args) -> value
        * iters: {iterable} -- 被处理的数据迭代器。
          * 当该迭代器为空时，返回一个支持proc的延时函数，该函数接收一个列表参数。(Delay Execute特性)
        * criteria: {None(default) | list} -- 分组条件
          * 参见'high order function.html'
        * others: -- proc处理所需的参数列表
            
        Returns:
        Iterator -- 处理结果迭代器。
        * 返回的是迭代器，需要使用list(return-value)来转化为链表。
        * next迭代返回一个列表结果；当列表中仅包含一个元素时，返回该元素
        """
        self.action = parity( action, **kargs )
        # self.action = Action( action, **kargs )
        self.iters = iters

    def __iter__(self):
        self._nxt_ = [iter(n) for n in self.iters]
        return self

    def __next__(self):

        nxt = [next(n) for n in self._nxt_]

        rst = self.action( *nxt )
        if rst == None: return self.__next__()
        return rst
        # return rst if len(rst) > 1 else rst[0]
        
    def __call__( self, *iters, **kargs ):
        self.iters = iters
        return self


def mapa(action, *iters, **kargs):
    return list(map( action, *iters, **kargs ))

