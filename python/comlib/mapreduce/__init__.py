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
class Proc:
    def __init__(self, proc, default=None, itn=1, **kargs):
        proc_param_tuple = proc.__code__.co_varnames[:proc.__code__.co_argcount]
        
        # 
        self.glb_param = {}
        for param in proc_param_tuple:
            if param in kargs:
                self.glb_param[param] = kargs[param]
        
        self.proc = proc
        self.default = default
        self.itn = xmin( itn, self.proc.__code__.co_argcount )
        
    def run(self, nxt, stop):
        if self.default != None:
            for i in range(len(nxt)):
                nxt[i] = self.default[i] if stop[i] else nxt[i]
        args_num = self.proc.__code__.co_argcount
        if args_num == 0:
            return self.proc( *nxt )
        elif args_num == 1:
            return self.proc( nxt[0] )
        else:
            if self.itn == 0:
                return self.proc( *nxt, **self.glb_param )
            else:
                return self.proc( *nxt[:self.itn], **self.glb_param )
            
        

class Procs:
    def __init__(self, proc=None, **args):

        # 默认参数
        default = {
            'index_name' : 'idx',   # 默认序号形参名称
        }
        
        
def gen_procs( proc=None, **args ):

    if isinstance( proc, list ):
        rst = []
        for p in proc:
            if hasattr( p, '__call__' ):
                rst.append( Proc( p, args.get('default', None), args.get('itn', 0), **args  ) )
            elif isinstance( p, dict ):
                rst.append( Proc( 
                    p.get( 'proc', None ),
                    default = args.get('itn', p.get('default', None)),
                    itn = args.get('itn', p.get('itn', 0)),
                    **dict( p, **args)
                ) )
        return rst
    elif hasattr( proc, '__call__' ):
        return [Proc( proc, args.get('default', None), args.get('itn', 0), **args )]
    else:
        return []


    



#=================================================================================================================
#====  xmap
#=================================================================================================================
class xmap:
    def __init__(self, proc, *iters, grp=None, grp_ignore=Proc(), **args):
        self.proc = gen_procs( proc, **args )
        self.iters = iters
        self.grp = grp
        self.grp_ignore = grp_ignore
        self.args = args

    def __iter__(self):
        self._nxt_ = [iter(n) for n in iters]
        self._grp_nxt_ = iter(self.grp)
        return self

    def __next__(self):
        #grp = next( self._grp_nxt_ )
        #procs = self.proc.get( grp, self.grp_ignore )
        procs = self.proc

        nxt, stop = [next(self._nxt_[0])], [False]

        for n in self._nxt_[1:]:
            try:
                nxt.append( next(n) )
                stop.append( False )
            except StopIteration:
                nxt.append( None )
                stop.append( True )

        rst = [proc.run( nxt, stop ) for proc in procs]
        return rst if len(rst) > 1 else rst[0]
