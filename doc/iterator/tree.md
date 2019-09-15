
# Introduce
树结构迭代器。

# Usage
```python
    ite = comlib.iterator.tree(*trees, dir="down")
```

## Parameter
- trees: 树结构列表
- dir: 遍历方向
  - 支持两种格式
    - string: 遍历方向字符串。
    - list: 遍历方向字符串列表。
  - 遍历方向字符串
    - "up": 深度优先，从子节点遍历到父节点
    - "down": 深度优先，从父节点遍历到子节点
    - "updown": 深度优先，先从子节点收拢到父节点，然后再从父节点遍历到子节点
    - "downup": 深度优先，先从父节点遍历到子节点，然后再从子节点回归到父节点
    - "wide": 广度优先

## Return
tree函数返回一个树结构迭代器。该迭代器的'next'函数返回一个<span id='rtnobj'>包含如下成员的对象</span>：
- <span id='rtnvalue'>value</span>: 当前迭代元素列表(或者元组)
- <span id='rtnstatus'>status</span>: 当前迭代状态。包含
  - PRE(0): 从父元素深入到当前元素时
  - POST(1): 从子元素返回当前元素时
  - DONE(2): 遍历完成时
- stack: 当前迭代堆栈
  - 栈顶元素为当前元素节点信息
  - 第二个元素为当前元素的父节点信息
  - 底元素为根元素节点信息
  - 每个节点信息为一个包含如下成员的对象
    - value: 参见[value](#rtnvalue)
    - sta: 参见[status](#rtnstatus)
- done: 迭代结束标识
  - True: 当前迭代已经超出迭代范围，迭代结束
  - False: 正常迭代元素

# Method

**mtree**

忽略第一个元素后，返回迭代器的当前值。

# Language Special
不同计算机语言的实现版本略有不同
|Language   |iter                                                   |next    |
|----       |----                                                   |----    |
|Javascript |实现了[Symbol.iterator]可迭代协议                       |实现了迭代器的.next方法，其返回结果[参考这里](#rtnobj)|
|python     |实现了.__iter__迭代协议                                 |实现了.__next__方法。迭代结束抛出StopException异常|

## javascript
**for**
```javascript
import comlib from 'comlib'

arr = [1,[2,3],4,5,[6,7]]
for( a of comlib.iterator.tree(arr) ){
    console.log(a[0])
}
```

**next**
```javascript
import comlib from 'comlib'

arr = [1,[2,3],4,5,[6,7]]
ite = comlib.iterator.tree(arr)[...]
while( (nxt=ite.next()).done == false ){
    console.log(nxt.value)
}
```

## python
**for**
```python
from comlib.iterator import tree

arr = [1,[2,3],4,5,[6,7]]
for a in tree(arr):
    print(a.value[0])
```

**next**
```python
from comlib.iterator import tree

arr = [1,[2,3],4,5,[6,7]]
ite = iter(tree(arr))

while:
    try:
        nxt = next(ite)
        print(nxt.value[0])
    catch StopException:
        ...
```