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
//var mqttclient = mqtt.connect("ws://pi:reefberry@192.168.1.217:15675/ws");
var mqttclient = mqtt.connect("ws://pi:reefberry@127.0.0.1:15675/ws");

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

  mqttclient.on("message", function(topic, message) {
    // message is Buffer
    console.log(message.toString());
    //mqttclient.end();
    sendMessage(message.toString());
  });

  /*amqp.connect(
    "amqp://pi:raspberry@192.168.1.168:5672" + "?heartbeat=60",
    function(err, conn) {
      if (err) {
        console.error(getTimeStamp() + " [AMQP]", err.message);
        return setTimeout(start, 1000);
      }
      conn.on("error", function(err) {
        if (err.code == "ECONNRESET") {
          console.error(getTimeStamp() + " [AMQP] reset error", err.code);
        }
        if (err.message !== "Connection closing") {
          console.error(getTimeStamp() + " [AMQP] conn error", err.message);
        }
      });
      conn.on("close", function() {
        console.error(getTimeStamp() + " [AMQP] reconnecting");
        return setTimeout(start, 1000);
      });

      console.log(getTimeStamp() + " [AMQP] connected");
      amqpConn = conn;

      amqpConn.createChannel(function(error1, channel) {
        if (error1) {
          console.log(
            getTimeStamp() + " [AMQP] createChannel error1",
            error1.message
          );
          throw error1;
        }
        channel.assertQueue(
          "",
          {
            exclusive: true
          },
          function(error2, q) {
            if (error2) {
              console.error(
                getTimeStamp() + " [AMQP] createChannel error2",
                error2.message
              );
              throw error2;
            }
            //var correlationId = getUniqueID();
            amqpChannel = channel;
            amqpRPCqueue = q;

            console.log(getTimeStamp() + " [AMQP] Assert Queue");
            //console.log(" [x] Requesting fib");
            channel.consume(
              q.queue,
              function(msg) {
                console.log(
                  getTimeStamp() +
                    " [AMQP] " +
                    msg.properties.correlationId +
                    " vs " +
                    correlationId
                );
                //if (clients[userID].rpcActivity.includes(msg.properties.correlationId)){
                //  console.log("USER ID " + userID);

                Object.keys(clients).map(client => {
                  if (
                    clients[client].rpcActivity.includes(
                      msg.properties.correlationId
                    )
                  ) {
                    //console.log ("Found a match!");

                    //console.log(msg.content.toString().length);
                    // if msg is zero length if caused a crash
                    if (msg.content.toString().length > 0) {
                      console.log(
                        getTimeStamp() + " [AMQP] Recieved: %s",
                        msg.content.toString()
                      );
                      handleRPC(msg);
                    }
                    //console.log(clients[client].rpcActivity);
                    // delete the correlation ID from the clients object after it has been sent
                    for (
                      var i = 0;
                      i < clients[client].rpcActivity.length;
                      i++
                    ) {
                      if (
                        clients[client].rpcActivity[i] ===
                        msg.properties.correlationId
                      ) {
                        clients[client].rpcActivity.splice(i, 1);
                      }
                      //console.log(clients[client].rpcActivity);
                    }
                  }
                  if (clients[client].rpcActivity.length == 0) {
                    console.log(getTimeStamp() + " RPC Queue is empty");
                  } else {
                    console.log(
                      getTimeStamp() + " " + clients[client].rpcActivity.length
                    );
                  }
                });
              },
              {
                noAck: true
              }
            );
            console.log(getTimeStamp() + " [AMQP] queue: " + q.queue);
          }
        ); 
      }); 

      startWorker();
    } 
  ); */
}

// A worker that acks messages only if processed succesfully
function startWorker() {
  amqpConn.createChannel(function(err, ch) {
    if (closeOnErr(err)) return;
    ch.on("error", function(err) {
      console.error("[AMQP] channel error", err.message);
    });
    ch.on("close", function() {
      console.log(getTimeStamp() + " [AMQP] channel closed");
    });
    ch.prefetch(10);

    var exchange = "rbp_currentstatus";
    ch.assertExchange(exchange, "fanout", {
      durable: false
    });

    ch.assertQueue("", { durable: false, exclusive: true }, function(err, q) {
      if (closeOnErr(err)) return;
      ch.bindQueue(q.queue, exchange, "");

      ch.consume("", processMsg, { noAck: true });
      console.log(getTimeStamp() + " [AMQP] Worker is started");
    });

    function processMsg(msg) {
      work(msg, function(ok) {
        try {
          if (ok)
            //ch.ack(msg);
            return;
          else ch.reject(msg, true);
        } catch (e) {
          closeOnErr(e);
        }
      });
    }
  });
}

function work(msg, cb) {
  //console.log("Got msg", msg.content.toString());

  //sendMessage('', msg.content.toString());
  // here
  sendMessage(msg);

  cb(true);
}

function closeOnErr(err) {
  if (!err) return false;
  console.error(getTimeStamp() + " [AMQP] error", err);
  amqpConn.close();
  return true;
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
      console.log("sendMessage", msg);
      //console.log(JSON.parse(msg)["uuid"].toString());
      clients[client].sendUTF(msg);
    } catch (err) {
      console.log(err);
    }
    if (clients[client].rpcActivity[0] != undefined) {
      //if (clients[client].rpcActivity.includes(msg.properties.correlationId)) {
      console.log("line 350", msg);
      //console.log(JSON.parse(msg)["uuid"]);
      if (
        clients[client].rpcActivity.includes(JSON.parse(msg)["uuid"]) !=
        undefined
      ) {
        //console.log(msg.properties.correlationId);
        clients[client].sendUTF(msg);
        console.log("keys:", Object.keys(clients));
        console.log("rpc activity:", clients[client].rpcActivity);
        console.log(msg);
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
  msgJSON = JSON.parse(msg.content.toString());
  rpcKey = Object.keys(msgJSON);

  if ((rpcKey = msgJSON["probelist"])) {
    probeKeys = msgJSON["probelist"];
    console.log(
      getTimeStamp() + " Number of probes: " + Object.keys(probeKeys).length
    );
    console.log(msg.properties.correlationId);
    // sendMessage(msg, msg.content.toString());
    // here
    sendMessage(msg);
  }

  if ((rpcKey = msgJSON["outletlist"])) {
    outletKeys = msgJSON["outletlist"];
    console.log(
      getTimeStamp() + " Number of outlets: " + Object.keys(outletKeys).length
    );
    //sendMessage(msg, msg.content.toString());
    // here
    sendMessage(msg);
  }

  if ((rpcKey = msgJSON["probedata"])) {
    probeKeys = msgJSON["probedata"];
    console.log(msg.properties.correlationId);
    // sendMessage(msg, msg.content.toString());
    // here
    sendMessage(msg);
  }
  if ((rpcKey = msgJSON["probedatadays"])) {
    probeKeys = msgJSON["probedatadays"];
    console.log(msg.properties.correlationId);
    // sendMessage(msg, msg.content.toString());
    // here
    sendMessage(msg);
  }
}

function rpc_call(msg) {
  //correlationId = getUniqueID();
  correlationId = JSON.parse(msg)["uuid"].toString();
  console.log(getTimeStamp() + " RPC call: " + correlationId + " " + msg);

  /* amqpChannel.sendToQueue("rpc_queue", Buffer.from(msg), {
    expiration: 300000,
    correlationId: correlationId,
    replyTo: amqpRPCqueue.queue
  }); */

  mqttclient.publish("reefberrypi/rpc", msg);
}

start();
