package comlib.chisel.component

import chisel3._

object dichotomy{

    private def apply[T<:Data,B<:Data](
        f: ((T,B), (T,B), Boolean)=>(T,B), 
        v: Seq[(T,B)],
        locked_stage: Int,
        stage: Int
    ):(T,B) = v.size match {

        case 1 => v(0)
        case x =>
            val left = apply( f, v.take( x/2 ), locked_stage, stage+1 )
            val right = apply( f, v.takeRight( x - x/2 ), locked_stage, stage+1 )
            f( left, right, (stage % locked_stage) == 0 )

    }

    def apply[T<:Data,B<:Data]( f: ((T,B), (T,B), Boolean)=>(T,B), v: Seq[(T,B)], locked_stage: Int=-2 ):(T,B)
        = apply( f, v, locked_stage, 1 )

 }

object dichotomyWithIndex {

    def apply[T<:Data]( f: ((T,UInt), (T,UInt), Boolean)=>(T,UInt), v: Vec[T], locked_stage: Int = -2 ):(T,UInt) = {
        val xs = (v.zipWidthIndex) map { case (v,i) => (v, i.U)}
        dichotomy( f, xs, locked_stage )
    }
}