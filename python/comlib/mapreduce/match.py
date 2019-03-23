import types

from comlib.mapreduce.action import ActionIter, Action

class Match:
    """条件匹配类。

    通过match函数来匹配返回对应的Action动作。
    Match类可以包含一个matchp函数。该函数用于调用Action类的reduce过程。matchp函数定义格式和match保持一致。matchp函数可以修改POST过程中的post动作内容，并执行reduce过程。
    """
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
        """根据当前节点数据datum，结合当前计算结果result和当前堆栈stack的状况返回匹配Action。
        返回None表示匹配失败，无Action可执行。
        """
        return None
        

def get_action(match, *datum, stack=[], result=None):
    while match:
        if act = match.match(*datum, stack=stack, result=result):
            return match, act
        else:
            match = match.brother
    return None, None


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
