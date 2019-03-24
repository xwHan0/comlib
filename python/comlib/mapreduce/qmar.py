"""
# 匹配执行
  Qmar使用Match对象来对数据进行过滤匹配和动作执行。Qmar使用Match.match函数进行匹配，若匹配成功则在PRE过程中
  执行Match.pre函数，在POST过程中执行Match.post函数。Match的详细定义参考：comlib.Match.
  User可以通过实例化或者扩展Match类来实现自定义的匹配和定义相对应的执行动作。

# Match匹配树
  Qmar通过Match定义的指向两一个Match实例的brother和next指针维护了一个Match匹配树。其结构类似于：

  match0 ----------(brother)---------- match1 ---(brother)--- match2
     |                                   |
   (next)                              (next)
     |                                   |
  match00 --(brother)-- match01        match10 --(brother)-- match11
 
  由brother指针串起来的一条match对象序列被称为一个匹配链。Qmar使用相同的datum节点数据按照brother
  指定的顺序在一条匹配链上依次匹配，直到找到第一个匹配的match对象。这一过程类似于'case'语句：使用
  同一个数据在多个条件中依次寻找第一个满足的条件。

  Qmar成功匹配到一个match后，数据节点的子节点就需要使用匹配match.next指向的match进行匹配。这一过程
  被称为条件顺次匹配。

  Qmar在PRE过程中的匹配过程为：
  1. 使用Datum树的头节点数据在和Match树的头节点对应的匹配链中进行匹配；
  2. 若匹配到一个match(matchX)，则记录下一次需要匹配的match链为matchX.next指向的匹配链；
  3. 若找不到，则判断为匹配失败。跳过当前树节点的子节点继续迭代；

  使用brother并行匹配的例子为：
  ```
  l = [1, 'Hello', 2, 'World', 3, (4.5, 6,7)]   # 待迭代的数据结构
  mt0 = Match(lambda x: type(x)==int, lambda (*d, result=None, stack=[]): return d[0]+1)   # 定义整型数匹配
  mt1 = Match(lambda x: type(x)==str, lambda (*d, result=None, stack=[]): return d[0]+',')   # 定义字符串匹配
  mt0.brother = mt1 # 定义Match关系
  rst = [for x in Qmar(l).match(mt0)]
  ```
"""
import re
import types

from comlib.mapreduce.child_relationship import TYPIC_CHILDREN_RELATIONSHIP, append_children_relationship
from comlib.mapreduce.stack import NodeInfo
from comlib.mapreduce.result import Result
from comlib.mapreduce.match import Match  #, MatchIter, MatchPredIter, get_match
from comlib.mapreduce.child import Child

PRE, POST, DONE, SKIP = 1,3,4,5 


