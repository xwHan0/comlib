
class Action:
    """执行动作函数定义

    Arguments:
    - datum: 当前节点数据tuple
    - stack: 当前树遍历堆栈
    - result: 当前树处理结果

    Return:
        当前需要返回(yield)的内容，None表示不需要返回。若需要其它节点可见，则使用result缓存。
        
    """
    def pre(self, *datum, stack=[], result=None):
        """PRE过程处理函数。当前节点匹配成功时执行。"""
        return None

    def reduce(self, *datum, stack=[], result=None):
        """REDUCE过程处理函数。
仅在有当前节点存在matchp函数，并且子节点和当前节点都匹配成功时执行。matchp定义参考Match说明。"""
        return None

    def post(self, *datum, stack=[], result=None):
        """POST过程处理函数。当前节点匹配成功时执行。
注意：当前节点有matchp函数定义时，使用matchp返回的action执行。"""
        return None



class ActionIter(Action):
    def pre(self, *datum, stack=[], result=None):
        if len(datum) == 1:
            return datum[0]
        else:
            return datum


