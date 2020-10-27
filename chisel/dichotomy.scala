package comlib.chisel.componment

import chisel3._

object dichotomy{

    private def apply[T,B](
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

    def apply[T,B]( f: ((T,B), (T,B), Boolean)=>(T,B), v: Seq[(T,B)], locked_stage: Int ):(T,B)
        = apply( f, v, locked_stage, 1 )

    def apply[T,B]( f: ((T,B), (T,B), Boolean)=>(T,B), v: Seq[(T,B)] ):(T,B)
        = apply( f, v, -2, 1 )

    // def applyWithIndex[T,B]( f: ((T,B), (T,B), Boolean)=>(T,B), v: Seq[T], locked_stage:Int):(T,B) = {
    //     val inner_v = v zip ((0 until v.size))
    //     apply( f, inner_v, locked_stage )
    // }

}