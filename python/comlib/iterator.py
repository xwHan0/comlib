import re
from comlib.iterator_operator import deq
        
PATT_SELECT = re.compile(r'\s*(\w+|\*)(?:\[([^]]+)\])?(/[a-zA-Z]+)?\s*')
PATT_ATTR = re.compile(r'{(\w+)}')
PATT_PRED = re.compile(r'(\w*)(\[(.*)\])?(/[oOcCsS]+)?')  # 单条件匹配模板

        
class Pred:
        
    def __init__(self, cfg, nflag='', cls_name = '', pred = '', flags = ''):
        
        flags = flags if flags else ''
        
        self.cls_name = cls_name
        self.pred = pred
            
        self.match_func(cfg)
        
        # 无论匹配成功与否，默认总是继续其余匹配
        self.obj_fail_rst, self.pred_fail_rst, self.match_succ_rst = (-1,-1,1)
        self.pre_yield, self.post_yield = (True, False)

        for f in flags: # 
            if f == 'o': self.obj_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
            elif f == 'O': self.obj_fail_rst = -3 # 匹配失败后，终止其余匹配
            elif f == 'c': self.pred_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
            elif f == 'C': self.pred_fail_rst = -3 # 匹配失败后，终止其余匹配
            elif f == 's': self.match_succ_rst = 2  # 匹配成功后，跳过当前节点的子节点
            elif f == 'S': self.match_succ_rst = 3  # 匹配成功后，终止其余匹配
            elif f == 'p': self.pre_yield = False  # 匹配成功后在调用子节点前返回当前节点
            elif f == 'P': self.post_yield = True # 匹配成功后调用子节点后返回当前节点

        for f in nflag:
            if f == '': 
                self.obj_fail_rst = -1
                self.pred_fail_rst = -1
            elif f.rstrip() == '>':
                self.obj_fail_rst = -2
                self.pred_fail_rst = -2

    def match_none(self, nodes): return self.match_succ_rst            
            
    def match_obj_condition( self, nodes ):
        # 对象匹配
        if nodes[0].__class__.__name__ != self.cls_name:
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

    def match_obj( self, nodes ):
        # 对象匹配
        if nodes[0].__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
                                 
        return self.match_succ_rst

    def match_condition( self, nodes ):
            
        # 条件匹配
        try:
            rst = eval(self.pred)
            if rst == False: return self.pred_fail_rst
            elif rst == True: return self.match_succ_rst
            else: raise Exception('Invalid condion result. CMD<{0}>'.format(self.pred))
        except Exception:
            raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
                      
        return self.match_succ_rst

    def match_full( self, nodes ):
        # 对象匹配
        if self.cls_name!='*' and nodes[0].__class__.__name__ != self.cls_name:
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


    
    def match_func( self, cfg ):
        #if cfg.ntyp == 5:
        #    self.match = self.match_condition
        if self.cls_name == '*' and self.pred == None:
            self.match = self.match_none
        elif self.cls_name == '*':  # pred!=None
            self.pred = self.pred if self.pred else ''
            self.pred = self.pred.replace('{idx}', 'idx').replace('{self}', 'node')
            self.pred = PATT_ATTR.sub( cfg.attr + '(node,"\g<1>")', self.pred, count=0 )
            self.match = self.match_condition
        elif self.pred == None:  # cls_name='*'
            self.match = self.match_obj
        else:
            self.match = self.match_full    

