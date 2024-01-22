import React, { Component } from "react";
import { ProbeWidget } from "./Components/ProbeWidget/ProbeWidget";
import { OutletWidget } from "./Components/OutletWidget/OutletWidget";
import appicon from "./Images/reefberry-pi-logo.svg";
import preficon from "./Images/cog-white.svg";
import GlobalPrefsModal from "./Components/GlobalPrefs/GlobalPrefsModal";
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
      globalPrefs: null,
    };

    this.setProbeData = this.setProbeData.bind(this);
    this.setOutletData = this.setOutletData.bind(this);
    this.createOutletSet = this.createOutletSet.bind(this);
    this.handleOutletButtonClick = this.handleOutletButtonClick.bind(this);
    this.handleCurrentOutletState = this.handleCurrentOutletState.bind(this);
    this.setDHTData = this.setDHTData.bind(this);
    this.setGlobalPrefs = this.setGlobalPrefs.bind(this);
  }

  async componentDidMount() {
    document.title = "Reefberry Pi";
    // probe list
    console.log(process.env.REACT_APP_API_GET_TEMPPROBE_LIST);
    this.apiCall(
      process.env.REACT_APP_API_GET_TEMPPROBE_LIST,
      this.setProbeData
    );
    this.interval = setInterval(() => {
      this.apiCall(
        process.env.REACT_APP_API_GET_TEMPPROBE_LIST,
        this.setProbeData
      );
    }, 2000);
    // outlet list
    this.apiCall(
      process.env.REACT_APP_API_GET_OUTLET_LIST,
      this.createOutletSet
    );
    this.interval2 = setInterval(() => {
      this.apiCall(
        process.env.REACT_APP_API_GET_OUTLET_LIST,
        this.handleCurrentOutletState
      );
    }, 2000);
    // dht sensor list
    this.apiCall(process.env.REACT_APP_API_GET_DHT_SENSOR, this.setDHTData);
    this.interval3 = setInterval(() => {
      this.apiCall(process.env.REACT_APP_API_GET_DHT_SENSOR, this.setDHTData);
    }, 2000);
    // global prefs
    this.apiCall(
      process.env.REACT_APP_API_GET_GLOBAL_PREFS,
      this.setGlobalPrefs
    );
    this.interval4 = setInterval(() => {
      this.apiCall(
        process.env.REACT_APP_API_GET_GLOBAL_PREFS,
        this.setGlobalPrefs
      );
    }, 3500);
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
        // this.setState({ apiResponse: data });
        callback(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  // API call structure
  apiCallPut = (endpoint, newdata) => {
    fetch(endpoint, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newdata),
    })
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.log(error));
  };

  setDHTData(probedata) {
    console.log(probedata);
    let DHTArray = [];

    if (probedata.dht_enable === "false") {
      return DHTArray;
    }

    for (let probe in probedata) {
      DHTArray.push(probedata[probe]);
    }
    if (DHTArray.length > 0) {
      this.setState({ DHTArray });
    }
    // console.log(ProbeArray);
    return DHTArray;
  }

  setGlobalPrefs(data) {
    console.log(data);
    this.setState({ globalPrefs: data });
    this.setState({ globalTempScale: data.tempscale });
    this.setState({ globalEnableDHT: data.dht_enable });

    return;
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
          outletListArrayClone[outletClone]["outletname"] =
            outletdata[outlet].outletname;
          outletListArrayClone[outletClone]["control_type"] =
            outletdata[outlet].control_type;
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

    let apiURL = process.env.REACT_APP_API_PUT_OUTLET_BUTTONSTATE.concat(
      outletid
    )
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

  ///////
  handleOpenGlobalPrefsModal = () => {
    console.log("global prefs button click");
    this.setState({ setGlobalPrefsModalOpen: true });
    this.setState({ isGlobalPrefsModalOpen: true });
  };

  handleCloseGlobalPrefsModal = () => {
    this.setState({ setGlobalPrefsModalOpen: false });
    this.setState({ isGlobalPrefsModalOpen: false });
  };

  handleGlobalPrefsFormSubmit = (data) => {
    let apiURL = process.env.REACT_APP_API_SET_GLOBAL_PREFS;
    let payload = {
      tempscale: data.tempScale,
      dht_enable: data.enableDHT,
      feed_a_time: "0",
      feed_b_time: "0",
      feed_c_time: "0", 
      feed_d_time: "0"
    };
    this.apiCallPut(apiURL, payload);
    this.handleCloseGlobalPrefsModal()
  };

 
  //////

  render() {
    return (
      <div className="App">
        <div class="appheader">
          <img className="appicon" src={appicon} alt="logo" />

          <span>Reefberry Pi</span>

          <div class="header-right">
            <button className="preficonbtn">
              <img
                className="preficon"
                src={preficon}
                alt="preferences"
                onClick={this.handleOpenGlobalPrefsModal}
              ></img>
            </button>
          </div>
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
              <div class="col2items">
                <OutletWidget
                  data={outlet}
                  onButtonStateChange={this.handleOutletButtonClick}
                  probearray={this.state.ProbeArray}
                  key={outlet.outletid}
                ></OutletWidget>
              </div>
            ))}
          </div>
        </div>

        {this.state.globalPrefs && this.state.isGlobalPrefsModalOpen ? (
          <GlobalPrefsModal
            isOpen={this.state.isGlobalPrefsModalOpen}
            onSubmit={this.handleGlobalPrefsFormSubmit}
            onClose={this.handleCloseGlobalPrefsModal}
            globalTempScale={this.state.globalTempScale}
            globalPrefs={this.state.globalPrefs}
          />
        ) : null}
      </div>
    );
  }
}
export default App;
