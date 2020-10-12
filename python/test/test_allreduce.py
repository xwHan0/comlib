import sys, os
sys.path.append( (os.path.abspath(os.path.join(os.path.dirname(__file__), './'))) )

print(sys.path)


# from comlib import xmap, xrange,xapply,mapa,xreduce,xflatten,find
# from comlib.allreduce import Action, parity
# from comlib.allreduce import conc, conj, comb,wapply
# import comlib
# import operator

# def add10(x): return x+10
# def add20(x): return x+20
# def add_2(a,b): return a + b
# def add_4(a,b,c=100,d=1000): return a+b+c+d
# def add_more(*v): return sum(v)

# class Test_xmap:

#     def test_basic(self):
#         # 基本操作
#         assert xmap(add10, [1,2,3,4]).to_list() == [11,12,13,14]

#     def test_mapa(self):
#         assert mapa(add10, [1,2,3,4]) == [11,12,13,14]
    
#     def test_2_iter(self):
#         # 支持多迭代器输入
#         assert xmap(add_2, [1,2,3,4],[10,20,30,40]).to_list() == [11,22,33,44]

#     def test_multi_iter(self):
#         # 支持无限迭代器输入
#         assert xmap(add_more, [1,2,3,4],[10,20,30,40],[100,200,300,400],[1000,2000,3000,4000]).to_list() == [1111,2222,3333,4444]

#     def test_kargs(self):
#         # 支持关键字参数
#         assert xmap(add_4, [1,2,3,4],[10,20,30,40],c=200, d=2000).to_list() == [2211,2222,2233,2244]

#     # def test_multi_result(self):
#     #     # 支持多结果返回
#     #     assert xmap([add10, add20], [1,2,3,4]).to_list() == [[11,21],[12,22],[13,23],[14,24]]

#     def test_ignore_iters(self):
#         """支持缺iters的偏函数返回"""
#         assert xmap( add10 )( [1,2,3,4] ).to_list() == [11,12,13,14]


# class Test_xrange:
#     def test_basic(self):
#         assert xrange(10,17).to_list() == [10,11,12,13,14,15,16]


# def max_2(a, b): return a if a > b else b

# class Test_xreduce:
#     def test_basic(self):
#         assert xreduce(add_2, [1,2,3,4,5]) == 15
#         assert xreduce( max_2, [1,2,3,4,5,4,3,2,1], init=4 ) == 5

#     def test_multi_result(self):
#         assert xreduce( [add_2, max_2], [1,5,3,2,4] ) == [15, 5]

#     def test_buildin_function(self):
#         assert xreduce( operator.add, [1,2,3,4,5] ) == 15

#     # def test_aggregate_function(self):
#     #     assert xreduce( sum, [1,2,3,4,5] ) == 15



# class Test_apply:
#     def test_basic(self):
#         # 基本操作
#         assert xapply((xmap, add10), [1,2,3,4]).to_list() == [11,12,13,14]

#     def test_3stage(self):
#         assert xapply((mapa, mapa,add10), [[1,2,3],[10,20,30],[100,200,300]]) == [[11,12,13],[20,30,40],[110,210,310]]

#     # def test_map_reduce(self):
#     #     assert wapply( sum, xmap, add10, *[1,2,3] ) == 36


# class Test_Action:
    
#     def test_kargs(self):
#         # 支持关键字参数
#         assert xmap(add_4, [1,2,3,4],[10,20,30,40],c=200, d=2000).to_list() == [2211,2222,2233,2244]

#     def test_Action(self):
#         """支持自定义Action"""
#         # assert mapa(Action(add_4,c=200, d=2000), [1,2,3,4],[10,20,30,40]) == [2211,2222,2233,2244]
#         assert mapa(parity(add_4,c=200, d=2000), [1,2,3,4],[10,20,30,40]) == [2211,2222,2233,2244]

#     def test_action_first(self):
#         """主动指明的Action参数会覆盖函数指定的kargs参数"""
#         assert mapa(parity(add_4, c=200, d=2000), [1,2,3,4],[10,20,30,40],c=2, d=3) == [2211,2222,2233,2244]
#         # assert mapa(Action(add_4, c=200, d=2000), [1,2,3,4],[10,20,30,40],c=2, d=3) == [2211,2222,2233,2244]


# class Test_XIterator:
#     def test_map_apply(self):
#         assert xmap(add10, [1,2,3,4]).apply( sum ) == 50


# class Test_flatten:
#     def test_basic(self):
#         assert xflatten([[1,2,3],[4,5,6]]).to_list() == [1,2,3,4,5,6]

#     def test_scalar_input(self):
#         assert xflatten(15).to_list() == [15]

#     def test_level_basic(self):
#         assert xflatten([[[1,2],[3,4]],[[5,6],[7,8]]], 2).to_list() == [1,2,3,4,5,6,7,8]

#     def test_level_more(self):
#         assert xflatten([[[1,2],[3,4]],[[5,6],[7,8]]], 1).to_list() == [[1,2],[3,4],[5,6],[7,8]]

#     def test_level_auto(self):
#         assert xflatten([[[1,2],[3,4]],[5,6,7,8]], 2).to_list() == [1,2,3,4,5,6,7,8]

#     def test_level_leaf(self):
#         assert xflatten([1,[2,[3,[4,[5,[6,7],8],[9,10]],[11]],[12]]],-1).to_list() == [1,2,3,4,5,6,7,8,9,10,11,12]


# class Test_Function:
#     def test_comb_basic(self):
#         # func = comb( mapa, Action(add10) )
#         func = comb( mapa, parity(add10) )
#         assert func( [1,2,3] ) == [11,12,13]

#     def test_conc_basic(self):
#         # 支持多结果返回
#         assert xmap(conc(add10, add20), [1,2,3,4]).to_list() == [[11,21],[12,22],[13,23],[14,24]]

#     def test_conc_basic2(self):
#         assert mapa( conj(add10, add20), [1,2,3,4] ) == [31,32,33,34]


# class Test_find:
#     def test_find_value_index(self):
#         assert find( 3, [1,2,3,4,5], xrange(), num=1, result_sel=1 ) == 2

#     def test_criteria(self):
#         assert find( lambda x: x>2, [1,2,3,4,5], num=1 ) == 3

#     def test_more(self):
#         assert find( lambda x: x>2, [1,2,3,4,5] ).to_list() == [3,4,5]
