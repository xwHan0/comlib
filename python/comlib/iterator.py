import re
from comlib.iterator_operator import deq
from comlib.iterators import *
        

PATT_CONDITION_BASE1 = r'[^[\]]'
PATT_CONDITION_1 = r'(?:{0})+'.format(PATT_CONDITION_BASE1)
PATT_CONDITION_BASE2 = r'{0}*\[{0}+\]{0}*'.format(PATT_CONDITION_BASE1)
PATT_CONDITION_2 = r'(?:{0})+'.format(PATT_CONDITION_BASE2)
PATT_CONDITION_BASE3 = r'(?:{0}|{1})*\[(?:{1})+\](?:{0}|{1})*'.format(PATT_CONDITION_BASE1, PATT_CONDITION_BASE2)
PATT_CONDITION_3 = r'(?:{0})+'.format(PATT_CONDITION_BASE3)
PATT_CONDITION = r'\s*(\w+|\*)(?:\[({0}|{1}|{2})\])?(/[a-zA-Z]+)?\s*'.format(
    PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3
)

CRITERIA_SEGMENT_PATT1 = r'(\w+|\*)'
CRITERIA_SEGMENT_PATT2 = r'\[({0}|{1}|{2})\]'.format(PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3)
CRITERIA_SEGMENT_PATT3 = r'(\w+|\*)\[({0}|{1}|{2})\]'.format(PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3)
CRITERIA_SEGMENT_PATT = r'\s*(?:{0}|{1}|{2})(/[a-zA-Z]+)?\s*'.format(CRITERIA_SEGMENT_PATT1, CRITERIA_SEGMENT_PATT2, CRITERIA_SEGMENT_PATT3)

PATT_CONDITION = CRITERIA_SEGMENT_PATT

PATT_SELECT = re.compile(PATT_CONDITION)
        
CRITERIA_PATT = [
    (re.compile(r'#(\d+)'), r'node[\g<1>]'),
    (re.compile(r'##'), r'node'),
    (re.compile(r'#\.'), r'node.'),
]
CRITERIA_NODE_PATT = re.compile(r'#(\d+)')
       

######################################################
# 定义常用的子节点关系类

#### 定义直接透传关系
class ChildBypass:
    def sub(self,*node):
        return node[0]


class ChildFunction:
    def __init__(self,func):
        self.func = func
        
    def sub(self,*node):
        return self.func(*node)


class ChildNone:
    def sub(self,*node):
        return []

        
class ChildAttr:
    def __init__(self, attr):
        self.attr = attr
    
    def sub(self,*node):
        return getattr(node[0], self.attr)
        

class ChildSub:
    def sub(self,*node):
        return node[0].sub(*node)


# 定义常见的数据类型children_relationship映射表
TYPIC_CHILDREN_RELATIONSHIP = {
    list : ChildBypass(),       # 列表的子元素集合就是列表本身
    tuple: ChildBypass(),
    Index: ChildSub(),   # iterator库包含的子项
    IndexSub: ChildSub(),
    Counter: ChildSub(),
}
DEFAULT_CHILDREN_RELATIONSHIP = ChildNone()

######################################################
# 定义匹配条件类

class Pred:        
    def __init__(self, nflag='', cls_name1='*', pred1='', cls_name2='*', pred2='', flags=''):
       
        if cls_name1:
            if cls_name1=='*':
                self.match = self.match_none
            else:
                self.cls_name = cls_name1
                self.match = self.match_obj
        elif pred1:
            self.pred = pred1
            for p,s in CRITERIA_PATT:
                self.pred = p.sub(s,self.pred)
            self.match = self.match_condition
        else:
            self.cls_name = cls_name2
            self.pred = pred2
            for p,s in CRITERIA_PATT:
                self.pred = p.sub(s, self.pred)
            self.match = self.match_full

               
        # 无论匹配成功与否，默认总是继续其余匹配
        self.obj_fail_rst, self.pred_fail_rst, self.match_succ_rst = (-1,-1,1)
        self.yield_typ = 1  # 默认子项前

        for f in (flags if flags else ''): # 
            if f == 'o': self.obj_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
            elif f == 'O': self.obj_fail_rst = -3 # 匹配失败后，终止其余匹配
            elif f == 'c': self.pred_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
            elif f == 'C': self.pred_fail_rst = -3 # 匹配失败后，终止其余匹配
            elif f == 's': self.match_succ_rst = 2  # 匹配成功后，跳过当前节点的子节点
            elif f == 'S': self.match_succ_rst = 3  # 匹配成功后，终止其余匹配
            elif f == 'P': self.yield_typ = 0  # 匹配成功后不返回当前节点
            elif f == 'p': self.yield_typ = 2 # 匹配成功后调用子节点后返回当前节点

        for f in nflag:
            if f == '': 
                self.obj_fail_rst = -1
                self.pred_fail_rst = -1
            elif f.rstrip() == '>':
                self.obj_fail_rst = -2
                self.pred_fail_rst = -2

    def match_none(self, *node): return self.match_succ_rst            
            
    def match_obj_condition( self, *node ):
        # 对象匹配
        if node[0].__class__.__name__ != self.cls_name:
                return self.obj_fail_rst
            
        # 条件匹配
        try:
            rst = eval(self.pred)
            if rst == False: return self.pred_fail_rst
            elif rst == True: return self.match_succ_rst
            else: raise Exception('Invalid condion result. CMD<{0}>'.format(self.pred))
        except Exception:
            raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
                    
        return self.match_succ_rst

    def match_obj( self, *node ):
        if node[0].__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
        return self.match_succ_rst

    def match_condition( self, *node ):
        try:
            rst = eval(self.pred)
            if rst == False: return self.pred_fail_rst
            elif rst == True: return self.match_succ_rst
            else: raise Exception('Invalid condion result. CMD<{0}>'.format(self.pred))
        except Exception:
            raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
        return self.match_succ_rst

    def match_full( self, *node ):
        # 对象匹配
        if self.cls_name!='*' and node[0].__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
            
        # 条件匹配
        if self.pred and self.pred!='':
            try:
                rst = eval(self.pred)
                if rst == False: return self.pred_fail_rst
                elif rst == True: return self.match_succ_rst
                else: raise Exception('Invalid condion result. CMD<{0}>'.format(self.pred))
            except Exception:
                raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
                      
        return self.match_succ_rst
    


