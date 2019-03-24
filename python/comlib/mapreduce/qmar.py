"""
Query-Match-Action-Return
第一个遍历引起
"""
import re
import types

from comlib.mapreduce.child_relationship import TYPIC_CHILDREN_RELATIONSHIP, append_children_relationship
from comlib.mapreduce.stack import NodeInfo
from comlib.mapreduce.result import Result
from comlib.mapreduce.match import Match, MatchIter, MatchPredIter, get_match
from comlib.mapreduce.child import Child

PRE = 1 POST = 3
DONE = 4
SKIP = 5


class Qmar:
    """
    在给定的树结构中，按给定顺序执行迭代(Query)-匹配(Match)-执行(Action)-返回(Return)动作。

    Qmar遍历树时，对于每个节点，都会经过3个小过程:
    - pre过程: 指从父节点第一次迭代到当前节点的遍历
    - reduce过程：指一个子节点遍历完成，返回当前节点的遍历
    - post过程: 指子节点迭代完成返回到当前节点的遍历

    # 迭代遍历(Query)
      Qmar按照一定的规则寻找每个树节点的子节点迭代器，然后一一遍历之。
      - Qmar的子节点迭代器规则由Child类来承载。详细定义参见Child类说明。
      - Qmar使用一个格式为{objType:ChildObj}的Dict来保存各个类型节点的子节点迭代器获取Child类。 除了使用Child实例来获取子节点迭代器外，若节点是Child的派生子类，Qmar也会使用该类(Child)定义的sub函数来获取
        子节点迭代器；或者若树节点定义了__iter__函数，则使用该函数来获取子节点迭代器。
# 匹配过滤(Match)
      Qmar使用Match对每个树节点进行过滤匹配，匹配成功则执行相关动作，否则跳过该节点。
      - Qmar的匹配由Match类定义。详细定义参见Match类说明。
      - Qmar使用一个[Match]的列表来存储定义的各个匹配动作。Qmar从该列表的头到尾依次匹配各个树节点。最终匹配成功的节点
        执行规定的相关动作

    # 执行动作(Action)
      Qmar匹配成功一个树节点后，执行预定义的动作。
      - 预定义动作由Action类定义。详细定义参见Action类说明。
      - Action包含了PRE、REDUCE和POST过程。
      - 每个Match的match函数若匹配成功，都会返回一个事先定义个Action实例。

    # 返回结果(Return)
      Qmar返回动作Action执行后的结果。
      - Qmar支持2种返回的结果类型：
        ** 迭代完成一次性返回最终结果
        ** 每匹配成功一个节点，就基于当前节点返回一个结果
      - Qmar定义并实例化了一个Result对象来保存返回结果。当前用户也可以使用stack来保存每级执行的结果
    """
    
    MAX_IT_NUM = 999999
    CRITERIA_NODE_PATT = re.compile(r'#(\d+)')
