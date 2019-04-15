![Qmar](qmar.svg)

Qmar支持2种形式的结果返回：
- 迭代器形式：把Qmar实例作为一个迭代器使用。
- Reduce形式：迭代完成后返回整体的运算结果。

# 迭代器形式返回
Qmar自身支持__iter__和__next__迭代器协议，可以作为迭代器来使用。
例如：
```python
   >>>  rst = [x for x in Qmar([1,2,3,4,5]).skip().all()]
```

# Reduce形式返回

Qmar没有提供显式的支持。Qmar提供了一些继承自CommonIterator的特殊的遍历器(Iterator)来实现结果的返回。其工作原理为：
1. 用户实例化一个Result对象，并作为输入数据datum传递给Qmar
  - 一般情况下Result作为datum的最后一个数据
2. Qmar把Result对象作为用户数据进行迭代
3. 用户在pre或者post中赋值运算结果到Result对象中
4. Qmar通过result函数返回结果


```python
   def func(*datun):
       datum[1].rst += datum[0]
       return None

   rst = Qmar([1,2,3,4,5], Result(rst=0) \
             .skip() \
             .match(pre=func) \
	     .result()
```

当前Qmar提供如下类型的Result：
- Result: 普通的结果返回类。继承自CommonIterator。其sub和next都指向自己。所以Qmar迭代过程中每个迭代节点的Result实例都指向相同一个实例。
- ResultTree: 树状结果返回类。继承自CommonIterator。在Qmar迭代时，会随着迭代而自动构造一个和源数据一样的树结构。每个迭代节点都是一个新的、独立的ResultTree实例，并且这些实例安装树结构组织起来。
