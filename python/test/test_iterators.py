import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib import iterator, Counter


class TestCounter:
    def test_counter(self):
        a = [10,20,30,40]
        r = [(c,x) for x,c in iterator(a).assist(Counter())]
        assert r == [(0,10),(1,20),(2,30),(3,40)]


