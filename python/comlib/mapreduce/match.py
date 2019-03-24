import types

from comlib.mapreduce.action import ActionIter, Action

class Match:
    """条件匹配类。

    Qmar在PRE过程开始判断当前树节点数据datum是否满足该类定义的match匹配条件。
    若满足则在PRE过程中调用该类定义的pre函数，在POST过程中调用该类定义的post函数。
    """
    MAX_CONCURRENT_PRED_NUM = 100000

    @staticmethod
    def _gen_match_(args, pre=None, reduce=None, post=None):
        if isinstance(args, Match): return args
        if isinstance(args, types.FunctionType): return MatchPredIter(args)
        if isinstance(args, type): return MatchType(args, pre=pre, reduce=reduce, post=post)
        return Match()

    def __init__(self, next=None, brother=None):
        self.next = next
        self.brother = brother

    def match(self, *datum, stack=[], result=None):
        """根据当前节点数据datum，结合当前计算结果result和当前堆栈stack的状况判断匹配结果。
        匹配成功返回True，失败返回False。
        """
        return False

    def pre(self, *datum, stack=[], result=None):
        """PRE过程处理函数。当前节点匹配成功时执行。"""
        return None

    def post(self, *datum, stack=[], result=None):
        """POST过程处理函数。当前节点匹配成功时执行。
注意：当前节点有matchp函数定义时，使用matchp返回的action执行。"""
        return None

    def set_loop(self):
        match, cnt = self, 0
        while match.next:
            if cnt <= Match.MAX_CONCURRENT_PRED_NUM:
                raise Exception('ERROR')
            match = match.next
        match.next = Match(True, next=self)
        return self
        

    def get_action(self, *datum, stack=[], result=None):
        while match:
            if cnt <= Match.MAX_CONCURRENT_PRED_NUM:
                raise Exception('ERROR')
            if act = match.match(*datum, stack=stack, result=result):
                return match, act
            else:
                match = match.brother
        return None


class MatchIter(Match):
    """在PRE过程中迭代返回每个树节点数据。"""
    action = ActionIter()
    def match(self, *datum, stack=[], result=None):
        return MatchIter.action


class MatchPredIter(MatchIter):
    """按照pred条件判断是否需要在PRE过程中返回节点数据。
    
    pred格式：(*datum) => Boolean"""
    def __init__(self, pred):
        self.pred = pred

    def match(self, *datum, stack=[], result=None):
        if self.pred( *datum ):
            return MatchIter.action
        else:
            return None
            

class MatchType(Match):
    """匹配数据类型"""
    def __init__(self, typ, pre=None, reduce=None, post=None):
        self.typ = typ

        # 定义基本Action对象
        act = ActionIter()      # 默认包含pre处理

        # 重新定义pre处理函数
        if pre:
            def pre_i(self, *datum, stack=[], result=None): 
                return pre(*datum, stack=stack, result=result)

            act.pre = types.MethodType(pre_i, act)  # 动态修改对象(非类)成员函数

        # 重新定义reduce处理函数
        if reduce:
            def reduce_i(self, *datum, stack=[], result=None): 
                return reduce(*datum, stack=stack, result=result)

            act.reduce = types.MethodType(reduce_i, act)

        # 重新定义pre处理函数
        if post:
            def post_i(self, *datum, stack=[], result=None): 
                return post(*datum, stack=stack, result=result)

            act.post = types.MethodType(post_i, act)

        self.action = act

    def match(self,*datum, stack=[], result=None):
        if isinstance( datum[0], self.typ ):
            return self.action
        else:
            return None
