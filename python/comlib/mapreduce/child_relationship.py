import re
from comlib.iterators import Index,IndexSub,Counter

######################################################
# 定义常用的子节点关系类

class ChildRelation:
    """子迭代器(Children-Relationship)

    子节点迭代器为一个接口协议，告知Query如何获取当前节点的子节点迭代器。

    Query预定义的子节点迭代器封装有(具体参见相关类帮助)：
    * ChildNone
    * ChildBypass
    * ChildFunction
    * ChildAttr
    * ChildSub

    Query定义了部分常用类型的迭代关系：
    * list and tuple: ChildBypass
    * Index, Counter, IndexSub: ChildSub

    此外，Query使用ChildNone对没有定义的类型进行处理。

    """
    def sub(self, *node): 
        """子节点获取协议函数：获取node[0]节点的子节点迭代器。"""
        return []


#### 定义直接透传关系
class ChildBypass(ChildRelation):
    """节点自身就是子节点迭代器。sub函数返回节点自身。"""
    def sub(self,*node): return node[0]


class ChildFunction(ChildRelation):
    """使用func(*node)返回子节点迭代器。"""
    def __init__(self,func): self.func = func
    def sub(self,*node): return self.func(*node)


class ChildNone(ChildRelation):
    """返回空列表作为子节点迭代器（无子节点）"""
    def sub(self,*node): return []

        
class ChildAttr(ChildRelation):
    """使用node[0].attr作为子节点迭代器。"""
    def __init__(self, attr): self.attr = attr
    def sub(self,*node): return getattr(node[0], self.attr)
        

class ChildSub(ChildRelation):
    """使用node[0].sub(*node)作为子节点迭代器。"""
    def sub(self,*node): return node[0].sub(*node)


# 定义常见的数据类型children_relationship映射表
TYPIC_CHILDREN_RELATIONSHIP = {
    list : ChildBypass(),       # 列表的子元素集合就是列表本身
    tuple: ChildBypass(),
    Index: ChildSub(),   # iterator库包含的子项
    IndexSub: ChildSub(),
    Counter: ChildSub(),
}
DEFAULT_CHILDREN_RELATIONSHIP = ChildNone()

import types

def append_children_relationship(dest, children):
    """Append new children relationship 'children' to this iterator object."""
    if isinstance(children,str):
        dest['*'] = ChildAttr(children)
    elif isinstance(children, types.FunctionType):
        dest['*'] = ChildFunction(children)
    elif isinstance(children,dict):
        for k,v in children.items():
            if isinstance(v, str):  # 字符串：查询属性
                dest[k] = ChildAttr(v)
            else:
                dest[k] = v
    return dest


__all__ = [
    'DEFAULT_CHILDREN_RELATIONSHIP',
    'TYPIC_CHILDREN_RELATIONSHIP',
    'ChildRelation',
    'ChildSub',
    'ChildAttr',
    'ChildNone',
    'ChildFunction',
    'ChildBypass',
    'append_children_relationship',
]
    


 

