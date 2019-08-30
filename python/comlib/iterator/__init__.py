"""
"""

########################################################################################################
########  index
########################################################################################################
class index:
    def __init__(self, prefix=[]):
        if isinstance(prefix, list):
            self.idx = prefix[:]
        elif isinstance(prefix, str):
            self.idx = []        # TBD

    def lvl(self): return len(self.idx)

    def __next__(self):
        self.idx[-1] += 1
        return index(self.idx)

    def __str__(self):
        return str(self.idx)

    def __iter__(self):
        return index(self.idx + [-1])



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


class tree:
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
        
        for _ in range(tree.ITIMES):
                
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
        
