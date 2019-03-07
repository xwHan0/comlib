import re
import types
from comlib.mapreduce.pred import Pred, PredString,  gen_preds, PredQMar
from comlib.mapreduce.child_relationship import TYPIC_CHILDREN_RELATIONSHIP, DEFAULT_CHILDREN_RELATIONSHIP, append_children_relationship, ChildRelation, ChildBypass
from comlib.iterators import LinkList
from comlib.mapreduce.stack import NodeInfo
from comlib.mapreduce.proc import Proc, ProcMap, ProcReduce, ProcIter, ProcQMar
from comlib.mapreduce.result import Result

from comlib.mapreduce.match import Match, MatchIter, MatchPredIter

PRE = 1
POST = 3
DONE = 4
SKIP = 5


class QMar:
    """
    在给定的树中，按给定顺序迭代-匹配过滤-执行动作。

    Query遍历树时，对于每个节点，都会遍历2遍。pre过程指从父节点第一次迭代到当前节点的遍历；post过程指子节点迭代完成返回到当前节点的遍历。

    # 基本概念

    * 查询字符串(query)：查找过滤条件表达式。具体格式参见Pred类说明
      Query中使用一个Pred列表来保存各个查询字符串的解析内容。

    * 匹配处理动作(procs)：查询匹配成功后的处理动作。参见Proc类说明
      Query中使用一个Proc列表来保存可能的多个动作对象。然后使用Pred类的动作序号中查找调用
      pre过程调用Proc.pre处理函数，post过程调用post处理函数
      

    * 子迭代器(children)：孩子节点迭代器获取类。参见ChildRelation类说明
      Query中以一个格式为：{objType:ChildRelationObj}的Dict保存子迭代器队形。
      Query按节点类型查找对应的子迭代器对象，然后获取节点的子节点Pred.match

    对于任何一个树节点，Query会依次执行如下动作:
    -- 执行Pred.match函数进行匹配
    -- 遍历子节点前执行match返回的Proc.pre处理函数
    -- 执行

    Query按照children定义的树结构的父-子节点关系遍历整个树，然后使用query定义的条件筛选满足条件的
    节点，筛选成功后使用procs定义的动作处理，然会返回。
  
    """
    
    MAX_IT_NUM = 999999
    CRITERIA_NODE_PATT = re.compile(r'#(\d+)')

    #===================  内部默认定义变量  ====================
    _matchIter_ = MatchIter()

    @staticmethod
    def configure(**cfg):
        for k,v in cfg.items():
            if k=='prefix':
                QMar.CRITERIA_PATT = [
                    (re.compile(r'{0}(\d+)'.format(v)), r'node[\g<1>]'),
                    (re.compile(r'{0}{0}'.format(v)), r'node'),
                    (re.compile(r'{0}\.'.format(v)), r'node[0].'),
                ]
                QMar.CRITERIA_NODE_PATT = re.compile(r'{0}(\d+)'.format(v))
            elif k=='max_it_num':
                QMar.MAX_IT_NUM = v
    

    def __init__(self, *datum, **cfg):
        """
        """
        
        # Set initial children relationship map table
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
    
        # New architecture fields
        self.step, self.result, self.cfg, self.matches = 1, Result(), cfg, []

        # self.pre_return/self.post_return
        
        self.stack = [NodeInfo(datum)]

    def query(self, pred):
        """设置pred匹配条件。
        pred: (*datum) => Boolean
        """
        self.matches.append( MatchPredIter(pred) )
        self.pre_return, self.post_return = True, False
        self.step = 10
        return self

    # 设置children获取表
    def append_children_relationship(self, children):
        """追加children子迭代器关系。

        children参数可以为以下类型：
        * string: 设置默认子迭代器为ChildAttr(children)
        * function: 设置默认子迭代器为ChildFunction(children)
        * dict: 追加children迭代器映射表到当前Query中。若其中key为string，则使用ChildAttr(val)作为子迭代器

            - [](Default): The "node" is iterable data, like array. The sub data can got by iterating the node data
    - [func]: Acquire the sub-nodes set via node.func() method
    - [func args]: Acquire the sub-nodes set via node.func(args) method. Now support below args parameter
      -- '$xxx': A string started with '$'. Iterator will use objName to replace this args
      -- Other string: Iterator use this string to fill the args of func

        """
        self.children_relationship = append_children_relationship(self.children_relationship, children)
        return self
   
    def append_proc(self, proc):
        """追加匹配成功动作处理Proc类实例proc"""
        self.procs.append(proc)
        return self

    def set_proc(self,proc):
        """修改处理动作为proc"""
        self.procs = [proc]
        return self
        
    def append_qmar(self, *qmars):
        """依次添加QMar类qmars到当前Query"""
        for qmar in qmars:
            if issubclass(qmar, ChildRelation):
                self.children_relationship += {qmar, ChildBypass()}
            if issubclass(qmar, Pred):
                self.preds[0].append(PredQMar(qmar))
                if issubclass(qmar, Proc):
                    self.preds[0][-1].proc = ProcQMar()
        return self
       
    def clear_pred(self):
        """清空当前Query的Pred条件"""
        self.preds = [[]]
        return self
       
    def initial(self, init=None):
        self.result.rst = init
        return self
   
    def assist(self, *datum, children={}):
        """
        Append assist collection 'node' which children is children for iterator.
        """
        self.append_children_relationship(children)
        self.stack[-1].datum += datum
        return self
   
    def filter(self, query='*'):
        """Set query-string"""
        self.preds = gen_preds(query)
        self.stack[-1].pred_idx = len(self.preds) - 1
        return self
        
    def map(self, proc=None):
        """并行处理"""
        if isinstance(proc, types.FunctionType):
            self.procs = [ProcMap(proc)]
        else:
            self.procs = [proc]
        self._bind_proc()
        return self
        
    def reduce(self, reduce_proc, initial=None, post=None):
        """归并"""

        self.procs = [ProcReduce(reduce_proc)]
        self.result.rst = initial
        self._bind_proc()

        return self._next_new( )
        
    def run(self): 
        """执行迭代并返回结果。"""
        if len(self.stack[0].datum) == 0:
            def delay_query(*datum, children={}):
                self.assist(*datum, children=children)
                return self._next_new()
            return delay_query
        else:
            self._initial_()
            return self._next_new()
        
    def r(self):
        """返回当前求值结果为内容的query"""
        return QMar(list(iter(self)))
        
    def skip( self, n=1 ):
        """跳过前n个节点后开始遍历。
         skip并不会破坏数据的树结构，仅仅是在遍历迭代是略过前几个节点。这里的略过不仅仅指pre过程，也包括post过程。
"""
        
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
            if self.step < 9:   # Step-9: Set matches
                self.pre_return = True
                self.post_return = False
            # Process Step-9
            self.matches = [QMar._matchIter_]
            
        self.step = 10

 

    def _get_children_iter(self, *node):
        nxt = self.children_relationship.get(
            type(node[0]),
            self.children_relationship.get('*',DEFAULT_CHILDREN_RELATIONSHIP))  # 查找处理类实例
        return nxt.sub(*node)  # 调用类函数处理
    
    def __iter__(self):
        self._initial_()
        return self

    def __next__(self):
        return self._next_new()
        
    def _next_new( self ):
        
        for ite_cnt in range(QMar.MAX_IT_NUM):
            
            # 获取当前处理的节点
            node = self.stack[-1]
            
            if node.sta == PRE: # PRE处理过程
                
                #================  Match子过程  ===============
                if isinstance(node.datum[0], Match):
                    node.action = node.datum[0].match(*node.datum, result=self.result, stack=self.stack)
                else:
                    pred = self.matches[node.pred_idx]
                    node.action = pred.match(*node.datum, result=self.result, stack=self.stack)

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
                    pred_idx = max(0, node.pred_idx - 1) if node.action else node.pred_idx
                    self.stack.append(NodeInfo(nxt_datum, pred_idx=pred_idx))
                    
                # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
                except (StopIteration,TypeError):   #Leaf node
                    # Process
                    if node.action:
                        node.children = None
                        rst = node.action.pre(*node.datum, result=self.result, stack=self.stack)
                    

                # Modify top element status of stack
                node.sta = POST
                
                # Return
                if node.action and self.pre_return:
                   return rst
                    
            elif node.sta == POST:

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
                        if self.stack[-1].action:
                            self.stack[-1].action.reduce(*node.datum, stack=self.stack, result=self.result)

                        # Parent element forward
                        nxt_datum = [next(i) for i in self.stack[-1].children]
                        self.stack.append(NodeInfo(nxt_datum))

                except StopIteration: # IndexError for empty-stack
                    pass

                if node.action and self.post_return:
                   return rst

            elif node.sta == DONE:
                
                node.sta = PRE  # 为下一次迭代做准备
                if self.pre_return or self.post_return:
                    raise StopIteration()
                else:
                    return self.result.rst

            elif node.sta == SKIP:  # SKIP 状态继续保持

                self.skip()  #恢复现场，为下次遍历做准备
                if self.pre_return or self.post_return:
                    raise StopIteration()
                else:
                    return self.result.rst

            else:
                raise Exception('Invalid status of FSM!')
        

            

