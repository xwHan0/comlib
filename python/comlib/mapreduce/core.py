import re
from comlib.mapreduce.pred import *
from comlib.mapreduce.child_relationship import *
from comlib.mapreduce.map import *
from comlib.iterators import *
        
import types

CRITERIA_NODE_PATT = re.compile(r'#(\d+)')

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
    @staticmethod
    def configure(**cfg):
        for k,v in cfg.items():
            if k=='prefix':
                CRITERIA_PATT = [
                    (re.compile(r'{0}(\d+)'.format(v)), r'node[\g<1>]'),
                    (re.compile(r'{0}{0}'.format(v)), r'node'),
                    (re.compile(r'{0}\.'.format(v)), r'node[0].'),
                ]
                CRITERIA_NODE_PATT = re.compile(r'{0}(\d+)'.format(v))
                
    
    def __init__(self, *node, sSelect='*', gnxt={}, **cfg):
        """
        Arguments:
        - node {collection}: operated data
        - sSlection {String}: Filter string
        - gnxt {list}: Sub-node acquire method
        - cfg {map}: optional parameters
        """
        
        if len(node) == 1:
            self.node = node[0]     # 保存待处理的数据结构
            self.get_children = self._get_children_iter     # 保存子关系
            self.isArray = isinstance(self.node,(list,tuple,LinkList))
        else:
            self.node = node
            self.get_children = self._get_children_iter_multi
            self.isArray = isinstance(self.node[0],(list,tuple,LinkList))
        
        # 保存并解析选择字符串
        self.preds = gen_preds(sSelect)
        self.min_node_num = max(map(int, CRITERIA_NODE_PATT.findall(sSelect)), default=1)
            
        # Set initial children relationship map table
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
        # Append new children relationship map table
        append_children_relationship(self.children_relationship, gnxt)
    
        self.map_proc = None
    
    # 设置children获取表
    def append_children_relationship(self, children):
        self.children_relationship = append_children_relationship(self.children_relationship, children)
        return self
   
    def assist(self, *node, gnxt={}):
        """
        Append assist collection 'node' which gnxt is gnxt for iterator.
        """
        if self.get_children == self._get_children_iter:
            self.node = [self.node] + node
            self.get_children = self._get_children_iter_multi
        else:
            for n in node:
                self.node.append(n)
            
        self.append_children_relationship(gnxt)

        return self
   
    def filter(self, sSelect):
        """过滤"""
        self.preds = gen_preds(sSelect)
        return self
        
    def map(self, proc=None):
        """并行处理"""
        if isinstance(proc, types.FunctionType):
            self.map_proc = MapFunction(proc)
        else:
            self.map_proc = proc
        return self
        
    def reduce(self, reduce_proc):
        """归并"""
        if self.get_children == self._get_children_iter:
            if self.min_node_num > 1:
                raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, 1))
        elif self.min_node_num > len(self.node):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.node)))
        
        if self.isArray:
            for ss in self.get_children(self.node):
                return self._iter_reduce( reduce_proc, self.preds, ss )
        else:
            return self._iter_reduce( reduce_proc, self.preds, self.node )
        
    def r(self):
        """返回当前求值结果为内容的xiter"""
        return xiter(list(iter(self)))

    def _get_children_iter(self, *node):
        nxt = self.children_relationship.get(
            type(node[0]),
            self.children_relationship.get('*',DEFAULT_CHILDREN_RELATIONSHIP))  # 查找处理类实例
        return nxt.sub(*node)  # 调用类函数处理
    
    def _get_children_iter_multi(self, node):
        return zip( *map(lambda n: self._get_children_iter(n, node), node))


    def _iter_common( self, preds, node ):
        pred = preds[0]
           
        # 过滤判断
        succ = pred.match( node ) if self.get_children==self._get_children_iter else pred.match(*node)
       
        if succ == 1:  # 匹配成功，迭代子对象
            if pred.yield_typ==1: 
                if self.map_proc==None:
                    yield node
                else:
                    yield self.map_proc.map(*node)
            
            nxt = self.get_children(node)
            if hasattr(nxt, '__iter__') and nxt!=[]:
                if len(preds)>1: preds = preds[1:]

                if pred.yield_typ == 1:     # 遍历行为
                    for ss in nxt:
                        yield from self._iter_common( preds, ss )
                else:   # 迭代行为
                    pass

            
        elif succ == -1:  # 匹配不成功，迭代子对象
            nxt = self.get_children(node)
            if hasattr(nxt, '__iter__') and nxt!=[]:
                for ss in nxt:
                    yield from self._iter_common( preds, ss )
                
        elif succ == 2: # 匹配成功，不迭代子对象
            if pred.yield_typ != 0:
                if self.map_proc==None:
                    yield node
                else:
                    yield self.map_proc.map(*node)

        elif succ == 3: # 匹配成功，终止迭代
            if pred.yield_typ != 0:
                if self.map_proc==None:
                    yield node
                else:
                    yield self.map_proc.run(*node)
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()

        # elif succ == -2: # 匹配不成功，不迭代子对象
        #     pass

               
    def __iter__(self):
        if self.get_children == self._get_children_iter:
            if self.min_node_num > 1:
                raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, 1))
        elif self.min_node_num > len(self.node):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.node)))
        
        if self.isArray:
            for ss in self.get_children(self.node):
                yield from self._iter_common( self.preds, ss )
        else:
            yield from self._iter_common( self.preds, self.node )
        
    def _iter_reduce( self, proc, preds, node ):
        """
        使用preds判断node处理动作。
        若需要处理，则使用self.reduce迭代处理node的子节点，最后self.reduce的结果使用self.post
        和node节点一并处理后返回。
        若不需要处理，则根据条件跳过该节点以及子节点，或者直接终止迭代。
        """
        
        pred = preds[0] # 获取头判断条件
           
        # 过滤判断。TBD：考虑到yield必须有后处理，所以是否有必要
        succ = pred.match( node ) if self.get_children==self._get_children_iter else pred.match(*node)
       
        if succ == 1:  # 匹配成功，迭代子对象
            nxt = self.get_children(node)
            if hasattr(nxt, '__iter__') and nxt!=[]:
                if len(preds)>1: preds = preds[1:]
                rst_l = proc.init(node) # 定义当前节点的reduce初始值
                for ss in nxt:
                    status, rst_n = self._iter_reduce( proc, preds, ss )    # 处理子节点

                    # 返回状态判断
                    # status > 0 : 匹配成功； status < 0: 匹配不成功
                    # |status|==
                    #   1: 继续处理；2：不迭代子对象(返回值不应该出现)；3：终止迭代；4：不迭代兄弟对象；
                    if status == 1: 
                        rst_l = self.reduce(rst_l, rst_n)
                    elif status == -1:
                        continue
                    elif status in [3,4]:
                        rst_l = self.reduce(rst_l, rst_n)
                        break
                    elif status in [-3,-4]:
                        break
                    
                rst_l = proc.reduce( node, rst_l )
                return 3 if status==3 else 1, rst_l
            else:
                return 1, proc.reduce( node )

        elif succ < 0:  # 匹配不成功，返回匹配结果和None。不应该出现匹配不成功，还要继续迭代
            return succ, None
        
        elif succ > 0: # 匹配成功，但所有可能都不需要继续
            return succ, proc.post(node)

        
    
            

