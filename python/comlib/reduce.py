import re
from comlib.iterator_operator import deq
from comlib.iterators import *
        



PATT_CONDITION_BASE1 = r'[^[\]]'
PATT_CONDITION_1 = r'(?:{0})+'.format(PATT_CONDITION_BASE1)
PATT_CONDITION_BASE2 = r'{0}*\[{0}+\]{0}*'.format(PATT_CONDITION_BASE1)
PATT_CONDITION_2 = r'(?:{0})+'.format(PATT_CONDITION_BASE2)
PATT_CONDITION_BASE3 = r'(?:{0}|{1})*\[(?:{1})+\](?:{0}|{1})*'.format(PATT_CONDITION_BASE1, PATT_CONDITION_BASE2)
PATT_CONDITION_3 = r'(?:{0})+'.format(PATT_CONDITION_BASE3)
PATT_CONDITION = r'\s*(\w+|\*)(?:\[({2}|{1}|{0})\])?(/[a-zA-Z]+)?\s*'.format(
    PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3
)

CRITERIA_SEGMENT_PATT1 = r'(\w+|\*)'
CRITERIA_SEGMENT_PATT2 = r'\[({2}|{1}|{0})\]'.format(PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3)
CRITERIA_SEGMENT_PATT3 = r'(\w+|\*)\[({2}|{1}|{0})\]'.format(PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3)
CRITERIA_SEGMENT_PATT = r'\s*(?:{2}|{1}|{0})(/[a-zA-Z]+)?\s*'.format(CRITERIA_SEGMENT_PATT1, CRITERIA_SEGMENT_PATT2, CRITERIA_SEGMENT_PATT3)

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
    def sub(*node):
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
    def __init__(self, nflag='', cls_name2='*', pred2='', pred1='', cls_name1='*', flags=''):
       
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
            self.match = self.match_condition if cls_name2=='*' else self.match_full

               
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


class xreduce:
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
        self.isArray = isinstance(node,(list,tuple,LinkList))
        self.min_node_num = max(map(int, CRITERIA_NODE_PATT.findall(sSelect)), default=1)
            
        self._configure_children_relationship(gnxt)

        # 获取处理函数参数
        self.init = cfg.get('init', None)
        self.reduce = cfg.get('reduce', lambda init, rst: rst)
        self.post = cfg.get('post', lambda node,rst: rst)


    
    # 设置children获取表
    def _configure_children_relationship(self, children):
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
        if isinstance(children,str):
            self.children_relationship['*'] = ChildAttr(children)
        elif isinstance(children, types.FunctionType):
            self.children_relationship['*'] = ChildFunction(children)
        elif isinstance(children,dict):
            for k,v in children.items():
                if isinstance(v, str):  # 字符串：查询属性
                    self.children_relationship[k] = ChildAttr(v)
                else:
                    self.children_relationship[k] = v
   
    def _get_children_iter(self, *node):
        nxt = self.children_relationship.get(
            type(node[0]),
            self.children_relationship.get('*',DEFAULT_CHILDREN_RELATIONSHIP))  # 查找处理类实例
        return nxt.sub(*node)  # 调用类函数处理
    
    def _get_children_iter_multi(self, node):
        return zip( *map(lambda n: self._get_children_iter(n, node), node))

    def _recur( self, preds, node ):
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
                rst_l = self.init(node) # 定义当前节点的reduce初始值
                for ss in nxt:
                    status, rst_n = self._recur( preds, ss )    # 处理子节点

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
                    
                rst_l = self.post( node, rst_l )
                return 3 if status==3 else 1, rst_l
            else:
                return 1, self.post( node, self.init(node) )

        elif succ < 0:  # 匹配不成功，返回匹配结果和None。不应该出现匹配不成功，还要继续迭代
            return succ, None
        
        elif succ > 0: # 匹配成功，但所有可能都不需要继续
            return succ, self.post(node,self.init(node))


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
        
            

