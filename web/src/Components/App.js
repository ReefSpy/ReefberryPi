import React, { Component, Fragment } from "react";
import "./App.css";
import { w3cwebsocket as W3CWebSocket } from "websocket";
import uuid from "uuid";
import { Header } from "./Layouts";

import TabBar from "./Layouts/TabBar";
//import ProbeWidget from "./RBP/ProbeWidget";

const client = new W3CWebSocket("ws://127.0.0.1:8001");
//const client = new W3CWebSocket("ws://192.168.1.217:8001");

const buttonStates = ["OFF", "AUTO", "ON"];

export default class extends Component {
  constructor(props) {
    super(props);
    this.state = {
      probeList: null,
      outletList: null,
      probeListArray: [],
      outletListArray: [],
      probeValueArray: [],
      primaryChartData: [],
      appConfig: "",
      feedmode: {
        feedtimer: null,
        timeremaining: null
      }
    };
  }
  handleFeedWidgetClick(val) {
    console.log("App got the feed click! " + val);
    // send request over to server
    client.send(
      JSON.stringify({
        rpc_req: "set_feedmode",
        feedmode: val,
        uuid: uuid.v4()
      })
    );
  }

  handleConfigSave(section, key, value) {
    console.log("App got the config change request:", section, key, value);
    // send request over to server

    client.send(
      JSON.stringify({
        rpc_req: "set_writeinifile",
        section: section,
        key: key,
        value: value,
        uuid: uuid.v4()
      })
    );
    // reload config after a short delay to give time to process on
    // controller, then we will grab new values again
    setTimeout(this.handleConfigLoad, 1000);
  }

  /* handleConfigLoad(section, key, defaultVal) {
    console.log("App got the config load request:", section, key, defaultVal);

    try {
      client.send(
        JSON.stringify({
          rpc_req: "get_readinifile",
          section: section,
          key: key,
          defaultval: defaultVal,
          uuid: uuid.v4()
        })
      );
    } catch (err) {
      console.log(err);
    }
    return "130"; // temp return val for testing
  } */

  handleConfigLoad() {
    console.log("App got the config load request");
    try {
      client.send(
        JSON.stringify({
          rpc_req: "get_appconfig",
          uuid: uuid.v4()
        })
      );
    } catch (err) {
      console.log(err);
    }
  }

  handlePrimaryChartSelect(value) {
    console.log("App got the chart request! " + value);
    this.getChartDataDays();
  }

