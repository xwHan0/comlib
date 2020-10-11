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
                rst += __inner_series_argument_proc_without_judge__( e, auto_level=auto_level-1 )
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


#### 处理函数
class SeriesArgumentIter:
    def __init__(self, cs, auto_level=999999999):
        self.cs = cs
        self.ite0 = None # 高层迭代器
        self.ite1 = None # 底层迭代器
        self.status = 0  # 当前迭代元素类型。0: Element; 1: Iter; 
        self.is_auto = False # 是否自动推断
        self.auto_level = auto_level # 自动推断层次

    def __iter__(self):
        if isinstance( self.cs[0], SeriesArgument ):

            self.ite0 = iter( self.cs ) # 获取迭代器
            option = next( self.ite0 ) # 获取第一个元素，作为选项参数

            if isinstance( option, __SeriesElement__ ):
                return self.ite0 # 返回迭代器
            elif isinstance( option, __SeriesIter__ ):
                self.status = 1
                self.ite1 = iter( SeriesArgumentIter(next( self.ite0 )) )
            elif isinstance( option, __SeriesAuto__ ):
                self.is_auto = True
                if isinstance( self.cs[1], list ):
                    self.status = 1
            else:
                raise NotSupportOption( 'Do not support this option: %s' % (option.__class__.__name__) )
        else:
            return iter( self.cs )  # 默认按照SeriesElement选择

        return self

    def __next__(self):

        if self.status == 0: # Element

            rst = next( self.ite0 )
            if isinstance( rst, SeriesArgument ):
                if isinstance( rst, __SeriesIter__ ):
                    self.status = 1
                    self.is_auto = False
                    self.ite1 = iter( SeriesArgumentIter( next( self.ite0 ) ) )
                    rst = self.__next__()
                elif isinstance( rst, __SeriesElement__ ):
                    self.is_auto = False
                    rst = self.__next__()
                elif isinstance( rst, __SeriesAuto__ ):
                    self.is_auto = True
                else:
                    raise NotSupportOption( 'Do not support this option: {} and value: {}'.format(rst.__class__.__name__, rst) )
            elif self.is_auto and isinstance( rst, list ):
                self.status = 1
                rst = self.__next__()

        elif self.status == 1: # Iter

            try:
                rst = next( self.ite1 )
            except StopIteration:
                nxt0 = next( self.ite0 )
                if isinstance( nxt0, SeriesArgument ):
                    if isinstance( nxt0, __SeriesElement__ ):
                        self.status = 0
                        rst = self.__next__()
                    elif isinstance( nxt0, __SeriesIter__ ):
                        self.ite1 = iter( SeriesArgumentIter( nxt0 ) )
                        rst = self.__next__()
                    else:
                        raise NotSupportOption( 'Do not support this option: {} and value: {}'.format(nxt0.__class__.__name__, nxt0) )
                else:
                    self.ite1 = iter( SeriesArgumentIter( nxt0 ) )
                    rst = self.__next__()

        return rst