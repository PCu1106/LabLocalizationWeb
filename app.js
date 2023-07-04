var net = require('net');
var k = "2";
var beacon_id = '0';
var Rssi = '0';
var exec = require('child_process').exec;
var arg1 = 'hello';
var arg2 = 'world';
//var filename = 'Hashing_KNN.py'
var filename = 'ANN.py'
var filename2 = '~/yolov7/realtimeD.py'


function full(Array) {
  for (let i = 0; i < Array.length; i++) {
    if (Array[i] == '0')
      return false;
  }
  return true;
}
let buffer = new Array(6);
buffer = ['0', '0', '0', '0', '0', '0'];
var Beacon_RSSi = '';
var t = 0;
var beacon_int = 0
var Rssi_int = 0;
var toclient = '0';
var rssi_result = '608'

var count = 0;
var fs = require('fs')
var clientHandler = function (socket) {


  //客戶端傳送資料的時候觸發data事件
  socket.on('data', function dataHandler(data) {//data是客戶端傳送給伺服器的資料

    //console.log(socket.remoteAddress, socket.remotePort, 'send', data.toString());
    k = data.toString();
    var K = k.split(",", 2);
    beacon_id = K[0];
    Rssi = K[1];

    let numStr = beacon_id.replace(/[^0-9]/ig, "");

    beacon_int = parseInt(numStr);
    Rssi_int = parseInt(Rssi);
    Rssi_int = (Rssi_int + 103) / (-48 + 103);

    if (beacon_int == 7) {
      buffer[5] = Rssi_int;
    }//因為用1 2 3 4 5 7
    else
      buffer[beacon_int - 1] = Rssi_int;
    //console.log(buffer[0], buffer[1], buffer[2], buffer[3], buffer[4], buffer[5]);
    if (full(buffer)) {
      Beacon_RSSi = `{q"Beacon_1q":q"${buffer[0]}q",q"Beacon_2q":q"${buffer[1]}q",q"Beacon_3q":q"${buffer[2]}q",q"Beacon_4q":q"${buffer[3]}q",q"Beacon_5q":q"${buffer[4]}q",q"Beacon_7q":q"${buffer[5]}q"}`;
      //console.log(Beacon_RSSi);
      exec('python' + ' ' + filename + ' ' + Beacon_RSSi + ' ' + count, function (err, stdout, stderr) {
        if (err) {
          console.log('stderr', err);
        }
        if (stdout) {
          console.log('RSSI: ', stdout);
          //toclient = stdout;
          rssi_result = stdout;
          fs.writeFile('./rssi_result.txt', rssi_result, function (error) {
            //console.log('ok')
          })
          //socket.write(toclient);
          if (type == 0) {
            if (queue.length < 10)
              queue.push(rssi_result);
            else {
              queue.shift();
              queue.push(rssi_result);
            }
          }
        }
      });
      buffer = ['0', '0', '0', '0', '0', '0'];
      count++;
    }


    socket.write(toclient);
  });

  //當對方的連線斷開以後的事件
  socket.on('close', function () {
    //console.log(socket.remoteAddress, socket.remotePort, 'disconnected');
  })
  socket.on('error', (err) => {
    console.log(err);
  })
  //socket.write(toclient);
};

var app = net.createServer(clientHandler);
var exec = require('child_process').exec;
var pos = '601';
//var prob = ['601', '601', '601', '601', '601', '601', '601', '601', '601', '601'];
var prob = [];
//var child = exec('python' + ' ' + filename2 + ' ' + '--weights ~/yolov7/weights/yolov7.pt --source http://140.116.72.67:8080/yen --nosave');
var child = exec('python' + ' ' + filename2 + ' ' + '--weights ~/yolov7/weights/yolov7.pt --source ~/yolov7/datasets/0408_testdata/101N.mp4 --nosave');
child.stdout.on('data', function (data) {
  if (isJSONString(data)) {
    var DATA = JSON.parse(data);
    pos = DATA[0];
    prob = DATA[1];
    if (type != 0) {
      if (queue.length < 10)
        queue.push(pos);
      else {
        queue.shift();
        queue.push(pos);
      }
    }
    console.log(queue);
  }

  toclient = pos;
})

app.listen(8000, '140.116.72.77');//change to server
console.log('tcp server running on tcp://', '140.116.72.77', ':', 8000);
//------------------------------------------------------------------------------------------------------------------------------------------------------->處理網頁的


const http = require("http");
var express = require('express');
var app2 = express();

app2.use(express.static(__dirname + '/public'));//重要 遠端把根目錄設在public裡  裡面放css js 圖片等等
app2.get('/', (req, res) => {
  //res.sendFile(__dirname + '/dd.html');
  res.sendFile(__dirname + '/public/map.html');
})
//控制要RSSI IMAGE 或兩個一起
var type = 0;//  0:RSSI     1:Image    2:Both
var particle_prev_count = 0;
var data_date = '0';
app2.get('/change_type', function (req, res) {
  type = req.query.value;
  fs.writeFile('./calculate_type.txt', type, function (error) {
    //console.log('ok')
  })
})
app2.get('/change_particle', function (req, res) {
  particle_prev_count = req.query.value;
  fs.writeFile('./particle_prev_count.txt', particle_prev_count, function (error) {
    //console.log('ok')
  })
})
app2.get('/change_data_date', function (req, res) {
  data_date = req.query.value;
  fs.writeFile('./data_date.txt', data_date, function (error) {
    //console.log('ok')
  })
})
//

server = http.createServer(app2)
const io = require('socket.io')(server);
server.listen(4000, () => {
  console.log('Express started, 140.116.72.77:4000')
})

var servIo = io.listen(server);



//let counter = 50;
setInterval(() => {
  //console.log(type);
  //rssi_result = '605';
  if (type == 0) {
    servIo.emit('counter', rssi_result);//用RSSI結果來當最終結果
    servIo.emit('rssi_result', rssi_result);
    servIo.emit('last_10', queue);
  }
  else {
    //console.log(pos);
    servIo.emit('counter', pos);            //影像的預測位置
    servIo.emit('rssi_result', rssi_result);//RSSI的預測位置
    servIo.emit('prob_list', prob);         //for 影像的機率分布
    servIo.emit('last_10', queue);          //RSSI最近10次position
  }
  //servIo.emit('counter', toclient);
  //console.log(counter)
}, 1000);

//const { val1, val2 } = pos_to_html(pos);

function isJSONString(str) {
  try {
    JSON.parse(str);
  } catch (e) {
    return false;
  }
  return true;
}
var queue = [];






