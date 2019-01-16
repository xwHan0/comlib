import re
from comlib.iterators import Index,IndexSub,Counter

######################################################
# 定义常用的子节点关系类

#### 定义直接透传关系
class ChildBypass:
    def sub(self,*node):
        return node[0]


class ChildFunction:
    def __init__(self,func):
        self.func = func
        
    def sub(self,*node):
        return self.func(*node)


class ChildNone:
    def sub(self,*node):
        return []

        
class ChildAttr:
    def __init__(self, attr):
        self.attr = attr
    
    def sub(self,*node):
        return getattr(node[0], self.attr)
        

class ChildSub:
    def sub(self,*node):
        return node[0].sub(*node)


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
    'ChildSub',
    'ChildAttr',
    'ChildNone',
    'ChildFunction',
    'ChildBypass',
    'append_children_relationship',
]
    


 

