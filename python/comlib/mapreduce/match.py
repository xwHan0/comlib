import types

# from comlib.mapreduce.action import ActionIter, Action

class Match:
    """条件匹配类。

    Qmar在PRE过程开始判断当前树节点数据datum是否满足该类定义的match匹配条件。
    若满足则在PRE过程中调用该类定义的pre函数，在POST过程中调用该类定义的post函数。
    """
    MAX_CONCURRENT_PRED_NUM = 100000

    # @staticmethod
    # def _gen_match_(args, pre=None, reduce=None, post=None):
    #     if isinstance(args, Match): return args
    #     if isinstance(args, types.FunctionType): return MatchPredIter(args)
    #     if isinstance(args, type): return MatchType(args, pre=pre, reduce=reduce, post=post)
    #     return Match()

    def __init__(self, pred=None, pre=None, post=None, next=None, brother=None):
        """
        - pred: 匹配函数。格式定义与Match.match函数定义一致。
        - pre: PRE过程执行函数。格式定义与Match.pre函数定义一致。
        - post: POST过程执行函数。格式定义与Match.post函数定义一致。
        - Qmar使用一个match图来表示树中各个节点的匹配条件与动作的关系。图中每一个节点都包含next和brother两个指向
          下一个match对象的指针。
        """
        self.next = next
        self.brother = brother

        # 重新定义match处理函数
        if pred:
            def match_i(self, *datum, stack=[], result=None): 
                return pred(*datum, stack=stack, result=result)
        elif pred==False:
            def match_i(self, *datum, stack=[], result=None): 
                return False
        else:
            def match_i(self, *datum, stack=[], result=None): 
                return True
        self.match = types.MethodType(match_i, self)  # 动态修改对象(非类)成员函数

        # 重新定义pre处理函数
        if pre:
            def pre_i(self, *datum, stack=[], result=None): 
                return pre(*datum, stack=stack, result=result)
        elif pre==False:
            def pre_i(self, *datum, stack=[], result=None): 
                return None
        else:
            def pre_i(self, *datum, stack=[], result=None): 
                return datum[0]
        self.pre = types.MethodType(pre_i, self)  # 动态修改对象(非类)成员函数

        # 重新定义post处理函数
        if post:
            def post_i(self, *datum, stack=[], result=None): 
                return post(*datum, stack=stack, result=result)
        else:
            def post_i(self, *datum, stack=[], result=None): 
                return None
        self.post = types.MethodType(post_i, self)  # 动态修改对象(非类)成员函数

    # def match(self, *datum, stack=[], result=None):
    #     """根据当前节点数据datum，结合当前计算结果result和当前堆栈stack的状况判断匹配结果。
    #     匹配成功返回True，失败返回False。
    #     """
    #     return False

    # def pre(self, *datum, stack=[], result=None):
    #     """PRE过程处理函数。当前节点匹配成功时根据当前节点数据datum，结合当前计算结果result和当前堆栈stack的状况执行。"""
    #     return None

    # def post(self, *datum, stack=[], result=None):
    #     """POST过程处理函数。当前节点匹配成功时根据当前节点数据datum，结合当前计算结果result和当前堆栈stack的状况执行。"""
    #     return None

    def set_loop(self):
        match, cnt = self, 0
        while match.next:
            if cnt <= Match.MAX_CONCURRENT_PRED_NUM:
                raise Exception('ERROR')
            match = match.next
        match.next = Match(True, next=self)
        return self

    def _match_full(self, *datum, stack=[], result=None):
        """Qmar在__next__函数中调用该函数进行真实匹配动作"""
        match, cnt = self, 0
        while match:
            if cnt <= Match.MAX_CONCURRENT_PRED_NUM:
                raise Exception('并发匹配条件超过了规定的上限Match.MAX_CONCURRENT_PRED_NUM({0}).请检查是否Match对象的brother指针有循环指示，或者提高允许上限。'.format(Match.MAX_CONCURRENT_PRED_NUM))
            cnt += 1

            if match.match(*datum, stack=stack, result=result):
                return match
            else:
                match = match.brother
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


# class MatchIter(Match):
#     """在PRE过程中迭代返回每个树节点数据。"""
#     action = ActionIter()
#     def match(self, *datum, stack=[], result=None):
#         return MatchIter.action


# class MatchPredIter(MatchIter):
#     """按照pred条件判断是否需要在PRE过程中返回节点数据。
    
#     pred格式：(*datum) => Boolean"""
#     def __init__(self, pred):
#         self.pred = pred

#     def match(self, *datum, stack=[], result=None):
#         if self.pred( *datum ):
#             return MatchIter.action
#         else:
#             return None
            

# class MatchType(Match):
#     """匹配数据类型"""
#     def __init__(self, typ, pre=None, reduce=None, post=None):
#         self.typ = typ

#         # 定义基本Action对象
#         act = ActionIter()      # 默认包含pre处理

#         # 重新定义pre处理函数
#         if pre:
#             def pre_i(self, *datum, stack=[], result=None): 
#                 return pre(*datum, stack=stack, result=result)

#             act.pre = types.MethodType(pre_i, act)  # 动态修改对象(非类)成员函数

#         # 重新定义reduce处理函数
#         if reduce:
#             def reduce_i(self, *datum, stack=[], result=None): 
#                 return reduce(*datum, stack=stack, result=result)

#             act.reduce = types.MethodType(reduce_i, act)

#         # 重新定义pre处理函数
#         if post:
#             def post_i(self, *datum, stack=[], result=None): 
#                 return post(*datum, stack=stack, result=result)

#             act.post = types.MethodType(post_i, act)

#         self.action = act

#     def match(self,*datum, stack=[], result=None):
#         if isinstance( datum[0], self.typ ):
#             return self.action
#         else:
#             return None
