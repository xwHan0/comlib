


class Proc:
        
    def pre(self,  *datum, node=None):
        if len(datum) == 1:
            return datum[0]
        else:
            return datum
            
    def post(self, init, *datum, node=None):
        if len(datum) == 1:
            return datum[0]
        else:
            return datum
        
        