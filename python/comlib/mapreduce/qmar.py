
import re
import types

from comlib.mapreduce.child_relationship import TYPIC_CHILDREN_RELATIONSHIP, append_children_relationship
from comlib.mapreduce.stack import NodeInfo
from comlib.mapreduce.result import Result
from comlib.mapreduce.match import Match  #, MatchIter, MatchPredIter, get_match
from comlib.mapreduce.child import Child

PRE, POST, DONE, SKIP = 1,3,4,5 

import warnings
warnings.filterwarnings("ignore")            

PATT_CONDITION_BASE1 = r'[^[\]]'
PATT_CONDITION_1 = r'(?:{0})+'.format(PATT_CONDITION_BASE1)
PATT_CONDITION_BASE2 = r'{0}*\[{0}+\]{0}*'.format(PATT_CONDITION_BASE1)
PATT_CONDITION_2 = r'(?:{0})+'.format(PATT_CONDITION_BASE2)
PATT_CONDITION_BASE3 = r'(?:{0}|{1})*\[(?:{1})+\](?:{0}|{1})*'.format(PATT_CONDITION_BASE1, PATT_CONDITION_BASE2)
PATT_CONDITION_3 = r'(?:{0})+'.format(PATT_CONDITION_BASE3)

PATT_MATCH = re.compile(r'\s*({2}|{1}|{0})\s*'.format(
    r'(?:\w+|\*)', 
    r'\[(?:{2}|{1}|{0})\]'.format(PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3), 
    r'(?:\w+|\*)\[(?:{2}|{1}|{0})\]'.format(PATT_CONDITION_1, PATT_CONDITION_2, PATT_CONDITION_3),
))

class Qmar:
    """
    在给定的树结构中，按给定顺序执行迭代(Query)-匹配(Match)-执行(Action)-返回(Return)动作。

    详细帮助参见'comblib.mapreduce'

    Qmar遍历树时，对于每个节点，都会经过3个小过程:
    - pre过程: 指从父节点第一次迭代到当前节点的遍历
    - reduce过程：指一个子节点遍历完成，返回当前节点的遍历
    - post过程: 指子节点迭代完成返回到当前节点的遍历

    # 迭代遍历(Query)
      Qmar按照一定的规则寻找每个树节点的子节点迭代器，然后一一遍历之。
      - Qmar的子节点迭代器规则由Child类来承载。详细定义参见Child类说明。
      - Qmar使用一个格式为{objType:ChildObj}的Dict来保存各个类型节点的子节点迭代器获取Child类。 除了使用Child实例来获取子节点迭代器外，若节点是Child的派生子类，Qmar也会使用该类(Child)定义的sub函数来获取
        子节点迭代器；或者若树节点定义了__iter__函数，则使用该函数来获取子节点迭代器。

    # 返回结果(Return)
      Qmar返回动作Action执行后的结果。
      - Qmar支持2种返回的结果类型：
        ** 迭代完成一次性返回最终结果
        ** 每匹配成功一个节点，就基于当前节点返回一个结果
      - Qmar定义并实例化了一个Result对象来保存返回结果。当前用户也可以使用stack来保存每级执行的结果
    """
    
    MAX_IT_NUM = 999999
    CRITERIA_NODE_PATT = re.compile(r'#(\d+)')
