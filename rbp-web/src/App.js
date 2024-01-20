import React, { Component } from "react";
import { ProbeWidget } from "./Components/ProbeWidget/ProbeWidget";
import { OutletWidget } from "./Components/OutletWidget/OutletWidget";
import appicon from "./Images/reefberry-pi-logo.svg";
import "./App.css";


class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      apiResponse: null,
      ProbeArray: [],
      OutletArray: [],
      DHTArray: [],
      AppUID: "",
    };

    this.setProbeData = this.setProbeData.bind(this);
    this.setOutletData = this.setOutletData.bind(this);
    this.createOutletSet = this.createOutletSet.bind(this);
    this.handleOutletButtonClick = this.handleOutletButtonClick.bind(this);
    this.handleCurrentOutletState = this.handleCurrentOutletState.bind(this);
    this.setDHTData = this.setDHTData.bind(this);
  }

  async componentDidMount() {
    document.title = "Reefberry Pi";
    // probe list
    console.log( process.env.REACT_APP_API_GET_TEMPPROBE_LIST)
    this.apiCall(process.env.REACT_APP_API_GET_TEMPPROBE_LIST, this.setProbeData);
    this.interval = setInterval(() => {
      this.apiCall(process.env.REACT_APP_API_GET_TEMPPROBE_LIST, this.setProbeData);
    }, 2000);
    // outlet list
    this.apiCall(process.env.REACT_APP_API_GET_OUTLET_LIST, this.createOutletSet);
    this.interval2 = setInterval(() => {
      this.apiCall(process.env.REACT_APP_API_GET_OUTLET_LIST, this.handleCurrentOutletState);
    }, 2000);
    // dht sensor list
    this.apiCall(process.env.REACT_APP_API_GET_DHT_SENSOR, this.setDHTData);
    this.interval3 = setInterval(() => {
      this.apiCall(process.env.REACT_APP_API_GET_DHT_SENSOR, this.setDHTData);
    }, 2000);
  }

  // generic API call structure
  apiCall(endpoint, callback) {
    fetch(endpoint)
      .then((response) => {
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Data not found");
          } else if (response.status === 500) {
            throw new Error("Server error");
          } else {
            throw new Error("Network response was not ok");
          }
        }
        return response.json();
      })
      .then((data) => {
        this.setState({ apiResponse: data });
        callback(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  setDHTData(probedata) {
    console.log(probedata);
    let DHTArray = [];
    for (let probe in probedata) {
      DHTArray.push(probedata[probe]);
    }
    if (DHTArray.length > 0) {
      this.setState({ DHTArray });
    }
    // console.log(ProbeArray);
    return DHTArray;
  }

  setProbeData(probedata) {
    console.log(probedata);

    let ProbeArray = [];
    for (let probe in probedata) {
      // let probename = probedata[probe]["probename"];
      // let lastTemp = probedata[probe]["lastTemperature"];
      // console.log(probedata[probe]);
      // console.log(probename + " = " + lastTemp);
      ProbeArray.push(probedata[probe]);
    }
    if (ProbeArray.length > 0) {
      this.setState({ ProbeArray });
    }

    // console.log(ProbeArray);

    return ProbeArray;
  }
  createOutletSet(outletdata) {
    console.log("Create Outlet Set");
    console.log(outletdata);

    let OutletArray = [];
    for (let outlet in outletdata) {
      OutletArray.push(outletdata[outlet]);
    }
    if (OutletArray.length > 0) {
      this.setState({ OutletArray });
    }

    console.log(OutletArray);

    return OutletArray;
  }
  handleCurrentOutletState(outletdata) {
    var outletListArrayClone = this.state.OutletArray.slice(0);
    console.log(outletdata);

    for (var outlet in outletdata) {
      for (var outletClone in outletListArrayClone) {
        if (
          outletListArrayClone[outletClone]["outletid"] ===
          outletdata[outlet].outletid
        ) {
          // console.log("Found a match");
          // console.log(outletdata[outlet].outletid);
          // console.log(outletListArrayClone[outletClone]["outletid"]);
          outletListArrayClone[outletClone]["outletstatus"] =
            outletdata[outlet].outletstatus;
          outletListArrayClone[outletClone]["button_state"] =
            outletdata[outlet].button_state;
        }
      }
      //console.log(this.state.OutletArray)
      this.setState({ OutletArray: outletListArrayClone });
      // console.log(this.state.OutletArray)
    }
  }

  setOutletData(outletdata) {
    console.log(outletdata);

    let OutletArray = [];
    for (let outlet in outletdata) {
      OutletArray.push(outletdata[outlet]);
    }
    if (OutletArray.length > 0) {
      this.setState({ OutletArray });
    }

    console.log(OutletArray);

    return OutletArray;
  }

  handleOutletButtonClick(outletid, buttonval) {
    console.log("I'm handling the button click " + outletid + " " + buttonval);
    var outletListArrayClone = this.state.OutletArray.slice(0);
    for (var outletClone in outletListArrayClone) {
      if (outletListArrayClone[outletClone]["outletid"] === outletid) {
        console.log("Found a match");
        // console.log(outletdata[outlet].outletid);
        // console.log(outletListArrayClone[outletClone]["outletid"]);
        outletListArrayClone[outletClone]["button_state"] = buttonval;
        outletListArrayClone[outletClone]["ischanged"] = true;
      }
    }
    //console.log(this.state.OutletArray)
    this.setState({ OutletArray: outletListArrayClone });
    console.log(this.state.OutletArray);

    let apiURL = process.env.REACT_APP_API_PUT_OUTLET_BUTTONSTATE
      .concat(outletid)
      .concat("/")
      .concat(buttonval);
    //console.log(apiURL)
    this.apiCall(apiURL);
  }

  buttonClickCallback() {
    console.log();
  }

  componentWillUnmount() {
    clearInterval(this.interval);
    clearInterval(this.interval2);
    clearInterval(this.interval3);
  }
  render() {
    return (
      <div className="App">
        <div class="appheader">
          <img class="appicon" src={appicon} alt="logo"></img>Reefberry Pi
          Aquarium Controller
        </div>
        <div class="maingridcontainer">
          <div class="maincol1">
            {this.state.ProbeArray.map((probe) => (
              <div class="col1items" key={probe.probeid}>
                <ProbeWidget data={probe}></ProbeWidget>
              </div>
            ))}
            {this.state.DHTArray.map((probe) => (
              <div class="col1items" key={probe.probeid}>
                <ProbeWidget data={probe}></ProbeWidget>
              </div>
            ))}
          </div>
          <div class="maincol2">
            {this.state.OutletArray.map((outlet) => (
              <div class="col2items" key={outlet.outletid}>
                <OutletWidget
                  data={outlet}
                  onButtonStateChange={this.handleOutletButtonClick}
                  probearray={this.state.ProbeArray}
                ></OutletWidget>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }
}
export default App;
