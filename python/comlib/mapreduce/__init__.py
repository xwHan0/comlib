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
    def __init__(self, proc=None, **args):

        # 默认参数
        default = {
            'index_name' : 'idx',   # 默认序号形参名称
        }

        if isinstance( proc, list ):
            self.proc = proc
            for p in self.proc:
                if hasattr( p, '__call__' ):
                    p = dict( default, **{'proc': p} )
                    p = dict( p, **args )
                elif isinstance( p, dict ):
                    p = dict( default, **p )
        elif hasattr( proc, '__call__' ):
            p = dict( default, **{'proc': p} )
            self.proc = [dict( p, **args )]
        else:
            self.proc = []


    



#=================================================================================================================
#====  xmap
#=================================================================================================================
class xmap:
    def __init__(self, proc, *iters, fillval=None, grp=None, grp_ignore=Proc(), **args):
        self.proc = proc
        self.iters = iters
        self.fillval = fillval
        self.grp = grp
        self.grp_ignore = grp_ignore
        self.args = args

    def __iter__(self):
        self._nxt_ = [iter(n) for n in iters]
        self._grp_nxt_ = iter(self.grp)
        self._idx_ = 0  # 序号
        return self

    def __next__(self):
        grp = next( self._grp_nxt_ )
        procs = self.proc.get( grp, self.grp_ignore )

        nxt, first = [], true
        for n in self._nxt_:
            try:
                nxt.append( next(n) )
            except StopIteration:
                if first: raise StopIteration()
                nxt.append( None )
            first = False


        rst = []
        for proc in procs:
            proc_arg_num = proc.__code__.co_argcount
            if proc_arg_num == 0:
                proc_nxt = []
                for i in range(len(self.iters)):
                    if nxt[i] == None:
                        proc_nxt.append( proc['default'][i-1] )
                    else:
                        proc_nxt.append( nxt[i] )
                if proc['index_name'] in proc.__code__.co_varname:
                    rst.append( *proc_nxt, **{proc['index_name']: self._idx_} )
                else:
                    rst.append( *proc_nxt )
            elif proc_arg_num == 1:
                rst.append( proc( nxt[0] ) )
            elif proc_arg_num == 2:
                if len( self.iters ) == 1:
                    rst.append( proc['proc']( nxt[0], self._idx_ ) )
                else:
                    rst.append( proc['proc']( nxt[0], proc['default'][0] if nxt[1]==None else nxt[1] ) )

        self._idx_ += 1     # 序号递增

        return rst

