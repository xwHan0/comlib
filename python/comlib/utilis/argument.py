
class SeriesArgument: pass
class __SeriesElement__(SeriesArgument): pass
class __SeriesIter___(SeriesArgument): pass
class __SeriesAuto___(SeriesArgument): pass
class __SeriesMix___(SeriesArgument): pass

SeriesElement = __SeriesElement__()
SeriesIter = __SeriesIter__()
SeriesAuto = __SeriesAuto__()
SeriesMix = __SeriesMix__()

class SeriesArgumentProc1:
    def __init__(self, *cs):
        self.cs = cs

    def __iter__(self):
        return self

    def __next__(self):
        if isinstance(self.cs[0], SeriesArgument):
            pass
        else:
            pass
