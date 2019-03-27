import types
import re


PATT_CONDITION_BASE1 = r'[^[\]]'
PATT_CONDITION_1 = r'(?:{0})+'.format(PATT_CONDITION_BASE1)
PATT_CONDITION_BASE2 = r'{0}*\[{0}+\]{0}*'.format(PATT_CONDITION_BASE1)
PATT_CONDITION_2 = r'(?:{0})+'.format(PATT_CONDITION_BASE2)
PATT_CONDITION_BASE3 = r'(?:{0}|{1})*\[(?:{1})+\](?:{0}|{1})*'.format(PATT_CONDITION_BASE1, PATT_CONDITION_BASE2)
PATT_CONDITION_3 = r'(?:{0})+'.format(PATT_CONDITION_BASE3)

PATT_MATCH = re.compile(r'\s*(?:{2}|{1}|{0})\s*'.format(
    r'(\w+|\*)', 
    r'\[({2}|{1}|{0})\]'.format(PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3), 
    r'(\w+|\*)\[({2}|{1}|{0})\]'.format(PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3),
))

     
PATT_VAR = [
    (re.compile(r'#(\d+)'), r'datum[\g<1>]'),
    (re.compile(r'##'), r'datum'),
    (re.compile(r'#\.'), r'datum[0].'),
]


class _DEFAULT: pass
class _TRUE: pass
class _FALSE: pass
class _PASS: pass
class _NONE: pass

DEFAULT = _DEFAULT()
TRUE = _TRUE()
FALSE = _FALSE()
PASS = _PASS()
NONE = _NONE()


