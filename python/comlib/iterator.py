import re
        
PATT_SELECT = re.compile(r'(.*)(/[pP]+)?')
PATT_ATTR = re.compile(r'{(\w+)}')
PATT_PRED = re.compile(r'(\w*)(\[(.*)\])?(/[oOcCsS]+)?')  # 单条件匹配模板


def iterator( node, sSelect='', gnxt=None, pred=None, count=-1 ):
    """ Get an iterator from data node.

# Introduce
  按序筛选并打平。
  Filter by designed order and flatten into dimension 1-D.

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

# Feature
* Support custom sub-pointer via parameter gnxt
  -- Support 3 types for gnxt
    *** None: Array-like data structure
    *** {String}: Link-list data structure
    *** {(node,idx)=>sub}: Custom function
  -- Support Array-like automatic get sub
    *** ***Note:*** Function gnxt NOT support

* Support JQuery-like search Syntax String via parameter 'sSelect'
  -- SearchString ::= SearchPattern, .../glb_flags
    *** SearchPattern ::= [obj][pred][flags]
  -- Support many flags in searchPattern
    *** The iterate process when object match fail
      ---- Default is continue next iterate
      ---- 'o': Continue next iterate except the sub node of current node
      ---- 'O': Break the iterate
    *** The iterate process when pred match fail
      ---- Default is continue next iterate
      ---- 'c': Continue next iterate except the sub node of current node
      ---- 'C': Break the iterate
    *** The iterate process when match success
      ---- Default is continue next iterate
      ---- 's': Continue next iterate except the sub node of current node
      ---- 'S': Break the iterate
    
* Support matching pred function via parameter 'pred'
  -- The format of pred is: (node,idx,count) => Boolean

* Support match number
  -- Support max match number via parameter 'count'. "0" represent unlimited(default)
  -- Support current match counter in Condition Matching String via identity '{cnt}'
  
  
    """
    class Config:
    
        def __init__(self, gnxt=0, flags='', pred=None):
            
            self.gnxt = gnxt
            self.pred = pred

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
    
        
        def __init__(self, cls_name = '', pred = '', flags = ''):
            self.cls_name = cls_name
            self.pred = pred.replace('{idx}', 'idx').replace('{self}', 'node').replace('{cnt}', 'count')
            self.pred = PATT_ATTR.sub( 'getattr(node,"\g<1>")', self.pred, count=0 )
            
            # 无论匹配成功与否，默认总是继续其余匹配
            self.obj_fail_rst, self.pred_fail_rst, self.match_succ_rst = (-1,-1,1)

            for f in flags: # 
                if f == 'o': self.obj_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
                elif f == 'O': self.obj_fail_rst = -3 # 匹配失败后，终止其余匹配
                elif f == 'c': self.pred_fail_rst = -2 # 匹配失败后，跳过该节点的子节点
                elif f == 'C': self.pred_fail_rst = -3 # 匹配失败后，终止其余匹配
                elif f == 's': self.match_succ_rst = 2  # 匹配成功后，跳过当前节点的子节点
                elif f == 'S': self.match_succ_rst = 3  # 匹配成功后，终止其余匹配

        def match( self, node, idx, count, cfg ):
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
                    
            if hasattr(cfg.pred, '__call_:'):
                if not cfg.pred(node, idx, count):
                    return self.pred_fail_rst
                    
            return self.match_succ_rst
    
    def parse(sSelect=''):
        preds = []
        if sSelect!= '':
            for cond in sSelect.split(','):
                (o, _, p, pf) = PATT_PRED.match(cond).groups('')
                preds.append( Pred(o, p, pf[1:]) )
        return preds

    def __iter( node, idx, count, preds, cfg ):
        
        # 过滤判断
        l = len(preds)
        if l == 0: succ = 1
        else:
            succ = preds[0].match( node, idx, count, cfg )
            if l > 1 and succ > 0: preds = preds[1:]


        if count == 0:
            raise StopIterator()
        elif succ == 1:  # 匹配成功，迭代子对象
            if isinstance(node, list) or isinstance(node, tuple): # 数组
                for i,s in enumerate( node ):
                    yield from __iter( s, idx + [i], count, preds, cfg )
            elif cfg.gtyp == 1: # 指针
                if cfg.proc_typ == 0: 
                    count -= 1
                    yield (idx, node)
                try:
                    sub = getattr( node, cfg.gnxt )
                except AttributeError:
                    pass
                else:
                    for i,s in enumerate( sub ):
                        yield from __iter( s, idx + [i], count, preds, cfg )
                if cfg.proc_typ == 1: 
                    count -= 1
                    yield (idx, node)
            elif cfg.gtyp == 2: #函数
                if cfg.proc_typ == 0: 
                    count -= 1
                    yield (idx, node)
                sub = gnxt( node, idx )
                if hasattr( sub, '__iter__' ):
                    for i,s in enumerate( sub ):
                        yield from __iter( s, idx + [i], count, preds, cfg )
                if cfg.proc_typ == 1: 
                    count -= 1
                    yield (idx, node)
            elif cfg.gtyp == 0: # 数组的最终元素不满足第一条
                count -= 1
                yield (idx, node)

        if succ == -1:  # 匹配不成功，迭代子对象
            if isinstance(node, list) or isinstance(node, tuple): # 数组
                for i,s in enumerate( node ):
                    yield from __iter( s, idx + [i], count, preds, cfg )
            elif cfg.gtyp == 1: # 指针
                try:
                    sub = getattr( node, cfg.gnxt )
                except AttributeError:
                    pass
                else:
                    for i,s in enumerate( sub ):
                        yield from __iter( s, idx + [i], count, preds, cfg )
            else: #函数
                sub = gnxt( node, idx )
                if hasattr( sub, '__iter__' ):
                    for i,s in enumerate( sub ):
                        yield from __iter( s, idx + [i], count, preds, cfg )
                

        elif succ == 2: # 匹配成功，不迭代子对象
            if cfg.proc_typ == 0: 
                count -= 1
                yield (idx,node)
            elif cfg.proc_typ == 1: 
                count -= 1
                yield (idx, node)

        elif succ == 3: # 匹配成功，终止迭代
            if cfg.proc_typ == 0: 
                count -= 1
                yield (idx,node)
            elif cfg.proc_typ == 1:
                count -= 1
                yield (idx, node)
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()
        
            

    # 匹配搜索条件
    p = PATT_SELECT.match(sSelect)
    filtes, flags = ('', '')
    if p: (filtes, flags) = p.groups('')
    
    return __iter( node, [], count, parse(filtes), Config(gnxt, flags, pred) )



