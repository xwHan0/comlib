![Qmar](qmar.svg)

Qmar使用next和sub两个指针来组织数据树结构;
- Qmar首先遍历处理当前节点
- 然后，使用child函数获取子节点迭代器
- 再依次遍历子节点

子节点遍历遵循python的标准遍历方法。获取子节点迭代器需要遵循Qmar的Child获取规则。

# Child
Qmar获取数据子节点迭代器的方法为：
1. 在children\_relationship映射表中查找是否注册了该数据类的child获取函数。
  - 若注册，则使用注册的获取函数获取子节点迭代器
  - 否则，按照下述方法获取
2. 若用户注册了默认Child获取方法，则使用该方法获取子节点迭代器。否则按下述方法获取
3. 若数据为comlib.mapreduce.Child的子类，则按照子之类的sub函数获取
4. 若定义了__iter__，则按照__iter__获取

# 子迭代器注册表

```python
   >>>  rst = [x for x in Qmar([1,2,3,4,5]).skip().all()]
```


