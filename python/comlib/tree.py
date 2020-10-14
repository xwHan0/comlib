
from comlib.utilis.argument import series_argument_proc

#### 异常
class ErrorReturnType(Exception): pass




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

    def show(self, keys=[], recur=True, lvl=[] ):
        """
        以表格方式打印显示节点属性值

        Argument:
        * keys: {list} ---- 打印的属性关键字
        * recur: {bool} ---- 是否打印子节点

        Return：
        返回打印字符串
        """

        rst = ''

        # 打印表头
        if lvl == []:
            rst += '   lvl  |'
            for key in keys:
                rst += ' %8s |' % (key)
            rst += '\n'

        # 打印内容
        rst += '%8s|' % (str(lvl))
        for key in keys:
            rst += ' %8s |' % (self.props[key])
        rst += '\n'

        # 打印子节点
        if recur:
            for i, child in enumerate(self.childNodes):
                rst += child.show( keys=keys, recur=recur, lvl=lvl+[i] )

        return rst

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
        * prev: {(node,udata,lvls)=>udata, Node} ---- 父-子过程处理
        * post: {(node,udata,lvls)=>udata, List<Node>|Node} ---- 兄弟之间或者子-父
            * None: 不进行Post处理，Prev处理结果作为最终结果
            * Function: 参考`prev`
        * udata: {dict} ---- 自顶向下传递的参数
        * lvls: {list} ---- 位置层次序号

        Return:
        * udata: {dict} ---- 自顶向下传递的参数
        * nodes: {List<Node>} ---- 新的节点
        """

        def _map_( node, prev, post, udata, lvls ):

            # prev处理
            udata, new_node = prev( node, udata, lvls )

            # 子节点处理
            new_children = []
            for i,child in enumerate(node.childNodes):
                udata, childs = _map_( child, prev, post, udata, lvls+[i] )
                if isinstance(childs, list):
                    for c in childs:
                        new_children.append( c )
                else:
                    new_children.append(childs)
                
            # 追加子节点
            new_node.childNodes = new_children

            # post处理
            if post:
                udata, new_node = post( new_node, udata, lvls )

            return udata, new_node

        return _map_( self, prev, post, udata, lvls )[1]
                


