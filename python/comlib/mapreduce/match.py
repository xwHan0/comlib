
class Match:
    """条件匹配类。

    通过match函数来匹配返回对应的Action动作。
    """
    def match(self, *datum, result=None, stack=[]):
        """根据当前节点数据datum，结合当前计算结果result和当前堆栈stack的状况返回匹配Action
        """
        return None