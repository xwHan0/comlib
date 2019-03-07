
class Child:
    """获取子节点迭代器。

    默认使用Python规定的iter获取子节点迭代器
    """
    pass



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