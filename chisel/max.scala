package comlib.chisel.componment

import chisel3._

object Max2 {

    def apply( a:Tuple2[UInt,UInt], b:Tuple2[UInt, UInt], locked:Boolean=false ) = {

        val (a_val, a_idx) = a
        val (b_val, b_idx) = b

        val ret_value = 
            if(locked)
                Reg(UInt(a_val.getWidth.W))
            else
                Wire(UInt(a_val.getWidth.W))

        val ret_idx = 
            if(locked)
                Reg(UInt(a_idx.getWidth.W))
            else
                Wire(UInt(a_idx.getWidth.W))

        when( a_val >= b_val ){
            ret_value := a_val
            ret_idx := a_idx
        }.otherwise{
            ret_value := b_val
            ret_idx := b_idx
        }

        (ret_value, ret_idx)
    }

}