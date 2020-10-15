import sys

######################################################################################
# 序列输入参数处理
######################################################################################

#### 定义类型选择类型
class SeriesArgument: pass
class __SeriesElement__(SeriesArgument): pass
class __SeriesIter__(SeriesArgument): pass
class __SeriesMixElement__(SeriesArgument): pass
class __SeriesMixIter__(SeriesArgument): pass
class __SeriesMixAuto__(SeriesArgument): pass

class __SeriesAuto__(SeriesArgument): 
    def __init__(self, auto_level=sys.maxsize):
        self.auto_level=sys.maxsize

#### 实例化
SeriesElement = __SeriesElement__()
SeriesIter = __SeriesIter__()
SeriesAuto = __SeriesAuto__()
SeriesMixElement = __SeriesMixElement__()
SeriesMixIter = __SeriesMixIter__()
SeriesMixAuto = __SeriesMixAuto__()

#### 异常
class NotSupportOption(Exception): pass

#### 处理函数
def __inner_series_argument_proc_without_judge__(cs, auto_level=sys.maxsize, status=0, is_auto=False):

    #### 结果返回
    rst = []
    for i,e in enumerate(cs):

        if isinstance( e, SeriesArgument ): # 内部协议处理
            last = cs[i+1:]

            if isinstance( e, __SeriesElement__ ):
                return rst + last
            elif isinstance( e, __SeriesIter__ ):
                for s in last:
                    rst += list(s)
                return rst
            elif isinstance( e, __SeriesAuto__ ):
                status, is_auto, auto_level = 0, True, e.auto_level
            elif isinstance( e, __SeriesMixElement__ ):
                status, is_auto = 0, False
            elif isinstance( e, __SeriesMixIter__ ):
                status, is_auto = 1, False
            elif isinstance( e, __SeriesMixAuto__ ):
                status, is_auto = 0, True
            else:
                raise NotSupportOption( 'Do not support this option: {} and value: {}'.format(e.__class__.__name__, e) )

            continue    # 跳过当前指令元素
            # rst += __inner_series_argument_proc_without_judge__( last[i:] )
            # break

        if is_auto: # 自动推导
            if isinstance( e, list ) and auto_level > 0:
                rst += __inner_series_argument_proc_without_judge__( e, auto_level=auto_level-1, is_auto=is_auto )
            else:
                rst.append( e )

        elif status == 0: # Element
            rst.append( e )

        elif status == 1: # Iter
            rst += __inner_series_argument_proc_with_judge__( e )

    return rst

def __inner_series_argument_proc_with_judge__(cs):
    if isinstance( cs[0], SeriesArgument ):
        return __inner_series_argument_proc_without_judge__( cs )
    else:
        return cs # 默认按照"元素"进行处理

def series_argument_proc( cs, a=None, b=None ):
    """按照<SeriesArgument>规则处理cs，然后返回"""

    cs_inner = []
    if a==None and b==None:
        cs_inner = cs
    else:
        if a!=None: cs_inner.append( a )
        if b!=None: cs_inner.append( b )
        cs_inner += cs

    return __inner_series_argument_proc_with_judge__(cs_inner)



#### 迭代异常
class ChildStopIteration(StopIteration): pass

####=======================================================================
#### 定义内部迭代类
####=======================================================================
class __flatten__:

    def __init__(self, cs, level, typ=0):
        self.ite = iter(cs)
        self.level = level
        self.typ = typ  # 0: SeriesElement; 1: SeriesIter;
        self.child_ite = None
        self.is_auto = False
    
    def __iter__(self):
        return self

    def __next__(self):

        ### 子迭代没有完成，可以继续子迭代
        if self.child_ite != None:
            try:
                return next( self.child_ite )  # 子迭代还没有迭代完 => 继续子迭代
            except ChildStopIteration:  # 子迭代已经迭代完
                self.child_ite = None
                return self.__next__()

        ### 子迭代完成后
        try:
            ele = next(self.ite)  # 获取下一个元素

            if isinstance( ele, SeriesArgument ):

                if isinstance( ele, __SeriesElement__ ) or self.level <= 0:
                    self.typ, self.is_auto = 0, False

                elif isinstance( ele, __SeriesIter__ ):
                    nxt = next(self.ite)
                    if hasattr( nxt, '__iter__' ):
                        self.typ, self.is_auto = 1, False
                        self.child_ite = __flatten__( nxt, self.level-1 )  # 记录子迭代器。这里不需要再try，因为娶不到的话，直接就是Stop
                    else:
                        self.typ, self.is_auto, self.child_ite = 0, False, None

                elif isinstance( ele, __SeriesAuto__ ):
                    self.is_auto = True

                return self.__next__()  # 跳过该命令，直接获取下一个元素

            elif self.is_auto:
                if isinstance( ele, list ) and self.level > 0:
                    self.child_ite = __flatten__(ele, self.level-1)  # 获取下一个子迭代
                    return self.__next__()
                else:
                    return ele
            elif self.typ == 0:
                return ele  # 获取元素类型 => 直接返回当前元素
            elif hasattr( ele, '__iter__' ):
                self.child_ite = __flatten__(ele, self.level-1)  # 获取下一个子迭代
                return self.__next__()
            else: # typ=1，但ele不可迭代
                return ele
                       
        except StopIteration: # 主迭代完成。抛出完成标识
            raise ChildStopIteration()


#### 处理函数
class flatten:
    """元素打平迭代器"""

    def __init__(self, cs:'被打平的元素', level:'打拼层次'=sys.maxsize):
        """返回打平迭代器"""
        self.ite = __flatten__( cs, level )

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next( self.ite )
        except ChildStopIteration:
            raise StopIteration

    