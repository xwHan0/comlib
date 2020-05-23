"""
常用高阶函数迭代器库。
"""
from types import FunctionType
from comlib import xmin
    
def xapply( action, *args, **kargs ):
    return action( *args, **kargs )
    

class XIterator:
    def apply( self, action, *args, **kargs ):
        return action( *args, self **kargs )
        
    def xmap( self, action, *iters, **kargs ):
        return xmap( action, self, *iters, **kargs )
        
    def to_list(self): return list(self)



#=================================================================================================================
#====  Proc
#=================================================================================================================
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
        
        if args_num == 1:
            return self.action( *nxt, **self.glb_param )
        else:
            return self.action( *nxt[:args_num-1], **self.glb_param )    
        
        
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
                self.action[p] = gen_actions( action[p], **args )
        else:
            self.action = gen_actions( action, **args )
            
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
        self._nxt_ += self.step
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
        


def mapa(action, *iters, **kargs):
    return xmap( action, *iters, **kargs ).to_list()
    
    
@classmethod
def xmap(cls, action, *iters, **kargs):
    return xmap( action, *iters, cls, **kargs )
    
list.xmap = xmap
    
    
    