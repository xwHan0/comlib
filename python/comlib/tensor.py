import re

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
        


def iterator( node, sSelect='', gnxt=None ):
    “““ Get an iterator from data node.
    
    Parameter "gnxt" indicates the link method to sub data. There are below style:
    - None(Default): The "node" is iterable data, like array. The sub data can got by iterating the node data
    - {String}: An attribute name of node indicates the sub data
    - {Function}: A function return sub data. The format of function is "(node, idx) => sub" 
    
    Parameter "sSelect" is a string who illustrates one filter condition when iterate.
    The sSelect is define:
    sSelect ::= (<filtes>.*)(/)?(<flags>.*)
    filtes ::= Filter content
    flags ::= Filter options ::= (p)(p)
        - p: How to process list node. Default is pre-sub-node process. If there is only ONE ‘p‘ flag, 
             it is post-sub-node process. When there are TWO 'p' flags, both pre- and post- will be processed.  
  
    ”””
    class Config:
    
        patt = re.compile(r'(p)(p)')
    
        def __init__(self, gnxt=0):
            self.gtyp = 0
            self.presub = True
            self.postsub = False
            self.gnxt = gnxt
            
            # 对吓一跳方式分类
            if gnxt == None: self.gtyp = 0  # 数组
            elif isinstance( gnxt, str ): self.gtyp = 1  # 链表
            elif hasattr( gnxt, '__call__' ): self.gtyp = 2  # 函数
            
            
        def parse(self, flags):
            p = Config.patt.match(flags)
            if p:
                (post, pre) = p.groups(None)
                if post and pre:
                    self.presub = True
                    self.postsub = True
                elif post:
                    self.presub = False
                    self.postsub = True
        
    
    class Pred:
    
        patt0 = re.compile(r'(.*)(/.*)?')
        patt1 = re.compile(r'(.+)\s*')
        patt2 = re.compile(r'(\w*)(\[(.*)\])?')
         
        def __init__(self, cls_name = ''):
            self.cls_name = cls_name
    
        def parse(sSelect=''):
            preds = []
            if sSelect != None:
                conds = Pred.patt1.findall(sSelect)
                for cond in conds:
                    (obj, _, condition) = Pred.patt2.match(cond).groups(None)
                    preds.append( Pred(cls_name=obj) )
            return preds
    
        def match( self, node, idx ):
            if self.cls_name != '':
                if node.__class__.__name__ != self.cls_name:
                    return False
            return True

    def __iter( node, idx, preds, cfg ):
        
        # 过滤判断
        l = len(preds)
        if l == 0: succ = True
        elif l == 1: succ = preds[0].match( node, idx )
        elif preds[0].match( node, idx ):
            preds = preds[1:]
            succ = False
            
   
        # 获取吓一跳位置
        if cfg.gtyp == 0: # 数组
            sub = node
        elif cfg.gtyp == 1: # 指针
            sub = getattr( node, cfg.gnxt )
            # 子项前处理
            if cfg.presub and succ: yield (idx, node)
        else: # 函数
            sub = gnxt( node, idx )
            # 子项前处理
            if sub!=node and cfg.presub and succ: yield (idx, node)
      
        # 迭代
        if hasattr( sub, '__iter__' ):
            for i,s in enumerate( sub ):
                yield from __iter(s, idx + [i], preds, cfg)
            if cfg.postsub and sub!=node and succ: yield (idx, node)
        elif succ:
            yield (idx, node)
            

    # 创建配置对象
    cfg = Config(gnxt=gnxt)
    
    # 匹配搜索条件
    p = Pred.patt0.match(sSelect)
    if p:
        (filtes, flags) = p.groups(None)
        cfg.parse( flags )
        preds = Pred.parse(filtes)
    
    return __iter( node, [], preds, cfg )



