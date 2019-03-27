"""
# Introduce
  一次Qmar调用分为2个步骤：
  1. 实例化Qmar对象
    Qmar对象的构建包含：数据绑定、偏移设置、子迭代器设置和匹配设置几个步骤。
    注意：!步骤之间的顺序不可以改写!
    ```
        a = [1,2,3,4]
        qm = Qmar(a, Index())   # MUST. 绑定数据
            .skip()  # Optional. 便宜设置
            .child(list, ChildSub('sub'))  # Optional. 子迭代器设置
            .match(lambda x: odd, lambda x: x+100)  # 匹配设置
    ```
  2. 迭代，并获取结果
    ```
        rst = [x for x in qm]
    ```

# 匹配执行
  Qmar使用Match对象来对数据进行过滤匹配和动作执行。Qmar使用Match.match函数进行匹配，若匹配成功则在PRE过程中
  执行Match.pre函数，在POST过程中执行Match.post函数。Match的详细定义参考：comlib.Match.
  User可以通过实例化或者扩展Match类来实现自定义的匹配和定义相对应的执行动作。

# 迭代栈
  Qmar在迭代时，会依照datum的树状层次把datum压入一个栈，同时为栈节点设置相关的状态表示。该栈被称为Qmar的迭代栈。
  
  迭代栈的[0]节点对应树的根节点信息，[-1]节点对应当前节点信息。[-2]节点对应当前节点的父节点信息，依此类推。

  每个迭代节点包含以下信息：
  - sta: 当前迭代过程：PRE|POST|DONE;
  - datum: 当前节点数据Tuple;
  - match: 当前节点的匹配链(见'Match匹配树'小节说明)起始match
  - matched: 当前节点匹配到的match。没有匹配成功，该域为None
  - children：当前节点子节点的迭代器
  - result(Option): Reduce操作的返回结果

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

  # Feature

  ### 支持多迭代
  Qmar支持实例化一次，然后多次迭代。Qmar每次迭代完成后，会恢复迭代状态，供下次迭代使用。例如：
  ```
      def test_1d_array(self):
        a = [10,20,30,40]
        que = Qmar(a).skip().all()
        r =[]
        for i in range(5):
            r += [x for x in que]
        assert r == [10,20,30,40]*5
  ```

  ### 支持条件过滤
  Qmar支持使用filter设置过滤条件。
  ```
      def test_func_pred(self):
        a = [1,2,3,4,5,6,7]
        r = [x for x in Qmar(a).skip().filter(lambda x:x%2==0)]
        assert r == [2,4,6]
  ```

  ### 支持map映射
  ```
    def test_map_commom(self):
        # rst = [x for x in Query([1,2,3,4]).map(lambda x:x+10).skip()]
        rst = [x for x in Qmar([1,2,3,4]).skip().map(lambda x:x+10)]
        assert rst == [11,12,13,14]
  ```

"""

from comlib.mapreduce.match import Match
