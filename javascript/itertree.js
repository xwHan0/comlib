
//=====================  常量定义  ===================
const ITIMES = 9999999

const PRE = 0
const POST = 1
const DONE = 2

const DEFAULT_MATCHES = [
    {
        pred: function(child){
            switch(typeof(child)){
                case "number": return true
                case "boolean": return true
                case "string": return true
                case "function": return true
                case "undefined": return true
                case "bigint": return true
                default: return false
            }
        },
        iter: function(child){return null}
    },
    {
        pred: function(child){return typeof(child[Symbol.iterator])=="function"},
        iter: function(child){return child[Symbol.iterator]()},
    },
]


//=====================  内部使用函数定义  =====================


//==================   对外接口定义  ======================

// 核心类定义
var IterTree = function(args){

    return {

        //--------  类常量定义


        //--------  实例变量定义
        stack : [{value:arguments, sta:PRE}],    //迭代堆栈
        matches : DEFAULT_MATCHES,

        // 获取子项迭代器
        _get_child_iter_ : function(child){
            for( let match of this.matches ){   //非this开放函数，this被转向
                if( match.pred(child) )
                    return match.iter(child)    //返回第一个匹配成功的迭代器获取函数
            }
            return null //无匹配条件，返回null
        },

        //获取节点数据集合的子节点迭代器集合
        //遵循最小迭代原则：一个节点数据没有迭代器，则整体返回null
        _get_children_iters_ : function(children){
            let rst = []
            for( let child of children ){
                iter = this._get_child_iter_(child)
                if( iter == null )
                    return null
                else
                    rst.push(iter)
            }
            return rst
        },

        //获取迭代器集合iters的每个迭代器的第一个元素集合。
        //遵循最小迭代原则：有一个迭代器返回done=true，则整体返回null
        _get_next_elements_ : function(iters){
            let rst = []
            for( let iter of iters ){
                nxt = iter.next()
                if( nxt.done )
                    return null
                else
                    rst.push(nxt.value)
            }
            return rst
        },

        //----------------------  迭代核心代码  --------------------------
        next : function(){
            for( let i=0; i<ITIMES; i++ ){
                //获取堆栈的顶节点，作为当前处理节点
                let node = this.stack[this.stack.length-1]

                //TBD: node一定存在？
                switch( node.sta ){
                    case PRE:
                        //获取子节点迭代器集合
                        if( node.iters = this._get_children_iters_(node.value) ){
                            //获取所有迭代器的第一个子节点
                            if( nxts = this._get_next_elements_(node.iters) ){
                                //把子节点压入堆栈
                                this.stack.push({value:nxts, sta:PRE})
                            }
                        }
                        //修改节点状态
                        node.sta = POST
                        //返回结果
                        return {value:node.value, done:false, sta:PRE, stack:this.stack}
                    
                    case POST:
                        if( this.stack.length == 1 ){
                            node.sta = DONE     //已经到了根节点
                        }else{
                            node.sta = PRE  //复位状态，供下一次迭代使用
                            this.stack.pop()    //当前节点出栈
                            if( nxts = this._get_next_elements_(this.stack[this.stack.length-1].iters) ){   //还需要继续迭代父元素的下一个
                                //处理下一个兄弟节点
                                this.stack.push({value:nxts, sta:PRE})
                            }
                        }
                        return {value:node.value, done:false, sta:POST, stack:this.stack}
                    
                    case DONE:
                        node.sta = PRE  //复位状态，供下一次迭代使用
                        return {done:true}
                    
                    default:
                        throw "Please do NOT modify stack[x].sta property!"
                }
            }
        },

        //Javascript可迭代协议
        [Symbol.iterator] : function(){return this}
    }

}

// export {
//     IterTree, 
// }

