import types

# from comlib.mapreduce.action import ActionIter, Action

class Match:
    """条件匹配类。

    Argument:
        - pred: 匹配条件函数。
          -- 该函数返回一个bool值。True代表匹配成功；False代表匹配失败
          -- 支持以下几种输入参数格式
            --- None(Default): 使用Qmar默认的匹配行为。Qmar默认总是匹配成功
            --- False：总是匹配失败行为
            --- <FunctionType>: 用户自定义行为
        - pre: PRE过程执行函数。
          -- 该函数返回一个需要yield的值。返回None表示不需要在PRE过程中yield
          -- 支持以下几种输入参数格式
            --- None(Default): 使用Qmar默认的PRE行为。Qmar默认返回dataum[0]
            --- False: 不进行任何动作，返回None
            --- <FunctionType>: 用户自定义行为
        - post: POST过程执行函数。
          -- 该函数返回一个需要yield的值。返回None表示不需要在POST过程中yield
          -- 支持以下几种输入参数格式
            --- None(Default): 使用Qmar默认的POST行为。Qmar默认不进行任何动作，返回None
            --- <FunctionType>: 用户自定义行为
        - Qmar使用一个match图来表示树中各个节点的匹配条件与动作的关系。图中每一个节点都包含next和brother两个指向
          下一个match对象的指针。
        - next: 当前match匹配成功后的下一跳匹配match
          -- 支持以下几种输入参数格式
            --- False(Default): 下一跳指向自己
            --- <Match>: 用户自定义下一跳
        
        pred/pre/post函数都有相同的参数定义：XXX(*datum, stack=[])
        - datum: 当前处理的树节点数据tuple
          -- Match会根据pred/pre/post实际需要的参数个数来使用*datum进行填充。所以支持函数参数个数小于datum个数的。
        - stack: 当前迭代栈
          -- Match会根据pred/pre/post是否定义了stack而决定调度行为。所以支持在pred/pre/post中不定义stack关键字参数
    """
    MAX_CONCURRENT_PRED_NUM = 100000

    # @staticmethod
    # def _gen_match_(args, pre=None, reduce=None, post=None):
    #     if isinstance(args, Match): return args
    #     if isinstance(args, types.FunctionType): return MatchPredIter(args)
    #     if isinstance(args, type): return MatchType(args, pre=pre, reduce=reduce, post=post)
    #     return Match()

    def __init__(self, pred=None, pre=None, post=None, next=False, brother=None):
        """
        Argument:
        - pred: 匹配条件函数。
          -- 该函数返回一个bool值。True代表匹配成功；False代表匹配失败
          -- 支持以下几种输入参数格式
            --- None(Default): 使用Qmar默认的匹配行为。Qmar默认总是匹配成功
            --- False：总是匹配失败行为
            --- <FunctionType>: 用户自定义行为
        - pre: PRE过程执行函数。
          -- 该函数返回一个需要yield的值。返回None表示不需要在PRE过程中yield
          -- 支持以下几种输入参数格式
            --- None(Default): 使用Qmar默认的PRE行为。Qmar默认返回dataum[0]
            --- False: 不进行任何动作，返回None
            --- <FunctionType>: 用户自定义行为
        - post: POST过程执行函数。
          -- 该函数返回一个需要yield的值。返回None表示不需要在POST过程中yield
          -- 支持以下几种输入参数格式
            --- None(Default): 使用Qmar默认的POST行为。Qmar默认不进行任何动作，返回None
            --- <FunctionType>: 用户自定义行为
        - Qmar使用一个match图来表示树中各个节点的匹配条件与动作的关系。图中每一个节点都包含next和brother两个指向
          下一个match对象的指针。
        - next: 当前match匹配成功后的下一跳匹配match
          -- 支持以下几种输入参数格式
            --- False(Default): 下一跳指向自己
            --- <Match>: 用户自定义下一跳
        
        pred/pre/post函数都有相同的参数定义：XXX(*datum, stack=[])
        - datum: 当前处理的树节点数据tuple
          -- Match会根据pred/pre/post实际需要的参数个数来使用*datum进行填充。所以支持函数参数个数小于datum个数的。
        - stack: 当前迭代栈
          -- Match会根据pred/pre/post是否定义了stack而决定调度行为。所以支持在pred/pre/post中不定义stack关键字参数
        """
        self.brother = brother

        # next处理
        if next == False: # 默认next处理为指向自己
            self.next = self
        else:
            self.next = next

        # 重新定义match处理函数
        if pred == None:    # 默认处理方式：总是匹配成功
            def match_i(self, *datum, stack=[], result=None): 
                return True
        elif pred==False:   # False代表匹配总是不成功
            def match_i(self, *datum, stack=[], result=None): 
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
        self.match = types.MethodType(match_i, self)  # 动态修改对象(非类)成员函数

        # 重新定义pre处理函数
        if pre == None:
            def pre_i(self, *datum, stack=[], result=None): 
                return datum[0] if len(datum)==1 else datum
        elif pre==False:
            def pre_i(self, *datum, stack=[], result=None): 
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
        self.pre = types.MethodType(pre_i, self)  # 动态修改对象(非类)成员函数

        # 重新定义post处理函数
        if not post:
            def post_i(self, *datum, stack=[], result=None): 
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

    def _match_full(self, *datum, stack=[]):
        """Qmar在__next__函数中调用该函数进行真实匹配动作"""
        match, cnt = self, 0
        while match:
            if cnt > Match.MAX_CONCURRENT_PRED_NUM:
                raise Exception('并发匹配条件超过了规定的上限Match.MAX_CONCURRENT_PRED_NUM({0}).请检查是否Match对象的brother指针有循环指示，或者提高允许上限。'.format(Match.MAX_CONCURRENT_PRED_NUM))
            cnt += 1

            if match.match(*datum, stack=stack):
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
