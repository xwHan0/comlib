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
CRITERIA_SEGMENT_PATT = r'\s*(?:{0}|{1}|{2})(/[a-zA-Z]+)?\s*'.format(CRITETIA_SEGMENT_PATT1, CEITETIA_SEGMENT_PATT2, CTITERIA_SEGMENT_PATT3)

PATT_CONDITION = CRITERIA_SEGMENT_PATT

PATT_SELECT = re.compile(PATT_CONDITION)
        
CRITERIA_PATT = [
    (re.compile(r'#(\d+)'), r'node[\g<1>]'),
    (re.compile(r'##'), r'node'),
    (re.compile(r'#\.'), r'node[0].'),
]
CRITERIA_NODE_PATT = re.compile(r'#(\d+)')
       
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

               
        #if cls_name == '*' and pred == None:
        #    self.match = self.match_none
        #elif cls_name == '*':  # pred!=None
        #    self.pred = pred if pred else ''
        #    for p,s in CRITERIA_PATT:
       #         self.pred = p.sub(s,self.pred)
        #    self.match = self.match_condition
       # elif pred == None:  # cls_name='*'
        #    self.match = self.match_obj
       # else:
        #    self.pred = pred if pred else ''
      #      for p,s in CRITERIA_PATT:
        #        self.pred = p.sub(s, self.pred)
        #    self.match = self.match_full

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

    def match_none(self, node): return self.match_succ_rst            
            
    def match_obj_condition( self, node ):
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

    def match_obj( self, node ):
        if node[0].__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
        return self.match_succ_rst

    def match_condition( self, node ):
        try:
            rst = eval(self.pred)
            if rst == False: return self.pred_fail_rst
            elif rst == True: return self.match_succ_rst
            else: raise Exception('Invalid condion result. CMD<{0}>'.format(self.pred))
        except Exception:
            raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
        return self.match_succ_rst

    def match_full( self, node ):
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
    
def get_subnode_args0(node, nodes, *args):
    """调用node(自身)获取子节点集合"""
    return node if hasattr(node,'__iter__') else []

def get_subnode_args1(gnxt):
    """使用node.gnxt[0]获取子节点集合"""
    nxt = gnxt[0]
    if isinstance(nxt, str):    # [sMethod] 第一个参数为字符串，一定为类成员函数
        def func(node, nodes, *args):
            if isinstance(node, (list, tuple)): return node
            try:
                sub = getattr(node,nxt)()
                return sub if hasattr( sub, '__iter__' ) else []
            except Exception:
                return []
    else:
        def func(node, nodes, *args):
            if isinstance(node, (list, tuple)): return node
            try:
                sub = nxt(node)
                return sub if hasattr( sub, '__iter__' ) else []
            except Exception:
                return []
    return func

def get_subnode_args2_attr(gnxt):
    """调用gnxt[0](node, gnxt[1])获取子节点集合"""
    nxt = gnxt[0]
    if isinstance(nxt, str):  # [sMethod] 第一个参数为字符串，一定为类成员函数
        def func(node, nodes, *args):
            if isinstance(node, (list, tuple)): return node
            try:
                sub = getattr(node,nxt)(gnxt[1])
                return sub if hasattr( sub, '__iter__' ) else []
            except Exception:
                return []
    else:
        def func(node, nodes, *args):
            if isinstance(node, (list, tuple)): return node
            try:
                sub = nxt(node, gnxt[1])
                return sub if hasattr( sub, '__iter__' ) else []
            except Exception:
                return []
    return func

def get_subnode_args2_search(gnxt):
    """调用gnxt[0](node, args[0])搜索子节点集合"""
    nxt = gnxt[0]
    if isinstance(nxt, str):
        def func(node, nodes, *args):
            if isinstance(node, (list, tuple)): return node
            try:
                sub = getattr(node,nxt)(node, args[0])
                return sub if hasattr( sub, '__iter__' ) else []
            except Exception:
                return []
    else:
        def func(node, nodes, *args):
            if isinstance(node, (list, tuple)): return node
            try:
                sub = nxt(node, args[0])
                return sub if hasattr( sub, '__iter__' ) else []
            except Exception:
                return []
    return func


class SubRelation:
    def __init__(self, gnxt=[]):
    
        l = len(gnxt)
        if l==0: self.sub = get_subnode_args0
        elif l==1: self.sub = get_subnode_args1(gnxt)
        elif l==2: self.sub = get_subnode_args2_search(gnxt) if gnxt[1][0] == '$' else get_subnode_args2_attr(gnxt)


    

DEFAULT_PREDS = [Pred()]
DEFAULT_SUB_RELATION = [SubRelation()]
COMMON_ITERATOR_RELATION = SubRelation(['sub'])