DEFAULT_PREDS = [Pred()]

######################################################
# 定义常用的返回处理函数

import types

class iterator:
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
    * #n: Get the n-th node
    * #n.attr: Get the attribute of nodes[n] like: 'nodes[n].attr'
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
                
    
    def __init__(self, node=None, sSelect='*', gnxt={}, children={}, **cfg):
        """
        Arguments:
        - node {collection}: operated data
        - sSlection {String}: Filter string
        - gnxt {list}: Sub-node acquire method
        - cfg {map}: optional parameters
        """
        self.node = node   # 保存数据结构
        
        # 条件判断
        if sSelect == '*':
            self.preds = DEFAULT_PREDS
        else:
            r = PATT_SELECT.split(sSelect)
            r = [deq(iter(r), 6) for i in range(int(len(r)/6))]
            self.preds = [Pred(n,o1,c1,o2,c2,f) for [n,o1,c1,o2,c2,f] in r]     
            
        self.get_children = self._get_children_iter

        # 判断主数据是否为典型线性集合对象。对于典型线性集合对象，iterator会跳过对顶层节点的yield
        self.isArray = isinstance(node, (list, tuple, LinkList))
        
        self.min_node_num = max(map(int, CRITERIA_NODE_PATT.findall(sSelect)), default=1)
            
        self._configure_children_relationship(gnxt)
    
    # 设置children获取表
    def _configure_children_relationship(self, children):
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
        if isinstance(children,str):
            self.children_relationship['*'] = ChildAttr(children)
        elif isinstance(children,types.FunctionType):
            self.children_relationship['*'] = ChildFunction(children)
        elif isinstance(children,dict)
            for k,v in children.items():
                if isinstance(v, str):  # 字符串：查询属性
                    self.children_relationship[k] = ChildAttr(v)
                else:
                    self.children_relationship[k] = v
   
    def _get_children_iter(self,*node):
        # 按照node节点的数据类型获取子节点指针索引类实例
        nxt = self.children_relationship.get(
            type(node[0]), # 无论是否有多个，都引用第一个
            self.children_relationship.get('*', DEFAULT_CHILDREN_RELATIONSHIP)) # ‘*’为用户定义默认节点处理
        # 调用索引类函数处理。注意：索引类函数的参数为“一系列”node对象。其中第一个为当前node，其余为整个nodes
        # 若len(node)==1，*node也可以引用第一个
        return nxt.sub(*node)

    def _get_children_iter_multi(self, node):
        return zip( *map(lambda n: self._get_children_iter(n, node), node))

    def _iter_common( self, preds, node ):
        pred = preds[0]
           
        # 过滤判断
        succ = pred.match( node )
       
        if succ == 1:  # 匹配成功，迭代子对象
            if pred.yield_typ==1: yield node
 
            nxt = self.get_children(node)
            if hasattr(nxt, '__iter__') and nxt!=[]:
                if len(preds)>1: preds = preds[1:]
                for ss in nxt:
                    yield from self._iter_common( preds, ss )
            
        elif succ == -1:  # 匹配不成功，迭代子对象
            nxt = self.get_children(node)
            if hasattr(nxt, '__iter__') and nxt!=[]:
                for ss in nxt:
                    yield from self._iter_common( preds, ss )
                
        elif succ == 2: # 匹配成功，不迭代子对象
            if pred.yield_typ != 0: yield node

        elif succ == 3: # 匹配成功，终止迭代
            if pred.yield_typ != 0: yield node
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()


    def assist(self, node, gnxt=[]):
        """
        Append assist collection for iterator.
        """
        if self.get_children == self._get_children_iter:
            self.node = [self.node, node]
            self.get_children = self._get_children_iter_multi
        else:
            self.node.append(node)

        return self
    
    def __iter__(self):
        if self.min_node_num > len(self.node):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.nodes)))
        
        if self.isArray:
            for ss in self.get_children(self.node):
                yield from self._iter_common( self.preds, ss )
        else:
            yield from self._iter_common( self.preds, self.node )
        
            

