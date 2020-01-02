from comlib.ex.math import xmul,xmin,xmax
import math

# 基本原理
#  1. 把所有维度先对齐到最大尺寸；
#  2. 从低维度开始，位置向前推进1；
#  3. 当低维度推进完一圈后，父维度推进1；
#  4. 当父维度也推进完后。结束迭代
def gen_standard_order(dims=[]):
    """按照仲裁维度dims生成标准的搜索顺序坐标列表。"""

    if dims == []: return []    # 错误过滤

    pos = [0] * len(dims)    # 初始化一个搜索位置坐标，零时变量
    rst = [pos.copy()]    # 结果列表。初始化填充原始坐标[0,0,...,0]
    max_dim_size = max(iter(dims))  # 最大维度尺寸。把所有维度都补全到最大维度尺寸后，推算各个位置信息
    max_pos_size = xmul(*dims)    # 最大位置个数

    while len(rst) < max_pos_size:

        carry = False   # 父维度进位标识

        for dim in range(len(dims)-1, -1, -1): # 从最底维度到最高维度遍历。最低维度在pos中的index大
            if carry:   # 进位有效
                pos[dim] = (pos[dim]+1) % max_dim_size   # 位置向前推进1
                carry = False   # 没有到最大，carry自动清零
                pos[dim] += 1   # 位置向前推进1

            elif pos[dim] >= max_dim_size-1: # 进位无效，但遍历到维度的最大

                pos[dim] = 0    # Round Robin
                carry = True    # 向前进位

            else:   # 进位无效，也没有遍历到维度的最大
                pos[dim] += 1
                
        # 判断是否当前位置超维度尺寸
        over = False
        for dim in range(len(dims)-1, -1, -1):  # 从最底维度到最高维度遍历。最低维度在pos中的index大
            if pos[dim] >= dims[dim]:
                over = True
                break
                
        if not over:    # 超维度尺寸，则放弃当前位置
            rst.append(pos.copy())

    return rst


def order2dim(order):
    dim = [0] * len(order[0])   # 每个维度初始化
    for ord in order:   # 枚举每个Order元素
        for d in range(len(dim)):   # 每个维度
            if dim[d] < ord[d]:
                dim[d] = ord[d] # 取最大值
    return dim


class Mask:
    def __init__(self, dims=[], gnum=1):
        
        # 每个维度、每个位置允许获得的Grant个数
        self.gnum = [[gnum]*dim_size for dim_size in dims] if isinstance(gnum, int) else gnum
        # 统计每个维度、每个位置的Grant个数
        self.gcnt = [[0]*dim_size for dim_size in dims] 
        # 统计每个维度还可以容纳Grant的维度量个数
        self.dim_permit_gnum = dims.copy()
        # 是否可以提前结束迭代
        self.stop = False
        
    def reset(self):
        self.stop = False
        for i in range(len(self.gcnt)):
            self.dim_permit_gnum[i] = len(self.gcnt[i]) # 重新加载可以选择的维度量个数
            for j in range(len(self.gcnt[i])):
                self.gcnt[i][j] = 0 # 清空选择的Grant个数
                
    def is_mask(self, pos):
        """判断位置pos是否被选择过。返回(可以结束迭代标识, 当前位置是否屏蔽标识)"""
        if self.stop:
            return (True, False)

        for dim in range(len(self.gnum)):   # 按维度遍历
            if self.gcnt[dim][pos[dim]] >= self.gnum[dim][pos[dim]]:
                return (False, True) # 只要任何一个维度Grant个数大于允许值，就判断为屏蔽
        return (False, False)    # 所有维度Grant个数都小于允许值，才判断为不屏蔽
        
    def mask(self, pos):
        """屏蔽位置pos，并返回是否某一个维度已经没有Grant令牌。仲裁可以停止的标识。"""
        for dim in range(len(self.gnum)):
            self.gcnt[dim][pos[dim]] += 1
            if self.gcnt[dim][pos[dim]] >= self.gnum[dim][pos[dim]]:    # 当前dim维度pos[dim]位置已经被屏蔽
                self.dim_permit_gnum[dim] -= 1
                if self.dim_permit_gnum[dim] == 0:
                    self.stop = True
                    return True # 当前dim维度的Grant令牌已经分完。可以直接结束仲裁
        return False    # 需要继续迭代搜索


