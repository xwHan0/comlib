"""
常用高阶函数迭代器库。
"""
from types import FunctionType
from comlib import xmin
    
import sys


#############################################################################################################
####  repeat
#############################################################################################################
def repeat( 
    ele_or_fun : '填充元素或者生成函数。函数格式: (idx)=>ele' , 
    *ns : '填充矩阵尺寸列表'
    ):
    """返回按照尺寸`ns`和元素ele填充的列表矩阵"""

    def _repeat_( ele_or_fun, ns, lvl ):

        if len( ns ) == 1:
            if isinstance(ele_or_fun, FunctionType):
                return [ele_or_fun(lvl+[i]) for i in range(ns[0])]
            else:
                return [ele_or_fun for _ in range(ns[0])]
        else:
            return [repeat(ele_or_fun, ns[1:], lvl+[i]) for i in range(ns[0])]

    return _repeat_( ele_or_fun, ns, [] )


class XIterator:
    def apply( self, action, *args, **kargs ):
        return action( *args, self, **kargs )
        
    def map( self, action, *iters, **kargs ):
        return xmap( action, self, *iters, **kargs )

    def reduce( self, action, *iters, init=None, **kargs ):
        return xreduce( action, self, *iters, init=init, **kargs )

    def flatten(self, level=1):
        return xflatten( self, level=level )
        
    def to_list(self): return list(self)

    def __iter__(self): return self

    def __next__(self): return self


class xiter(XIterator):
    def __init__(self, ite):
        if hasattr(ite, '__next__'):
            self.ite = ite
        else:
            self.ite = iter(ite)
        
    def __iter__(self): return self.ite


#############################################################################################################
####  Function operator
#############################################################################################################
class Func:
    def conc( self, *actions ): return conc( self, *actions )
    def conj( self, *actions ): return conj( self, *actions )
    def comb( self, *actions ): return comb( self, *actions )


class conc(Func):
    """Concurrent"""
    def __init__( self, *actions ):
        self.actions = actions

    def __call__( self, *args, **kargs ):
        return [action(*args, **kargs) for action in self.actions]


class conj(Func):
    """Conjoin"""
    def __init__( self, *actions ):
        self.actions = actions

    def __call__( self, *args, **kargs ):
        n = len( self.actions )
        if n==0: return None
        if n==1: return self.actions[0]( *args )
        nxt = conj( *self.actions[1:] )
        return nxt( self.actions[0]( *args ) )


class comb(Func):
    """Conbine"""
    def __init__( self, *actions ):
        self.actions = actions

    def __call__( self, *args, **kargs ):
        n = len( self.actions )
        if n==0: return None
        if n==1: return self.actions[0]( *args )
        nxt = comb( *self.actions[1:] )
        return self.actions[0]( nxt, *args )


class parity(Func):
    def __init__( self, action, num=None, profile=[], *args, **kargs ):
        
        if isinstance( action, parity ):
            self.action = action.action
            self.num = action.num
            self.profile = action.pofile
            self.args = action.args
            self.kargs = action.kargs
        else:
            self.action = action
            self.num = num
            self.profile = profile
            self.args = args
            self.kargs = kargs

    def __call__( self, *args, **kargs ):
        if self.num != None:
            args1 = ( args + self.args )[:self.num]
        elif len( self.profile ) > 0:
            args += self.args
            args1 = [args[p] for p in self.profile]
        else:
            args1 = args
            
        return self.action( *args1, **self.kargs )

#=================================================================================================================
#====  Action
#=================================================================================================================
class Action:
    """
    allreduce内部处理接口协议。转化外部函数的形参格式到内部处理格式。
    """
    def __init__( self, action, args_required_num=0, **kargs ):

        if isinstance( action, Action ):
            self.action = action.action
            self.kargs = action.kargs
            self.args_required_num = action.args_required_num
        else:
            self.action = action
            self.kargs = kargs
            self.args_required_num = args_required_num
        
    def __call__( self, *args, **kargs ):
        if not hasattr( self.action, '__call__' ):
            return self.action

        if self.args_required_num > 0:
            args = args[:self.args_required_num]
        
        return self.action( *args, **self.kargs )

    def conc(self, *actions):
        self.action = Action( conc(self.action, *actions ) )
        return self
        
    def conj(self, *actions):
        self.action = Action( conj(self.action, *actions ) )
        return self
        
    def comb(self, *actions):
        self.action = Action( comb(self.action, *actions ) )
        return self


# class Actions:
#     def __init__( self, actions = None, kargs={} ):
        
#         self.actions = self.set_actions( actions, kargs=kargs ) if actions else None

#     def set_actions( self, actions, kargs = {} ):
        
#         if not isinstance( actions, list ):
#             actions = [actions]
#         actions = [a if isinstance(a, Action) else Action( a, **kargs ) for a in actions]
            
#         return actions

#     def __call__( self, *args, **kargs ):
        
