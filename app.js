var net = require('net');
var k = "2";
var beacon_id = '0';
var Rssi = '0';
//var exec = require('child_process').exec;
//var filename = 'Hashing_KNN.py'
// var filename = '/home/mcs/troy2/ANN.py'
// var filename2 = '/home/mcs/yolov7/realtimeD.py'


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
var pos = '608'

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
    Rssi_int = (Rssi_int + 103) / (-48 + 103); //min-max normalization
    if (beacon_int == 7) {
      buffer[5] = Rssi_int;
    }//因為用1 2 3 4 5 7
    else
      buffer[beacon_int - 1] = Rssi_int;
    if (full(buffer)) {
      Beacon_RSSi = `{q"Beacon_1q":q"${
        [0]}q",q"Beacon_2q":q"${buffer[1]}q",q"Beacon_3q":q"${buffer[2]}q",q"Beacon_4q":q"${buffer[3]}q",q"Beacon_5q":q"${buffer[4]}q",q"Beacon_7q":q"${buffer[5]}q"}`;
      console.log(Beacon_RSSi);
      buffer = ['0', '0', '0', '0', '0', '0'];
      count++;
    }
    socket.write(toclient);
  });

  //當對方的連線斷開以後的事件
  socket.on('end', () => { 
    socket.destroy(); 
  });
  socket.on('close', function () {
    console.log(socket.remoteAddress, socket.remotePort, 'disconnected');
  })
  socket.on('error', (err) => {
    console.log(err);
  })
  //socket.write(toclient);
};

var app = net.createServer(clientHandler);
port = 8000
app.listen(port, '140.116.72.77');//change to server
console.log('tcp server running on tcp://', '140.116.72.77', ':', port);

//---------------------------------------->處理網頁的----------------------------------------------


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
var realtime = '0';
var particle_prev_count = 0;
var data_date = '0';
var prob = ['601', '601', '601', '601', '601', '601', '601', '601', '601', '601'];
let pythonProcess = null;
const { spawn } = require('child_process');




function startPythonProcess() { //執行control.py
  const pythonArgs = [type, realtime, Beacon_RSSi, particle_prev_count]; //抓argument的時候從1開始
  const pythonFile = '/home/mcs/LabLocalizationWeb/control.py';
  if (pythonProcess) { //換type的時候要砍掉process重新執行
    pythonProcess.kill();
  }
  pythonProcess = spawn('python', [pythonFile, ...pythonArgs]);
  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    console.log('Result: ', output);
    
    try { //處裡影像丟的預測機率
      const outputArray = JSON.parse(output);
      if (Array.isArray(outputArray)) {
        pos = outputArray[0];
        prob = outputArray[1];
      } else {
        pos = output;
      }
    } catch (error) {
      pos = output;
    }


    console.log('position:', pos);
    console.log('prob:', prob);

    fs.writeFile('./rssi_result.txt', pos, function (error) {
      if (error) {
        console.error('Error writing to file:', error);
      }
    });

    if (type == 0) {
      if (queue.length < 10) {
        queue.push(pos);
      } else {
        queue.shift();
        queue.push(pos);
      }
    }
  });

  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error executing the Python file: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python script process exited with code ${code}`);
  });
}




app2.get('/change_data_input', function (req, res) {
  realtime = req.query.value;
  fs.writeFile('./data_input.txt', realtime, function (error) {
  })
  startPythonProcess();
})



app2.get('/change_type', function (req, res) {
  type = req.query.value;
  fs.writeFile('./calculate_type.txt', type, function (error) {
  })
  startPythonProcess();
})
app2.get('/change_particle', function (req, res) {
  particle_prev_count = req.query.value;
  fs.writeFile('./particle_prev_count.txt', particle_prev_count, function (error) {
    startPythonProcess();
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
  console.log('Express started')
})

var servIo = io.listen(server);



//let counter = 50;
setInterval(() => {
  //console.log(type);
  //rssi_result = '605';
  if (type == 0) {
    servIo.emit('counter', pos);//用RSSI結果來當最終結果
    servIo.emit('rssi_result', pos);
    servIo.emit('realtime_rssi', prob);
    servIo.emit('last_10', queue);
  }
  else {
    //console.log(pos);
    servIo.emit('counter', pos);
    servIo.emit('rssi_result', pos);
    servIo.emit('realtime_rssi', prob);
    //servIo.emit('prob_list', prob);
    servIo.emit('last_10', queue);
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






