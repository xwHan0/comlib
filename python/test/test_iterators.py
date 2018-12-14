import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib import iterator, Counter, LinkList, interpose


class TestCounter:
    def test_counter(self):
        a = [10,20,30,40]
        r = [(c,x) for x,c in iterator(a).assist(Counter())]
        assert r == [(0,10),(1,20),(2,30),(3,40)]

    def test_linklist_of_none(self):
        r = [x for x in LinkList(None,'sub')]
        assert r == []
        
    def test_interpose_of_none(self):
        r = [x for x in interpose(None,'sub')]
        assert r == []

