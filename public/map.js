// var socket = io();
// socket.on('message', function (data) {
//     // 在這裡處理從Node.js服務器接收到的消息
//     document.getElementById("box").innerHTML = data;
// });
function pos_to_html(pos) {
    pos = pos.replace(/\r\n|\n/g, "");
    y = pos.substr(-2, 2)//'605'--->05
    x = pos.slice(0, -2);//'605'--->6
    y = parseInt(y, 10);
    x = parseInt(x, 10);

    y = 92.3 - 7.3 * y
    x = 24.65 + 4.7 * x
    //alert(x)
    return { val1: x, val2: y };
}
// const { val1, val2 } = pos_to_html();
// console.log(val1);
// console.log(val2); 