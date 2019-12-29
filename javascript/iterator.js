
var iterator = (function(it){

    // 位置迭代器定义
    it.index = function(prefix=[]){

        var _prefix = []

        if( Object.prototype.toString.call(prefix) === '[object Array]' )
            _prefix = prefix.slice()
        else if( typeof prefix === "string" ){
            _prefix = prefix.match(/\d+/g)
            for( let i=0; i<_prefix.length; i++ )
                _prefix[i] = parseInt(_prefix[i])
        }

        return {
            idx : _prefix, //防止指针传递问题
            lvl : function(){return this.idx.length},

            next : function(){
                // var nprefix = prefix.slice()
                this.idx[this.idx.length-1] += 1
                return {value:comlib.iterator.index(this.idx), done:false}
            },

            toString: function(){
                return "[" + _prefix.toString() + "]"
            },

            [Symbol.iterator] : function(){
                return comlib.iterator.index(this.idx.concat([-1]))
            },
        }
    }

    // 过滤器定义
    // it.filter = function(arguments){

    //     var iters = Array.from(arguments)
    //     var pred = iters.shift()

    //     var next_elements = function(iters){
    //         var rst = []
    //         for( let iter of iters ){
    //             var ele = iter.next()
    //             if( ele.done )
    //                 return null
    //             else
    //                 rst.push(ele.value)
    //         }
    //         return rst
    //     }

    //     return {
    //         next : function(){
    //             do{
    //                 var nxts = next_elements(iters)
    //             }while(nxts && !pred(nxts))
                
    //             return {value:nxts, done: nxts==null}
    //         },
    //         //Javascript Iterable Protocol
    //         [Symbol.iterator] : function(){return this},
    //     }
    // }

    // 核心类定义
    it.tree = function(args){

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



        var tree = this
        // 获取子项迭代器
        var _get_child_iter_ = function(child, matches){
            for( let match of matches ){   //非this开放函数，this被转向
                if( match.pred(child) )
                    return match.iter(child)    //返回第一个匹配成功的迭代器获取函数
            }
            return null //无匹配条件，返回null
        }

        //获取节点数据集合的子节点迭代器集合
        //遵循最小迭代原则：一个节点数据没有迭代器，则整体返回null
        var _get_children_iters_ = function(children, matches){
            let rst = []
            for( let child of children ){
                iter = _get_child_iter_(child, matches)
                if( iter == null )
                    return null
                else
                    rst.push(iter)
            }
            return rst
        }

        //获取迭代器集合iters的每个迭代器的第一个元素集合。
        //遵循最小迭代原则：有一个迭代器返回done=true，则整体返回null
        var _get_next_elements_ = function(iters){
            let rst = []
            for( let iter of iters ){
                nxt = iter.next()
                if( nxt.done )
                    return null
                else
                    rst.push(nxt.value)
            }
            return rst
        }

        var _result_ = function(stack){
            this.value = stack[-1].value
            this.done = stack[-1].sta == DONE
            this.stack = stack

            this.is_root = function(){return this.stack.length == 1}
            this.is_leaf = function(){return this.stack[this.stack.length-1].children==null}
            this.depth = function(){return this.stack.length}

            this.is_pre = function(){
                let node = this.stack[this.stack.length-1]
                return node.children == null || node.sta == PRE
            }
            this.is_post = function(){
                let node = this.stack[this.stack.length-1]
                return node.children == null || node.sta == POST
            }
            this.is_done = function(){return this.done == 2}
            this.iter_status = function(){return this.stack[this.stack.length-1].sta}

            this.v = function(func=null){
                if( func == null ){
                    return this.value
                }else if( typeof func === Number ){
                    return this.value[func]
                }else if( Object.prototype.toString.call(func) === '[object Array]' ){
                    var rst = []
                    for( let f of func ){
                        rst.push( this.value[f] )
                    }
                    return rst
                }else if( typeof func === Function ){
                    return func( this.value )
                }
            }
        }

        //----------------------  返回对象定义  --------------------
        var obj = {
            stack : [{value:arguments, sta:PRE}],    //迭代堆栈
            matches : DEFAULT_MATCHES,
            pred : null,
            dirs: [],
            [Symbol.iterator] : function(){return this},

            require_pop : false,
            goto_post : false,
            preappend : null,
        }

        obj.next = function(){
            for(dir of self.dirs)
                return dir()
        }

        obj.mtree = function(){
            this.down(false, false, 1)
            this.stack[this.stack.length-1].sta = DONE
            return this
        }

        obj.down = function(down=true, up=false, it_num=ITIMES){
            for( let i=0; i<it_num; i++ ){

                if( this.require_pop ){
                    this.stack.pop()
                    this.require_pop = false
                }

                if( this.goto_post ){
                    this.stack[this.stack.length-1].sta = POST
                    this.goto_post = false
                }

                if( this.preappend ){
                    this.stack.push(self.preappend)
                    self.preappend = null
                }

                //获取堆栈的顶节点，作为当前处理节点
                let node = this.stack[this.stack.length-1]

                //TBD: node一定存在？
                switch( node.sta ){
                    case PRE:
                        //获取子节点迭代器集合
                        if( node.children = _get_children_iters_(node.value, this.matches) ){
                            //获取所有迭代器的第一个子节点
                            if( nxts = _get_next_elements_(node.children) ){
                                //把子节点压入堆栈
                                // this.stack.push({value:nxts, sta:PRE})
                                this.preappend = {value:nxts, sta:PRE}
                                this.goto_post = true

                                if( down )
                                    return new _result_(this.stack)
                                else
                                    continue
                            }
                        }

                        // 以下仅叶子节点处理
                        if( nxts = _get_next_elements_(this.stack[this.stack.length-2].children) ){
                            this.preappend = {value:nxts, sta:PRE}
                        }

                        this.require_pop = true
                        return new _result_(this.stack)
                    
                    case POST:
                        if( this.stack.length == 1 ){
                            node.sta = DONE     //已经到了根节点
                        }else{
                            this.require_pop = true
                            if( nxts = _get_next_elements_(this.stack[this.stack.length-1].children) ){   //还需要继续迭代父元素的下一个
                                //处理下一个兄弟节点
                                this.preappend = {value:nxts, status:PRE}
                            }
                        }
                        if(up)
                            return new _result_(this.stack)
                    
                    case DONE:
                        node.sta = PRE  //复位状态，供下一次迭代使用
                        return new _result_(this.stack)
                    
                    default:
                        throw "Please do NOT modify stack[x].status property!"
                }
            }
        }

        obj.up = function(){return obj.down(false,true)}
        obj.downup = function(){return obj.down(true,true)}

        obj.wide = function(){
            if( this.stack.length == 0 )
                return new _result_(null, true, PRE, this.stack) 

            let node = this.stack.shift()
            if( node.children = _get_children_iters_(node.value, this.matches) ){
                for( child of node.children ){
                    //获取所有迭代器的第一个子节点
                    if( nxts = _get_next_elements_(child) ){
                        //把子节点压入堆栈
                        this.stack.push({value:nxts, sta:PRE})
                    }
                }
            }
            return new _result_(this.stack)
        }

        var dir = "down"
        var dirs = ( Object.prototype.toString.call(dir) === '[object Array]' ) ? dir : [dir]
        for( dir of dirs ){
            if(dir == "up") obj.dirs.push(obj.up)
            else if(dir == "down") obj.dirs.push(obj.down)
            else if(dir == "downup") obj.dirs.push(obj.downup)
            else if(dir == "updown"){
                obj.dirs.push(obj.up)
                obj.dirs.push(obj.down)
            }
            else if(dir == "wide") obj.dirs.push(obj.wide)
        }

        // 返回对象接口
        return obj
    }

    return it
}(iterator||{}));


// module.exports = iterator
export {iterator}



// export {
//     IterTree, 
// }

