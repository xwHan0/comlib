// (function webpackUniversalModuleDefinition(root, factory) {
//     if (typeof exports === 'object' && typeof module === 'object') {
//         module.exports = factory();
//     } else if (typeof define === 'function' && define.amd) {
//         define([], factory);
//     }else if(typeof exports === 'object'){
//         exports["comlib"] = factory();
//     } else {
//         // root['comlib'] = factory()
//         var comlib = factory()
//     }
// })(this, function (){
    
//     var com = {}

//     // com.datetime = require('./datetime')
//     // com.iterator = require('./iterator')

//     com.test = function(){
//         return "xwHan,hello!"
//     }
    
//     return com
// });

import {datetime} from './datetime'
import {iterator} from './iterator'

var comlib = {}

comlib.datetime = datetime
comlib.iterator = iterator

comlib.test = function(){
    return "xwHan,hello!"
}


export {comlib as default}