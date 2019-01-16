import re

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
    def sub(*node):
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

__all__ = [
    'DEFAULT_CHILDREN_RELATIONSHIP',
    'TYPIC_CHILDREN_RELATIONSHIP',
    'ChildSub',
    'ChildAttr',
    'ChildNone',
    'ChildFunction',
    'ChildBypass',
]
    


 

