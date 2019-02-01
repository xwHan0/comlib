    
PRE = 1
ITE = 2
POST = 3
DONE = 4

class NodeInfo:
    def __init__(self, datum=[], ites=[], sta=1, rst=None, pred_idx=0 ):
        self.datum = datum
        self.ites = ites
        self.sta = sta
        self.rst = rst
        self.idx = 0
        self.pred_idx = pred_idx
        self.succ = False
        self.is_post_yield = False
        
        
        