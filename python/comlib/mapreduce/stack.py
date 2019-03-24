

class NodeInfo:
    """迭代栈节点信息。
    - match: 当前节点起始匹配match(父节点.next)指向的match
    - sta: 当前节点的遍历状态:PRE|POST
    - matched: 当前节点匹配成功的match(匹配成功，返回有效action的match)
    - action: 当前节点匹配成功的match对应的action
    - datum: 当前节点对应的树节点数据
    - children: 当前节点子节点迭代器 
    """
    def __init__(self, datum=[],  sta=1, pred_idx=0 ):
        self.datum, self.sta, self.pred_idx = datum, sta, pred_idx
        # self.children  define when used
        # self.succ = False  define when used
        # self.proc_idx = 0    define when used
        # self.action = 0    define when used
        
        
        
        
