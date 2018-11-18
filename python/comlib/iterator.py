import re
from comlib.iterator_operator import deq
from comlib.iterators import *
        
PATT_SELECT = re.compile(r'\s*(\w+|\*)(?:\[([^]]+)\])?(/[a-zA-Z]+)?\s*')
PATT_ATTR = re.compile(r'{(\w+)}')
PATT_PRED = re.compile(r'(\w*)(\[(.*)\])?(/[oOcCsS]+)?')  # 单条件匹配模板

        
class Pred:
        
    def __init__(self, cfg, nflag='', cls_name = '', pred = '', flags = ''):
        
        if cls_name == '*' and pred == None:
            self.match = self.match_none
        elif cls_name == '*':  # pred!=None
            pred = pred if pred else ''
            pred = pred.replace('{idx}', 'idx').replace('{self}', 'node')
            self.pred = PATT_ATTR.sub( cfg.attr + r'(node,"\g<1>")', pred, count=0 )
            self.match = self.match_condition
        elif pred == None:  # cls_name='*'
            self.cls_name = cls_name
            self.match = self.match_obj
        else:
            self.cls_name = cls_name
            self.pred = pred
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
    

def get_subnode_from_index(node, nodes, *args): return node.sub()
def get_subnode_from_array(node, nodes, *args): return node if hasattr(node,'__iter__') else []
def get_subnode_from_list(subn): 
    def tmp( node, nodes, *args ):
        if isinstance(node, (list, tuple)):
            return node
        else:
            try:
                sub = getattr(node, subn)
                return sub if hasattr( sub, '__iter__' ) else []
            except AttributeError:
                return []
    return tmp

def get_subnode_from_filter(nfunc):
    def tmp(node, nodes, *args): 
        if isinstance(node, (list, tuple)):
            return node
        else:
            return nfunc(node, args[0])
    return tmp

def get_subnode_from_func(nfunc):
    def tmp(node, nodes, *args):
        if isinstance(node, (list, tuple)):
            return node
        else:
            sub = nfunc(nodes)
            return sub if hasattr( sub, '__iter__' ) else []
    return tmp

class SubRelation:
    def __init__(self, ntyp=None, nfunc=None, sub = None):
    
        l = len(sub)
        if l==0:
            self.sub = get_subnode_from_array
        elif l==1:
            self.sub = 
            
    
        if sub != None:
            self.sub = sub
        elif nfunc == None: # 数组
            self.sub = get_subnode_from_array
        elif isinstance( nfunc, str ): # 链表
            self.sub = get_subnode_from_list( nfunc )
        # elif isinstance( nfunc, Index ):
        #     self.sub = get_subnode_from_index
        elif hasattr( nfunc, '__call__' ): # 普通函数
            if ntyp == 5:  # 非用户自定义搜索函数
                self.sub = get_subnode_from_filter(nfunc)
            else:
                self.sub = get_subnode_from_func(nfunc)

    def redirect(self, sub): self.sub = sub

    

    


