var net = require('net');
var k = "2";
var beacon_id = '0';
var Rssi = '0';
//var exec = require('child_process').exec;
//var filename = 'Hashing_KNN.py'
// var filename = '/home/mcs/troy2/ANN.py'
// var filename2 = '/home/mcs/yolov7/realtimeD.py'
let buffer = new Array(7);
buffer = ['0', '0', '0', '0', '0', '0', '000']; 
var Beacon_RSSi = '';
var t = 0;
var beacon_int = 0
var Rssi_int = 0;
var toclient = '0';
var pos = '608'
let pythonProcess = null;


const fs = require('fs');
//const lockfile = require('lockfile'); //Synchronize control.py 和 app.js rssi_buffer.csv用
const filePath = 'rssi_buffer.csv';
//const lockFilePath = 'l.lock';

function writeToCsvFile(Beacon_RSSi) {
  // // Check if the lock file already exists
  // try {
  //     if (fs.existsSync(lockFilePath)) {
  //         setTimeout(() => {
  //             writeToCsvFile(Beacon_RSSi); // Retry after a delay
  //         }, 1); // Adjust the delay as needed
  //         return;
  //     }
  // } catch (error) {
  //     console.error("Error checking lock file:", error);
  //     return;
  // }

  // lockfile.lock(lockFilePath, { retries: 10, retryWait: 100, stale: 10 }, (lockErr) => {
  //     if (lockErr) {
  //         console.error("Error locking the file:", lockErr);
  //         // You can retry or handle the error here
  //     } else {
  //         fs.writeFile(filePath, `${Beacon_RSSi}\n`, (err) => {
  //             if (err) {
  //                 console.error("Error writing to the file:", err);
  //             } else {
  //                 console.log("Data written to file successfully.");
  //             }
  //             lockfile.unlock(lockFilePath, (unlockErr) => {
  //                 if (unlockErr) {
  //                     console.error("Error unlocking the file:", unlockErr);
  //                 }
  //                 // Continue processing or exit the script as needed
  //             });
  //         });
  //     }
  // });
  const sanitizedBeacon_RSSi = Beacon_RSSi.replace(/\x00/g, '').replace(/\x03/g, '');
  fs.writeFile(filePath, `${sanitizedBeacon_RSSi}\n`, (err) => {
    if (err) {
        console.error("Error writing to the file:", err);
    } else {
        console.log("Data written to file successfully.");
    }
  });


}





function full(Array) {
  for (let i = 0; i < Array.length ; i++) {
    if (Array[i] == '0')
      return false;
  }
  return true;
}


var count = 0;

var clientHandler = function (socket) {
  //客戶端傳送資料的時候觸發data事件
  socket.on('data', function dataHandler(data) {//data是客戶端傳送給伺服器的資料
    //console.log("app.js", data);
    k = data.toString();
    //console.log(k)
    if(!k.includes(",")){ //分辨傳過來的是不是groundtruth座標
      buffer[6] = k;
      console.log(buffer[6]);
    }
    else{
      var K = k.split(",", 2);
      beacon_id = K[0];
      Rssi = K[1];
      let numStr = beacon_id.replace(/[^0-9]/ig, "");
      beacon_int = parseInt(numStr);
      Rssi_int = parseInt(Rssi);
      //console.log("app.js", beacon_int,Rssi_int);
      Rssi_int = (Rssi_int + 103) / (-48 + 103); //min-max normalization
      if (beacon_int == 7) {
        buffer[5] = Rssi_int;
      }//因為用1 2 3 4 5 7
      else
        buffer[beacon_int - 1] = Rssi_int;
      if(full(buffer)){ //full 邏輯是buffer裡全部值都不是0才成立, 所以6個rssi值沒收滿前不會成立
        Beacon_RSSi = `{q"Beacon_1q":q"${buffer[0]}q",q"Beacon_2q":q"${buffer[1]}q",q"Beacon_3q":q"${buffer[2]}q",q"Beacon_4q":q"${buffer[3]}q",q"Beacon_5q":q"${buffer[4]}q",q"Beacon_7q":q"${buffer[5]}q", q"Ground_truthq":q"${buffer[6]}q"}`;
        console.log("app.js", Beacon_RSSi)
        writeToCsvFile(Beacon_RSSi)
        buffer = ['0', '0', '0', '0', '0', '0', '000']; //還原等收下一次值，第7個(buffer[6])是groundtruth position
        count++;
      }
    }
    socket.write(toclient);
  });

  //當對方的連線斷開以後的事件
  socket.on('close', function () {
    socket.destroy(); 
    //pythonProcess.stdin.end();
    //console.log(socket.remoteAddress, socket.remotePort, 'disconnected'); 
  })
  socket.on('error', (err) => {
    console.log(err);
  })
  //socket.write(toclient);
};

var app = net.createServer(clientHandler);
app.listen(8000, '140.116.72.77');//change to server

console.log('tcp server running on tcp://', '140.116.72.77', ':', 8000);

//-------------------------------------->處理網頁的---------------------------------------------------------


const http = require("http");
var express = require('express');
var app2 = express();

app2.use(express.static(__dirname + '/public'));//重要 遠端把根目錄設在public裡  裡面放css js 圖片等等
app2.get('/', (req, res) => {
  //res.sendFile(__dirname + '/dd.html');
  res.sendFile(__dirname + '/public/map2.html');
})



//控制要RSSI IMAGE 或兩個一起
var type = 0;//  0:RSSI     1:Image    2:Both
var realtime = '0';
var particle_prev_count = 0;
var data_date = '0';
var prob = ['601', '601', '601', '601', '601', '601', '601', '601', '601', '601'];
//let pythonProcess = null;
const { spawn } = require('child_process');








function startPythonProcess() { //執行control.py
  processactivate = 1;
  //console.log('app.js start control.py');
  const pythonArgs = [type, realtime, Beacon_RSSi, particle_prev_count]; //抓argument的時候從1開始
  const pythonFile = '/home/mcs/troy2/control.py';
  if (pythonProcess) { //換type的時候要砍掉process重新執行
    pythonProcess.kill();
  }
  pythonProcess = spawn('python', ['-u', pythonFile, ...pythonArgs], { stdio: ['pipe', 'pipe', 'pipe'] });
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







app2.get('/change_type', function (req, res) {
  type = req.query.value;
  fs.writeFile('./calculate_type.txt', type, function (error) {
  })
  startPythonProcess();
})
app2.get('/change_data_input', function (req, res) {
  realtime = req.query.value;
  fs.writeFile('./change_data_input.txt', realtime, function (error) {
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
    servIo.emit('last_10', queue);
  }
  else {
    //console.log(pos);
    servIo.emit('counter', pos);
    servIo.emit('rssi_result', pos);
    servIo.emit('prob_list', prob);
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
processactivate = 0;






