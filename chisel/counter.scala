package comlib.chisel.component

import chisel3._

object Count {

    /* Counter计算过程函数
     @params inc: Increase enable flag
     @params ival: Increase value
     @params dec: Decrease enable flag
     @params dval: Decrease value
     @params value: Counter current value
     @params min: Counter minimal value threshold
     @params max: Counter max value threshold

     @return: (new-count-value, overflow-flag, under-flow-flag)
     */
    def apply[T<:UInt]( inc:Bool, ival:T, dec:Bool, dval:T, value:T, min:T, max:T ): (T,Bool,Bool) = {
        
        val ret = Wire(chiselTypeOf(value))
        val of = Wire(Bool())
        val uf = Wire(Bool())

        of := false.B
        uf := false.B

        when( inc && dec ){
            when( ival >= dval ){
                when( value > max - (ival - dval) ){
                    ret := max
                    of := true.B
                }.otherwise{
                    ret := value + (ival - dval)
                }
            }.otherwise{
                when( value < min + (dval-ival) ){
                    ret := min
                    uf := true.B
                }.otherwise{
                    ret := value - (dval-ival)
                }
            }
        }.elsewhen( inc && !dec ){
            when( value > max - ival ){
                ret := max
                of := true.B
            }.otherwise{
                ret := value + ival
            }
        }.elsewhen( !inc && dec ){
            when( value < min + dval ){
                ret := min
                uf := true.B
            }.otherwise{
                ret := value - dval
            }
        }.otherwise{
            val ret = value
        }

        (ret, of, uf)
    }

    def apply[T<:UInt]( inc:Bool, ival:T, dec:Bool, dval:T, value:T ): T = {
        
        val ret = Wire(chiselTypeOf(value))

        when( inc && dec ){
            when( ival >= dval ){
                ret := value + (ival - dval)
            }.otherwise{
                ret := value - (dval - ival)
            }
        }.elsewhen( inc && !dec ){
            ret := value + ival
        }.elsewhen( !inc && dec ){
            ret := value - dval
        }.otherwise{
            ret := value
        }

        ret
    }

}

object Counter {
    def apply[T<:UInt]( inc:Bool, ival:T, dec:Bool, dval:T, init:T, min:T, max:T ): (T,Bool,Bool) = {
        val cnt = RegInit( init )
        (cnt, of, uf) := Count( inc, ival, dec, dval, cnt, min, max )
        (cnt, of, uf)
    }

    def apply[T<:UInt]( inc:Bool, ival:T, dec:Bool, dval:T, init:T ): T = {
        val cnt = RegInit( init )
        cnt := Count( inc, ival, dec, dval, cnt )
        cnt
    }
}

object ReadClearCount {

    def apply[T<:UInt]( inc:Bool, ival:T, clear:Bool, value:T, min:T, max:T ):(T,Bool,Bool)
        = Count( inc, ival, clear, value, value, min, max )

    def apply[T<:UInt]( inc:Bool, ival:T, clear:Bool, value:T ):T
        = Count( inc, ival, clear, value, value )
}

object ReadClearCounter {
    def apply[T<:UInt]( inc:Bool, ival:T, clear:Bool, init:T, min:T, max:T ): (T,Bool,Bool) = {
        val cnt = RegInit( init )
        (cnt, of, uf) := ReadClearCount( inc, ival, clear, cnt, min, max )
        (cnt, of, ul)
    }

    def apply[T<:UInt]( inc:Bool, ival:T, clear:Bool, init:T ): T = {
        val cnt = RegInit( init )
        cnt := ReadClearCount( inc, ival, clear, cnt )
        cnt
    }
}