import React, { Component } from "react";
import "./Settings.css";
import probeicon from "../../Images/probe.svg"
import outleticon from "../../Images/outlet.svg"
import usericon from "../../Images/user.svg"
import analogicon from "../../Images/analog.svg"
import globalicon from "../../Images/global.svg"
import OutletPrefsModal from "../OutletPrefs/OutletPrefsModal";
import ProbePrefsModal from "../ProbePrefs/ProbePrefsModal";



class Settings extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someState: 0,
    };
  }

  handleOpenOutletPrefsModal = () => {
    this.setState({ setOutletPrefsModalOpen: true });
    this.setState({ isOutletPrefsModalOpen: true });
  };

  handleCloseOutletPrefsModal = () => {
    this.setState({ setOutletPrefsModalOpen: false });
    this.setState({ isOutletPrefsModalOpen: false });
  };

  handleOutletPrefsFormSubmit = (data) => {
    this.handleCloseOutletPrefsModal();
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

  handleOpenProbePrefsModal = () => {
    this.setState({ setProbePrefsModalOpen: true });
    this.setState({ isProbePrefsModalOpen: true });
  };

  handleCloseProbePrefsModal = () => {
    this.setState({ setProbePrefsModalOpen: false });
    this.setState({ isProbePrefsModalOpen: false });
  };

  render() {
    


    return (
      <div>
        <br></br>
        
        <div className="settingscontainer">
        <h1>Application Settings</h1>
        <button className="settingsbtn"><img src={probeicon} alt="Temperature" className="btnicon"></img>Temperature Probes</button>
        <button className="settingsbtn" onClick={this.handleOpenOutletPrefsModal}><img src={outleticon} alt="Outlets" className="btnicon"></img>Outlets</button>
        <button className="settingsbtn"><img src={usericon} alt="Users" className="btnicon"></img>Users</button>
        <button className="settingsbtn"><img src={globalicon} alt="Global" className="btnicon"></img> Global</button>
        <button className="settingsbtn" onClick={this.handleOpenProbePrefsModal}><img src={analogicon} alt="Analog Probes" className="btnicon"></img> Analog Probes</button>
        </div>

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

export default Settings;
