[TOC]

#### 支持内联匹配
内联匹配指用户通过扩展Match和Child类，把数据、匹配、子节点迭代器都柔和到一个数据类中的方法。在Qmar中，内联匹配(Qmar检测使用派生自Match)的执行优先级是高于普通的Match、Child捆绑的。

内联匹配类的定义时，必须<font color='red'>**注意**</font>以下点：
- 必须定义__init__初始化函数。并且在__init__中调用super.__init__函数。
  - Match包含3个动作函数: pred,pre和post。需要在内联匹配类中定义的动作，必须在super.__init__的参数中设置为Match.NONE。否则无法执行派生类的行为
- Child行为由sub函数进行继承

首先从Match和Child派生一个包含数据的内联匹配子类。
```python
    class MyQMar(comlib.mapreduce.Match, comlib.mapreduce.Child): # 定义派生类
      def __init__(self, v, sub=[]):    # 定义初始化函数
          super().__init__(pred=Match.NONE, pre=Match.NONE) # **注意**：必须派生必须关闭原类定义的函数行为
          self.v = v
          self.subs = sub

      def sub(self, *datum): return self.subs # 子迭代器获取函数
      def match(self,*datum, stack=[]): return datum[0].v % 2 == 0 # 定义Match行为
      def pre(self, *datum, stack=[]): return datum[0].v + 100 # 定义pre行为

```
然后实例化该类，并由Qmar进行遍历。
```python
class TestQMar:
    def test_common_qmar(self):
        node = MyQMar(0, [MyQMar(i) for i in range(1,5)])
        r = [x for x in Qmar(node).all()]
        assert r == [100,102,104]
```
