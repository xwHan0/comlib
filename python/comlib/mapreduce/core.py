import re
import types
from comlib.mapreduce.pred import Pred, PredSelect, PredSkip, gen_preds
from comlib.mapreduce.child_relationship import TYPIC_CHILDREN_RELATIONSHIP, DEFAULT_CHILDREN_RELATIONSHIP, append_children_relationship
from comlib.iterators import LinkList
from comlib.mapreduce.stack import NodeInfo,PRE,POST
from comlib.mapreduce.proc import Proc, ProcMap, ProcReduce, ProcIter
from comlib.mapreduce.result import Result



class Query:
    """
    在给定的树中，按给定顺序迭代-匹配过滤-执行动作。


    # 查询字符串(Query-String)
    查询字符串是由用户指定的、告知query如何进行查询的字符串。查询字符串定义了查询过滤的动作，查询成功的执行动作和查询后的迭代动作。
    每个查询字符串由查询类型，过滤条件，动作序号和跳转标识四个部分组成。其格式为：
    '''
    关系条件 objName[过滤条件]@动作序号/跳转标识
    '''
    
    
    ## Relation Condition
    * ' ': Ancestor-Descendant relationship.
    * '>': Parent-Son relationship.

    
    ## 查询类型(Query-Type)
    匹配数据的数据类型。'*'或者忽略查询类型表示匹配所有的数据类型。

    ## 过滤条件(Query-Creitial)
    由'['和']'包裹的匹配条件表达式。该表达式的运算结果必须返回True或者False。省略过滤条件时（包括'[]'），表示无条件匹配。
    条件表达式为满足python的任意表达式。可以包括：变量，运算符，函数等任意类型。
    条件表达式支持下面的特殊变量表达。: ('nodes' represents current access nodes from all node)
    * #.attr: 获取节点nodes[0]的'attr'属性值。Get the attribute of nodes[0] like: 'nodes[0].attr'
    * #n: 获取nodes序列中的第n个节点node(n=0-N)。
    * #n.attr: Get the attribute of nodes[n] like: 'nodes[n].attr' (n=0-N)
    * ##: List of all nodes
    The special expression prefix '#' can be configured via 'prefix' argument of **cfg in constructor. For example,
    cfg['prefix']='$' means using '$n', '$n.attr' and '$$' to replace '#n', '#n.attr' and '##'
        
    * Node: Support 3-level '[]' pair in max in condition statement
     

    ## 动作序号(Match-Action)
    由'@'开头的数字字符串表达式(n=0~$)。省略动作序号时（包括'@'），表示采用默认的动作序号：0
    该序号为Actions定义的动作列表的序号。
    为Proc类的子类实例。请参考Proc类说明。

    ## 跳转标识(Jump-Flags)
    由'/'开头的字符表达式。表示匹配后的搜索跳转控制标识。
    'flags' decide the selection action and direction. They can be ignore with '/'
    - The iterate process when object match fail
      -- Default is continue next iterate
      -- 'o': Continue next iterate except the sub node of current node
      -- 'O': Break the iterate
    - The iterate process when pred match fail
      -- Default is continue next iterate
      -- 'c': Continue next iterate except the sub node of current node
      -- 'C': Break the iterate
    - The iterate process when match success
      -- Default is continue next iterate
      -- 's': Continue next iterate except the sub node of current node
      -- 'S': Break the iterate
    

    # 子迭代器(Children-Relationship)
    Parameter "children" formatted with list indicates the link method to sub data. There are below style:
    - [](Default): The "node" is iterable data, like array. The sub data can got by iterating the node data
    - [func]: Acquire the sub-nodes set via node.func() method
    - [func args]: Acquire the sub-nodes set via node.func(args) method. Now support below args parameter
      -- '$xxx': A string started with '$'. Iterator will use objName to replace this args
      -- Other string: Iterator use this string to fill the args of func
    
    'func' support below two type:
    - Function format: func has __call__ attribute. Iterator use this func
    - String format: 对于类方法函数，存在继承。需要根据当前实例的类来调用对应的继承函数。所以使用字符串来标识这种函数

    * Notes: iterator supports getting the sub from List, Tuple and CommonIterator automatic 
    
    * Support 单跳节点：
      ** 若获取的下一跳不是迭代器，则返回[下一跳]。
 





# Feature
* Support custom sub-pointer via parameter children
  -- Support 3 types for children. See 'Sub-node Acquire Method Define' for more detail
  -- Support Array-like automatic get sub
    *** ***Note:*** Function children NOT support

* Support JQuery-like search Syntax String via parameter 'query'
  -- SearchString ::= SearchPattern, .../glb_flags
    *** SearchPattern ::= [obj][pred][flags]
  -- Support many flags in searchPattern
    
* Support matching pred function via parameter 'pred'
  -- The format of pred is: (node,idx,count) => Boolean

  
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
        self.min_node_num = max(map(int, Query.CRITERIA_NODE_PATT.findall(query)), default=1)
            
        # Set initial children relationship map table
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
        # Append new children relationship map table
        append_children_relationship(self.children_relationship, children)
    
        # New architecture fields
        #self.stack = []       declare when used
        self.datum, self.result, self.procs, self.cfg = datum, Result(), self.procs = procs if procs else [ProcIter()], self.cfg = cfg

        # Skip first sequence process
        skip_first_seq = self.cfg.get('skip_first_seq', True)
        if skip_first_seq and isinstance(self.datum[0], (list,tuple,LinkList)):
            self.preds.append(PredSkip())


    # 设置children获取表
    def append_children_relationship(self, children):
        """追加children子迭代器关系。"""
        self.children_relationship = append_children_relationship(self.children_relationship, children)
        return self
   
    def append_proc(self, proc):
        self.procs.append(proc)
        return self
       
    def set_proc(self,proc):
        self.procs = [proc]
        return self
       
    def initial(self, init=None):
        self.result.rst = init
        return self
   
    def assist(self, *datum, children={}):
        """
        Append assist collection 'node' which children is children for iterator.
        """
        self.datum += datum
        self.append_children_relationship(children)
        return self
   
    def filter(self, query='*'):
        """Set query-string"""
        self.preds = gen_preds(query)
        return self
        
    def map(self, proc=None):
        """并行处理"""
        if isinstance(proc, types.FunctionType):
            self.procs = [ProcMap(proc)]
        else:
            self.procs = [proc]
        return self
        
    def reduce(self, reduce_proc, initial=None, post=None):
        """归并"""

        if self.min_node_num > len(self.datum):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.datum)))
        
        self.procs = [ProcReduce(reduce_proc)]
        self.result.rst = initial
        self.stack = [NodeInfo(self.datum, pred_idx=len(self.preds)-1)]

        return self._next_new( )
        
    def run(self): 
        self.stack = [NodeInfo(self.datum, pred_idx=len(self.preds)-1)]
        return self._next_new()
        
    def r(self):
        """返回当前求值结果为内容的query"""
        return Query(list(iter(self)))

    def _get_children_iter(self, *node):
        nxt = self.children_relationship.get(
            type(node[0]),
            self.children_relationship.get('*',DEFAULT_CHILDREN_RELATIONSHIP))  # 查找处理类实例
        return nxt.sub(*node)  # 调用类函数处理
    
    def __iter__(self):
        if self.min_node_num > len(self.datum):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.datum)))
        
        # Initial process stacks
        self.stack = [NodeInfo(self.datum, pred_idx=len(self.preds)-1)]

        return self

    def __next__(self):
        return self._next_new()
        
    def _next_new( self ):
        
        for ite_cnt in range(Query.MAX_IT_NUM):
            # Finish judgement
            if len(self.stack) == 0:
                if self.procs[0].is_yield():
                    raise StopIteration()
                else:
                    return self.result.rst
            
            # Get stack tail information for process
            node = self.stack[-1]
            
            # Process with sta
            if node.sta == PRE:
                
                # Filter
                pred = self.preds[node.pred_idx]
                result = pred.match(*node.datum)
            
                # Record filter result
                node.succ, node.proc_idx = pred.is_succ(result), qpred.proc_idx
                
                # Next prepare
                try:
                    
                    if pred.is_sub(result):
                        # Get all datum iterators and assign to parent
                        node.children = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                        # Get next elements of iterators
                        nxt_datum = [next(i) for i in node.children]

                    # Process
                    if node.succ:
                        self.procs[node.proc_idx].pre(self.result, *node.datum, stack=self.stack)

                    # Push next elements into stack
                    if len(self.stack) > 0: 
                        pred_idx = max(0, node.pred_idx - 1) if pred.is_done(result) else node.pred_idx
                        self.stack.append(NodeInfo(nxt_datum, pred_idx=pred_idx))
                    
                # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
                except (StopIteration,TypeError): 
                    node.children = None
                    # Process
                    if node.succ:
                        self.procs[node.proc_idx].pre(self.result, *node.datum, stack=self.stack)
                
                    
                # Modify top element status of stack
                node.sta = POST
                
                # Stop judgement: implement in Proc via clear stack
                # if pred.is_stop(result): self.stack.clear()
                    

                # Return
                if node.succ and self.procs[node.proc_idx].pre_yield():
                    return self.result.rst
                    
            elif node.sta == POST:
                # Process
                if node.succ:
                    self.procs[node.proc_idx].post(self.result, *node.datum, stack=self.stack)
                    
                try:
                    # Pop stack
                    self.stack.pop()
                    # Parent element forward
                    nxt_datum = [next(i) for i in self.stack[-1].children]
                    self.stack.append(NodeInfo(nxt_datum))
                except (IndexError, StopIteration): # IndexError for empty-stack
                    pass

                if node.succ and self.procs[node.proc_idx].post_yield():
                    return self.result.rst

            else:
                raise Exception('Invalid status of FSM!')
        

            

