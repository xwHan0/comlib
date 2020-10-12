
from comlib.utilis.argument import series_argument_proc

class Node:
    """树节点定义"""
    def __init__(self, **props):
        self.props = props
        self.childNodes = []
        self.parents = []

    def getAttribute(self, key, default=None): return self.props.get([key], default)
    def setAttribute(self, key, value): self.props[key] = value

    def getChild(self, idx): return self.childNodes[idx]
    def setChild(self, idx, child): self.childNodes[idx] = child

    def __getitem__(self, key):
        if isinstance( key, int ):
            return self.childNodes[key]
        else:
            return self.props[key]

    def __setitem__(self, key, value):
        if isinstance( key, int ):
            self.childNodes[key] = value
        else:
            self.props[key] = value

    def append_child( self, *children ):
        children = series_argument_proc( children )
        for child in children:
            self.childNodes.append( child )
        return self

    def append_parent( self, *parents ):
        parents = series_argument_proc( parents )
        for parent in parents:
            self.parents.append( parent )
        return self

    def __iter__(self):
        return iter( self.childNodes )

    def map(self, prev, post=None, pprev=None, parent=None, lvls=[]):
        """遍历整个树
        Arguments:
        * prev: {(node,lvls,pprev)=>object} ---- Prev过程处理函数
        * post: {(node,lvls,prev_rst,children_rst)=>object | None} ---- Post过程处理函数
            * None: 不进行Post处理，Prev处理结果作为最终结果
            * Function: 参考`prev`
        * pprev: 父节点Prev过程处理结果
        * parent: 父节点
        * lvls: {list} ---- 位置层次序号
        """

        # prev处理
        rst = prev( self, lvls=lvls, pprev=pprev )

        # 子节点处理
        children_return = [child.map( prev, post, rst, self, lvls+[i] ) for i,child in enumerate(self.childNodes)]
            
        # post处理
        if post:
            rst = post( self, lvls=lvls, prev_rst=rst, children_rst=children_return )
        
        return rst
                


