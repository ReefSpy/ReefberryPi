const webSocketsServerPort = 8001;
const webSocketServer = require("websocket").server;
const http = require("http");
// Spinning the http server and the websocket server.
const server = http.createServer();
server.listen(webSocketsServerPort);
const wsServer = new webSocketServer({
  httpServer: server
});

//var amqp = require("amqplib/callback_api");

var mqtt = require("mqtt");
var mqttclient = mqtt.connect("ws://pi:reefberry@192.168.1.217:15675/ws");
//var mqttclient = mqtt.connect("ws://pi:reefberry@127.0.0.1:15675/ws");

// if the connection is closed or fails to be established at all, we will reconnect
//var amqpConn = null;
//var amqpChannel = null;
var amqpRPCqueue = null;
var correlationId = null;

// I'm maintaining all active connections in this object
const clients = {};
// I'm maintaining all active users in this object
const users = {};
// The current editor content is maintained here.
let editorContent = null;
// User activity history.
let userActivity = [];

wsServer.on("request", function(request) {
  var userID = getUniqueID();
  console.log(
    getTimeStamp() +
      " [WS] Recieved a new connection from origin " +
      request.origin +
      "."
  );
  // You can rewrite this part of the code to accept only the requests from allowed origin
  const connection = request.accept(null, request.origin);
  clients[userID] = connection;
  clients[userID].rpcActivity = []; // create array to hold the uuids for commands sent in
  //console.log(clients);

  console.log(
    getTimeStamp() +
      " [WS] connected: " +
      userID +
      " in " +
      Object.getOwnPropertyNames(clients)
  );
  // when message recieved from client
  connection.on("message", function(message) {
    console.log(
      getTimeStamp() + " [WS] " + message.utf8Data + " from " + userID
    );
    clients[userID].rpcActivity.push(JSON.parse(message.utf8Data)["uuid"]); // add this request id to the list so we can compare it later
    console.log(
      getTimeStamp() +
        " ClientID: " +
        userID +
        " | RPC Activity: " +
        clients[userID].rpcActivity
    );
    rpc_call(message.utf8Data);
  });

  // user disconnected
  connection.on("close", function(connection) {
    console.log(getTimeStamp() + " [WS] Peer " + userID + " disconnected.");
    //const json = { type: typesDef.USER_EVENT };
    // userActivity.push(`${users[userID].username} left the document`);
    //json.data = { users, userActivity };
    delete clients[userID];
    delete users[userID];

    //sendMessage(JSON.stringify(json));
    // sendMessage('', 'disconnected');
    // here
    sendMessage("disconnected");
  });
});

function start() {
  mqttclient.on("connect", function() {
    mqttclient.subscribe("reefberrypi/demo", function(err) {
      if (!err) {
        //mqttclient.publish("reefberrypi/demo", "Hello mqtt");
      }
    });
  });

  mqttclient.on("message", function(topic, msg) {
    // message is Buffer
    //console.log(msg.toString());
    //mqttclient.end();
    //console.log("uuid: ", JSON.parse(msg)["uuid"]);
    Object.keys(clients).map(client => {
      //if (clients[client].rpcActivity.includes(msg.properties.correlationId)) {
      if (clients[client].rpcActivity.includes(JSON.parse(msg)["uuid"])) {
        console.log("Found a match!");

        //console.log(msg.content.toString().length);
        // if msg is zero length if caused a crash
        if (msg.toString().length > 0) {
          console.log(getTimeStamp() + " [MQTT] Recieved: %s", msg.toString());
          handleRPC(msg);
        }
        console.log(clients[client].rpcActivity);
        // delete the correlation ID from the clients object after it has been sent
        for (var i = 0; i < clients[client].rpcActivity.length; i++) {
          if (clients[client].rpcActivity[i] === JSON.parse(msg)["uuid"]) {
            console.log("delete rpc from list");
            clients[client].rpcActivity.splice(i, 1);
          }
          //console.log(clients[client].rpcActivity);
        }
      }
      if (clients[client].rpcActivity.length == 0) {
        //console.log(getTimeStamp() + " RPC Queue is empty");
      } else {
        //console.log(JSON.parse(msg)["uuid"]);
        //console.log(clients[client].rpcActivity);
        console.log(getTimeStamp() + " " + clients[client].rpcActivity.length);
      }
    });

    sendMessage(msg.toString());
  });
}

// Generates unique ID for every new connection
const getUniqueID = () => {
  const s4 = () =>
    Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
  return s4() + s4() + "-" + s4();
};