class iterator:
    """
    # Introduce
  按序筛选并打平。
  Filter by designed order and flatten into dimension 1-D.

    Parameter "gnxt" indicates the link method to sub data. There are below style:
    - None(Default): The "node" is iterable data, like array. The sub data can got by iterating the node data
    - {String}: An attribute name of node indicates the sub data
    - {Function}: A function return sub data. The format of function is "(node, idx) => sub" 
    
    Parameter "sSelect" is a string who illustrates one filter condition when iterate.
    The sSelect is define:
    sSelect ::= (<filtes>.*)(/)?(<flags>.*)
    filtes ::= Filter content
    flags ::= Filter options ::= (p)(p)
        - p: How to process list node. Default is pre-sub-node process. If there is only ONE ‘p‘ flag, 
             it is post-sub-node process. When there are TWO 'p' flags, both pre- and post- will be processed.  

# Feature
* Support custom sub-pointer via parameter gnxt
  -- Support 3 types for gnxt
    *** None: Array-like data structure
    *** {String}: Link-list data structure
    *** {(node,idx)=>sub}: Custom function
  -- Support Array-like automatic get sub
    *** ***Note:*** Function gnxt NOT support

* Support JQuery-like search Syntax String via parameter 'sSelect'
  -- SearchString ::= SearchPattern, .../glb_flags
    *** SearchPattern ::= [obj][pred][flags]
  -- Support many flags in searchPattern
    *** The iterate process when object match fail
      ---- Default is continue next iterate
      ---- 'o': Continue next iterate except the sub node of current node
      ---- 'O': Break the iterate
    *** The iterate process when pred match fail
      ---- Default is continue next iterate
      ---- 'c': Continue next iterate except the sub node of current node
      ---- 'C': Break the iterate
    *** The iterate process when match success
      ---- Default is continue next iterate
      ---- 's': Continue next iterate except the sub node of current node
      ---- 'S': Break the iterate
    
* Support matching pred function via parameter 'pred'
  -- The format of pred is: (node,idx,count) => Boolean

* Support match number
  -- Support max match number via parameter 'count'. "0" represent unlimited(default)
  -- Support current match counter in Condition Matching String via identity '{cnt}'
  
  
    """
    def __init__(self, node=None, sSelect='*', **cfg):
        """
        Generate a iterator for data structure 'node' with configure parameters of '**cfg'.

        'node' can be applied via .select function.

        'sSelect' is a string represent one or more filter conditions called filter-string.
        The filter-string is form of a set of filter-patterns seperated by ' ' or '>':
        - ' ': Ancestor-Descendant relationship.
        - '>': Parent-Son relationship.

        filter-pattern ::= objName[filter-condition]/flags

        'objName' is the node class name or '*' represented all class.

        'filter-condition' can be ignore with pair '[' and ']'.
        There are some special attributes in filter-condition:
        - {idx}: The position of current node in whole node tree
        - {self}: Current node

        'flags' decide the selection action and direction. They can be ignore with '/'
        - P: Disable yield current node before sub-nodes enumerate. Default is enable
        - p: Enable yield current node after sub-nodes enumerate. Default is disable

        Parameter 'cfg' supplement extend optonals:
        - gnxt: A function formatted (node,attr,idx)=>iter represent the sub-nodes selection action for each node
        - pred: A function formatted (node,idx)=>bool represent filter condition for each node
        - ntyp: Special gnxt flag
          -- 5: 'gnxt' is a filter function
        - attr: A string represent how to get the attribute of node. Default is 'getattr'
        """

        if isinstance(node, (list,tuple)):
            self._iter = self._iter_single_root
        else:
            self._iter_single

        self.nodes = node

        self.subrs = [SubRelation(cfg.get('ntyp', 0), cfg.get('gnxt', None))]    

        # self.pred = cfg.get('pred', None)  # 条件函数，和sSelect共存同时有效
        # if not hasattr(self.pred, '__call__'):
        #     self.pred = None
        
        self.attr = cfg.get('attr', 'getattr')  # 获取属性的函数
            
        r = PATT_SELECT.split(sSelect)
        r = [deq(iter(r), 4) for i in range(int(len(r)/4))]
        self.preds = [Pred(self, n,o,c,f) for [n,o,c,f] in r]        
    
    def assist(self, node, gnxt=None, ntyp=None):
        if self._iter == self._iter_single:
            self.nodes = [self.nodes, node]
        else:
            self.nodes.append(node)

        if isinstance( node, Index ):
            self.subrs.append( SubRelation( sub = get_subnode_from_index ) )
        else:
            self.subrs.append( SubRelation( ntyp, gnxt ) )

        self._iter = self._iter_multi if self._iter==self._iter_single else self._iter_multi_root
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
        
    def _iter_multi_root( self, preds, node ):
        for ss in zip( *map(lambda n,rs:rs.sub(n,nodes,preds[0].cls_name), nodes, self.subrs)):
                yield from self._iter_single( preds, ss )

    def _iter_multi( self, preds, nodes ):
        pred = preds[0]
           
        # 过滤判断
        succ = pred.match( nodes )
        
        if succ == 1:  # 匹配成功，迭代子对象
            if pred.yield_typ==1: yield nodes
                
            if len(preds)>1: preds = preds[1:]
        
            for ss in zip( *map(lambda n,rs:rs.sub(n,nodes,pred.cls_name), nodes, self.subrs)):
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
        
    def select(self, node): 
        self.node = node
        return self
        
    def __iter__(self):
        return self._iter( self.preds, self.nodes )
        
            

