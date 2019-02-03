import re
from comlib.mapreduce.pred import Pred, PredSelect, PredSkip, gen_preds
from comlib.mapreduce.child_relationship import TYPIC_CHILDREN_RELATIONSHIP, DEFAULT_CHILDREN_RELATIONSHIP, append_children_relationship
from comlib.iterators import LinkList
from comlib.mapreduce.stack import NodeInfo,PRE,POST
from comlib.mapreduce.proc import Proc, ProcMap, ProcReduce
        
import types



__all__ = [
    'xiter',
]

class xiter:
    """
    # Introduce
  按序筛选并打平。
  Filter by designed order and flatten into dimension 1-D.

# Sub-node Acquire Method Defineu.
    Parameter "gnxt" formatted with list indicates the link method to sub data. There are below style:
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
 
# Filter String
    Filter string is a string represent one or more filter conditions.
    The filter-string is form of a set of filter-patterns seperated by ' ' or '>':
    - ' ': Ancestor-Descendant relationship.
    - '>': Parent-Son relationship.

    filter-pattern ::= objName[filter-condition]/flags

  ## objName
    'objName' is the node class name or '*' represented all class.

  ## Filter-Condition
    'filter-condition' can be wrapped with pair '[' and ']'.
    
    Support below special expression: ('nodes' represents current access nodes from all node)
    * #.attr: Get the attribute of nodes[0] like: 'nodes[0].attr'
    * #n: Get the n-th node(n=0-N)
    * #n.attr: Get the attribute of nodes[n] like: 'nodes[n].attr' (n=0-N)
    * ##: List of all nodes
    The special expression prefix '#' can be configured via 'prefix' argument of **cfg in constructor. For example,
    cfg['prefix']='$' means using '$n', '$n.attr' and '$$' to replace '#n', '#n.attr' and '##'
        
    * Node: Support 3-level '[]' pair in max in condition statement
     
  ## Flags   
    'flags' decide the selection action and direction. They can be ignore with '/'
    - P: Disable yield current node before sub-nodes enumerate. Default is enable
    - p: Enable yield current node after sub-nodes enumerate. Default is disable
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
    

Issue:
1. 条件中node和nodes的写法
2. 子函数如何判断继承关系

# Feature
* Support custom sub-pointer via parameter gnxt
  -- Support 3 types for gnxt. See 'Sub-node Acquire Method Define' for more detail
  -- Support Array-like automatic get sub
    *** ***Note:*** Function gnxt NOT support

* Support JQuery-like search Syntax String via parameter 'sSelect'
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
                xiter.CRITERIA_PATT = [
                    (re.compile(r'{0}(\d+)'.format(v)), r'node[\g<1>]'),
                    (re.compile(r'{0}{0}'.format(v)), r'node'),
                    (re.compile(r'{0}\.'.format(v)), r'node[0].'),
                ]
                xiter.CRITERIA_NODE_PATT = re.compile(r'{0}(\d+)'.format(v))
            elif k=='max_it_num':
                xiter.MAX_IT_NUM = v
    

    def __init__(self, *node, sSelect='*', gnxt={}, **cfg):
        """
        Arguments:
        - node {collection}: operated data
        - sSlection {String}: Filter string
        - gnxt {list}: Sub-node acquire method
        - cfg {map}: optional parameters
        """
        
        # 保存并解析选择字符串
        self.preds = gen_preds(sSelect)
        self.min_node_num = max(map(int, xiter.CRITERIA_NODE_PATT.findall(sSelect)), default=1)
            
        # Set initial children relationship map table
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
        # Append new children relationship map table
        append_children_relationship(self.children_relationship, gnxt)
    
        # New architecture fields
        #self.stack = []       declare when used
        self.datum = list(node)
        self.iterable = True
        self.result = None
        self.proc = Proc() 
        self.cfg = cfg

        # Skip first sequence process
        skip_first_seq = self.cfg.get('skip_first_seq', True)
        if skip_first_seq and isinstance(self.datum[0], (list,tuple,LinkList)):
            self.preds.append(PredSkip())


    # 设置children获取表
    def append_children_relationship(self, children):
        self.children_relationship = append_children_relationship(self.children_relationship, children)
        return self
   
    def assist(self, *datum, gnxt={}):
        """
        Append assist collection 'node' which gnxt is gnxt for iterator.
        """
        for d in datum:
            self.datum.append(d)
            
        self.append_children_relationship(gnxt)

        return self
   
    def filter(self, sSelect):
        """过滤"""
        self.preds = gen_preds(sSelect)
        return self
        
    def map(self, proc=None):
        """并行处理"""
        if isinstance(proc, types.FunctionType):
            self.proc = ProcMap(proc)
        else:
            self.proc = proc
        return self
        
    def reduce(self, reduce_proc, initial=None, post=None):
        """归并"""

        if self.min_node_num > len(self.datum):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.node)))
        
        self.proc = ProcReduce(reduce_proc)
        self.result = initial
        self.stack = [NodeInfo(self.datum, pred_idx=len(self.preds)-1)]

        return self._next_new( )
        
    def r(self):
        """返回当前求值结果为内容的xiter"""
        return xiter(list(iter(self)))

    def _get_children_iter(self, *node):
        nxt = self.children_relationship.get(
            type(node[0]),
            self.children_relationship.get('*',DEFAULT_CHILDREN_RELATIONSHIP))  # 查找处理类实例
        return nxt.sub(*node)  # 调用类函数处理
    
    def __iter__(self):
        if self.min_node_num > len(self.datum):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.node)))
        
        # Initial process stacks
        self.stack = [NodeInfo(self.datum, pred_idx=len(self.preds)-1)]

        return self

    def __next__(self):
        return self._next_new()
        
    def _next_new( self ):
        
        for ite_cnt in range(xiter.MAX_IT_NUM):
            # Finish judgement
            if len(self.stack) == 0 or ite_cnt >= xiter.MAX_IT_NUM:
                if self.iterable:
                    raise StopIteration()
                else:
                    return self.result
            
            # Get stack tail information for process
            node = self.stack[-1]
            
            # Process with sta
            if node.sta == PRE:
                # Modify top element status of stack
                node.sta = POST
                try:
                    # Filter
                    pred = self.preds[node.pred_idx]
                    result = pred.match(*node.datum)
            
                   # Stop judgement
                    if pred.is_stop(result):
                        self.stack.clear()

                    # Record filter result
                    node.succ = pred.is_succ(result)
                    node.is_post_yield = pred.is_post_yield()

                    if pred.is_sub(result):
                        # Get all datum iterators and assign to parent
                        node.ites = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                        # Get next elements of iterators
                        nxt_datum = [next(i) for i in node.ites]

                    # Push next elements into stack
                    pred_idx = max(0, node.pred_idx - 1) if pred.is_done(result) else node.pred_idx
                    self.stack.append(NodeInfo(nxt_datum, pred_idx=pred_idx))

                # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
                except (StopIteration,TypeError): 
                    pass

                if node.succ:
                    rst = self.proc.pre(*node.datum, node=node)
                    if self.proc.pre_yield():
                        return rst
                    
            elif node.sta == POST:
                try:
                    # Pop stack
                    self.stack.pop()
                    # Parent element forward
                    nxt_datum = [next(i) for i in self.stack[-1].ites]
                    self.stack.append(NodeInfo(nxt_datum))
                except (IndexError, StopIteration): # IndexError for empty-stack
                    pass

                if node.succ:
                    rst = self.proc.post(self.result, *node.datum, node=node)
                    if self.proc.post_yield():
                        return rst
              
            else:
                raise Exception('Invalid status of FSM!')
        

            

