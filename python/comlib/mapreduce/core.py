import re
import types
from comlib.mapreduce.pred import Pred, PredString,  gen_preds, PredQMar
from comlib.mapreduce.child_relationship import TYPIC_CHILDREN_RELATIONSHIP, DEFAULT_CHILDREN_RELATIONSHIP, append_children_relationship, ChildRelation, ChildBypass
from comlib.iterators import LinkList
from comlib.mapreduce.stack import NodeInfo
from comlib.mapreduce.proc import Proc, ProcMap, ProcReduce, ProcIter, ProcQMar
from comlib.mapreduce.result import Result

PRE = 1
POST = 3
DONE = 4
SKIP = 5


class Query:
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

    @staticmethod
    def configure(**cfg):
        for k,v in cfg.items():
            if k=='prefix':
                Query.CRITERIA_PATT = [
                    (re.compile(r'{0}(\d+)'.format(v)), r'node[\g<1>]'),
                    (re.compile(r'{0}{0}'.format(v)), r'node'),
                    (re.compile(r'{0}\.'.format(v)), r'node[0].'),
                ]
                Query.CRITERIA_NODE_PATT = re.compile(r'{0}(\d+)'.format(v))
            elif k=='max_it_num':
                Query.MAX_IT_NUM = v
    

    def __init__(self, *datum, query='*', children={}, procs=None, **cfg):
        """cfg argument:
            * skip_first_seq{Boolean}:
        """
        
        # 保存并解析选择字符串
        self.preds = gen_preds(query)
        # self.min_node_num = max(map(int, Query.CRITERIA_NODE_PATT.findall(query)), default=1)
            
        # Set initial children relationship map table
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
        # Append new children relationship map table
        append_children_relationship(self.children_relationship, children)
    
        # New architecture fields
        self.step, self.datum, self.result, self.cfg, self.procs = 1, datum, Result(), cfg, procs if procs else [ProcIter()]
        
        self._bind_proc()
        
        self.stack = [NodeInfo(self.datum, pred_idx=len(self.preds)-1)]

        # Skip first sequence process
        # skip_first_seq = self.cfg.get('skip_first_seq', True)
        # if skip_first_seq and isinstance(self.datum[0], (list,tuple,LinkList)):
        #     # self.preds.append(PredSkip())
        #     self.skip()

        # self.stack = [NodeInfo(self.datum, pred_idx=len(self.preds)-1)]
        


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
                self.preds[0].append(PredQMar())
                if issubclass(qmar, Proc):
                    self.preds[0][-1].proc = ProcQMar()
                
        return self
       
    def clear_pred(self):
        """清空当前Query的Pred条件"""
        self.preds = [[]]
       
    def initial(self, init=None):
        self.result.rst = init
        return self
   
    def assist(self, *datum, children={}):
        """
        Append assist collection 'node' which children is children for iterator.
        """
        self.datum += datum
        self.append_children_relationship(children)
        self.stack[-1].datum = self.datum
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
        if len(self.datum) == 0:
            def delay_query(*datum, children={}):
                self.assist(*datum, children=children)
                return self._next_new()
            return delay_query
        else:
            return self._next_new()
        
    def r(self):
        """返回当前求值结果为内容的query"""
        return Query(list(iter(self)))
        
    def skip( self, n=1 ):
        """跳过前n个节点后开始遍历。
         skip并不会破坏数据的树结构，仅仅是在遍历迭代是略过前几个节点。这里的略过不仅仅指pre过程，也包括post过程。
"""
        
        for ite_cnt in range(n):
            
            # Get stack tail information for process
            node = self.stack[-1]
            
            node.sta, node.succ = SKIP, False   # 不需要迭代
            
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
        
    def _bind_proc(self):
        for preds in self.preds:
            for pred in preds:
                pred.proc = self.procs[pred.proc_idx]

    def _match(self, preds, datum):
        for pred in preds:
            rst = pred.match(*datum)
            if rst > 0: # Succcess
                return rst, pred.proc, pred
        return 0, Proc(), Pred()

    def _get_children_iter(self, *node):
        nxt = self.children_relationship.get(
            type(node[0]),
            self.children_relationship.get('*',DEFAULT_CHILDREN_RELATIONSHIP))  # 查找处理类实例
        return nxt.sub(*node)  # 调用类函数处理
    
    def __iter__(self):
        # if self.min_node_num > len(self.datum):
        #     raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.datum)))
        
        # self.stack[-1].sta = PRE
        return self

    def __next__(self):
        return self._next_new()
        
    def _next_new( self ):
        
        #if self.step < 3: # Step3 is normal work
       #     if self.step < 2: # Step2 need append proc
              #  if self.step < 1: # Step1 need re-calculate proc
                    # Step0:
         #           pass
            # Srep1:
   #         for pred in self.preds:
           #     pred.bind_proc(self.procs)
                    
         # Step2:
     #    for pred in self.preds:
  #          if pred.proc == None:
           #     pred.bind_proc(self.procs)
        
        for ite_cnt in range(Query.MAX_IT_NUM):
            
            # Get stack tail information for process
            node = self.stack[-1]
            
            # Process with sta
            if node.sta == PRE:
                
                # Filter
                preds = self.preds[node.pred_idx]
                #result, proc = pred.match(*node.datum)
                result, proc, pred = self._match(preds, node.datum)
                
                # is_pre, is_pre_yield, is_post, is_post_yield = self.procs[pred.proc_idx].actions(result)
            
                # Record filter result
                node.succ, node.proc_idx, node.pred, node.proc = pred.is_succ(result), pred.proc_idx, pred, proc

                
                # Next prepare
                try:
                    
                    is_sub = pred.is_sub(result)
                    if is_sub:
                        # Get all datum iterators and assign to parent
                        node.children = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                        # Get next elements of iterators
                        nxt_datum = [next(i) for i in node.children]

                    # Process
                    if node.succ:
                        #self.procs[node.proc_idx].pre(self.result, *node.datum, stack=self.stack)
                        proc.pre(self.result, *node.datum, stack=self.stack)

                    # Push next elements into stack
                    if is_sub: 
                        pred_idx = max(0, node.pred_idx - 1) if pred.is_done(result) else node.pred_idx
                        self.stack.append(NodeInfo(nxt_datum, pred_idx=pred_idx))
                    
                    node.sta = POST
              
                    # Return
                    if node.succ and proc.pre_yield():
                    #if node.succ and self.procs[node.proc_idx].pre_yield():
                        return self.result.rst
                    
                # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
                except (StopIteration,TypeError):   #Leaf node
                    # Process
                    if node.succ:
                        node.children = None
                        #self.procs[node.proc_idx].pre(self.result, *node.datum, stack=self.stack)
                        proc.pre(self.result, *node.datum, stack=self.stack)
                    
                    #     self.procs[node.proc_idx].post(self.result, *node.datum, stack=self.stack)
                    
                    # if len(self.stack) == 1: # Just ONE element in tree
                    #     node.sta = DONE
                    # else: # 非根节点
                    #     # Parent element forward
                    #     try:
                    #         self.stack.pop()
                    #         nxt_datum = [next(i) for i in self.stack[-1].children]
                    #         self.stack.append(NodeInfo(nxt_datum))
                    #     except StopIteration:
                    #         pass
                            
                    # if node.succ and self.procs[node.pred.proc_idx].is_yield():
                    #     return self.result.rst
                    
                # Modify top element status of stack
                node.sta = POST
                
                # Return
                if node.succ and proc.pre_yield():
                #if node.succ and self.procs[node.proc_idx].pre_yield():
                   return self.result.rst
                    
            elif node.sta == POST:

                # Process
                if node.succ:
                    #self.procs[node.pred.proc_idx].post(self.result, *node.datum, stack=self.stack)
                    node.proc.post(self.result, *node.datum, stack=self.stack)
                    
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
                        self.stack.append(NodeInfo(nxt_datum))

                except StopIteration: # IndexError for empty-stack
                    pass

                if node.succ and node.proc.post_yield():
                #if node.succ and self.procs[node.pred.proc_idx].post_yield():
                   return self.result.rst

            elif node.sta == DONE:
                
                node.sta = PRE  # 为下一次迭代做准备
                if self.procs[0].is_yield():
                    raise StopIteration()
                else:
                    return self.result.rst

            elif node.sta == SKIP:  # SKIP 状态继续保持

                # self.stack.append(self.skip_node) 
                self.skip()  #恢复现场，为下次遍历做准备
                if self.procs[0].is_yield():
                    raise StopIteration()
                else:
                    return self.result.rst

            else:
                raise Exception('Invalid status of FSM!')
        

            

