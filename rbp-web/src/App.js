import React, { Component } from "react";
import { ProbeWidget } from "./Components/ProbeWidget";
import { OutletWidget } from "./Components/OutletWidget";


import "./App.css";

const URL_get_tempprobe_list = "http://xpi01.local:5000/get_tempprobe_list/";
const URL_get_outlet_list = "http://xpi01.local:5000/get_outlet_list/";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      apiResponse: null,
      ProbeArray: [],
      OutletArray: [],
    };

    this.setProbeData = this.setProbeData.bind(this);
    this.setOutletData = this.setOutletData.bind(this);
    this.handleOutletButtonClick = this.handleOutletButtonClick.bind(this)
  }

  async componentDidMount() {
    // probe list
    this.apiCall(URL_get_tempprobe_list, this.setProbeData);
    this.interval = setInterval(() => {
      this.apiCall(URL_get_tempprobe_list, this.setProbeData);
    }, 2000);
    // outlet list
    this.apiCall(URL_get_outlet_list, this.setOutletData);
    this.interval2 = setInterval(() => {
      this.apiCall(URL_get_outlet_list, this.setOutletData);
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

  setProbeData(probedata) {
    console.log(probedata);

    let ProbeArray = [];
    for (let probe in probedata) {
      let probename = probedata[probe]["probename"];
      let lastTemp = probedata[probe]["lastTemperature"];
      // console.log(probedata[probe]);
      console.log(probename + " = " + lastTemp);
      ProbeArray.push(probedata[probe]);
    }
    if (ProbeArray.length > 0) {
      this.setState({ ProbeArray });
    }

    console.log(ProbeArray);

    return ProbeArray;
  }

  setOutletData(outletdata) {
    console.log(outletdata);

    let OutletArray = [];
    for (let outlet in outletdata) {
      let outletid = outletdata[outlet]["outletid"];
      let outletname = outletdata[outlet]["outletname"];
      let control_type = outletdata[outlet]["control_type"];
      console.log(outletid + ": " + outletname + " = " + control_type);
      OutletArray.push(outletdata[outlet]);
    }
    if (OutletArray.length > 0) {
      this.setState({ OutletArray });
    }

    console.log(OutletArray);

    return OutletArray;
  }

handleOutletButtonClick(outletid, buttonval){
  console.log("I'm handling the button click "+ outletid + " " + buttonval)
  console.log(this.state.OutletArray)
}

  componentWillUnmount() {
    clearInterval(this.interval);
    clearInterval(this.interval2);
  }
  render() {

    return (
      <div className="App">
        <h1>Reefberry Pi Demo</h1>
        {this.state.ProbeArray.map((probe) => (
          <div key={probe.probeid}>
            <ProbeWidget data={probe}></ProbeWidget>
          </div>
        ))}

        {this.state.OutletArray.map((outlet) => (
          <div key={outlet.outletid}>
            <OutletWidget data={outlet} onButtonStateChange = {this.handleOutletButtonClick}></OutletWidget>
          </div>
        ))}
      </div>
    );
  }
}
export default App;
