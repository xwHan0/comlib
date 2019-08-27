
var comlib = (function(com){

    com.datetime = require('./datetime.js')
    com.iterator = require('./iterator.js')

    return com
}(comlib||{}));

module.exports = comlib