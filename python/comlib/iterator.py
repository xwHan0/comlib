import re
from iterator_operator import deq
        
PATT_SELECT = re.compile(r'\s*(\w+|\*)(?:\[([^]]+)\])?(/[a-zA-Z]+)?\s*')
PATT_ATTR = re.compile(r'{(\w+)}')
PATT_PRED = re.compile(r'(\w*)(\[(.*)\])?(/[oOcCsS]+)?')  # 单条件匹配模板

        
class Pred:
        
    def __init__(self, cfg, nflag='', cls_name = '', pred = '', flags = ''):
        self.cls_name = cls_name
        self.pred = pred.replace('{idx}', 'idx').replace('{self}', 'node')
        self.pred = PATT_ATTR.sub( cfg.attr + '(node,"\g<1>")', self.pred, count=0 )
            
        match_func(cfg)
        
        # 无论匹配成功与否，默认总是继续其余匹配
        self.obj_fail_rst, self.pred_fail_rst, self.match_succ_rst = (-1,-1,1)
        self.pre_yield, self.post_yield = (False, False)

        for f in flags: # 
            if f == 'o': self.obj_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
            elif f == 'O': self.obj_fail_rst = -3 # 匹配失败后，终止其余匹配
            elif f == 'c': self.pred_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
            elif f == 'C': self.pred_fail_rst = -3 # 匹配失败后，终止其余匹配
            elif f == 's': self.match_succ_rst = 2  # 匹配成功后，跳过当前节点的子节点
            elif f == 'S': self.match_succ_rst = 3  # 匹配成功后，终止其余匹配
            elif f == 'p': self.pre_yield  # 匹配成功后在调用子节点前返回当前节点
            elif f == 'P': self.post_yield # 匹配成功后调用子节点后返回当前节点

        for f in nflag:
            if f == '': 
                self.obj_fail_rst = -1
                self.pred_fail_rst = -1
            elif f.rstrip() == '>':
                self.obj_fail_rst = -2
                self.pred_fail_rst = -2
            
    def match_obj_condition( self, node, idx ):
        # 对象匹配
        if node.__class__.__name__ != self.cls_name:
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

            
    def match_obj( self, node, idx ):
        # 对象匹配
        if node.__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
                                 
        return self.match_succ_rst

    def match_condition( self, node, idx ):
        # 对象匹配
        if node.__class__.__name__ != self.cls_name:
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

    
    def match_func( self, cfg ):
        if cfg.ntyp == 5:
            self.match = match_condition
        elif self.cls_name == '*':
            self.match = match_condition
        elif self.pred == '':
            self.match = match_obj
    


def get_subnode_from_array(node, attr, nfun): return node

def get_subnode_from_filter(node, attr, nfun): 
    if isinstance(node, list) or isinstance(node, tuple):
        return node
    else:
        return nfun(node, attr)
       
def get_subnode_from_list(node, attr, nfun): 
    if isinstance(node, list) or isinstance(node, tuple):
        return node
    else:
        try:
            sub = getattr(node, attr)
            if hasattr( sub, '__iter__' ):
                return sub
            else:
                return []
        except AttributeError:
            return []

def get_subnode_from_func(node, attr, nfun):
    if isinstance(node, list) or isinstance(node, tuple):
        return node
    else:
        sub = nfun(node)
        if hasattr( sub, '__iter__' ):
            return sub
        else:
            raise Exception('sub[{0}] of {1} is not a iterator.'.format(attr, node))
    
        
class iterator:
    def __init__(self, node=None, sSelect='*', **cfg):
        self.node = node
        self.sSelect = sSelect
        
        # 构造全局配置变量
        self.configure(flags='', **cfg)
        
        self.step = 0

    def configure(self, flags='', **cfg):  
        self.pred = cfg.get('pred', None)  # 条件函数，和sSelect共存同时有效
        if not hasattr(self.pred, '__call__'):
            self.pred = None
        
        self.attr = cfg.get('attr', 'getattr')  # 获取属性的函数
            
        # 下一跳方式分类
        ntyp = cfg.get('ntyp', None)
        gnxt = cfg.get('gnxt', 0)
        if ntyp == 5:  # 非用户自定义搜索函数
            self.sub = get_subnode_from_filter
        else:
            if gnxt == None: # 数组
                self.sub = get_subnode_from_array
            elif isinstance( gnxt, str ): # 链表
                self.sub = get_subnode_from_list
            elif hasattr( gnxt, '__call__' ): # 普通函数
                self.sub = get_subnode_from_func

        for f in flags: pass

    def compile(self, sSelect = '*'):
        r = PATT_SELECT.split(sSelect)
        it = iter(r)
        r = [deq(it, 4) for i in range(int(len(r)/4))]
        self.preds = [Pred(self, n,o,c,f) for [n,o,c,f] in r]        
        self.step = 1
        return self
        
    def __iter( node, idx, preds ):
        
        # 过滤判断
        l = len(preds)
        if l == 0: succ = 1
        else:
            succ = preds[0].match( node, idx )
            if l > 1 and succ > 0: preds = preds[1:]
        
        if succ == 1:  # 匹配成功，迭代子对象
            if pred[0].pre_yield == 0: 
                yield (idx, node)
                
            for i,s in enumerate( self.sub(node, attr, self.nfun) ):
                yield from self.__iter( s, idx + [i], preds )
            
            if pred[0].post_yield == 1: 
                yield (idx, node)
         
        if succ == -1:  # 匹配不成功，迭代子对象
            for i,s in enumerate( self.sub(node, attr, self.nfun) ):
                yield from self.__iter( s, idx + [i], preds )
            
        elif succ == 2: # 匹配成功，不迭代子对象
            if pred[0].pre_yield == 0: 
                yield (idx,node)
            if pred[0].post_yield == 1: 
                yield (idx, node)

        elif succ == 3: # 匹配成功，终止迭代
            if pred[0].pre_yield == 0: 
                yield (idx,node)
            if pred[0].post_yield == 1:
                yield (idx, node)
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()

    def select(self, node): 
        self.node = node
        return self
        
    def __iter__(self):
        if self.step == 0:
            self.compile(self.sSelect)
        return self.__iter( self.node, [], self.preds )
        
    def count(self, count):
        for v in self:
            if count <= 0:
                raise StopIteration()
            else:
                count -= 1
                yield v
                
                
def iterator_old( node, sSelect='', count=-1, **kwargs ):
    """ Get an iterator from data node.

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
    
    
   pass