#===================  内部默认定义变量  ====================
    # _matchIter_ = MatchIter()

    @staticmethod
    def configure(**cfg):
        for k,v in cfg.items():
            if k=='prefix':
                Qmar.CRITERIA_PATT = [
                    (re.compile(r'{0}(\d+)'.format(v)), r'node[\g<1>]'),
                    (re.compile(r'{0}{0}'.format(v)), r'node'),
                    (re.compile(r'{0}\.'.format(v)), r'node[0].'),
                ]
                Qmar.CRITERIA_NODE_PATT = re.compile(r'{0}(\d+)'.format(v))
            elif k=='max_it_num':
                Qmar.MAX_IT_NUM = v
    

    def __init__(self, *datum, **cfg):
        """使用树结构*datum来创建一个Qmar遍历实例。
        """
        
        # Set initial children relationship map table
        self.children_relationship = TYPIC_CHILDREN_RELATIONSHIP.copy()
    
        # New architecture fields
        # self.step, self.result, self.cfg, self.matches = 1, Result(), cfg, []
        self.step, self.cfg = 1, cfg

        # self.pre_return/self.post_return
        
        self.stack = [NodeInfo(datum)]

    def child(self, typ, sub):
        """追加child关系定义"""
        self.children_relationship[typ] = Child._gen_child_(sub)
        return self

    def match(self, *match_context, pos=None):
        """追加一个匹配链match_context到位置为pos的match中。若pos=None，表示为顶层match。顶层match放入当前stack[-1]中
        
        match_context被拆分为多个如下的格式，每个格式构造一个Match对象，然后依次使用brother指针连起来。
        - <Match>：占用一个match_context元素。该元素为独立的一个match对象。
        - <Tuple or List>: 占用一个match_context元素。该元素作为Match初始化参数使用。
        - <Function or str>: 根据连续的<Function>个数占用1~3个match_context元素：
          -- 占用1个：表示一个指定pred函数的match
          -- 占用2个：表示一个指定pred和pre函数的match
          -- 占用3个：表示一个指定pred、pre和post函数的match
        - Match需要的参数定义参见'comlib.mapreduce.Match'
        - 创建的匹配链中所有match节点的next都指向该匹配链的头match
        """

        i, match_result, match_last, params_num = 0, None, None, len(match_context)
        while i < params_num: # 循环每个match_context元素

            if isinstance( match_context[i], (types.FunctionType,str) ):    # 直接函数格式
                pred = match_context[i]
                if i < params_num -1 and isinstance( match_context[i+1], types.FunctionType ):
                    pre = match_context[i+1]
                    if i < params_num -2 and isinstance( match_context[i+2], types.FunctionType ):
                        post, i = match_context[i+2], i+3
                    else:
                        post, i = Match.DEFAULT, i+2
                else:
                    pre, post, i = Match.DEFAULT, Match.DEFAULT, i+1
                match_node = Match(pred, pre, post, next=match_result if match_result else Match.DEFAULT)

            elif isinstance( match_context[i], Match ):   # 直接Match对象
                match_node, i = match_context[i], i+1
                match_node.next = match_node if match_result==None else match_result 

            elif isinstance( match_context[i], (tuple, list) ): # Tuple格式
                match_node, i = Match(*match_context[i], next=match_result if match_result else Match.DEFAULT), i+1

            if match_result:    # match_result保存该匹配链的头match。头match已经存在
                match_last.brother = match_node # 串brother
                match_last = match_last.brother # match_last为最后一个建立的match
            else: # 建立第一个match
                match_result = match_last = match_node

        # 加入当前Match树结构中
        if pos == None:     # 头节点填充            
            self.stack[0].match = self.stack[-1].match = match_result
        elif isinstance(pos, (tuple, list)):   # 默认父节点处理的next都指向当前头节点
            node = self.stack[0].match.get_match(pos)
            node.next = match_result

        self.step = 10
        return self

    def matches(self, *args, pos=None):
        """定义串行匹配链。"""

        arg_num = len(args)

        if isinstance(args[0], str):
            r = PATT_MATCH.split(args[0])

            # 头匹配
            match_result = match_node = Match(r[1], pre=Match.PASS, post=Match.PASS)
            match_result.brother = Match(pred=Match.TRUE, pre=Match.PASS, post=Match.PASS, next=match_node)

            i, size = 3, len(r)-2
            while i < size:
                match_node.next = Match(r[i], pre=Match.PASS, post=Match.PASS)
                match_node = match_node.next
                match_node.brother = Match(pred=Match.TRUE, pre=Match.PASS, post=Match.PASS, next=match_node)
                i += 2

            # 尾节点
            i = 0
            if i < arg_num -1 and isinstance( args[i+1], types.FunctionType ):
                pre = args[0+1]
                if i < arg_num -2 and isinstance( args[i+2], types.FunctionType ):
                    post, i = args[i+2], i+3
                else:
                    post, i = Match.DEFAULT, i+2
            else:
                pre, post, i = Match.DEFAULT, Match.DEFAULT, i+1
            match_node.next = Match(r[-2], pre, post)
            match_node = match_node.next
            match_node.brother = Match(pred=Match.TRUE, pre=Match.PASS, next=match_node)

            # 加入当前Match树结构中
            if pos == None:     # 头节点填充            
                self.stack[0].match = self.stack[-1].match = match_result
            elif isinstance(pos, (tuple, list)):   # 默认父节点处理的next都指向当前头节点
                node = self.stack[0].match.get_match(pos)
                node.next = match_result

        self.step = 10
        return self


    def all(self):
        """遍历所有元素"""
        self.stack[0].match = self.stack[-1].match = Match()
        return self

    def filter(self, pred, pre=Match.DEFAULT, post=Match.DEFAULT):
        """为当前Qmar设置全局过滤匹配条件pre，并设置对应的pre和post处理。
        filter本质上定义了一个满足参数pred, pre和post的Match，和一个匹配常成功，next指向自身匹配链的Match.
        详细参数使用方法可以参考Match
        """
        self.match( Match(pred=pred, pre=pre, post=post), Match(pre=Match.PASS) )
        self.step = 10
        return self

    def map(self, pre):
        """对数据每一个数据datum使用函数pre，返回pre处理的的结果列表。
        map本质上为设置一个pre的Match"""
        self.match(Match(pre=pre))
        self.step = 10
        return self

    def initial(self, init=None):
        self.stack[-1].result = init
        return self
   
    def assist(self, *datum, children={}):
        """
        Append assist collection 'node' which children is children for iterator.
        """
        # self.append_children_relationship(children)
        self.stack[-1].datum += datum
        return self
       
    def run(self, enumrate=True): 
        """执行迭代并返回结果。"""
        self._enumerate_ = enumerate
        if len(self.stack[0].datum) == 0:
            def delay_query(*datum, children={}):
                self.assist(*datum, children=children)
                return self.__next__()
            return delay_query
        else:
            self._initial_()
            return self.__next__()
        
    def skip( self, n=1 ):
        """跳过前n个节点后开始遍历。
         skip并不会破坏数据的树结构，仅仅是在遍历迭代是略过前几个节点。这里的略过不仅仅指pre过程，也包括post过程。
         
         注意：! Skip必须在Qmar定义后马上调用 !
         """
        
        for _ in range(n):
            
            # Get stack tail information for process
            node = self.stack[-1]
            
            node.sta, node.action = SKIP, None   # 不需要迭代
            
            # Next prepare
            try:
                    
                # Get all datum iterators and assign to parent
                node.children = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                # Get next elements of iterators
                nxt_datum = [next(i) for i in node.children]

                self.stack.append(NodeInfo(nxt_datum))
                    
            # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
            except (StopIteration,TypeError): 
                node.children = None
                break

        return self
        
    def _initial_(self):
        if self.step < 10:      # Step-10: Normal Process
         
            # Process Step-9
            # self.matches = [Qmar._matchIter_]
            pass
        self.step = 10

 

    def _get_children_iter(self, *node):
        nxt = self.children_relationship.get(
            type(node[0]),
            self.children_relationship.get('*'))  # 查找处理类实例

        if nxt:
            return nxt.sub(*node)  # 调用类函数处理
        elif hasattr(node[0], '__iter__'):
            return iter(node[0])
        elif isinstance(node[0], Child):
            return node[0].sub(*node)
        
    def __iter__(self):
        self._initial_()
        self._enumerate_ = True
        return self
        
    def __next__( self ):
        
        for _ in range(Qmar.MAX_IT_NUM):
            
            # 获取当前处理的节点
            node = self.stack[-1]
            
            if node.sta == PRE: # PRE处理过程
                
                #================  Match子过程  ===============
                if isinstance(node.datum[0], Match):
                    # node.match, node.action = node.datum[0], node.datum[0].match(*node.datum, stack=self.stack)
                    if node.datum[0].match(*node.datum, stack=self.stack):
                        node.matched = node.datum[0]
                    else:
                        node.matched = None
                else:
                    # 匹配当前节点，并获取匹配match与action
                    node.matched = node.match._match_full( *node.datum, stack=self.stack)
                    #pred = self.matches[node.pred_idx]
                    #node.action = pred.match(*node.datum, result=self.result, stack=self.stack)

                # Next prepare
                try:
                    
                    # 获取datum子节点迭代器集合
                    node.children = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                    # 获取下一个子节点
                    nxt_datum = [next(i) for i in node.children]

                    # PRE处理
                    if node.matched:
                        rst = node.matched.pre(*node.datum, stack=self.stack)

                    # Push next elements into stack
                    # pred_idx = max(0, node.pred_idx - 1) if node.action else node.pred_idx
                    self.stack.append(NodeInfo(nxt_datum))
                    self.stack[-1].match = node.matched.next
                    
                # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
                except (StopIteration,TypeError):   #Leaf node
                    # Process
                    if node.matched:
                        node.children = None
                        rst = node.matched.pre(*node.datum, stack=self.stack)
                    

                # Modify top element status of stack
                node.sta = POST
                
                # Return
                if node.matched and rst!=None:
                   return rst
                    
            elif node.sta == POST:

                # if hasattr(node.datum[0], 'matchp'):
                #     node.action = node.datum[0].matchp(*node.datum, stack=self.stack, result=self.result)

                # Process
                if node.matched:
                    rst = node.matched.post(*node.datum, stack=self.stack)
                    
                try:

                    # 判断是否到根节点
                    if len(self.stack) == 1:
                        node.sta = DONE
                    else: # 非根节点
                        node.sta = PRE  # For next status
                        # Pop stack
                        self.stack.pop()

                        # 执行Reduce子过程
                        # if hasattr(self.stack[-1].datum[0], 'matchp') and node.action and self.stack[-1].action:
                        #     self.stack[-1].action.reduce(*node.datum, stack=self.stack, result=self.result)

                        # Parent element forward
                        nxt_datum = [next(i) for i in self.stack[-1].children]
                        self.stack.append(NodeInfo(nxt_datum))
                        self.stack[-1].match = node.match

                except StopIteration: # IndexError for empty-stack
                    pass

                if node.matched and rst!=None:
                   return rst

            elif node.sta == DONE:
                
                node.sta = PRE  # 为下一次迭代做准备
                if self._enumerate_:
                    raise StopIteration()
                else:
                    return self.stack[-1].result

            elif node.sta == SKIP:  # SKIP 状态继续保持

                self.skip()  #恢复现场，为下次遍历做准备
                self.stack[-1].match = self.stack[0].match
                if self._enumerate_:
                    raise StopIteration()
                else:
                    return self.stack[-1].result

            else:
                raise Exception('Invalid status of FSM!')
        


