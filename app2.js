


var myPythonScript = "./test.py";
var pythonExecutable = "python";
var uint8arrayToString = function (data) {
    return String.fromCharCode.apply(null, data);
};
const spawn = require('child_process').spawn;
// The '-u' tells Python to flush every time
const scriptExecution = spawn(pythonExecutable, ['-u', myPythonScript]);
const scriptExecution2 = spawn(pythonExecutable, ['-u', './test2.py']);
scriptExecution.stdout.on('data', (data) => {
    console.log(uint8arrayToString(data));

});
scriptExecution2.stdout.on('data', (data) => {
    console.log(uint8arrayToString(data));

});
var filename2 = '~/yolov7/realtimeD.py'