class Qmar:
    """
    在给定的树结构中，按给定顺序执行迭代(Query)-匹配(Match)-执行(Action)-返回(Return)动作。

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
        self.step, self.result, self.cfg = 1, Result(), cfg

        # self.pre_return/self.post_return
        
        self.stack = [NodeInfo(datum)]

    def child(self, typ, sub):
        """追加child关系定义"""
        self.children_relationship[typ] = Child._gen_child_(sub)
        return self

    # def query(self, pred):
    #     """设置pred匹配条件。
    #     pred: (*datum) => Boolean
    #     """
    #     self.matches.append( MatchPredIter(pred) )
    #     self.step = 10
    #     return self

    # def match(self, pred, pre=None, reduce=None, post=None):
    #     self.matches.append( Match._gen_match_(pred, pre=pre, reduce=reduce, post=post) )
    #     self.step = 10
    #     return self
        
    def match(self, *match_context, pos=None):
        """追加一个匹配链match_context到位置为pos的match中。若pos=None，表示为顶层match。
        
        match_context被拆分为多个如下的格式，每个格式构造一个Match对象，然后依次使用brother指针连起来。
        - Match对象：占用一个match_context元素。该元素为独立的一个match对象。
        - Tuple or List: 占用一个match_context元素。该元素作为Match初始化参数使用。
        - Function: 占用1~3个match_context元素：
          -- 占用1个：表示一个指定pred函数的match
          -- 占用2个：表示一个指定pred和pre函数的match
          -- 占用3个：表示一个指定pred、pre和post函数的match
        """

        i, match_result, match_last, params_num = 0, None, None, len(match_context)
        while i < params_num:
            if isinstance( match_context[i], types.FunctionType ):    # 直接函数格式

                pred = match_context[i]
                if i < params_num -1 and isinstance( match_context[i+1], types.FunctionType ):
                    pre = match_context[i+1]
                    if i < params_num -2 and isinstance( match_context[i+2], types.FrameType ):
                        post, i = match_context[i+2], i+3
                    else:
                        post, i = None, i+2
                else:
                    pre, post, i = None, None, i+1
                match_node = Match(pred, pre, post)

            elif isinstance( match_context[i], Match ):   # 直接Match对象
                match_node, i = match_context[i], i+1

            elif isinstance( match_context[i], (tuple, list) ): # Tuple格式
                match_node, i = Match(*match_context[i]), i+1

            if match_result:
                match_last.brother = match_node
                match_last = match_last.brother
            else:
                match_result = match_last = match_node

        # 加入当前Match树结构中
        if pos == None:     # 头节点填充            
            self.stack[-1].match = match_result
        elif isinstance(pos, (tuple, list)):   # 默认父节点处理的next都指向当前头节点
            node = self.stack[-1].match.get_match(pos)
            while node:
                node.next = match_result
                node = node.brother

        self.step = 10
        return self

    def filter(self, pred, pre=None, post=None):
        """为当前Qmar设置全局过滤匹配条件pre，并设置对应的pre和post处理。若pre为None, 则pre不进行处理；若post为None，则post不进行处理；若pre和post全部为None，则在PRE阶段返回节点数据。"""
        self.stack[-1].match = Match(pre, pre, post)
        self.step = 10
        return self

    def initial(self, init=None):
        self.result.rst = init
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
         skip并不会破坏数据的树结构，仅仅是在遍历迭代是略过前几个节点。这里的略过不仅仅指pre过程，也包括post过程。"""
        
        for ite_cnt in range(n):
            
            # Get stack tail information for process
            node = self.stack[-1]
            
            node.sta, node.action = SKIP, None   # 不需要迭代
            
            # Next prepare
            try:
                    
                # Get all datum iterators and assign to parent
                node.children = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                # Get next elements of iterators
                nxt_datum = [next(i) for i in node.children]

                self.stack.append(NodeInfo(nxt_datum, pred_idx=0))
                    
            # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
            except (StopIteration,TypeError): 
                node.children = None
                break
                
        # self.skip_node = self.stack[-1] # 保存遍历开始节点，为遍历结束后恢复现场准备

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
        
        for ite_cnt in range(Qmar.MAX_IT_NUM):
            
            # 获取当前处理的节点
            node = self.stack[-1]
            
            if node.sta == PRE: # PRE处理过程
                
                #================  Match子过程  ===============
                if isinstance(node.datum[0], Match):
                    node.match, node.action = node.datum[0], node.datum[0].match(*node.datum, result=self.result, stack=self.stack)

                else:
                    # 匹配当前节点，并获取匹配match与action
                    node.matched, node.action = node.match._match_full( *node.datum, stack=self.stack, result=self.result)
                    #pred = self.matches[node.pred_idx]
                    #node.action = pred.match(*node.datum, result=self.result, stack=self.stack)

                # Next prepare
                try:
                    
                    # 获取datum子节点迭代器集合
                    node.children = [iter(self._get_children_iter(d, *node.datum)) for d in node.datum]
                    # 获取下一个子节点
                    nxt_datum = [next(i) for i in node.children]

                    # PRE处理
                    if node.action:
                        rst = node.action.pre(*node.datum, stack=self.stack, result=self.result)

                    # Push next elements into stack
                    # pred_idx = max(0, node.pred_idx - 1) if node.action else node.pred_idx
                    # self.stack.append(NodeInfo(nxt_datum, match=node.matched.next)
                    
                # Sub node is not iterable<TypeError>, iteration finish<StopIteration>
                except (StopIteration,TypeError):   #Leaf node
                    # Process
                    if node.action:
                        node.children = None
                        rst = node.action.pre(*node.datum, result=self.result, stack=self.stack)
                    

                # Modify top element status of stack
                node.sta = POST
                
                # Return
                if node.action and rst!=None:
                   return rst
                    
            elif node.sta == POST:

                if hasattr(node.datum[0], 'matchp'):
                    node.action = node.datum[0].matchp(*node.datum, stack=self.stack, result=self.result)

                # Process
                if node.action:
                    rst = node.action.post(*node.datum, stack=self.stack, result=self.result)
                    
                try:

                    # 判断是否到根节点
                    if len(self.stack) == 1:
                        node.sta = DONE
                    else: # 非根节点
                        node.sta = PRE  # For next status
                        # Pop stack
                        self.stack.pop()

                        # 执行Reduce子过程
                        if hasattr(self.stack[-1].datum[0], 'matchp') and node.action and self.stack[-1].action:
                            self.stack[-1].action.reduce(*node.datum, stack=self.stack, result=self.result)

                        # Parent element forward
                        nxt_datum = [next(i) for i in self.stack[-1].children]
                        self.stack.append(NodeInfo(nxt_datum))

                except StopIteration: # IndexError for empty-stack
                    pass

                if node.action and rst!=None:
                   return rst

            elif node.sta == DONE:
                
                node.sta = PRE  # 为下一次迭代做准备
                if self._enumerate_:
                    raise StopIteration()
                else:
                    return self.result.rst

            elif node.sta == SKIP:  # SKIP 状态继续保持

                self.skip()  #恢复现场，为下次遍历做准备
                if self._enumerate_:
                    raise StopIteration()
                else:
                    return self.result.rst

            else:
                raise Exception('Invalid status of FSM!')
        

            

