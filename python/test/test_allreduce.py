import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), './'))) )

print(sys.path)


from comlib import xmap, xrange,xapply,mapa,xreduce
import comlib

def add10(x): return x+10
def add20(x): return x+20
def add_2(a,b): return a + b
def add_4(a,b,c=100,d=1000): return a+b+c+d
def add_more(*v): return sum(v)

class Test_xmap:

    def test_basic(self):
        # 基本操作
        assert xmap(add10, [1,2,3,4]).to_list() == [11,12,13,14]
        assert mapa(add10, [1,2,3,4]) == [11,12,13,14]
        # 支持多迭代器输入
        assert xmap(add_2, [1,2,3,4],[10,20,30,40]).to_list() == [11,22,33,44]
        # 支持无限迭代器输入
        assert xmap(add_more, [1,2,3,4],[10,20,30,40],[100,200,300,400],[1000,2000,3000,4000]).to_list() == [1111,2222,3333,4444]

    def test_kargs(self):
        # 支持关键字参数
        assert xmap(add_4, [1,2,3,4],[10,20,30,40],c=200, d=2000).to_list() == [2211,2222,2233,2244]

    def test_multi_result(self):
        # 支持多结果返回
        assert xmap([add10, add20], [1,2,3,4]).to_list() == [[11,21],[12,22],[13,23],[14,24]]


class Test_xrange:
    def test_basic(self):
        assert xrange(10,17).to_list() == [10,11,12,13,14,15,16]


def max_2(a, b): return a if a > b else b

class Test_xreduce:
    def test_basic(self):
        assert xreduce(add_2, [1,2,3,4,5]) == 15
        assert xreduce( max_2, [1,2,3,4,5,4,3,2,1], init=4 ) == 5

    def test_multi_result(self):
        assert xreduce( [add_2, max_2], [1,5,3,2,4] ) == [15, 5]



class Test_xapply:
    def test_basic(self):
        # 基本操作
        assert xapply(xmap, add10, [1,2,3,4]).to_list() == [11,12,13,14]



class Test_mix:
    def test_map_map(self):
        assert xmap(mapa,add10, [[1,2,3],[10,20,30],[100,200,300]]).to_list() == [[11,12,13],[20,30,40],[110,210,310]]