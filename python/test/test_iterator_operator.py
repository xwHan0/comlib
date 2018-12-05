import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib import deq, interpose


class TestInterpose:
    def test_interpose(self):
        a = [10,20,30,40]
        r = [x for x in interpose(a,'>')]
        assert r == [10,'>',20,'>',30,'>',40]

class TestDeq:
    def test_deq(self):
        a = [10,20,30,40,50,60]
        r = deq(a,3)
        assert r == [10,20,30]

