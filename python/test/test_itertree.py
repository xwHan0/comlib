import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib.mapreduce import iterTree


class TestBasic:
    def test_1d_array(self):
        """简单数组测试"""
        a = [10,20,30]
        ite = iterTree(a)
        r = [n for n in ite]
        assert r == [[10,20,30],10,10,20,20,30,30,[10,20,30]]