  handleOutletWidgetClick(val, outletid) {
    console.log("App got the click! " + val + " " + outletid);
    var outletListArrayClone = this.state.outletListArray.slice(0);
    for (var outletClone in outletListArrayClone) {
      //console.log(outletListArrayClone[outletClone]);
      if (outletListArrayClone[outletClone]["outletid"] === outletid) {
        console.log("I found a match");
        outletListArrayClone[outletClone]["statusmsg"] = "waiting...";
        outletListArrayClone[outletClone]["buttonstate"] = buttonStates[val];
        outletListArrayClone[outletClone]["buttonstateidx"] = val;

        //console.log(outletListArrayClone);
        // set state so prop can trickle down to widget and change the button
        this.setState({ outletListArray: outletListArrayClone });
        //console.log(this.state.outletListArray);
        // last value in outlet ID is the outlet number
        var outletnum = outletid.split("_");
        outletnum = outletnum[outletnum.length - 1];
        // send request over to server
        client.send(
          JSON.stringify({
            rpc_req: "set_outletoperationmode",
            bus: outletListArrayClone[outletClone]["outletbus"],
            outletnum: outletnum,
            opmode: buttonStates[val],
            uuid: uuid.v4()
          })
        );
      }
    }
  }
  componentWillMount() {
    client.onopen = () => {
      console.log("WebSocket Client Connected");
      client.send(
        JSON.stringify({ rpc_req: "get_probelist", uuid: uuid.v4() })
      );
      client.send(
        JSON.stringify({ rpc_req: "get_outletlist", uuid: uuid.v4() })
      );
      this.handleConfigLoad();
    };
    client.onmessage = message => {
      //console.log(message);
      var msgJSON = JSON.parse(message.data);
      //console.log(Object.keys(msgJSON).toString());
      //if (Object.keys(msgJSON).toString() != "status_currentoutletstate") {
      //  console.log(message);
      //}
      //console.log(msgJSON);
      //console.log(JSON.stringify(msgJSON));
      //if (Object.keys(msgJSON).toString() === "probelist") {
      if (msgJSON.hasOwnProperty("probelist")) {
        this.handleProbelist(msgJSON);
        this.getChartData(msgJSON);
      }
      //if (Object.keys(msgJSON).toString() === "outletlist") {
      if (msgJSON.hasOwnProperty("outletlist")) {
        this.handleOutletlist(msgJSON);
      }
      //if (Object.keys(msgJSON).toString() === "status_currentprobeval") {
      if (msgJSON.hasOwnProperty("status_currentprobeval")) {
        // console.log("Got probeval");
        // console.log(msgJSON["status_currentprobeval"]["probeid"]);
        var { probeListArrayClone, probeClone } = this.handleCurrentProbeVal(
          msgJSON
        );
      }
      //if (Object.keys(msgJSON).toString() === "status_currentoutletstate") {
      if (msgJSON.hasOwnProperty("status_currentoutletstate")) {
        //console.log("Got outletstate");
        this.handleCurrentOutletState(msgJSON);
      }
      //if (Object.keys(msgJSON).toString() === "status_feedmode") {
      if (msgJSON.hasOwnProperty("status_feedmode")) {
        //console.log("Feed Mode");
        this.handleFeedMode(msgJSON);
      }
      //if (Object.keys(msgJSON).toString() === "probedata") {
      if (msgJSON.hasOwnProperty("probedata")) {
        console.log("Got probedata for chart");
        // console.log(msgJSON["probedata"]["probeid"]);

        probeListArrayClone = this.handleProbeData(
          probeListArrayClone,
          probeClone,
          msgJSON
        );
      }
      //if (Object.keys(msgJSON).toString() === "probedatadays") {
      if (msgJSON.hasOwnProperty("probedatadays")) {
        console.log("Got probedatadays for chart");
        //console.log(msgJSON["probedata"]["probeid"]);

        this.handleGraphPageData(msgJSON);
      }
      if (msgJSON.hasOwnProperty("readinifile")) {
        console.log(
          "Got readinifile value",
          msgJSON["readinifile"],
          msgJSON["uuid"]
        );
        this.setState({ configReturnVal: msgJSON["uuid"] });
      }
      if (msgJSON.hasOwnProperty("get_appconfig")) {
        console.log("Got appConfig value", msgJSON["uuid"]);
        console.log(JSON.parse(msgJSON["get_appconfig"]));
        this.setState({ appConfig: JSON.parse(msgJSON["get_appconfig"]) });
        console.log("feed a:", this.state.appConfig["feed_a_time"]);
      }
    };
  }
  handleFeedMode(msgJSON) {
    this.setState({
      feedmode: {
        feedtimer: msgJSON["status_feedmode"]["feedmode"],
        timeremaining: msgJSON["status_feedmode"]["timeremaining"]
      }
    });
    //console.log(this.state.feedmode)
  }
  handleCurrentProbeVal(msgJSON) {
    var probeListArrayClone = this.state.probeListArray.slice(0);
    for (var probeClone in probeListArrayClone) {
      //console.log(probeListArrayClone[probeClone]);
      if (
        probeListArrayClone[probeClone]["probeid"] ===
        msgJSON["status_currentprobeval"]["probeid"]
      ) {
        probeListArrayClone[probeClone]["probeval"] =
          msgJSON["status_currentprobeval"]["probeval"];
        this.setState({ probeListArray: probeListArrayClone });
      }
    }
    return { probeListArrayClone, probeClone };
  }

  handleProbelist(msgJSON) {
    console.log(msgJSON["probelist"].toString());
    var probeArray = [];
    this.setState({ probeList: msgJSON });
    for (var probe in msgJSON["probelist"]) {
      msgJSON["probelist"][probe]["probeval"] = "--";
      probeArray.push(msgJSON["probelist"][probe]);
      //console.log(probeArray);
    }
    console.log(probeArray);
    this.setState({ probeListArray: probeArray });
  }

  getChartData(msgJSON) {
    console.log("Getting Chart data");
    for (var probe in msgJSON["probelist"]) {
      console.log(msgJSON["probelist"][probe]["probetype"]);
      console.log(msgJSON["probelist"][probe]["probeid"]);
      client.send(
        JSON.stringify({
          rpc_req: "get_probedata24h_ex",
          probetype: msgJSON["probelist"][probe]["probetype"],
          probeid: msgJSON["probelist"][probe]["probeid"],
          uuid: uuid.v4()
        })
      );
    }
  }

  getChartDataDays() {
    console.log("Getting Chart data days");
    console.log("ds18b20");
    console.log("ds18b20_28-0416525f5eff");
    client.send(
      JSON.stringify({
        rpc_req: "get_probedatadays_ex",
        probetype: "ds18b20",
        probeid: "ds18b20_28-0416525f5eff",
        numdays: "30",
        uuid: uuid.v4()
      })
    );
  }

