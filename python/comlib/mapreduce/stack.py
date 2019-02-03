    
PRE = 1
ITE = 2
POST = 3
DONE = 4

class NodeInfo:
    def __init__(self, datum=[], ites=[], sta=1, pred_idx=0 ):
        self.datum = datum
        # self.ites = ites  define when used
        self.sta = sta
        # self.rst = rst
        # self.idx = 0
        self.pred_idx = pred_idx
        # self.succ = False  define when used
        #self.is_post_yield = False
        # self.proc_idx = 0    define when used
        
        
        
        