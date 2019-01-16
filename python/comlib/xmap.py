from comlib.mapreduce.core import IterCore

class xmap(IterCore):

    def __init__(self, proc, *node, sSelect='*', gnxt={}, children={}, **cfg):
        super().__init__(*node, sSelect=sSelect, gnxt=gnxt, children=children, **cfg)
        self.proc = proc


    def _iter_common( self, preds, node ):
        pred = preds[0]
           
        # 过滤判断
        succ = pred.match( node ) if self.get_children==self._get_children_iter else pred.match(*node)
       
        if succ == 1:  # 匹配成功，迭代子对象
            if pred.yield_typ==1: yield self.proc(node)
            
            nxt = self.get_children(node)
            if hasattr(nxt, '__iter__') and nxt!=[]:
                if len(preds)>1: preds = preds[1:]

                if pred.yield_typ == 1:     # 遍历行为
                    for ss in nxt:
                        yield from self._iter_common( preds, ss )
                else:   # 迭代行为
                    pass

            
        elif succ == -1:  # 匹配不成功，迭代子对象
            nxt = self.get_children(node)
            if hasattr(nxt, '__iter__') and nxt!=[]:
                for ss in nxt:
                    yield from self._iter_common( preds, ss )
                
        elif succ == 2: # 匹配成功，不迭代子对象
            if pred.yield_typ != 0: yield self.proc(node)

        elif succ == 3: # 匹配成功，终止迭代
            if pred.yield_typ != 0: yield self.proc(node)
            raise StopIteration()

        elif succ == -3: # 匹配不成功，终止迭代
            raise StopIteration()

        # elif succ == -2: # 匹配不成功，不迭代子对象
        #     pass

               
    def __iter__(self):
        if self.get_children == self._get_children_iter:
            if self.min_node_num > 1:
                raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, 1))
        elif self.min_node_num > len(self.node):
            raise Exception('The except node number(:{0}) in sSelection is larger than provieded node number(:{1}).'.format(self.min_node_num, len(self.node)))
        
        if self.isArray:
            for ss in self.get_children(self.node):
                yield from self._iter_common( self.preds, ss )
        else:
            yield from self._iter_common( self.preds, self.node )
        
            

