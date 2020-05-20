"""
"""

from comlib.ex.math import xmin

from comlib.mapreduce.match import Match
from comlib.mapreduce.child import Child

from comlib.mapreduce.iterator_result import Result
from comlib.mapreduce.tree.result_tree import ResultTree

from comlib.mapreduce.middleware.middleware import MiddleWare



PRE,POST,DONE = 0,1,2


class IterTreeResult:
     def __init__(self, value, done, status, stack):
        self.value = value
        self.done = done
        self.status = status
        self.stack = stack


class IterTreeNode:
    def __init__(self, value, sta=PRE):
        self.value = value
        self.sta = sta

    
class IterTreeMatch:
    def __init__(self, pred, iter):
        self.pred = pred
        self.iter = iter


DEFAULT_MATCHES = [
    IterTreeMatch(lambda x:hasattr(x,'__iter__'), iter),
]


class iterTree:
    ITIMES = 999999

    def __init__(self, *value):
        self.stack = [IterTreeNode(value)]
        self.matches = DEFAULT_MATCHES

    def _get_child_iter_(self, child):
        for match in self.matches:
            if match.pred(child):
                return match.iter(child)
        return None

    def _get_children_iters_(self, children):
        rst = []
        for child in children:
            iter = self._get_child_iter_(child)
            if iter == None:
                return None
            else:
                rst.append(iter)
        return rst

    def __iter__(self):
        return self

    def __next__( self ):
        
        for _ in range(iterTree.ITIMES):
                
            # 获取当前处理的节点
            node = self.stack[-1]
                
            if node.sta == PRE: # PRE处理过程
                      
                # Next prepare
                try:
                        
                    # 获取datum子节点迭代器集合
                    node.children = self._get_children_iters_(node.value)
                    if node.children:
                        # 获取下一个子节点
                        nxt_datum = [next(i) for i in node.children]
                        # Push next elements into stack
                        self.stack.append(IterTreeNode(nxt_datum))
                except (StopIteration,TypeError):   #Leaf node
                    node.children = None
                        
                # Modify top element status of stack
                node.sta = POST
                # Return
                return IterTreeResult(node.value, False, PRE, self.stack)
                        
            elif node.sta == POST:
                try:
                    # 判断是否到根节点
                    if len(self.stack) == 1:
                        node.sta = DONE
                    else: # 非根节点
                        node.sta = PRE  # For next status
                        # Pop stack
                        self.stack.pop()
    
                        # Parent element forward
                        nxt_datum = [next(i) for i in self.stack[-1].children]
                        self.stack.append(IterTreeNode(nxt_datum))
    
                except StopIteration: # IndexError for empty-stack
                    pass
    
                return IterTreeResult(node.value, False, PRE, self.stack)
    
            elif node.sta == DONE:
                    
                node.sta = PRE  # 为下一次迭代做准备
                raise StopIteration()
    
            else:
                raise Exception('Invalid status of FSM!')
        


#=================================================================================================================
#====  Proc
#=================================================================================================================
class Action:
    def __init__(self, action, default=None, itn=1, **kargs):

        self.action, self.default = action, default

        if hasattr( action, '__call__' ):
            # 生成action处理所需的额外参数
            self.glb_param = {}
            for param in action.__code__.co_varnames[:action.__code__.co_argcount]:
                if param in kargs:
                    self.glb_param[param] = kargs[param]
            
            self.itn = xmin( itn, self.action.__code__.co_argcount )
        
    def run(self, nxt, stop):

        if hasattr( action, '__call__' ):
            if self.default != None:
                for i in range(len(nxt)):
                    nxt[i] = self.default[i] if stop[i] else nxt[i]
            args_num = self.action.__code__.co_argcount
            if args_num == 0:
                return self.action( *nxt )
            elif args_num == 1:
                return self.action( nxt[0] )
            else:
                if self.itn == 0:
                    return self.action( *nxt, **self.glb_param )
                else:
                    return self.action( *nxt[:self.itn], **self.glb_param )
        else:
            return self.action
         
        
def gen_actions( action=None, **args ):

    if isinstance( action, list ):
        rst = []
        for p in action:
            if hasattr( p, '__call__' ):
                rst.append( Action( p, args.get('default', None), args.get('itn', 0), **args  ) )
            elif isinstance( p, dict ):
                rst.append( Action( 
                    p.get( 'action', None ),
                    default = args.get('itn', p.get('default', None)),
                    itn = args.get('itn', p.get('itn', 0)),
                    **dict( p, **args)
                ) )
        return rst
    elif hasattr( action, '__call__' ):
        return [Action( action, args.get('default', None), args.get('itn', 0), **args )]
    else:
        return [action]


    
class Group:
    def __init__( self, action=None, **args ):
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
        
    def run( self, nxt, stop ):
        if self.criteria == None:
            return [action.run( nxt, stop ) for action in self.action]
        
        cls = next( self.cri_nxt )
        procs = self.action.get( cls, self.action.get('else', None)  )
        if procs:
            return [proc.run( nxt, stop ) for proc in procs]
        else:
            return None


#=================================================================================================================
#====  xmap
#=================================================================================================================
class xmap:
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
        * default: {None(default) | list} -- 迭代器填充值
        * itn: {integer} -- 迭代参数个数
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

        nxt, stop = [next(self._nxt_[0])], [False]

        for n in self._nxt_[1:]:
            try:
                nxt.append( next(n) )
                stop.append( False )
            except StopIteration:
                nxt.append( None )
                stop.append( True )

        rst = self.action.run( nxt, stop )
        if rst == None: return self.__next__()
        return rst if len(rst) > 1 else rst[0]