class SubRelation:
    def __init__(self, ntyp, nfunc):
        if ntyp == 5:  # 非用户自定义搜索函数
            self.sub = self.get_subnode_from_filter(nfunc)
        else:
            if nfunc == None: # 数组
                self.sub = self.get_subnode_from_array()
            elif isinstance( nfunc, str ): # 链表
                self.sub = self.get_subnode_from_list( nfunc )
            elif hasattr( nfunc, '__call__' ): # 普通函数
                self.sub = self.get_subnode_from_func(nfunc)
        self.nfun = nfunc
        self.ntyp = ntyp  

    def get_subnode_from_array(self):
        def tmp(node, nodes, *args): 
            if hasattr(node,'__iter__'):
                return node
            else:
                return []
        return tmp

    def get_subnode_from_list(self, subn): 
        def tmp( node, nodes, *args ):
            if isinstance(node, list) or isinstance(node, tuple):
                return node
            else:
                try:
                    sub = getattr(node, subn)
                    if hasattr( sub, '__iter__' ):
                        return sub
                    else:
                        return []
                except AttributeError:
                    return []
        return tmp

    def get_subnode_from_filter(self, nfunc):
        def tmp(node, nodes, *args): 
            if isinstance(node, list) or isinstance(node, tuple):
                return node
            else:
                return nfunc(node, args[0])
        return tmp

    def get_subnode_from_func(self, nfunc):
        def tmp(node, nodes, *args):
            if isinstance(node, list) or isinstance(node, tuple):
                return node
            else:
                sub = nfunc(nodes)
                if hasattr( sub, '__iter__' ):
                    return sub
                else:
                    raise Exception('sub[{0}] of {1} is not a iterator.'.format(attr, node))
        return tmp
        
class iterator:
    def __init__(self, node=None, sSelect='*', **cfg):
        self.nodes = [node]
        self.sSelect = sSelect
        
        # 构造全局配置变量
        self.configure(flags='', **cfg)

        ntyp = cfg.get('ntyp', 0)
        gnxt = cfg.get('gnxt', None)
        self.subrs = [SubRelation(ntyp, gnxt)]    
            
        self.yield_node = self.yield_single
        self.get_sub = self.sub_single
        self.step = 0

    def configure(self, flags='', **cfg):  
        self.pred = cfg.get('pred', None)  # 条件函数，和sSelect共存同时有效
        if not hasattr(self.pred, '__call__'):
            self.pred = None
        
        self.attr = cfg.get('attr', 'getattr')  # 获取属性的函数
            
        for f in flags: pass

    def compile(self, sSelect = '*'):
        r = PATT_SELECT.split(sSelect)
        it = iter(r)
        r = [deq(it, 4) for i in range(int(len(r)/4))]
        self.preds = [Pred(self, n,o,c,f) for [n,o,c,f] in r]        
        self.step = 1
        return self
    
    def assist(self, node, gnxt=None, ntyp=None):
        self.nodes.append(node)
        self.subrs.append(SubRelation(ntyp,gnxt))
        self.yield_node = yield_multi
        self.get_sub = sub_multi
        return self
        
    def yield_single(self, node): return node[0]
    def yield_multi(self, node): return node
    
    def sub_single(self, node, *args): return self.subrs[0].sub(node[0],node,args[0])
    def sub_multi(self, node, *args): return zip( *map(lambda n,rs:rs.sub(n,node,args[0]), node, self.subrs)):
                
        
    def _iter( self, preds, node ):
        pred = preds[0]
           
        # 过滤判断
        succ = pred.match( node )
        if succ > 0 and len(preds)>1: preds = preds[1:]
        
        if succ == 1:  # 匹配成功，迭代子对象
            if pred.pre_yield: self.yield_node(node)
                
            for ss in self.get_sub(nodes[0],nodes,pred.cls_name):
                yield from self._iter( preds, ss )
            
            if pred.post_yield: self.yield_node( node )
         
        elif succ == -1:  # 匹配不成功，迭代子对象
            for ss in self.get_sub(nodes[0],nodes,pred.cls_name):
                yield from self.iter_single( preds, ss )
            
        elif succ == 2: # 匹配成功，不迭代子对象
            if pred.pre_yield: yield nodes[0]
            if pred.post_yield: yield nodes[0]

        elif succ == 3: # 匹配成功，终止迭代
            if pred.pre_yield: self.yield_node( node )
            if pred.post_yield: self.yield_node( node )
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()
        
        
    def select(self, node): 
        self.node = node
        return self
        
    def __iter__(self):
        if self.step == 0:
            self.compile(self.sSelect)
        return self.__iter( self.nodes, self.preds )
        
            
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


