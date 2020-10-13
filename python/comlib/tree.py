
from comlib.utilis.argument import series_argument_proc

#### 异常
class ErrorReturnType(Exception): pass


class NodeMapReturn:
    def __init__(self, *nodes):
        self.nodes = nodes



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

    def iter(self, prev, post=None, data={}, lvls=[]):
        """遍历整个树
        Arguments:
        * prev: {(node,lvls,data)=>object} ---- Prev过程处理函数
        * post: {(node,lvls,data)=>object | None} ---- Post过程处理函数
            * None: 不进行Post处理，Prev处理结果作为最终结果
            * Function: 参考`prev`
        * data: {dict} ---- 传递参数
        * lvls: {list} ---- 位置层次序号
        """

        # prev处理
        data = prev( self, lvls=lvls, data=data )

        # 子节点处理
        for i,child in enumerate(self.childNodes):
            data = child.iter( prev, post, data, lvls+[i] )
            
        # post处理
        if post:
            data = post( self, lvls=lvls, data=data )
        
        return data

    def map(self, prev, post=None, udata={}, lvls=[]):
        """遍历整个树

        Arguments:
        * prev: {(node,udata,lvls)=>udata, List<Node>} ---- Prev过程处理函数
        * post: {(node,nnode,lvls)=>List<Node>} ---- Post过程处理函数
            * None: 不进行Post处理，Prev处理结果作为最终结果
            * Function: 参考`prev`
        * udata: {dict} ---- 自顶向下传递的参数
        * lvls: {list} ---- 位置层次序号

        Return:
        * udata: {dict} ---- 自顶向下传递的参数
        * nodes: {List<Node>} ---- 新的节点
        """

        # prev处理
        udata, new_nodes = prev( self, udata=udata, lvls=lvls )

        # 子节点处理
        new_children = []
        for i,child in enumerate(self.childNodes):
            udata, child_nodes = child.map( prev, post, udata=udata, lvls=lvls+[i] )
            for c in child_nodes:
                new_children.append( c )
            
        # 追加子节点
        for c in new_nodes:
            c.childNodes = new_children

        # post处理
        if post:
            new_nodes = post( self, nnode=new_nodes, lvls=lvls )

        return udata, new_nodes
                