class Match:
    """条件匹配类。

    Argument:
    - pred: 匹配条件函数。
      -- 该函数返回一个bool值。True代表匹配成功；False代表匹配失败
      -- 支持以下几种输入参数格式
        --- Match.DEFAULT: 使用Qmar默认的匹配行为。Qmar默认总是匹配成功
        --- Match.FALSE：总是匹配失败行为
        --- <FunctionType>: 用户自定义行为
        --- <str>: 字符串表示的条件表达式。格式为: 'objName[condition]'
            ---- objName: 遍历的datum[0]的类型。可以为'*'或者空''，代表匹配任意的数据类型
            ---- condition：任意的Python支持的条件表达式（表达式的结果必须为True或者False）。condition中支持一些特殊的变量：
              ----- 条件支持最多3层'[]'嵌套
              ----- #.attr: 获取节点nodes[0]的'attr'属性值。Get the attribute of nodes[0] like: 'nodes[0].attr'
              ----- #n: 获取nodes序列中的第n个节点node(n=0-N)。
              ----- #n.attr: Get the attribute of nodes[n] like: 'nodes[n].attr' (n=0-N)
              ----- ##: List of all nodes
    - pre: PRE过程执行函数。
      -- 该函数返回一个需要yield的值。返回None表示不需要在PRE过程中yield
      -- 支持以下几种输入参数格式
        --- Match.DEFAULT: 使用Qmar默认的PRE行为。Qmar默认返回dataum[0]
        --- Match.PASS: 不进行任何动作，返回None
        --- <FunctionType>: 用户自定义行为
    - post: POST过程执行函数。
      -- 该函数返回一个需要yield的值。返回None表示不需要在POST过程中yield
      -- 支持以下几种输入参数格式
        --- Match.DEFAULT: 使用Qmar默认的POST行为。Qmar默认不进行任何动作，返回None
        --- <FunctionType>: 用户自定义行为
    - Qmar使用一个match图来表示树中各个节点的匹配条件与动作的关系。图中每一个节点都包含next和brother两个指向
        下一个match对象的指针。
    - next: 当前match匹配成功后的下一跳匹配match
      -- 支持以下几种输入参数格式
        --- Match.DEFAULT: 下一跳指向自己
        --- <Match>: 用户自定义下一跳
    
    pred/pre/post函数都有相同的参数定义：XXX(*datum, stack=[])
    - datum: 当前处理的树节点数据tuple
        -- Match会根据pred/pre/post实际需要的参数个数来使用*datum进行填充。所以支持函数参数个数小于datum个数的。
    - stack: 当前迭代栈
        -- Match会根据pred/pre/post是否定义了stack而决定调度行为。所以支持在pred/pre/post中不定义stack关键字参数
    """
    MAX_CONCURRENT_PRED_NUM = 100000
    



    def __init__(self, pred=TRUE, pre=DEFAULT, post=DEFAULT, next=DEFAULT, brother=None):

        self.brother = brother

        # next处理
        self.next = self if next==DEFAULT else next

        # 重新定义match处理函数
        if pred == TRUE:    # 默认处理方式：总是匹配成功
            def match_i(self, *datum, stack=[]): 
                return True

        elif pred==FALSE:   # False代表匹配总是不成功
            def match_i(self, *datum, stack=[]): 
                return False

        elif isinstance(pred, types.FunctionType):  # User自定义函数处理
            if 'stack' in pred.__code__.co_varnames:    # pred函数包含stack参数
                arg_num = pred.__code__.co_argcount-1
                if arg_num == -1:
                    def match_i(self, *datum, stack=[]): 
                        return pred(*datum, stack=stack)
                else:
                    def match_i(self, *datum, stack=[]): 
                        return pred(*(datum[:arg_num]), stack=stack)
            else:
                arg_num = pred.__code__.co_argcount
                if arg_num == 0:
                    def match_i(self, *datum, stack=[]):
                        return pred(*datum)
                else:
                    def match_i(self, *datum, stack=[]):
                        return pred(*(datum[:arg_num]))

        elif isinstance(pred, str): #字符串解析函数
            [_, o1, c1, o2, c2, _] = PATT_MATCH.split(pred)
            objName, condStr = o1 if o1 else o2, c1 if c1 else c2
            
            # 替换变量
            for p,s in PATT_VAR:
                condStr = p.sub(s, condStr)

            # 定义返回函数
            def match_i(self, *datum, stack=[]):
                # 对象类型匹配
                if objName!='*' and datum[0].__class__.__name__ != objName:
                    return False
            
                # 条件匹配
                if condStr and condStr !='':
                    try:
                        rst = eval(condStr)
                        if rst == False: return False
                        elif rst == True: return True
                        else: raise Exception('Cannot cast the result<{1}> of CMD<{0}> to Boolean'.format(condStr, rst))
                    except Exception:
                        raise Exception('Invalid condition statement. CONDITION<{0}>'.format(condStr))
                      
                return True

        if pred != NONE:
            self.match = types.MethodType(match_i, self)  # 动态修改对象(非类)成员函数

        # 重新定义pre处理函数
        if pre == DEFAULT:
            def pre_i(self, *datum, stack=[]): 
                return datum[0] if len(datum)==1 else datum
        elif pre==PASS:
            def pre_i(self, *datum, stack=[]): 
                return None
        elif isinstance(pre, types.FunctionType):
            if 'stack' in pre.__code__.co_varnames:
                arg_num = pre.__code__.co_argcount-1
                if arg_num == -1:
                    def pre_i(self, *datum, stack=[]): 
                        return pre(*datum, stack=stack)
                else:
                    def pre_i(self, *datum, stack=[]): 
                        return pre(*(datum[:arg_num]), stack=stack)
            else:
                arg_num = pre.__code__.co_argcount
                if arg_num == 0:
                    def pre_i(self, *datum, stack=[]): 
                        return pre(*datum)
                else:
                    def pre_i(self, *datum, stack=[]): 
                        return pre(*(datum[:arg_num]))

        if pre != NONE:
            self.pre = types.MethodType(pre_i, self)  # 动态修改对象(非类)成员函数

        # 重新定义post处理函数
        if post == DEFAULT or post == PASS:
            def post_i(self, *datum, stack=[]): 
                return None
        elif isinstance(post, types.FunctionType):
            if 'stack' in post.__code__.co_varnames:
                arg_num = post.__code__.co_argcount-1
                if arg_num == -1:
                    def post_i(self, *datum, stack=[]): 
                        return post(*datum, stack=stack)
                else:
                    def post_i(self, *datum, stack=[]): 
                        return post(*(datum[:arg_num]), stack=stack)
            else:
                arg_num = post.__code__.co_argcount
                if arg_num == 0:
                    def post_i(self, *datum, stack=[]): 
                        return post(*datum)
                else:
                    def post_i(self, *datum, stack=[]): 
                        return post(*(datum[:arg_num]))

        if post != NONE:
            self.post = types.MethodType(post_i, self)  # 动态修改对象(非类)成员函数

    def set_loop(self):
        match, cnt = self, 0
        while match.next:
            if cnt <= Match.MAX_CONCURRENT_PRED_NUM:
                raise Exception('ERROR')
            match = match.next
        match.next = Match(True, next=self)
        return self

    def _match_full(self, *datum, stack=[]):
        """Qmar在__next__函数中调用该函数进行真实匹配动作"""
        match_node, cnt = self, 0
        while match_node:
            if cnt > Match.MAX_CONCURRENT_PRED_NUM:
                raise Exception('并发匹配条件超过了规定的上限Match.MAX_CONCURRENT_PRED_NUM({0}).请检查是否Match对象的brother指针有循环指示，或者提高允许上限。'.format(Match.MAX_CONCURRENT_PRED_NUM))
            cnt += 1

            if match_node.match(*datum, stack=stack):
                return match_node
            else:
                match_node = match_node.brother
        return None

    def get_match(self, pos=[]):
        """获取从当前节点开始的，树序号为pos的match实例。若pos深度大于当前match树深度，则搜索停止到当前match叶子节点；
        若pos[i]大于当前match的brother个数，则搜索终止到最后一个有戏的brother"""
        node = self
        for p in pos:
            node1 = node._get_brother_match(p).next
            if node1:
                node = node1
            else:   # next已经是None
                return node
        return node

    def _get_brother_match(self, idx):
        """获取从当前节点开始的，第idx个brother的match。若idx大于brother个数，则搜索终止到最后一个match节点。"""
        node, i = self, 0
        while node and i<idx:
            node = node.brother
        return node


Match.DEFAULT = DEFAULT
Match.NONE = NONE
Match.TRUE = TRUE
Match.FALSE = FALSE
Match.PASS = PASS
