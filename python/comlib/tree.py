
from comlib.utilis.argument import series_argument_proc

class Node:
    """树节点定义"""
    def __init__(self, **props):
        self.props = props
        self.childNodes = []
        self.parents = []

    def getAttribute(self, key, default=None): return self.props.get([key], default)
    def setAttribute(self, key, value): self.props[key] = value

    def getChild(self, idx): return self.childNodes[idx]
    def setChild(self, idx, child): self.childNodes[idx] = child

    def __getitem__(self, key):
        if isinstance( key, int ):
            return self.childNodes[key]
        else:
            return self.props[key]

    def __setitem__(self, key, value):
        if isinstance( key, int ):
            self.childNodes[key] = value
        else:
            self.props[key] = value

    def append_child( self, *children ):
        children = series_argument_proc( children )
        for child in children:
            self.childNodes.append( child )
        return self

    def append_parent( self, *parents ):
        parents = series_argument_proc( parents )
        for parent in parents:
            self.parents.append( parent )
        return self

    def __iter__(self):
        return iter( self.childNodes )