#===================  内部默认定义变量  ====================
    _matchIter_ = MatchIter()

    @staticmethod
    def configure(**cfg):
        for k,v in cfg.items():
            if k=='prefix':
                Qmar.CRITERIA_PATT = [
                    (re.compile(r'{0}(\d+)'.format(v)), r'node[\g<1>]'),
                    (re.compile(r'{0}{0}'.format(v)), r'node'),
                    (re.compile(r'{0}\.'.format(v)), r'node[0].'),
                ]
                Qmar.CRITERIA_NODE_PATT = re.compile(r'{0}(\d+)'.format(v))
            elif k=='max_it_num':
                Qmar.MAX_IT_NUM = v
    

    def __init__(self, *datum, **cfg):
        """使用树结构*datum来创建一个Qmar遍历实例。
        """
        
        # Set initial children relationship map table
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
    
        # New architecture fields
        self.step, self.result, self.cfg, self.matches = 1, Result(), cfg, []

        # self.pre_return/self.post_return
        
        self.stack = [NodeInfo(datum)]

    def child(self, typ, sub):
        """追加child关系定义"""
        self.children_relationship[typ] = Child._gen_child_(sub)
        return self

    def query(self, pred):
        """设置pred匹配条件。
        pred: (*datum) => Boolean
        """
        self.matches.append( MatchPredIter(pred) )
        self.step = 10
        return self

    def match(self, pred, pre=None, reduce=None, post=None):
        self.matches.append( Match._gen_match_(pred, pre=pre, reduce=reduce, post=post) )
        self.step = 10
        return self
        
    def match2(self, mt):
        self.stack[-1].match = mt
        self.step = 10
        return self

    def initial(self, init=None):
        self.result.rst = init
        return self
   
    def assist(self, *datum, children={}):
        """
        Append assist collection 'node' which children is children for iterator.
        """
        # self.append_children_relationship(children)
        self.stack[-1].datum += datum
        return self
       
    def run(self, enumrate=True): 
        """执行迭代并返回结果。"""
        self._enumerate_ = enumerate
        if len(self.stack[0].datum) == 0:
            def delay_query(*datum, children={}):
                self.assist(*datum, children=children)
                return self.__next__()
            return delay_query
        else:
            self._initial_()
            return self.__next__()
        
    def skip( self, n=1 ):
        """跳过前n个节点后开始遍历。
         skip并不会破坏数据的树结构，仅仅是在遍历迭代是略过前几个节点。这里的略过不仅仅指pre过程，也包括post过程。"""
        
        for ite_cnt in range(n):
            
            # Get stack tail information for process
            node = self.stack[-1]
            
            node.sta, node.action = SKIP, None   # 不需要迭代
            
            # Next prepare
            try:
                    
                # Get all datum iterators and assign to parent
                node.children = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                # Get next elements of iterators
                nxt_datum = [next(i) for i in node.children]

                self.stack.append(NodeInfo(nxt_datum, pred_idx=0))
                    
            # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
            except (StopIteration,TypeError): 
                node.children = None
                break
                
        # self.skip_node = self.stack[-1] # 保存遍历开始节点，为遍历结束后恢复现场准备

        return self
        
    def _initial_(self):
        if self.step < 10:      # Step-10: Normal Process
         
            # Process Step-9
            self.matches = [Qmar._matchIter_]
            
        self.step = 10

 

    def _get_children_iter(self, *node):
        nxt = self.children_relationship.get(
            type(node[0]),
            self.children_relationship.get('*'))  # 查找处理类实例

        if nxt:
            return nxt.sub(*node)  # 调用类函数处理
        elif hasattr(node[0], '__iter__'):
            return iter(node[0])
        elif isinstance(node[0], Child):
            return node[0].sub(*node)
        

    
    def __iter__(self):
        self._initial_()
        self._enumerate_ = True
        return self
        
    def __next__( self ):
        
        for ite_cnt in range(Qmar.MAX_IT_NUM):
            
            # 获取当前处理的节点
            node = self.stack[-1]
            
            if node.sta == PRE: # PRE处理过程
                
                #================  Match子过程  ===============
                if isinstance(node.datum[0], Match):
                    node.match, node.action = node.datum[0], node.datum[0].match(*node.datum, result=self.result, stack=self.stack)

                else:
                    # 匹配当前节点，并获取匹配match与action
                    node.matched, node.action = get_match(node.match, *node.datum, stack=self.stack, result=self.result)
                    #pred = self.matches[node.pred_idx]
                    #node.action = pred.match(*node.datum, result=self.result, stack=self.stack)

                # Next prepare
                try:
                    
                    # 获取datum子节点迭代器集合
                    node.children = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                    # 获取下一个子节点
                    nxt_datum = [next(i) for i in node.children]

                    # PRE处理
                    if node.action:
                        rst = node.action.pre(*node.datum, stack=self.stack, result=self.result)

                    # Push next elements into stack
                    # pred_idx = max(0, node.pred_idx - 1) if node.action else node.pred_idx
                    self.stack.append(NodeInfo(nxt_datum, match=node.matched.next)
                    
                # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
                except (StopIteration,TypeError):   #Leaf node
                    # Process
                    if node.action:
                        node.children = None
                        rst = node.action.pre(*node.datum, result=self.result, stack=self.stack)
                    

                # Modify top element status of stack
                node.sta = POST
                
                # Return
                if node.action and rst!=None:
                   return rst
                    
            elif node.sta == POST:

                if hasattr(node.datum[0], 'matchp'):
                    node.action = node.datum[0].matchp(*node.datum, stack=self.stack, result=self.result)

                # Process
                if node.action:
                    rst = node.action.post(*node.datum, stack=self.stack, result=self.result)
                    
                try:

                    # 判断是否到根节点
                    if len(self.stack) == 1:
                        node.sta = DONE
                    else: # 非根节点
                        node.sta = PRE  # For next status
                        # Pop stack
                        self.stack.pop()

                        # 执行Reduce子过程
                        if hasattr(self.stack[-1].datum[0], 'matchp') and node.action and self.stack[-1].action:
                            self.stack[-1].action.reduce(*node.datum, stack=self.stack, result=self.result)

                        # Parent element forward
                        nxt_datum = [next(i) for i in self.stack[-1].children]
                        self.stack.append(NodeInfo(nxt_datum))

                except StopIteration: # IndexError for empty-stack
                    pass

                if node.action and rst!=None:
                   return rst

            elif node.sta == DONE:
                
                node.sta = PRE  # 为下一次迭代做准备
                if self._enumerate_:
                    raise StopIteration()
                else:
                    return self.result.rst

            elif node.sta == SKIP:  # SKIP 状态继续保持

                self.skip()  #恢复现场，为下次遍历做准备
                if self._enumerate_:
                    raise StopIteration()
                else:
                    return self.result.rst

            else:
                raise Exception('Invalid status of FSM!')
        

            

