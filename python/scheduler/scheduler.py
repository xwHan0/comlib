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


class Mask:
    def __init__(self, dims=[], gnum=1):
        
        # 每个维度、每个位置允许获得的Grant个数
        self.gnum = [[gnum]*dim_size for dim_size in dims] if isinstance(gnum, int) else gnum
        # 统计每个维度、每个位置的Grant个数
        self.gcnt = [[0]*dim_size for dim_size in dims] 
        
    def reset(self):
        for gcnts in self.gcnt: # 清空所有统计
            for i in range(len(gcnts)):
                gcnts[i] = 0
                
    def is_mask(self, pos):
        """判断位置pos是否被选择过"""
        for dim in range(len(self.gnum)):   # 按维度遍历
            if self.gcnt[dim][pos[dim]] >= self.gnum[dim][pos[dim]]:
                return True # 只要任何一个维度Grant个数大于允许值，就判断为屏蔽
        return False    # 所有维度Grant个数都小于允许值，才判断为不屏蔽
        
    def mask(self, pos):
        """统计pos位置获得一个Grant"""
        for dim in range(len(self.gnum)):
            self.gcnt[dim][pos[dim]] += 1


class Pointer:
    def __init__(self, dims=[]):
        self.scope = xmul(*dims)    # order长度
        self.step = int(self.scope/xmax(*dims))   # 指针在order中的步长
        
    def pointer2index(self, ptr):
        return ptr * self.step

    def index2pointer(self, idx):
        return int(idx/self.step)

    def search2index(self, ptr, search_cnt):
        return (self.pointer2index(ptr) + search_cnt) % self.scope

    def next_pointer(self, idx):
        pointer = self.index2pointer(idx) 
        return (pointer + 1) % int(self.scope / self.step)  # 更新到下一个指针


class WPointer(Pointer):
    def __init__(self, dims=[]):
        super().__init__(dims)
        self.pointer_table = [0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,1,1,1,1]
        self.pointer_idx = 0

    def next_pointer(self, idx):
        self.pointer_idx = (self.pointer_idx + 1) % 20
        return self.pointer_table[self.pointer_idx]


class Algorithm:
    def __init__(self, dims=[], order=None, tdm=False, pointer=None):
        
        if dims == []:
            self.order = None   # 搜索位置顺序列表
        elif order == None:
            self.order = gen_standard_order(dims)
        else:
            self.order = order

        # 每次搜索的最大范围
        self.select_num = xmin(*dims) if tdm else len(self.order)

        # 步骤指针
        # 0: 仲裁初始化还未开始。等待调度__iter__
        # 1: 仲裁初始化结束，开始仲裁。__iter__运行结束
        # 2: 新指针已经找到。record已经记录到新指针
        self.step = 0

        self.pointer = WPointer(dims)    
        self.ptr = 0    # 当前指针
        self.next_ptr = 0   # 下一跳指针
        self.search_cnt = 0    # 当前搜索指针。内部搜索用指针，并非调度器指针
        self.mask = Mask(dims, 1)   # 设置屏蔽看门狗

    def set_pointer(self, ptr):
        self.ptr = ptr
        self.step = 0

    def record(self, pos):
        """记录当前位置获得Grant"""
        self.mask.mask(pos)

        if self.step == 1:
            self.step = 2
            # idx = (self.pointer.pointer2index(self.ptr) + self.search_cnt-1) % len(self.order)
            idx = self.pointer.search2index(self.ptr, self.search_cnt-1)
            self.next_ptr = self.pointer.next_pointer(idx)
            # pointer = math.ceil(idx/self.pointer_step)
            # self.next_pointer = (pointer + 1) * self.pointer_step % len(self.order)

        # return self.next_pointer # 返回新指针位置

    def __iter__(self):
        self.mask.reset()
        self.search_cnt = 0
        
        if self.step == 2:
            self.ptr = self.next_ptr
        self.step = 1

        return self

    def __next__(self):
        if self.search_cnt < self.select_num:   # 搜索一圈
            # idx = (self.pointer.pointer2index(self.ptr) + self.search_cnt) % len(self.order)    # 搜索位置Round Robin
            idx = self.pointer.search2index(self.ptr, self.search_cnt)
            pos = self.order[idx]  # 获取当前指针位置
            self.search_cnt += 1    # 搜索过的位置个数加1

            if self.mask.is_mask(pos):  # 若位置被屏蔽，则遍历下一个节点
                return self.__next__()

            return pos
        else:
            raise StopIteration()


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
# # req = [[4,4,4,4], [4,4,4,4], [4,4,4,4],[4,4,4,4]]
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


for _ in range(100):


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
