package comlib.chisel.componment

import chisel3._

object Count {

    def apply( inc:Bool, ival:UInt, dec:Bool, dval:UInt, value:UInt, min:Option[UInt], max:Option[UInt] ): UInt = {
        
        def overflow( value:UInt, ival:UInt, max:Option[UInt] ): UInt = {
            val ret = Wire(UInt(value.getWidth.W))
            max match{
                case Some(m) =>
                    when( value >= m - ival ){
                        ret := m
                    }.otherwise{
                        ret := value + ival
                    }
                case None =>
                    ret := value + ival
            }
            ret
        } 

        def underflow( value:UInt, dval:UInt, min:Option[UInt] ):UInt = {
            val ret = Wire(UInt(value.getWidth.W))
            min match{
                case Some(m) =>
                    when( value <= m + dval ){
                        ret := m
                    }.otherwise{
                        ret := value - dval
                    }
                case None =>
                    ret := value - dval
            }
            ret
        }
        
        val ret = Wire(UInt(value.getWidth.W))

        when( inc && dec ){
            when( ival >= dval ){
                ret := overflow( value, ival-dval, max )
            }.otherwise{
                ret := underflow( value, dval-ival, min )
            }
        }.elsewhen( inc && !dec ){
            ret := overflow( value, ival, max )
        }.elsewhen( !inc && dec ){
            ret := underflow( value, dval, min )
        }.otherwise{
            ret := value
        }

        ret
    }

    def apply( inc:Bool, ival:UInt, dec:Bool, dval:UInt, value:UInt ): UInt
        = apply( inc, ival, dec, dval, value, None, None )

}

object Counter {
    def apply( inc:Bool, ival:UInt, dec:Bool, dval:UInt, init:UInt, min:Option[UInt], max:Option[UInt] ): UInt = {
        val cnt = RegInit( UInt(init.getWidth.W), init )
        cnt := Count( inc, ival, dec, dval, cnt, min, max )
        cnt
    }
}

object ReadClearCount {

    def apply( inc:Bool, ival:UInt, clear:Bool, value:UInt, min:Option[UInt], max:Option[UInt] ):UInt
        = Count( inc, ival, clear, value, value, min, max )

    def apply( inc:Bool, ival:UInt, clear:Bool, value:UInt ):UInt
        = apply( inc, ival, clear, value, None, None )
}

object ReadClearCounter {
    def apply( inc:Bool, ival:UInt, clear:Bool, init:UInt, min:Option[UInt], max:Option[UInt] ): UInt = {
        val cnt = RegInit( UInt(init.getWidth.W), init )
        cnt := ReadClearCount( inc, ival, clear, cnt, min, max )
        cnt
    }
}