import re
from ast import literal_eval

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
        
PATT_SELECT = re.compile(r'(.*)(/[pP]+)?')
PATT_ATTR = re.compile(r'{(\w+)}')
PATT_PRED = re.compile(r'(\w*)(/[bcBC]+)?(\[(.*)\])?(/[bcBC]+)?')  # 单条件匹配模板


def iterator( node, sSelect='', gnxt=None ):
    """ Get an iterator from data node.
    
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
  
    """
    class Config:
    
        def __init__(self, gnxt=0, flags=''):
            
            self.gnxt = gnxt

            # 对吓一跳方式分类
            self.gtyp = 0

            if gnxt == None: self.gtyp = 0  # 数组
            elif isinstance( gnxt, str ): self.gtyp = 1  # 链表
            elif hasattr( gnxt, '__call__' ): self.gtyp = 2  # 函数
            
            self.proc_typ = 0   # 默认子项前返回

            for f in flags:
                if f == 'p': self.proc_typ = 1  # 子项后返回
                elif f == 'P': self.proc_typ = 2    # 不返回当前项

    
    class Pred:
    
        
        def __init__(self, cls_name = '', obj_flags = '', pred = '', pred_flags = ''):
            self.cls_name = cls_name
            self.pred = pred.replace('{idx}', 'idx').replace('{self}', 'node')
            self.pred = PATT_ATTR.sub( 'getattr(node,"\g<1>")', self.pred, count=0 )
            
            # 无论匹配成功与否，默认总是继续其余匹配
            self.obj_fail_rst, self.pred_fail_rst, self.match_succ_rst = (-1,-1,1)

            for f in obj_flags: # obj匹配
                if f == 'c': self.obj_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
                elif f == 'b': self.obj_fail_rst = -3 # 匹配失败后，终止其余匹配
                
            for f in pred_flags: # pred匹配
                if f == 'c': self.pred_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
                elif f == 'b': self.pred_fail_rst = -3 # 匹配失败后，终止其余匹配
                elif f == 'C': self.match_succ_rst = 2  # 匹配成功后，跳过当前节点的子节点
                elif f == 'B': self.match_succ_rst = 3  # 匹配成功后，终止其余匹配

        def match( self, node, idx ):
            # 对象匹配
            if self.cls_name != '' and self.cls_name!='*':
                if node.__class__.__name__ != self.cls_name:
                    return self.obj_fail_rst
            
            # 条件匹配
            if self.pred != '':
                try:
                    rst = eval(self.pred)
                    if rst == False: return self.pred_fail_rst
                    elif rst == True: return self.match_succ_rst
                    else: raise Exception('Invalid condion result. CMD<{0}>'.format(self.pred))
                except Exception:
                    raise Exception('Invalid condition statement. CONDITION<{0}>'.format(self.pred))
                    
            return self.match_succ_rst
    
    def parse(sSelect=''):
        preds = []
        if sSelect!= '':
            for cond in sSelect.split(','):
                (o, of, _, p, pf) = PATT_PRED.match(cond).groups('')
                preds.append( Pred(o, of, p, pf[1:]) )
        return preds

    def __iter( node, idx, preds, cfg ):
        
        # 过滤判断
        l = len(preds)
        if l == 0: succ = 1
        else:
            succ = preds[0].match( node, idx )
            if l > 1 and succ > 0: preds = preds[1:]


        if succ == 1:  # 匹配成功，迭代子对象
            if isinstance(node, list) or isinstance(node, tuple): # 数组
                for i,s in enumerate( node ):
                    yield from __iter( s, idx + [i], preds, cfg )
            elif cfg.gtyp == 1: # 指针
                if cfg.proc_typ == 0: yield (idx, node)
                try:
                    sub = getattr( node, cfg.gnxt )
                except AttributeError:
                    pass
                else:
                    for i,s in enumerate( sub ):
                        yield from __iter( s, idx + [i], preds, cfg )
                if cfg.proc_typ == 1: yield (idx, node)
            elif cfg.gtyp == 2: #函数
                if cfg.proc_typ == 0: yield (idx, node)
                sub = gnxt( node, idx )
                if hasattr( sub, '__iter__' ):
                    for i,s in enumerate( sub ):
                        yield from __iter( s, idx + [i], preds, cfg )
                if cfg.proc_typ == 1: yield (idx, node)
            elif cfg.gtyp == 0: # 数组的最终元素不满足第一条
                yield (idx, node)

        if succ == -1:  # 匹配不成功，迭代子对象
            if isinstance(node, list) or isinstance(node, tuple): # 数组
                for i,s in enumerate( node ):
                    yield from __iter( s, idx + [i], preds, cfg )
            elif cfg.gtyp == 1: # 指针
                try:
                    sub = getattr( node, cfg.gnxt )
                except AttributeError:
                    pass
                else:
                    for i,s in enumerate( sub ):
                        yield from __iter( s, idx + [i], preds, cfg )
            else: #函数
                sub = gnxt( node, idx )
                if hasattr( sub, '__iter__' ):
                    for i,s in enumerate( sub ):
                        yield from __iter( s, idx + [i], preds, cfg )
                

        elif succ == 2: # 匹配成功，不迭代子对象
            if cfg.proc_typ == 0: yield (idx,node)
            elif cfg.proc_typ == 1: yield (idx, node)

        elif succ == 3: # 匹配成功，终止迭代
            if cfg.proc_typ == 0: yield (idx,node)
            elif cfg.proc_typ == 1: yield (idx, node)
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()
        
            

    # 匹配搜索条件
    p = PATT_SELECT.match(sSelect)
    filtes, flags = ('', '')
    if p: (filtes, flags) = p.groups('')
    
    return __iter( node, [], parse(filtes), Config(gnxt, flags) )