#         return [action( *args, **kargs ) for action in self.actions]









#=================================================================================================================
#====  xmap
#=================================================================================================================
class xmap(XIterator):
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
    return list(xmap( action, *iters, **kargs ))



#############################################################################################################
####  Reduce
#############################################################################################################
def xreduce( action, *iters, init=None, **kargs ):
    # 初始化变量
    # actions = Actions(action)
    if isinstance( action, list ):
        actions = conc( *action )
    else:
        actions = conc( action )
    nxts = [iter(ite) for ite in iters]
    rst_num = len( actions.actions )
    
    try:
        if init == None:
            last = [next(n) for n in nxts]
            if len( last ) == 1: last = last[0]
            last = [last] * rst_num
        else:
            last = [init] * rst_num

        while True:
            curr = [next(n) for n in nxts]
            last = [actions.actions[i](last[i], *curr) for i in range( rst_num )]

    except StopIteration:
        pass

    return last if len(last) > 1 else last[0]


    
    
#############################################################################################################
####  Apply
#############################################################################################################
def apply( actions, args=None, **kargs ):
    """
    高阶函数降级处理。
    Constraint-001: 当actions仅包含一个元素时，该action必须满足格式：(*args, **kargs)
    Constraint-002: 当actions包含多个元素时，非最后一个action元素必须满足格式：(action, *args, **kargs)
    """
    if args == None:
        def _action_( *args1 ):
            return apply( actions, args1, **kargs )
        return _action_
    
    if not isinstance( actions, (tuple, list) ):
        actions = [actions]
    
    action_num = len( actions )

    # 0阶处理：直接返回数据
    if action_num == 0: return args
        
    # 1阶处理：返回处理的结果
    # Issue: 该1阶处理函数是否有该调用格式？这里貌似多了一个协议接口定义
    if action_num == 1: return actions[0]( *args, **kargs )

    # 2阶函数，直接求解该2阶函数的解
    if action_num == 2: return actions[0]( actions[1], *args, **kargs )

    # 高于2阶函数，逐阶降阶处理
    def _sub_(*s, **kargs): return apply(actions[1:], s, **kargs)
    return actions[0]( _sub_, *args, **kargs )

def xapply( actions, *args, **kargs ):
    return apply( actions, args, **kargs )
    
def wapply( *args, **kargs ):
    if 'anum' in kargs:
        action_num = kargs.get( 'anum', 0 )
        del kargs['anum']
    else:
        action_num = 0
    
    if action_num == 0:
        for i in range( len(args) ):
            if not hasattr( args[i], '__call__' ):
                break
        actions = args[:i]
        args = args[i:]
    else:
        actions = args[:action_num]
        args = args[action_num:]
        
    return apply( actions, args, **kargs )


#############################################################################################################
####  Find
#############################################################################################################
class _criteria_val_:
    def __init__( self, val ):
        self.val = val

    def __call__( self, *nxt, **kargs ):
        return nxt[0] == self.val


class _find_(XIterator):
    def __init__(self, criteria, *iters, result_sel=[], find_num=None ):
        self.criteria = criteria
        self.iters = iters
        self.result_sel = result_sel
        self.find_cnt = 0
        self.find_num = find_num

    def __iter__(self):
        self._nxt_ = [iter(n) for n in self.iters]
        self.find_cnt = 0
        return self

    def __next__(self):

        if self.find_cnt >= self.find_num:
            raise StopIteration()

        nxt = [next(n) for n in self._nxt_]

        rst = self.criteria( *nxt )
        if rst == False: 
            return self.__next__()
            
        self.find_cnt += 1
        rst = [nxt[pos] for pos in self.result_sel]
        return rst if len(rst)>1 else rst[0]
        
    def __call__( self, *iters, **kargs ):
        self.iters = iters
        return self



def find( criteria, *itera, result_sel=0, num=None, default=None, **kargs ):
    """
    """

    if not hasattr( criteria, '__call__' ):
        criteria = _criteria_val_( criteria )
    # else:
        # criteria = parity( criteria, num=None, profile=[], **kargs )

    if isinstance( result_sel, int ):
        result_sel = [result_sel]

    if num == 1:  # 返回itera的某个列表对应位置的元素

        its = [iter(n) for n in itera]
        try:
            while True:
                nxt = [next(i) for i in its]
                if criteria( *nxt, **kargs ): # 找到元素
                    rst = [nxt[pos] for pos in result_sel]
                    return rst if len(rst)>1 else rst[0] # 返回对应元素
        except StopIteration:   # 找不到返回
            return default

    if num == None:
        num = sys.maxsize

    return _find_( criteria, *itera, result_sel=result_sel, find_num=num, **kargs )

def finda( criteria, *itera, result_sel=0, num=None, default=None, **kargs ):
    return list( find( criteria, *itera, result_sel=0, num=None, default=None, **kargs ) )

