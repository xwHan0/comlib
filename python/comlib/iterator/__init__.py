"""
"""

import re
import types

########################################################################################################
########  index
########################################################################################################
class index:
    def __init__(self, prefix=[]):
        if isinstance(prefix, list):
            self.idx = prefix[:]
        elif isinstance(prefix, str):
            patt = re.compile(r'\d+')
            rst = patt.findall(prefix)
            self.idx = [int(n) for n in rst]        # TBD

    def lvl(self): return len(self.idx)

    def __next__(self):
        self.idx[-1] += 1
        return index(self.idx)

    def __str__(self):
        return str(self.idx)

    def __iter__(self):
        return index(self.idx + [-1])



PRE,POST,DONE, Brach, LEAF = 0,1,2, 3,4
ITIMES = 999999

class IterTreeResult:
    def __init__(self, stack):
        self.value = stack[-1].value
        self.done = stack[-1].sta == DONE
        self.stack = stack

    def is_root(self):
        return len(self.stack) == 1
        
    def is_pre(self):
        node = self.stack[-1]
        return node.children == None or node.sta == PRE

    def is_post(self):
        node = self.stack[-1]
        return node.children == None or node.sta == POST or node.sta == DONE

    def is_done(self):
        return self.stack[-1].sta == DONE

    def iter_status(self):
        return self.stack[-1].sta

    def is_leaf(self):
        return self.stack[-1].children == None

    def depth(self):
        return len(self.stack)

    def v(self, func=None):
        if func == None:
            return self.value
        elif isinstance(func, int):
            return self.value[func]
        elif isinstance(func, list):
            return [self.value[f] for f in func]
        elif isinstance(func, types.FunctionType):
            return func(self.value)


class IterTreeNode:
    def __init__(self, value, sta=PRE):
        self.value = value
        self.sta = sta
        self.children = None

    
class IterTreeMatch:
    def __init__(self, pred, iter):
        self.pred = pred
        self.iter = iter


DEFAULT_MATCHES = [
    IterTreeMatch(lambda x:hasattr(x,'__iter__'), iter),
]


class tree:

    def __init__(self, *value, dir="down"):
        self.stack = [IterTreeNode(value)]
        self.matches = DEFAULT_MATCHES

        # 计算遍历方向
        dirs = dir if isinstance(dir, list) else [dir]
        self.dirs = []
        for dir in dirs:
            if dir == "up": self.dirs.append(self.up)
            elif dir == "down": self.dirs.append(self.down)
            elif dir == "updown": self.dirs.extend([self.up, self.down])
            elif dir == "downup": self.dirs.append(self.downup)
            elif dir == "wide": self.dirs.append(self.wide)

        # ==== Modify
        self.preappend = None   # 用于暂存预压入的节点
        self.require_pop = False # 用于记录是否需要弹出上一个节点
        self.goto_post = False
        # ==== End of Modify

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
        for dir in self.dirs:
            return dir()

    def mtree(self):
        self.down(False, False, 1)
        self.stack[-1].sta = DONE
        return self

    def down( self, down=True, up=False, it_num=ITIMES ):
        """深度优先遍历，从父节点遍历到子节点"""
        
        for _ in range(it_num):

            # ==== Modify: 把预存储的节点压入栈
            if self.require_pop:    # 需要把旧节点弹出栈
                self.stack.pop()    # 弹出栈
                self.require_pop = False    # 清除状态

            if self.goto_post:
                self.stack[-1].sta = POST   # 修改Brach节点状态为POST。会出现重复修改的问题
                self.goto_post = False

            if self.preappend: # 若有需要预入栈的节点
                self.stack.append(self.preappend)   # 把预入栈的节点压入栈
                self.preappend = None # 压入栈后，释放预入栈信息 
            # ==== End of Modify

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

                        # ==== Modify: 把原始需要压入stack的节点，先暂存到迭代器中。下次迭代前先压入
                        # Old:
                        # Push next elements into stack
                        # self.stack.append(IterTreeNode(nxt_datum))    # 注释掉

                        # New:
                        self.preappend = IterTreeNode(nxt_datum)    # 暂存
                        self.goto_post = True
                        # node.sta = POST
                        if down:
                            return IterTreeResult(self.stack)
                        else:
                            continue    # 否则执行到了Leaf节点
                        # ==== End of Modify

                except (StopIteration,TypeError):   #Leaf node
                    node.children = None
                        
                # ==== Modify
                # Old:
                # node.sta = POST # Modify top element status of stack
                # # Return
                # if down:
                #     return IterTreeResult(node.value, False, node, self.stack)
                # New:
                # if len(self.stack) == 1:
                    
                try:    # 叶子节点处理
                    nxt_datum = [next(i) for i in self.stack[-2].children]  # Parent element forward
                    self.preappend = IterTreeNode(nxt_datum)    # 保存需要入栈的节点
                except (StopIteration):
                    pass    # 迭代到最后一个元素，直接返回到父元素
                self.require_pop = True
                return IterTreeResult(self.stack)
                # ==== End of Modify
                        
            elif node.sta == POST:
                try:
                    # 判断是否到根节点
                    if len(self.stack) == 1:
                        node.sta = DONE
                    else: # 非根节点
                        # node.sta = PRE  # For next status. //没有必要，因为一定会被再次压入堆栈

                        # ==== Modify: 保存需要弹出节点的命令，和需要压入栈的新节点
                        # Old:
                        # self.stack.pop() # Pop stack
                        # New:
                        self.require_pop = True # 保存需要弹出节点状态
    
                        # Old:
                        # nxt_datum = [next(i) for i in self.stack[-1].children]  # Parent element forward
                        # self.stack.append(IterTreeNode(nxt_datum)) # 压入新节点
                        # New:
                        nxt_datum = [next(i) for i in self.stack[-2].children]  # Parent element forward
                        self.preappend = IterTreeNode(nxt_datum)    # 保存需要入栈的节点
                        # End of Modify
    
                except StopIteration: # IndexError for empty-stack
                    pass
    
                if up:
                    return IterTreeResult(self.stack)
    
            elif node.sta == DONE:
                    
                node.sta = PRE  # 为下一次迭代做准备
                raise StopIteration()
    
            else:
                raise Exception('Invalid status of FSM!')

    def up(self): return self.down(False, True)
    def downup(self): return self.down(True, True)
        
    def wide( self ):
        """广度优先遍历算法"""

        if len(self.stack) == 0: raise StopIteration

        node = self.stack[0]    #获取头节点，作为当前处理节点
        self.stack = self.stack[1:]

        try:
            node.children = self._get_children_iters_(node.value)   #获取子节点迭代器
            if node.children:
                for child in node.children: #遍历所有子节点
                    nxt_datum = [next(i) for i in child]    #获取子节点数据
                    self.stack.append(IterTreeNode(nxt_datum)) #压入队列
        except (StopIteration, TypeError): #Leaf node
            node.children = None

        return IterTreeResult(self.stack)

        
