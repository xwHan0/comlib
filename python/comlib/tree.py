
from comlib.utilis.argument import series_argument_proc

#### 异常
class ErrorReturnType(Exception): pass




class Node:
    """树节点定义"""
    def __init__(self, **props):
        self.props = props              # 节点属性字典
        self.childNodes = []            # 子节点列表
        self.parents = None             # 父节点列表
        self.brother = None             # 前述哥哥指针
        self.lvl = []                   # 层次位置信息

    def build(self, lvl=[]):
        """编译树节点，填充其它信息"""

        def _compile_( node, parent, brother, lvl ):

            ## 填充当前节点
            node.parent = parent    # 编译父节点
            node.brother = brother
            node.lvl = lvl

            ## 调度子节点
            brother = None
            for i, child in enumerate(node.childNodes):
                _compile_( child, node, brother, node.lvl+[i] )
                brother = child

        _compile_( self, None, None, lvl )

        return self


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

    def iter(self, 
        prev : '{(node,data,lvls)=>data} -- 从父节点遍历到当前节点(lvls[-1]==0)，或者从前一个兄弟节点遍历到当前节点(lvls[-1]>0)时调用', 
        post : '{(node,data,lvls)=>data} -- 子节点都处理完成，准备返回父节点时调用' =None,
        data={},
        lvls=[]
        ):
        """遍历整个树
        Arguments:
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

    def map(self, prev, post=None):
        """按深度遍历整个树，然后返回新的树Root节点

        Arguments:
        * prev: {(node)=>Node} -- 子节点迭代前回调函数。从父节点遍历到当前节点(lvls[-1]==0)，或者从前一个兄弟节点遍历到当前节点(lvls[-1]>0)时调用
            * node: {Node} -- 当前遍历节点
            * Return: 返回新节点
        * post: {(node)=>List<Node>|Node} -- 子节点迭代后回调函数。子节点都处理完成，准备返回父节点时调用
            * post=None: 不进行Post处理，Prev处理结果作为最终结果
            * node: {Node} -- 当前节点生成的新节点
            * Return: 返回新节点或者新节点列表

        Return:
        新树节点
        """

        def _map_( node, prev, post ):

            # prev处理
            new_node = prev( node )

            # 子节点处理
            new_children = []
            for child in node.childNodes:
                childs = _map_( child, prev, post  )
                if isinstance(childs, list):
                    for c in childs:
                        new_children.append( c )
                else:
                    new_children.append(childs)
                
            # 追加子节点
            new_node.childNodes = new_children

            # post处理
            if post:
                new_node = post( new_node )

            return new_node

        return _map_( self, prev, post )
                
