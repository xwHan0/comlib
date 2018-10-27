
var JqTreeGrid = function(
    name,
    img_path
){
    // 插入按钮图片
    $("tr[id^='" + name + "']").each(function(i){
        // 添加状态变量
        $(this).attr({'jq_treegrid_display': 'display'})
        
        //
        id = $(this).attr('id')
        
        // 匹配，获取树层次
        m = id.match(/_\d+/g)
        
        p = ""
        if(m == null){  // 根节点
            if( $("tr[id^='" + id + "_']").length != 0 ){ // 非仅根节点
                p += '<img id="expand_flag" src="' + img_path + '/flag_contract_root.svg" />'
            }else{
                p += '<img id="expand_flag" src="' + img_path + '/flag_empty.svg" />'
            }
        }else{
            for(i=0; i<m.length;i++){
                p += '<img src="' + img_path + '/flag_vectical.svg" />'
            }
            if( $("tr[id^='" + id + "_']").length == 0 ){ // leaf node
                p += '<img src="' + img_path + '/flag_leaf.svg" />'
            }else{
                p += '<img id="expand_flag" src="' + img_path + '/flag_contract_sub.svg" />'
            }
        }
        $(this).children().first().prepend(p)
    })
        
    //添加按钮(展开/折叠)事件
    $("img[id='expand_flag']").on("click", function(e){
        tr = $(e.target).parent().parent()
        is_root = (tr.attr('id').match(/_\d+/g)==null)
        id = tr.attr('id')
        
        if(tr.attr('jq_treegrid_display') == 'display'){
            // 翻转图片
            if(is_root){
                img = img_path + '/flag_expand_root.svg'
            }else{
                img = img_path + '/flag_expand_sub.svg'
            }
            $(this).attr('src',img)
            
            // 修改状态
            tr.attr({'jq_treegrid_display': 'hidden'})
            $("tr[id^='" + id + "_']").hide()
        }else{
            // 翻转图片
            if(is_root){
                img = img_path + '/flag_contract_root.svg'
            }else{
                img = img_path + '/flag_contract_sub.svg'
            }
            $(this).attr('src',img)
            
            // 修改状态
            tr.attr({'jq_treegrid_display': 'display'})
            $("tr[id^='" + id + "_']").show()
        
            // 记录状态处理
            $("tr[id^='" + id + "_']").each(function(i){
                id = $(this).attr('id')
                if( $(this).attr('jq_treegrid_display') == 'hidden' ){
                    $("tr[id^='" + id + "_']").hide()
                }
            })
        
        }
    })
}