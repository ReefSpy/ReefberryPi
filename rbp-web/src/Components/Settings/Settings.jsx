import React, { Component } from "react";
import "./Settings.css";
import probeicon from "../../Images/probe.svg";
import outleticon from "../../Images/outlet.svg";
import usericon from "../../Images/user.svg";
import analogicon from "../../Images/analog.svg";
import globalicon from "../../Images/global.svg";
import OutletPrefsModal from "../OutletPrefs/OutletPrefsModal";
import ProbePrefsModal from "../ProbePrefs/ProbePrefsModal";
import TempPrefsModal from "../TempPrefs/TempPrefsModal";
import UserPrefsModal from "../UserPrefs/UserPrefsModal";
import ChangePasswordModal from "../ChangePassword/ChangePasswordModal"
import AddUserModal from "../AddUser/AddUserModal";
import appicon from "../../Images/reefberrypi-by-reefspy.svg";
import * as VERSION from "../Version/Version.js"


class Settings extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someState: 0,
    };
  }

  // Outlet Prefs Modal
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

// Change Password Modal
  handleOpenChangePasswordModal = () => {
    this.setState({ setChangePasswordModalOpen: true });
    this.setState({ isChangePasswordModalOpen: true });
  };

  handleCloseChangePasswordModal = () => {
    this.setState({ setChangePasswordModalOpen: false });
    this.setState({ isChangePasswordModalOpen: false });
    this.handleOpenUserPrefsModal()
    
  };

  handleChangePasswordSubmit = (data) => {
    this.handleCloseChangePasswordModal();
  };

  // Add User Modal
  handleOpenAddUserModal = () => {
    this.setState({ setAddUserModalOpen: true });
    this.setState({ isAddUserModalOpen: true });
  };

  handleCloseAddUserModal = () => {
    this.setState({ setAddUserModalOpen: false });
    this.setState({ isAddUserModalOpen: false });
    this.handleOpenUserPrefsModal()
    
  };

  handleAddUserSubmit = (data) => {
    this.handleCloseAddUserModal();
  };