  handleOutletlist(msgJSON) {
    // console.log("Got outlet list", msgJSON);
    this.setState({ outletList: msgJSON });
    var outletArray = [];
    for (var outlet in msgJSON["outletlist"]) {
      msgJSON["outletlist"][outlet]["statusmsg"] = "waiting...";
      msgJSON["outletlist"][outlet]["buttonstate"] = "waiting...";
      msgJSON["outletlist"][outlet]["buttonstateidx"] = buttonStates.indexOf(
        "AUTO"
      );
      outletArray.push(msgJSON["outletlist"][outlet]);
    }
    // sort the array by outlet id
    // sort by name
    outletArray.sort(function(a, b) {
      var idA = a.outletid.toUpperCase(); // ignore upper and lowercase
      var idB = b.outletid.toUpperCase(); // ignore upper and lowercase
      if (idA < idB) {
        return -1;
      }
      if (idA > idB) {
        return 1;
      }

      // names must be equal
      return 0;
    });
    console.log("Outlet array");
    console.log(outletArray);
    this.setState({ outletListArray: outletArray });
  }

  handleCurrentOutletState(msgJSON) {
    var outletListArrayClone = this.state.outletListArray.slice(0);
    for (var outletClone in outletListArrayClone) {
      //console.log(outletListArrayClone[outletClone]);
      if (
        outletListArrayClone[outletClone]["outletid"] ===
        msgJSON["status_currentoutletstate"]["outletid"]
      ) {
        //console.log(msgJSON["status_currentoutletstate"]["button_state"]);
        outletListArrayClone[outletClone]["buttonstate"] =
          msgJSON["status_currentoutletstate"]["button_state"];
        outletListArrayClone[outletClone]["statusmsg"] =
          msgJSON["status_currentoutletstate"]["statusmsg"];
        outletListArrayClone[outletClone][
          "buttonstateidx"
        ] = buttonStates.indexOf(
          msgJSON["status_currentoutletstate"]["button_state"]
        );
        // this.setState({ outletListArray: outletListArrayClone });
      }
    }
    // console.log("handleCurrentOutletState");
  }

  handleProbeData(probeListArrayClone, probeClone, msgJSON) {
    probeListArrayClone = this.state.probeListArray.slice(0);
    for (probeClone in probeListArrayClone) {
      //console.log("probeclone: ", probeListArrayClone[probeClone]);
      if (
        probeListArrayClone[probeClone]["probeid"] ===
        msgJSON["probedata"]["probeid"]
      ) {
        // we need to zip the date array and value arrays togther
        console.log("match");
        var a = msgJSON["probedata"]["datetime"],
          b = msgJSON["probedata"]["probevalue"],
          bplus = b.map(Number);
        var c = [];
        for (var i = 0; i < a.length; i++) {
          c.push([a[i], bplus[i]]);
        }
        //console.log(c); // [[1, "a"], [2, "b"], [3, "c"]]
        probeListArrayClone[probeClone]["chartdata"] = c;
        //probeListArrayClone[probeClone]["chartdata"] = bplus;
        console.log("probeListArrayClone:", probeListArrayClone);
        console.log("probeListArray:", this.state.probeListArray);
        console.log(msgJSON);

        this.setState({ probeListArray: probeListArrayClone });
        // console.log("state");
        console.log("probeListArray:", this.state.probeListArray);
      }
    }
    return probeListArrayClone;
  }

  handleGraphPageData(msgJSON) {
    console.log("HandleGraphPageData");
    var primaryChartDataClone = this.state.primaryChartData.slice(0);

    // we need to zip the date array and value arrays togther
    var a = msgJSON["probedatadays"]["datetime"],
      b = msgJSON["probedatadays"]["probevalue"],
      bplus = b.map(Number);
    var c = [];
    for (var i = 0; i < a.length; i++) {
      c.push([Date.parse(a[i].replace(" ", "T")), bplus[i]]);
    }
    //console.log(c); // [[1, "a"], [2, "b"], [3, "c"]]
    primaryChartDataClone = c;
    //probeListArrayClone[probeClone]["chartdata"] = bplus;
    console.log("merged data");
    console.log(primaryChartDataClone);
    //console.log(msgJSON);

    this.setState({ primaryChartData: primaryChartDataClone });
    // console.log("state");
    console.log(this.state.primaryChartData);

    return primaryChartDataClone;
  }

  render() {
    return (
      <Fragment>
        <div className="rbp-dashboard">
          <div>
            <Header />
            <TabBar
              probes={this.state.probeListArray}
              probevals={this.state.probeValueArray}
              outlets={this.state.outletListArray}
              feedmode={this.state.feedmode}
              onOutletWidgetClick={this.handleOutletWidgetClick.bind(this)}
              onFeedWidgetClick={this.handleFeedWidgetClick.bind(this)}
              onConfigSave={this.handleConfigSave.bind(this)}
              onConfigLoad={this.handleConfigLoad.bind(this)}
              onPrimaryChartSelect={this.handlePrimaryChartSelect.bind(this)}
              primaryChartData={this.state.primaryChartData}
              appConfig={this.state.appConfig}
            />
          </div>
        </div>
      </Fragment>
    );
  }
}
