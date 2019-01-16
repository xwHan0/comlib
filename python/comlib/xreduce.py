from comlib.mapreduce.core import IterCore

class xreduce(IterCore):

    def _recur( self, preds, node ):
        """
        使用preds判断node处理动作。
        若需要处理，则使用self.reduce迭代处理node的子节点，最后self.reduce的结果使用self.post
        和node节点一并处理后返回。
        若不需要处理，则根据条件跳过该节点以及子节点，或者直接终止迭代。
        """
        
        pred = preds[0] # 获取头判断条件
           
        # 过滤判断。TBD：考虑到yield必须有后处理，所以是否有必要
        succ = pred.match( node ) if self.get_children==self._get_children_iter else pred.match(*node)
       
        if succ == 1:  # 匹配成功，迭代子对象
            nxt = self.get_children(node)
            if hasattr(nxt, '__iter__') and nxt!=[]:
                if len(preds)>1: preds = preds[1:]
                rst_l = self.init(node) # 定义当前节点的reduce初始值
                for ss in nxt:
                    status, rst_n = self._recur( preds, ss )    # 处理子节点

                    # 返回状态判断
                    # status > 0 : 匹配成功； status < 0: 匹配不成功
                    # |status|==
                    #   1: 继续处理；2：不迭代子对象(返回值不应该出现)；3：终止迭代；4：不迭代兄弟对象；
                    if status == 1: 
                        rst_l = self.reduce(rst_l, rst_n)
                    elif status == -1:
                        continue
                    elif status in [3,4]:
                        rst_l = self.reduce(rst_l, rst_n)
                        break
                    elif status in [-3,-4]:
                        break
                    
                rst_l = self.post( node, rst_l )
                return 3 if status==3 else 1, rst_l
            else:
                return 1, self.post( node, self.init(node) )

        elif succ < 0:  # 匹配不成功，返回匹配结果和None。不应该出现匹配不成功，还要继续迭代
            return succ, None
        
        elif succ > 0: # 匹配成功，但所有可能都不需要继续
            return succ, self.post(node,self.init(node))

               
    def run(self, proc):
        if self.get_children == self._get_children_iter:
            if self.min_node_num > 1:
                raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, 1))
        elif self.min_node_num > len(self.node):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.node)))
        
        if self.isArray:
            for ss in self.get_children(self.node):
                yield from self._iter( self.preds, ss )
        else:
            yield from self._iter( self.preds, self.node )
        
            

