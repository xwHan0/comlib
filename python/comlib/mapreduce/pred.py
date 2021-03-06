import re
from comlib.iterator_operator import deq
import types


########################################## Global variable definition


#########################################  Local variable definition

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

# Action pattern
ACTION_PATT = r'(?:@([0-9]+))?'

CRITERIA_SEGMENT_PATT = r'\s*(?:{2}|{1}|{0}){3}(/[a-zA-Z]+)?\s*'.format(
    CRITERIA_SEGMENT_PATT1, 
    CRITERIA_SEGMENT_PATT2, 
    CRITERIA_SEGMENT_PATT3,
    ACTION_PATT)

PATT_CONDITION = CRITERIA_SEGMENT_PATT

PATT_SELECT = re.compile(PATT_CONDITION)
        
     
CRITERIA_PATT = [
    (re.compile(r'#(\d+)'), r'datum[\g<1>]'),
    (re.compile(r'##'), r'datum'),
    (re.compile(r'#\.'), r'datum[0].'),
]


######################################################
# 定义匹配条件类

class Pred:
    """条件处理类。
    
    查询字符串(Query-String)
    查询字符串是由用户指定的、告知query如何进行查询的字符串。查询字符串定义了查询过滤的动作，查询成功的执行动作和查询后的迭代动作。
    每个查询字符串由查询类型，过滤条件，动作序号和跳转标识四个部分组成。其格式为：

    '''
    {关系条件 objName[过滤条件]@动作序号/跳转标识 ...}/global_flags
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
    


    """

    def __init__(self, proc_idx=0):
        self.proc_idx = 0
        self.proc = None
        
    # Always success match function
    def match(self, *datum): 
        """Return match result: True or False"""
        return 1

    # Return weather or not stop all other nodes iteration
    def is_stop(self, result): return (result==3) or (result==-3)
    # Return weather or not stop sub nodes iteration
    def is_sub(self, result):  return not ((result==-2) or (result==2))
    # Return weather or not match success
    def is_succ(self, result):  return result > 0
    # 返回当前Pred是否已经匹配完成
    def is_done(self, result): return result > 0
    # 返回是否子迭代前处理
    # def is_pre_yield(self): return True
    # 返回是否子迭代后处理
    # def is_post_yield(self): return False
    # 设置自定义过滤函数
    def set_match(self,pred): 
        self.match = pred
        return self
    # Return weather or not stop sub nodes iteration
    # def is_sub(self, result):  return not ((result==-2) or (result==2))
    # # 设置自定义过滤函数
    # def set_match(self,pred): 
    #     self.match = pred
    #     return self
        

# class PredSkip(Pred):
#     def is_succ(self,result): return False
#     def is_done(self,result): return True

class PredFunction(Pred):
    def __init__(self, func, iproc=0):
        self.match = func
        self.proc_idx = iproc


class PredQMar(Pred):
    def __init__(self, qmar):
        self.qmar = qmar

    def match(self, *datum):
        if isinstance(datum[0], self.qmar):
            return datum[0].match(*datum)
        else:
            return -1


class PredString(Pred):        

    def __init__(self, nflag='', cls_name2='*', pred2='', pred1='', cls_name1='*', proc_idx=None, flags=''):
       
        # super().__init__() Because super Just initial proc_idx
       
        if cls_name1:
            if cls_name1=='*':
                self.match = self.match_none
            else:
                self.cls_name, self.match = cls_name1, self.match_obj
        elif pred1:
            self.pred = pred1
            for p,s in CRITERIA_PATT:
                self.pred = p.sub(s,self.pred)
            self.match = self.match_condition
        else:
            self.cls_name, self.pred = cls_name2,  pred2
            for p,s in CRITERIA_PATT:
                self.pred = p.sub(s, self.pred)
            self.match = self.match_condition if cls_name2=='*' else self.match_full

               
        # 无论匹配成功与否，默认总是继续其余匹配
        self.obj_fail_rst, self.pred_fail_rst, self.match_succ_rst,  self.proc_idx = -1,-1,1,  int(proc_idx) if proc_idx else 0

        for f in (flags if flags else ''): # 
            if f == 'o': self.obj_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
            elif f == 'O': self.obj_fail_rst = -3 # 匹配失败后，终止其余匹配
            elif f == 'c': self.pred_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
            elif f == 'C': self.pred_fail_rst = -3 # 匹配失败后，终止其余匹配
            elif f == 's': self.match_succ_rst = 2  # 匹配成功后，跳过当前节点的子节点
            elif f == 'S': self.match_succ_rst = 3  # 匹配成功后，终止其余匹配

        for f in nflag:
            if f == '': 
                self.obj_fail_rst, self.pred_fail_rst = -1, -1
            elif f.rstrip() == '>':
                self.obj_fail_rst, self.pred_fail_rst = -2, -2
        
    def match_obj_condition( self, *datum ):
        # 对象匹配
        if datum[0].__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
            
        # 条件匹配
        try:
            rst = eval(self.pred)
            if rst == False: 
                return self.pred_fail_rst
            elif rst == True: 
                return self.match_succ_rst
            else: raise Exception('Cannot cast the result<{1}> of CMD<{0}> to Boolean'.format(self.pred, rst))
        except Exception:
            raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
                    
        return self.match_succ_rst

    def match_obj( self, *datum ):
        if datum[0].__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
        return self.match_succ_rst

    def match_condition( self, *datum ):
        try:
            rst = eval(self.pred)
            if rst == False: 
                return self.pred_fail_rst
            elif rst == True: 
                return self.match_succ_rst
            else: raise Exception('Cannot cast the result<{1}> of CMD<{0}> to Boolean'.format(self.pred, rst))
        except Exception:
            raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
        return self.match_succ_rst

    def match_full( self, *datum ):
        # 对象匹配
        if self.cls_name!='*' and datum[0].__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
            
        # 条件匹配
        if self.pred and self.pred!='':
            try:
                rst = eval(self.pred)
                if rst == False: 
                    return self.pred_fail_rst
                elif rst == True: 
                    return self.match_succ_rst
                else: raise Exception('Cannot cast the result<{1}> of CMD<{0}> to Boolean'.format(self.pred, rst))
            except Exception:
                raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
                      
        return self.match_succ_rst
    

def gen_preds(sSelect):
    if sSelect == '*':
        return [[Pred()]]
    if isinstance(sSelect, str):
        r = PATT_SELECT.split(sSelect)
        r = [deq(iter(r), 7) for i in range(int(len(r)/7))]
        r = [PredString(n,o1,c1,o2,c2,a,f) for [n,o1,c1,o2,c2,a,f] in r]
        r.reverse()
        return [r]
    if isinstance(sSelect, types.FunctionType):
        return [[PredFunction(sSelect)]]
    return [[Pred()]]

