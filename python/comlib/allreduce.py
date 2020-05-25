"""
常用高阶函数迭代器库。
"""
from types import FunctionType
from comlib import xmin
    

class XIterator:
    def apply( self, action, *args, **kargs ):
        return action( *args, self **kargs )
        
    def xmap( self, action, *iters, **kargs ):
        return xmap( action, self, *iters, **kargs )

    def xreduce( self, action, *iters, init=None, **kargs ):
        return xreduce( action, self, *iters, init=init, **kargs )
        
    def to_list(self): return list(self)


#=================================================================================================================
#====  Action
#=================================================================================================================
class Proc:
    """
    allreduce内部处理接口协议。转化外部函数的形参格式到内部处理格式。
    """
    def __init__( self, proc, kargs={}, args_required_num=0 ):
        self.proc = proc
        self.kargs = kargs
        self.args_required_num = args_required_num
        
    def __call__( self, *args, **kargs ):
        if self.args_required_num > 0:
            args = args[:self.args_required_num]
        
        return self.proc( *args, **self.kargs )


class Action:
    def __init__(self, action, itn=0, ext_bys=False, ext_kargs={},  **kargs):

        self.action, self.itn = action, itn

        if type(self.action) is FunctionType:
            self._action_mode = 0  # Function
            actor = self.action
        elif hasattr( action, '__call__' ):
            self._action_mode = 1 # Class
            actor = self.action.__init__
        else:
            self._action_mode = 2
            
        if self._action_mode < 2:
            # 生成action处理所需的额外参数
            
            self.glb_param = {}
            if ext_bys:
                self.glb_param = dict( ext_kargs, **kargs )
            else:
                params = actor.__code__.co_varnames[:action.__code__.co_argcount]

                for param in params:
                    if param in ext_kargs:
                        self.glb_param[param] = ext_kargs[param]
                self.glb_param = dict( self.glb_param, **kargs )
        
    def run(self, nxt):

        if self._action_mode > 1: return self.action

        if self.itn > 0:
            args_num = xmin( self.itn, len(nxt ) )
        elif self._action_mode == 0:
            args_num = self.action.__code__.co_argcount
        elif self._action_mode == 1:
            args_num = self.action.__init__.__code__.co_argcount - 1
        
        if args_num == 0:
            return self.action( *nxt, **self.glb_param )
        else:
            return self.action( *nxt[:args_num], **self.glb_param )    

    def run2(self, last, curr):
        return self.action( last, curr, **self.glb_param )
        
        
def gen_actions( action, ext_kargs ):

    if not isinstance( action, list ):
        action = [action]
        
    rst = []
    for p in action:
        if hasattr( p, '__call__' ):
            rst.append( Action( p,  ext_kargs=ext_kargs  ) )
        elif isinstance( p, Action ):
            rst.append( p )
    return rst

    
class Group:
    def __init__( self, action, **args ):
        self.action = {}
        if isinstance( action, dict ):
            for p in action:
                self.action[p] = gen_actions( action[p], args )
        else:
            self.action = gen_actions( action, args )
            
        self.criteria = args.get( 'criteria', None )
        
    def reset( self ):
        if self.criteria:
            self.cri_nxt = iter( self.criteria )
        
    def run( self, nxt ):
        if self.criteria == None:
            return [action.run( nxt ) for action in self.action]
        
        cls = next( self.cri_nxt )
        procs = self.action.get( cls, self.action.get('else', None)  )
        if procs:
            return [proc.run( nxt ) for proc in procs]
        else:
            return None

#######################################################################################################
####  Range
#######################################################################################################

class xrange(XIterator):
    def __init__(self, begin=0, end=None, step=1, mode='unlimmitted'):
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
        if self.end == None: return self._nxt_ + self.step
        
        rst = self._nxt_
        if self.mode == 'unlimmitted':
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









#=================================================================================================================
#====  xmap
#=================================================================================================================
class xmap(XIterator):
    def __init__(self, action, *iters, **args):
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
        self.action = Group( action, **args )
        self.iters = iters

    def __iter__(self):
        self._nxt_ = [iter(n) for n in self.iters]
        self.action.reset()
        return self

    def __next__(self):

        nxt = [next(n) for n in self._nxt_]

        rst = self.action.run( nxt )
        if rst == None: return self.__next__()
        return rst if len(rst) > 1 else rst[0]
        

#############################################################################################################
####  Reduce
#############################################################################################################
def xreduce( action, *iters, init=None, **kargs ):
    # 初始化变量
    actions = gen_actions( action, ext_kargs = kargs )
    nxts = [iter(ite) for ite in iters]
    rst_num = len( actions )
    in_num = len( nxts )
    
    try:
        if init == None:
            last = [[next(n) for n in nxts]] * rst_num
            if in_num == 1: last = [ele[0] for ele in last]
        else:
            last = [init] * rst_num

        while True:
            curr = [next(n) for n in nxts]
            if len( curr ) == 1: curr = curr[0]
            last = [actions[i].run2(curr, last[i]) for i in range( rst_num )]

    except StopIteration:
        pass

    return last if len(last) > 1 else last[0]



def mapa(action, *iters, **kargs):
    return list(xmap( action, *iters, **kargs ))
    
    
#############################################################################################################
####  Apply
#############################################################################################################
def apply( actions, args, **kargs ):
    """
    高阶函数降级处理。
    Constraint-001: 当actions仅包含一个元素时，该action必须满足格式：(*args, **kargs)
    Constraint-002: 当actions包含多个元素时，非最后一个action元素必须满足格式：(action, *args, **kargs)
    """
    action_num = len( actions )

    # 0阶处理：直接返回数据
    if action_num == 0: return args
        
    # 1阶处理：返回处理的结果
    # Issue: 该1阶处理函数是否有该调用格式？这里貌似多了一个协议接口定义
    if action_num == 1: return actions[0]( *args, **kargs )

    # 2阶函数，直接求解该2阶函数的解
    if action_num == 2: return actions[0]( actions[1], *args, **kargs )

    # 高于2阶函数，逐阶降阶处理
    def _sub_(*s): return apply(actions[1:], s, **kargs)
    return actions[0]( _sub_, *args, **kargs )

def xapply( actions, *args, **kargs ):

    if not isinstance( actions, (list, tuple) ):
        actions = [actions]

    return apply( actions, args, **kargs )
    
def wapply( *args, **kargs ):
    action_num = kargs.get( 'anum', 0 )
    del kargs['anum']
    
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