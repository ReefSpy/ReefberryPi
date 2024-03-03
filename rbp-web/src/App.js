import React, { Component } from "react";
import MainTabContainer from "./Components/MainTabContainer/MainTabContainer";
import appicon from "./Images/reefberry-pi-logo.svg";
import preficon from "./Images/cog-white.svg";
import logouticon from "./Images/logout-white.svg";
import probeIcon from "./Images/probe-white.svg";
import outletIcon from "./Images/outlet-white.svg"
import GlobalPrefsModal from "./Components/GlobalPrefs/GlobalPrefsModal";
import ProbePrefsModal from "./Components/ProbePrefs/ProbePrefsModal";
import OutletPrefsModal from "./Components/OutletPrefs/OutletPrefsModal";
import "./App.css";
//import useToken from "./useToken";
import Login from "./Components/Login/Login";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      col2items: [],
      col1items: [],
      ProbeArray: [],
      DragDisabled: false,
      globalPrefs: null,
      col1rawitems: [],
    };
    this.setProbeData = this.setProbeData.bind(this);
    this.setOutletData = this.setOutletData.bind(this);
    this.setGlobalPrefs = this.setGlobalPrefs.bind(this);
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
        callback(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  setProbeData(probedata) {
    let col1items = [];
    let i = 0;
    for (let probe in probedata) {
      probedata[probe]["id"] = `item-${String(i++)}`;
      probedata[probe]["widgetType"] = `probe`;
      col1items.push(probedata[probe]);
    }

    if (col1items.length > 0) {
      this.setState({ col1items });
    }
    this.setState({ ProbeArray: col1items });

    return col1items;
  }

  setOutletData(outletdata) {
    let col2items = [];
    let i = 0;
    for (let outlet in outletdata) {
      outletdata[outlet]["id"] = `item-${String(200 + i++)}`;
      outletdata[outlet]["widgetType"] = `outlet`;
      col2items.push(outletdata[outlet]);
    }

    if (col2items.length > 0) {
      this.setState({ col2items });
      this.setState({ OutletArray: col2items });
    }
    return col2items;
  }

  async componentDidMount() {
    this.apiCall(process.env.REACT_APP_API_GET_PROBE_LIST, this.setProbeData);

    this.apiCall(process.env.REACT_APP_API_GET_OUTLET_LIST, this.setOutletData);

    // global prefs
    this.apiCall(
      process.env.REACT_APP_API_GET_GLOBAL_PREFS,
      this.setGlobalPrefs
    );
    this.interval = setInterval(() => {
      this.apiCall(
        process.env.REACT_APP_API_GET_GLOBAL_PREFS,
        this.setGlobalPrefs
      );
    }, 3500);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  //   ///////
  handleOpenProbePrefsModal = () => {
    this.setState({ setProbePrefsModalOpen: true });
    this.setState({ isProbePrefsModalOpen: true });
  };

  handleCloseProbePrefsModal = () => {
    this.setState({ setProbePrefsModalOpen: false });
    this.setState({ isProbePrefsModalOpen: false });
  };

  handleOpenOutletPrefsModal = () => {
    this.setState({ setOutletPrefsModalOpen: true });
    this.setState({ isOutletPrefsModalOpen: true });
  };

  handleCloseOutletPrefsModal = () => {
    this.setState({ setOutletPrefsModalOpen: false });
    this.setState({ isOutletPrefsModalOpen: false });
  };

  handleOpenGlobalPrefsModal = () => {
    this.setState({ setGlobalPrefsModalOpen: true });
    this.setState({ isGlobalPrefsModalOpen: true });
  };

  handleCloseGlobalPrefsModal = () => {
    this.setState({ setGlobalPrefsModalOpen: false });
    this.setState({ isGlobalPrefsModalOpen: false });
  };

  handleGlobalPrefsFormSubmit = (data) => {
    let apiURL = process.env.REACT_APP_API_SET_GLOBAL_PREFS;
    console.log(data);
    let payload = {
      tempscale: data.tempScale,
      dht_enable: data.enableDHT,
      feed_a_time: data.feedA,
      feed_b_time: data.feedB,
      feed_c_time: data.feedC,
      feed_d_time: data.feedD,
    };
    this.apiCallPut(apiURL, payload);
    this.handleCloseGlobalPrefsModal();
 
  };

  handleProbePrefsFormSubmit = (data) => {
    this.handleCloseProbePrefsModal();
    
  };

  handleOutletPrefsFormSubmit = (data) => {
    this.handleCloseOutletPrefsModal();
    
  };

  setGlobalPrefs(data) {
    this.setState({ globalPrefs: data });
    this.setState({ globalTempScale: data.tempscale });
    this.setState({ globalEnableDHT: data.dht_enable });

    return;
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
      .then( alert("Settings saved.  Window will refresh to reflect changes"))
      .then ( window.location.reload(false))
      .catch((error) => console.log(error));
  };

  getToken = () => {
    const tokenString = sessionStorage.getItem("token");
    if (tokenString !== undefined) {
      const userToken = JSON.parse(tokenString);
      return userToken?.token;
    }
  };

  setToken(userToken) {
    console.log("settoken");
    if (userToken !== undefined) {
      sessionStorage.setItem("token", JSON.stringify(userToken));
    }
  }

  logout() {
    sessionStorage.clear();
  }

  render() {
    if (!this.getToken()) {
      return <Login setToken={this.setToken} />;
    }
    return (
      <div className="App">
        <div className="appheader">
          <img className="appicon" src={appicon} alt="logo" />

          <span>Reefberry Pi</span>

          <div className="header-right">
          {/* <button className="headericonbtn">
              <img
                className="headericon"
                src={outletIcon}
                alt="Outlets"
                onClick={this.handleOpenOutletPrefsModal}
              ></img>
            </button>

            <button className="headericonbtn">
              <img
                className="headericon"
                src={probeIcon}
                alt="Probes"
                onClick={this.handleOpenProbePrefsModal}
              ></img>
            </button> */}

            <button className="headericonbtn">
              <img
                className="headericon"
                src={preficon}
                alt="Preferences"
                onClick={this.handleOpenGlobalPrefsModal}
              ></img>
            </button>
            <button className="headericonbtn">
              <img
                className="headericon"
                src={logouticon}
                alt="Logout"
                onClick={this.logout}
              ></img>
            </button>
          </div>
        </div>

        <div>
          <MainTabContainer
            feedmode={this.state.globalPrefs?.feed_CurrentMode}
            probearray={this.state.ProbeArray}
            outletarray={this.state.OutletArray}
            globalPrefs={this.state.globalPrefs}
          ></MainTabContainer>
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

        {this.state.isProbePrefsModalOpen ? (
          <ProbePrefsModal
            isOpen={this.state.isProbePrefsModalOpen}
            onSubmit={this.handleProbePrefsFormSubmit}
            onClose={this.handleCloseProbePrefsModal}
            globalPrefs={this.state.globalPrefs}
          />
        ) : null}

{this.state.isOutletPrefsModalOpen ? (
          <OutletPrefsModal
            isOpen={this.state.isOutletPrefsModalOpen}
            onSubmit={this.handleOutletPrefsFormSubmit}
            onClose={this.handleCloseOutletPrefsModal}
          />
        ) : null}
      </div>
    );
  }
}

export default App;
