import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib import iterator, Index, interpose

class node:
    def __init__(self, v, sub=[]):
        self.sub = sub
        self.val = v



class TestIterator:
    def test_interpos(self):
        a = [10,20,30,40]
        r = [x for x in iterpose(a,'>')]
        assert r == [10,'>',20,'>',30,'>',40]