class Order:
    def __init__(self, dims=[], order=[], search_num=-1):
        """
        Arguments:
        * dims: 仲裁维度列表
            * 若为[]，则dims由order推导
        * order: 仲裁搜索位置列表
            * 若为[]，则由dims推导。默认采用标准的DPA搜索顺序
        * search_num: 一次仲裁搜索的最大步长
          * -1：搜索所有的可选范围
          * 0: TDM搜索。仅搜索第一个位置相互正交的范围
          * other: 用户选的的搜索范围
        """
        if dims != []:
            self.scope = xmul(*dims)
            self.order = gen_standard_order(dims)
        elif order != []:
            dims = order2dim(order)
            self.scope = len(order)
            self.order = order

        self.step = int(self.scope/xmax(*dims))
        self.ptr = 0
        self.search_cnt = 0

        if search_num == 0:
            self.search_num = int( self.scope / xmax(*dims) )
        elif search_num == -1:
            self.search_num = self.scope
        else:
            self.search_num = search_num

    def pointer2index(self, ptr):
        return ptr * self.step

    def index2pointer(self, idx):
        return int(idx/self.step)

    def pointer(self, val):
        self.ptr = val

    def __iter__(self):
        self.search_cnt = 0
        return self

    def __next__(self):
        if self.search_cnt < self.search_num:
            idx = (self.pointer2index(self.ptr) + self.search_cnt) % self.scope
            pos = self.order[idx]  # 获取当前指针位置
            ptr = self.index2pointer(idx)

            self.search_cnt += 1    # 搜索过的位置个数加1

            return (ptr, pos)
        else:
            raise StopIteration()


class Algorithm:
    def __init__(self, dims=[], order=[], search_num=-1, gnum=1):
        self.dims = dims if dims!= [] else order2dim(order)

        self.order = Order(self.dims, order, search_num)    # Order组件例化
        self.mask = Mask(self.dims, gnum)   # Mask组件例化

        self.first_grant = True
        self.pointer = self.ptr = 0    # 指针和下一跳指针

        self.order_ite = None

    def __iter__(self):
        self.first_grant = True
        self.order.pointer(self.pointer)
        self.mask.reset()
        self.order_ite = iter(self.order)
        return self

    def __next__(self):
        (self.ptr, pos) = next(self.order_ite)
        (stop, mask) = self.mask.is_mask(pos)
        if stop:
            raise StopIteration()
        elif mask:
            return self.__next__()
        else:
            return pos

    def record(self, pos):
        self.mask.mask(pos)
        if self.first_grant:
            self.pointer = self.ptr
            self.first_grant = False


class Scheduler:
    def __init__(self, dims=[], order=None):
        
        self.algo = Algorithm(dims, order)

    def get_req(self, req, pos):
        r = req
        for p in pos:
            r = r[p]
        return r > 0

    def run(self, req, ptr=0):
        rst = []
        # self.algo.ptr = ptr
        for pos in self.algo:
            if self.get_req(req, pos):
                self.algo.record(pos)
                rst.append(pos)
        return rst


sch = Scheduler([4,4])

req = [[4,0,0,0], [4,4,0,0], [4,4,4,0],[4,4,8,0]]
# req = [[4,4,4,4], [4,4,4,4], [4,4,4,4],[4,4,4,4]]
# # req = [[2,2,2,2], [7,7,7,7], [4,4,4,4],[3,3,3,3]]
qm = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]


# reqs = [
#     [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],
#     [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],
#     [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],
#     [[1,0,0,0],[1,0,0,0],[1,0,0,0],[1,0,0,0]],

#     [[0,0,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
#     [[0,0,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
#     [[0,0,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],
#     [[0,0,0,0],[0,1,0,0],[0,1,0,0],[0,1,0,0]],

#     [[0,0,0,0],[0,0,0,0],[0,0,1,0],[0,0,1,0]],
#     [[0,0,0,0],[0,0,0,0],[0,0,1,0],[0,0,1,0]],
#     [[0,0,0,0],[0,0,0,0],[0,0,1,0],[0,0,1,0]],
#     [[0,0,0,0],[0,0,0,0],[0,0,1,0],[0,0,1,0]],

#     [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,1,0]],
#     [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,1,0]],
#     [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,1,0]],
#     [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,1,0]],

# ]


for _ in range(1000):


    for r in range(4):
        for c in range(4):
            qm[r][c] += req[r][c]

    for i in range(16):

        gnt = sch.run(qm)
        
        for [i,j] in gnt:
            qm[i][j] -= 1

        # print("")
        # print(gnt)
        # print(qm)
        # print("Pointer is: " + str(sch.algo.next_ptr))

print(qm)
