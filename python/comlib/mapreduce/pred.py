import re
from comlib.iterator_operator import deq
import types


########################################## Global variable definition


#########################################  Local variable definition

PRE_YIELD = 1
POST_YIELD = 2
NONE_YIELD = 0

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
    (re.compile(r'#(\d+)'), r'node[\g<1>]'),
    (re.compile(r'##'), r'node'),
    (re.compile(r'#\.'), r'node.'),
]


######################################################
# 定义匹配条件类

class Pred:
    def __init__(self, proc_idx=0):
        self.proc_idx = 0
        
    # Always success match function
    def match(self, *node): return 1

    # Return weather or not stop all other nodes iteration
    def is_stop(self, result): return (result==3) or (result==-3)
    # Return weather or not stop sub nodes iteration
    def is_sub(self, result):  return not ((result==-2) or (result==2))
    # Return weather or not match success
    def is_succ(self, result):  return result > 0
    # 返回当前Pred是否已经匹配完成
    def is_done(self, result): return result > 0
    # 返回是否子迭代前处理
    def is_pre_yield(self): return True
    # 返回是否子迭代后处理
    def is_post_yield(self): return False
    # 设置自定义过滤函数
    def set_match(self,pred): 
        self.match = pred
        return self
        


class PredSkip(Pred):
    def is_succ(self,result): return False
    def is_done(self,result): return True


class PredSelect(Pred):        

    def __init__(self, nflag='', cls_name2='*', pred2='', pred1='', cls_name1='*', proc_idx=None, flags=''):
       
        super().__init__()
       
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
        self.obj_fail_rst, self.pred_fail_rst, self.match_succ_rst = -1,-1,1

        # Searh and process prox_idx
        self.proc_idx = int(proc_idx) if proc_idx else 0

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
        
    def match_obj_condition( self, *node ):
        # 对象匹配
        if node[0].__class__.__name__ != self.cls_name:
            return self.obj_fail_rst
            
        # 条件匹配
        try:
            rst = eval(self.pred)
            if rst == False: 
                return self.pred_fail_rst
            elif rst == True: 
                return self.match_succ_rst
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
            if rst == False: 
                return self.pred_fail_rst
            elif rst == True: 
                return self.match_succ_rst
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
                if rst == False: 
                    return self.pred_fail_rst
                elif rst == True: 
                    return self.match_succ_rst
                else: raise Exception('Invalid condion result. CMD<{0}>'.format(self.pred))
            except Exception:
                raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
                      
        return self.match_succ_rst
    

def gen_preds(sSelect):
    if sSelect == '*':
        return [Pred()]
    if isinstance(sSelect, str):
        r = PATT_SELECT.split(sSelect)
        r = [deq(iter(r), 7) for i in range(int(len(r)/7))]
        r = [PredSelect(n,o1,c1,o2,c2,a,f) for [n,o1,c1,o2,c2,a,f] in r]
        r.reverse()
        return r
    if isinstance(sSelect, types.FunctionType):
        return Pred().set_match(sSelect)
    return [Pred()]

