
class Action:
    """执行动作函数定义

    Arguments:
    - datum: 当前节点数据tuple
    - stack: 当前树遍历堆栈
    - result: 当前树处理结果

    Return:
        当前需要返回(yield)的内容。若需要其它节点可见，则使用result缓存。
    """
    def pre(self, *datum, stack=[], result=None):
        """PRE过程处理函数"""
        pass

    def reduce(self, *datum, stack=[], result=None):
        """REDUCE过程处理函数"""
        pass

    def post(self, *datum, stack=[], result=None):
        """POST过程处理函数"""
        pass



class ActionIter(Action):
    def pre(self, *datum, stack=[], result=None):
        if len(datum) == 1:
            return datum[0]
        else:
            return datum