function getTimeStamp() {
  var timeNow = new Date();

  timeStamp =
    timeNow.getFullYear() +
    "-" +
    getMonth(timeNow) +
    "-" +
    getDay(timeNow) +
    " " +
    getHour(timeNow) +
    ":" +
    getMinute(timeNow) +
    ":" +
    getSecond(timeNow) +
    "." +
    getMilliSecond(timeNow);

  function getMonth(date) {
    var month = date.getMonth() + 1;
    return month < 10 ? "0" + month : "" + month; // ('' + month) for string result
  }
  function getDay(date) {
    var day = date.getDate();
    return day < 10 ? "0" + day : "" + day; // ('' + day) for string result
  }
  function getHour(date) {
    var hour = date.getHours();
    return hour < 10 ? "0" + hour : "" + hour; // ('' + hour) for string result
  }
  function getMinute(date) {
    var minute = date.getMinutes();
    return minute < 10 ? "0" + minute : "" + minute; // ('' + minute) for string result
  }
  function getSecond(date) {
    var second = date.getSeconds();
    return second < 10 ? "0" + second : "" + second; // ('' + second) for string result
  }
  function getMilliSecond(date) {
    var millisecond = date.getMilliseconds();
    if (millisecond.toString().length == 1) {
      return "00" + millisecond; // ('' + millisecond) for string result
    } else if (millisecond.toString().length == 2) {
      return "0" + millisecond; // ('' + millisecond) for string result
    } else {
      return millisecond;
    }
  }

  return timeStamp;
}

const sendMessage = msg => {
  // We are sending the current data to all connected client
  Object.keys(clients).map(client => {
    // uncomment to send status updates
    try {
      //console.log("sendMessage", msg);
      //console.log(JSON.parse(msg)["uuid"].toString());
      clients[client].sendUTF(msg);
    } catch (err) {
      console.log(err);
    }
    if (clients[client].rpcActivity[0] != undefined) {
      //if (clients[client].rpcActivity.includes(msg.properties.correlationId)) {
      //console.log(JSON.parse(msg)["uuid"]);
      if (
        clients[client].rpcActivity.includes(JSON.parse(msg)["uuid"]) !=
        undefined
      ) {
        //console.log(msg.properties.correlationId);
        clients[client].sendUTF(msg);
        console.log("keys:", Object.keys(clients));
        console.log("rpc activity:", clients[client].rpcActivity);
        //console.log(msg);
      }
    }

    // console.log(getTimeStamp()  + ' [WS] msg sent to ' + userID);
  });
};

//const typesDef = {
//  USER_EVENT: "userevent",
//  CONTENT_CHANGE: "contentchange"
//}

function handleRPC(msg) {
  console.log("Handle RPC");
  msgJSON = JSON.parse(msg.toString());
  rpcKey = Object.keys(msgJSON);

  if ((rpcKey = msgJSON["probelist"])) {
    probeKeys = msgJSON["probelist"];
    console.log(
      getTimeStamp() + " Number of probes: " + Object.keys(probeKeys).length
    );
    console.log(JSON.parse(msg)["uuid"]);
    // sendMessage(msg, msg.content.toString());
    // here
    sendMessage(msg.toString());
  }

  if ((rpcKey = msgJSON["outletlist"])) {
    outletKeys = msgJSON["outletlist"];
    console.log(
      getTimeStamp() + " Number of outlets: " + Object.keys(outletKeys).length
    );
    //sendMessage(msg, msg.content.toString());
    // here
    sendMessage(msg.toString());
  }

  if ((rpcKey = msgJSON["probedata"])) {
    probeKeys = msgJSON["probedata"];
    console.log(JSON.parse(msg)["uuid"]);
    // sendMessage(msg, msg.content.toString());
    // here
    sendMessage(msg.toString());
  }
  if ((rpcKey = msgJSON["probedatadays"])) {
    probeKeys = msgJSON["probedatadays"];
    console.log(JSON.parse(msg)["uuid"]);
    // sendMessage(msg, msg.content.toString());
    // here
    sendMessage(msg.toString());
  }
}

function rpc_call(msg) {
  //correlationId = getUniqueID();
  correlationId = JSON.parse(msg)["uuid"].toString();
  console.log(getTimeStamp() + " RPC call: " + correlationId + " " + msg);

  mqttclient.publish("reefberrypi/rpc", msg);
}

start();