// Global Prefs Modal
  handleGlobalPrefsFormSubmit = (data) => {
    console.log(data);
    this.handleCloseGlobalPrefsModal();
  };


  // Probe Prefs Modal
  handleOpenProbePrefsModal = () => {
    this.setState({ setProbePrefsModalOpen: true });
    this.setState({ isProbePrefsModalOpen: true });
  };

  handleCloseProbePrefsModal = () => {
    this.setState({ setProbePrefsModalOpen: false });
    this.setState({ isProbePrefsModalOpen: false });
  };

  handleProbePrefsFormSubmit = (data) => {
    this.handleCloseProbePrefsModal();
  };

  // User Prefs Modal
  handleChangePwBtnClick= () => {
    this.handleCloseUserPrefsModal()
    this.handleOpenChangePasswordModal()
  };

 

  handleAddUserBtnClick= () => {
   this.handleCloseUserPrefsModal()
   this.handleOpenAddUserModal()
  };

  handleOpenUserPrefsModal = () => {
    this.setState({ setUserPrefsModalOpen: true });
    this.setState({ isUserPrefsModalOpen: true });
  };

  handleCloseUserPrefsModal = () => {
    this.setState({ setUserPrefsModalOpen: false });
    this.setState({ isUserPrefsModalOpen: false });
  };

  handleUserPrefsFormSubmit = (data) => {
    this.handleCloseUserPrefsModal();
  };


  // Temperature Probe Prefs Modal
  handleTempPrefsFormSubmit = (data) => {
    this.handleCloseTempPrefsModal();
  };

  handleOpenTempPrefsModal = () => {
    this.setState({ setTempPrefsModalOpen: true });
    this.setState({ isTempPrefsModalOpen: true });
  };

  handleCloseTempPrefsModal = () => {
    this.setState({ setTempPrefsModalOpen: false });
    this.setState({ isTempPrefsModalOpen: false });
  };

  render() {
    return (
      <div>
        <br></br>
        <div className="settingsmain">
          <div className="settingscontainer">
            <h1>Application Settings</h1>
            <button
              className="settingsbtn"
              onClick={this.handleOpenTempPrefsModal}
            >
              <img src={probeicon} alt="Temperature" className="btnicon"></img>
              Temperature Probes
            </button>
            <button
              className="settingsbtn"
              onClick={this.handleOpenOutletPrefsModal}
            >
              <img src={outleticon} alt="Outlets" className="btnicon"></img>
              Outlets
            </button>
            <button className="settingsbtn" onClick={this.handleOpenUserPrefsModal}>
              <img src={usericon} alt="Users" className="btnicon"></img>Users
            </button>
            {/* <button className="settingsbtn" onClick={this.handleOpenChangePasswordModal}>
              <img src={keyicon} alt="Password" className="btnicon"></img>Change Password
            </button> */}
            <button className="settingsbtn" onClick={this.props.openGlobalPrefs}>
              <img src={globalicon} alt="Global" className="btnicon"></img>{" "}
              Global
            </button>
            <button
              className="settingsbtn"
              onClick={this.handleOpenProbePrefsModal}
            >
              <img
                src={analogicon}
                alt="Analog Probes"
                className="btnicon"
              ></img>{" "}
              Analog Probes
            </button>
          </div>

          <div className="aboutcontainer">
            <img
              src={appicon}
              alt="Reefberry Pi Logo"
              className="applogo"
            ></img>
            <br></br>
            Open source aquarium controller running on Raspberry Pi.
            <br />

            <a href="https://github.com/ReefSpy/ReefberryPi" target="_blank" rel='noreferrer'>https://github.com/ReefSpy/ReefberryPi </a>
            <br></br>
            <br></br>
            Controller Firmware: {this.props.globalPrefs?.controller_version}
            <br></br>
            Web Interface: {VERSION.WEB_VERSION}
            <br></br>
            <br></br>
          </div>

          {this.state.isProbePrefsModalOpen ? (
            <ProbePrefsModal
              isOpen={this.state.isProbePrefsModalOpen}
              onSubmit={this.handleProbePrefsFormSubmit}
              onClose={this.handleCloseProbePrefsModal}
              globalPrefs={this.state.globalPrefs}
              onRefreshRequest={this.props.onRefreshRequest}
            />
          ) : null}

          {this.state.isOutletPrefsModalOpen ? (
            <OutletPrefsModal
              isOpen={this.state.isOutletPrefsModalOpen}
              onSubmit={this.handleOutletPrefsFormSubmit}
              onClose={this.handleCloseOutletPrefsModal}
              onRefreshRequest={this.props.onRefreshRequest}
            />
          ) : null}

          {this.state.isUserPrefsModalOpen ? (
            <UserPrefsModal
              isOpen={this.state.isUserPrefsModalOpen}
              onSubmit={this.handleUserPrefsFormSubmit}
              onAddUser={this.handleAddUserBtnClick}
              onChangePW = {this.handleChangePwBtnClick}
              onClose={this.handleCloseUserPrefsModal}
              onRefreshRequest={this.props.onRefreshRequest}
            />
          ) : null}

{this.state.isChangePasswordModalOpen ? (
            <ChangePasswordModal
              isOpen={this.state.isChangePasswordModalOpen}
              onSubmit={this.handleChangePasswordSubmit}
              onClose={this.handleCloseChangePasswordModal}
              onRefreshRequest={this.props.onRefreshRequest}
            />
          ) : null}

{this.state.isAddUserModalOpen ? (
            <AddUserModal
              isOpen={this.state.isAddUserModalOpen}
              onSubmit={this.handleAddUserSubmit}
              onClose={this.handleCloseAddUserModal}
              onRefreshRequest={this.props.onRefreshRequest}
            />
          ) : null}

          {this.state.isTempPrefsModalOpen ? (
            <TempPrefsModal
              isOpen={this.state.isTempPrefsModalOpen}
              onSubmit={this.handleTempPrefsFormSubmit}
              onClose={this.handleCloseTempPrefsModal}
              onRefreshRequest={this.props.onRefreshRequest}
            />
          ) : null}
        </div>
      </div>
    );
  }
}

export default Settings;
