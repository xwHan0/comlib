
# def reduce_deep(node, init = None, sub_get = None, pre_proc = None, post_proc = None, post = None, idx = [] ):
#     """深度优先迭代。
    
#     Arguments:
#       node {Object} -- 树节点
#       init {Object: None} -- 初始化值
#       sub_get {Function} -- 获取子节点函数
#       pre_proc {Function: None} -- 迭代子节点前的父节点处理
#       post_proc {Function: None} -- 迭代子节点后的父节点处理
#       post {Function: None} -- 收尾处理
#       idx {List<int>: []} -- 节点序号
#     """

#     def reduce_iter_pre(node, sub_get, init, proc, idx):
#         # 处理当前节点
#         rst = proc(node, idx, init)
#         # 迭代子节点。叶子节点node.sub为空
#         for i, sub in sub_get(node):
#             rst = reduce_iter_pre( sub, idx.append(i), rst )
#         return rst
        
#     def reduce_iter_post(node, sub_get, init, proc, idx):
#         rst = init
#         # 迭代子节点。叶子节点node.sub为空
#         for i, sub in sub_get(node):
#             rst = reduce_iter_post( sub, idx.append(i), rst )
#         # 处理当前节点
#         rst = proc(node, idx, rst)
#         # 返回
#         return rst
    
#     # 初始值处理
#     if init == None:
#         if pre_post: init = pre_post(node, idx)
#         elif:
#         else: throw Exception('')
#     elif hashattr(init, '__call__'):
#         init = init(node)
        
#     # 迭代处理
#     if pre_proc:
#         rst = reduce_iter_post(node, sub_get, init, post_proc, idx)
#     elif post_proc:
#         rst = reduce_iter_pre(node, sub_get, init, post_proc, idx)
#     else:
#         rst = init
    
#     # 后处理
#     if post: rst = post(rst)
        
#     return rst
        
from collections import Iterable

def iterator( node, sSelect='', gnxt=None ):

    class config:
        def __init__(self):
            self.gtyp = 0
            self.presub = True
            self.postsub = False
    	

    def __iter( node, idx, gnxt, cfg ):
        
        # 获取吓一跳位置
        if cfg.gtyp == 0: # 数组
        	sub = node
        elif cfg.gtyp == 1: # 指针
        	sub = node.__class__.__dict__[gnxt]
        	if presub: yield node
        else: # 函数
        	sub = gnxt( node, idx )
        	if sub!=node and cfg.presub: yield node
      
        # 迭代
        if sub and isinstance( sub, Iterable ):
            for i,s in enumerate( sub ):
                yield from __iter(s, idx + [i], gnxt, cfg)
            if cfg.postsub and sub!=node: yield node
        else:
            yield (idx, node)
            

    # 创建配置对象
    cfg = config()
    
    if gnxt == None:
        cfg.gtyp = 0  # 数组
    elif isinstance( gnxt, str ):
        cfg.gtyp = 1  # 链表
    elif hasattr( gnxt, '__call__' ):
        cfg.gtyp = 2  # 函数
    else:
        return
    
    
    return __iter( node, [], cfg )



a = [[1,2], [3,4]]

for x in iterator(a):
    print(x)