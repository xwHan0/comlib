from comlib.mapreduce.action import ActionIter

class Match:
    """条件匹配类。

    通过match函数来匹配返回对应的Action动作。
    """
    def match(self, *datum, stack=[], result=None):
        """根据当前节点数据datum，结合当前计算结果result和当前堆栈stack的状况返回匹配Action。
        返回None表示匹配失败。
        """
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