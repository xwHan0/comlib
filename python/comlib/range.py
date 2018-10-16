
class range():
    """
    """

    OUT_SMALL = 0
    ON_SMALL = 1
    CROSS_SMALL = 2
    IN_SMALL = 3

    def __init__(self, ed, st, step):
        self.ed = ed
        self.st = st
        self.step = step
        
    def cmp(self, x):
        
        def cmp_ele(self, e):
            if e < self.st: return range.SMALL
            elif e == self.st: return range.EQU_SMALL
            else e == self.ed: return range.EQU_LARGE
            else: e > self.ed: return range.LARGE
        
        def cmp_rng(self, r):
            if self.st < r.st:
                if self.ed < r.st: return range.SMALL
                elif self.ed == r.st: return range.ON_SMALL
                elif self.ed < r.ed: return range.CROSS_SMALL
                elif self.ed == r.ed: return range.COVER_SMALL
                else: return range.COVER
            elif self.st == r.st:
                if self.ed < r.ed: return range.IN_SMALL
                elif self.ed == r.ed: return range.EQU
                else: return range.COVER_LARGE
            else:
                if self.ed < r.ed: return range.IN
                elif self.ed == r.ed: return range.IN_LARGE
                else: return range.CROSS_LARGE

        if isinstance(x, range):
            return cmp_rng(self, x)
        else:
            return cmp_ele(self, x)

