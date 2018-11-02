import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) )

from comlib.tensor import iterator

class TestIterator:
    def test_1d_array(self):
        a = [10,20,30,40]
        r = [x for x in iterator(a)]
        assert r == [([0], 10),([1], 20), ([2], 30), ([3], 40)]

    def test_3d_array(self):
        a = [10, [20, 30], [40, [[50,60], 70, 80], 90]]
        r = [x for x in iterator(a)]
        assert r == [([0], 10), ([1,0], 20), ([1,1], 30), ([2,0], 40), ([2,1,0,0], 50), 
            ([2,1,0,1], 60), ([2,1,1], 70), ([2,1,2], 80), ([2,2], 90)]

    def test_2d_list(self):
        class node:
            def __init__(self, v):
                self.sub = []
                self.val = v
            
        n0 = node(100)
        n1 = node(1000)
        n2 = node(2000)
        n0.sub = [n1, n2]
        r = [x[1].val for x in iterator(n0, gnxt='sub')]
        assert r == [100, 1000, 2000]

    def test_hybrid(self):
        class node:
            def __init__(self, v):
                self.sub = []
                self.val = v

        def gnxt(node, idx):
            if len(idx) == 1:
                return node.sub
            else:
                return node

        n0 = node(100)
        n0.sub = [100,200,300]
        n1 = node(200)
        n1.sub = [1000,2000,3000]
        a = [n0, n1]
        r = [x for x in iterator(a, gnxt=gnxt ) if isinstance(x[1], int)]
        assert r == [([0,0], 100), ([0,1], 200), ([0,2], 300), ([1,0], 1000), ([1,1], 2000), ([1,2], 3000)]

    def test_select_object(self):
        class node:
            def __init__(self, v):
                self.sub = []
                self.val = v

        def gnxt(node, idx):
            if len(idx) == 1:
                return node.sub
            else:
                return node

        n0 = node(100)
        n0.sub = [100,200,300]
        n1 = node(200)
        n1.sub = [1000,2000,3000]
        a = [n0, n1]
        r = [x[1].val for x in iterator(a, gnxt=gnxt, sSelect='node' )]
        assert r == [100,200]
        
    def test_select_condition(self):
        class node:
            def __init__(self,v, sub = []):
                self.sub = sub
                self.val = v
                
        n1, n2 = (node(200), node(300))
        n0 = node(100, [n1, n2])
        r = [x[1].val for x in iterator(n0, gnxt='sub', sSelect='[not (len({idx})==1 and {val}==300)]')]
        assert r == [100,200]