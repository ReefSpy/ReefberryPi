///////////////////////////////////////////////////////////////////////////////
// mqttproxy.js
//
// broker communication between the web application and MQTT server
// over websockets
//
// Written by ReefSpy for the ReefBerry Pi, (c) 2020
// www.youtube.com/reefspy
//
///////////////////////////////////////////////////////////////////////////////

console.log(getTimeStamp(), "Reefberry Pi MQTT Proxy starting");

const webSocketServer = require("websocket").server;
const http = require("http");
var fs = require("fs");
var ini = require("ini");

///////////////////////////////////////////////////////////////////////////////
// read configuration from config.ini
///////////////////////////////////////////////////////////////////////////////

if (!fs.existsSync("./config/config.ini")) {
  //file doesn't exist
  console.log(
    getTimeStamp(),
    "Configuration file does not exit, creating file..."
  );
  fs.writeFile("./config/config.ini", "", function(err) {
    console.log(getTimeStamp(), "Configuration file created successfully.");
  });
}
while(!fs.existsSync("./config/config.ini")){
  // wait for file to be created...
}

console.log(getTimeStamp(), "Reading configuration...");
var config = ini.parse(fs.readFileSync("./config/config.ini", "utf-8"));

if (config.mqtt_broker_host == undefined) {
  config.mqtt_broker_host = "127.0.0.1";
  fs.writeFileSync("./config/config.ini", ini.stringify(config));
}

if (config.mqtt_broker_port == undefined) {
  config.mqtt_broker_port = "15675";
  fs.writeFileSync("./config/config.ini", ini.stringify(config));
}

if (config.web_sockets_server_port == undefined) {
  config.web_sockets_server_port = "8001";
  fs.writeFileSync("./config/config.ini", ini.stringify(config));
}

var mqtt_broker_host = config.mqtt_broker_host;
var mqtt_broker_port = config.mqtt_broker_port;
var webSocketsServerPort = config.web_sockets_server_port;

///////////////////////////////////////////////////////////////////////////////
// Spinning up the http server and the websocket server.
///////////////////////////////////////////////////////////////////////////////
const server = http.createServer();
server.listen(webSocketsServerPort);
const wsServer = new webSocketServer({
  httpServer: server
});

console.log(
  getTimeStamp(),
  "Listening on Websocket Port",
  webSocketsServerPort
);

///////////////////////////////////////////////////////////////////////////////
// connect to MQTT server
///////////////////////////////////////////////////////////////////////////////

var mqtt = require("mqtt");
var mqttclient = mqtt.connect(
  "ws://pi:reefberry@" + mqtt_broker_host + ":" + mqtt_broker_port + "/ws"
);
//var mqttclient = mqtt.connect("ws://pi:reefberry@127.0.0.1:15675/ws");

console.log(
  getTimeStamp(),
  "Connected to MQTT Server at",
  mqtt_broker_host + ":" + mqtt_broker_port
);
console.log(getTimeStamp(), "Waiting for communication...");

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
  clients[userID].clientID = userID;
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
    //sendMessage("disconnected");
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
          // handleRPC(msg);
          clients[client].sendUTF(msg);
        }
        console.log(clients[client].rpcActivity);
        console.log(clients[client].clientID);
        // delete the correlation ID from the clients object after it has been sent
        for (var i = 0; i < clients[client].rpcActivity.length; i++) {
          if (clients[client].rpcActivity[i] === JSON.parse(msg)["uuid"]) {
            console.log("delete rpc from list");
            clients[client].rpcActivity.splice(i, 1);
          }
          //console.log(clients[client].rpcActivity);
        }
        return;
      } else {
        if (msg.toString().includes(["status_currentprobeval"])) {
          //console.log(getTimeStamp(), clients[client].clientID, msg.toString());
          clients[client].sendUTF(msg);
        } else if (msg.toString().includes(["status_currentoutletstate"])) {
          //console.log(getTimeStamp(), clients[client].clientID, msg.toString());
          clients[client].sendUTF(msg);
        } else if (msg.toString().includes(["status_feedmode"])) {
          //console.log(getTimeStamp(), clients[client].clientID, msg.toString());
          clients[client].sendUTF(msg);
        }

        // console.log(getTimeStamp(), clients[client].clientID, "outletstatus");
        // clients[client].sendUTF(msg);
      }
    });

    //sendMessage(msg.toString());
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
      console.log("sending message to", Object.keys(clients));
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

function rpc_call(msg) {
  //correlationId = getUniqueID();
  correlationId = JSON.parse(msg)["uuid"].toString();
  console.log(getTimeStamp() + " RPC call: " + correlationId + " " + msg);

  mqttclient.publish("reefberrypi/rpc", msg);
}

start();
