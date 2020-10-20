

class XIterator:
    # def apply( self, action, *args, **kargs ):
    #     return action( *args, self, **kargs )
        
    # def map( self, action, *iters, **kargs ):
    #     return xmap( action, self, *iters, **kargs )

    # def reduce( self, action, *iters, init=None, **kargs ):
    #     return xreduce( action, self, *iters, init=init, **kargs )

    def flatten(self, level=1):
        return flatten( self, level=level )
        
    def to_list(self): return list(self)

    def __iter__(self): return self

    def __next__(self): return self