class iterator:
    """
    # Introduce
  按序筛选并打平。
  Filter by designed order and flatten into dimension 1-D.

# Sub-node Acquire Method Define
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
    def configure(**cfg):
        for k,v in cfg.items():
            if k=='prefix':
                CRITERIA_PATT = [
                    (re.compile(r'{0}(\d+)'.format(v)), r'node[\g<1>]'),
                    (re.compile(r'{0}{0}'.format(v)), r'node'),
                    (re.compile(r'{0}\.'.format(v)), r'node[0].'),
                ]
                CRITERIA_NODE_PATT = re.compile(r'{0}(\d+)'.format(v))
                
    
    def __init__(self, node=None, sSelect='*', gnxt=[], **cfg):
        """
        Arguments:
        - node {collection}: operated data
        - sSlection {String}: Filter string
        - gnxt {list}: Sub-node acquire method
        - cfg {map}: optional parameters
        """
        
        self.nodes = node   # 保存数据结构
        # self.attr = cfg.get('attr', 'getattr')  # 获取属性读取函数
        # 迭代调用函数选择
        self._iter = self._iter_single_root if isinstance(node, (list,tuple)) else self._iter_single

        # 条件判断
        if sSelect == '*':
            self.preds = DEFAULT_PREDS
        else:
            r = PATT_SELECT.split(sSelect)
            r = [deq(iter(r), 6) for i in range(int(len(r)/6))]
            self.preds = [Pred(self, n,o1,c1,o2,c2,f) for [n,o1,c1,o2,c2,f] in r]     
            
        # 子节点索引
        self.subrs = DEFAULT_SUB_RELATION if gnxt==[] else [SubRelation(gnxt)]

        # Filter string特殊表示前缀符
        
        self.min_node_num = max(map(int, CRITERIA_NODE_PATT.findall(sSelect)), default=1)
            
            
   
    
    def assist(self, node, gnxt=[]):
        """
        Append assist collection for iterator.
        """
        if self._iter == self._iter_single:
            self.nodes = [self.nodes, node]
            self._iter = self._iter_multi
        elif self._iter == self._iter_single_root:
            self.nodes = [self.nodes, node]
            self._iter = self._iter_multi_root
        else:
            self.nodes.append(node)

        if isinstance( node, CommonIterator ):
            self.subrs.append( COMMON_ITERATOR_RELATION )
        else:
            self.subrs.append( SubRelation( gnxt ) )

        return self

    def _iter_single_root( self, preds, node ):
        for ss in self.subrs[0].sub(node, node, preds[0].cls_name):
                yield from self._iter_single( preds, ss )
        
    def _iter_single( self, preds, node ):
        pred = preds[0]
           
        # 过滤判断
        succ = pred.match( (node,) )
       
        if succ == 1:  # 匹配成功，迭代子对象
            if pred.yield_typ==1: yield node
                
            if len(preds)>1: preds = preds[1:]
 
            for ss in self.subrs[0].sub(node, node, pred.cls_name):
                yield from self._iter_single( preds, ss )
            
            if pred.yield_typ==2: yield node
         
        elif succ == -1:  # 匹配不成功，迭代子对象
            for ss in self.subrs[0].sub(node, node, pred.cls_name):
                yield from self._iter_single( preds, ss )
            
        elif succ == 2: # 匹配成功，不迭代子对象
            if pred.yield_typ != 0: yield node

        elif succ == 3: # 匹配成功，终止迭代
            if pred.yield_typ != 0: yield node
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()
        
    def _get_subnode(self, n, rs, nodes, args):
        sub = rs.sub(n,nodes, args)
        return sub if hasattr(sub, '__iter__') else []
        
    def _iter_multi_root( self, preds, node ):
        for ss in zip( *map(lambda n,rs: self._get_subnode(n,rs,node,preds[0].cls_name), node, self.subrs)):
            yield from self._iter_multi( preds, ss )

    def _iter_multi( self, preds, nodes ):
        pred = preds[0]
           
        # 过滤判断
        succ = pred.match( nodes )
        
        if succ == 1:  # 匹配成功，迭代子对象
            if pred.yield_typ==1: yield nodes
                
            if len(preds)>1: preds = preds[1:]
        
            for ss in zip( *map(lambda n,rs: self._get_subnode(n,rs,nodes,pred.cls_name), nodes, self.subrs)): # 当nodes[0]不需要迭代时，退出nodes[1]的处理
                yield from self._iter_multi( preds, ss )
            
            if pred.yield_typ==2: yield nodes
         
        elif succ == -1:  # 匹配不成功，迭代子对象

            for ss in zip( *map(lambda n,rs:rs.sub(n,nodes,pred.cls_name), nodes, self.subrs) ):
                yield from self._iter_multi( preds, ss )
            
        elif succ == 2: # 匹配成功，不迭代子对象
            if pred.yield_typ!=0: yield nodes

        elif succ == 3: # 匹配成功，终止迭代
            if pred.yield_typ!=0: yield nodes
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()    
               
    def __iter__(self):
        if self._iter == self._iter_single or self._iter == self._iter_single_root:
            if self.min_node_num > 1:
                raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, 1))
        elif self.min_node_num > len(self.nodes):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.nodes)))
        
        return self._iter( self.preds, self.nodes )
        
            

