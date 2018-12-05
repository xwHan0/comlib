import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib import iterator, Counter


class TestCounter:
    def test_counter(self):
        a = [10,20,30,40]
        r = [(x,c) for x,c in iterator(a).assist(Counter())]
        assert r == [(1,10),(2,20),(3,30),(4,40)]


