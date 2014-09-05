var collector_url = "";
var session_id = "";
var queue = [];
var timeout = undefined;
var data_version = 0;
var SEND_TIMEOUT = 500;
var CLOSE_TIMEOUT = 1000;

function send(entry) {
  queue.push(entry);
  if (timeout == undefined) {
    timeout = setTimeout(sendToServer, SEND_TIMEOUT);
  }
};

function sendToServer() {
  var request = new XMLHttpRequest();
  request.open("POST", collector_url);
  request.onreadystatechange = function() {
    if (request.readyState === 4) {
        if (queue.length > 0) {
          timeout = setTimeout(sendToServer, SEND_TIMEOUT);
        } else {
          timeout = undefined;
        }
    }
  };
 request.setRequestHeader("Content-Type", "application/json");
 var q = queue;
 queue = [];
 request.send(JSON.stringify([session_id, data_version, q]));
};

function attemptClose() {
  if ((timeout == undefined) && (queue.length == 0)) {
    self.close();
  } else {
    setTimeout(attemptClose, CLOSE_TIMEOUT);
  }
};

self.addEventListener("message", function(e) {
    var message = e.data;
    var cmd = message.cmd;
    if (cmd == "post") {
      send(message.entry);
    } else if (cmd == "configure") {
      collector_url = message.url + 'api/v1/upload';
      data_version = message.data_version;
      session_id = message.session_id;
    } else if (cmd == "close") {
      attemptClose();
    }
  }, false);
