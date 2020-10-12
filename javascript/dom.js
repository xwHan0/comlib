var dom = (function(d){

    d.select = function( el, sels, multiple=false ){

        // 统一参数到Array
        if( Object.prototype.toString.call(sels) != '[object Array]' ){
            sels = [sels]
        }
    
        let r_el = el
        for( var i=0; i<sels.length; i++ ){
    
            if( r_el == null || r_el == undefined ){
                return null
            }else if( sels[i] == "svg:" ){
                r_el = r_el.getSVGDocument()
            }else if( i == sels.length - 1 ){
                if( multiple ){
                    return r_el.querySelectorAll( sels[i] )
                }else{
                    return r_el.querySelector( sels[i] )
                }
            }else{
                r_el = r_el.querySelector( sels[i] )
            }
    
        }
   
        return r_el
    }

}(dom||{}));

export {dom}


