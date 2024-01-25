import React, { Component } from "react";
import MultiToggle from "react-multi-toggle";
import "./togglestyle.css";
import "./OutletWidget.css"
import cogicon from "./cog.svg";
import OutletWidgetModal from "./OutletWidgetModal";

const groupOptions = [
  {
    displayName: "OFF",
    value: "OFF",
    optionClass: "styleOff",
  },
  {
    displayName: "AUTO",
    value: "AUTO",
    optionClass: "styleAuto",
  },
  {
    displayName: "ON",
    value: "ON",
    optionClass: "styleOn",
  },
];

export class OutletWidget extends Component {
  constructor(props) {
    super(props);
    this.state = { buttonstateidx: undefined };
  }

  onToggleSelect = (value) => {
    console.log(value);

    this.handleClick(value, this.props.data.outletid);
  };

  handleClick(val, outletid) {
    console.log("Click detected! " + val + " " + outletid);
    console.log(this.props.data);

    this.setState({ buttonstateidx: val });
    //this.props.onOutletWidgetClick(val, outletid);
    this.props.onButtonStateChange(outletid, val);
  }
  componentDidMount() {
    this.setState({ buttonstateidx: this.props.data.button_state });
  }

///////
handleOpenOutletPrefsModal = () => {
  this.setState({ setOutletPrefsModalOpen: true });
  this.setState({ isOutletPrefsModalOpen: true });
};

handleCloseOutletPrefsModal = () => {
  this.setState({ setOutletPrefsModalOpen: false });
  this.setState({ isOutletPrefsModalOpen: false });

};

handleOutletPrefsFormSubmit = (data) => {
 // this.setState({ setOutletPrefsFormData: data });
  this.handleCloseOutletPrefsModal();
  console.log(data)

  // let updateApiURL = "http://xpi01.local:5000/set_probe_name/"
  //   .concat(data.probeid)
  //   .concat("/")
  //   .concat(data.probename);
  // this.apiCall(updateApiURL, );
};
//////


  render() {
    // const widgetstyle = {
    //   color: "black",
    //   backgroundColor: "white",
    //   padding: "10px",
    //   border: "1px solid black",
    //   width: "300px",
    //   display: "block",
    // };


    return (
      <div class="outletcontainer">
        <div class="outletitem outletname">{this.props.data.outletname}</div>
        <div class = "outletitem multitoggle">
          <MultiToggle
            options={groupOptions}
            label={this.props.data.outletstatus}
            onSelectOption={this.onToggleSelect}
            selectedOption={this.props.data.button_state}
            //selectedOption={this.state.buttonstateidx}
            className={"outletSlider"}
          />
        </div>
        <div class="outletitem outletseticon">
          <button class = "outletsetbtn"><img
            src={cogicon}
            alt="settings"
            height="14"
            width="14"
            onClick={this.handleOpenOutletPrefsModal}
          /></button>
        </div>

        {(this.state.isOutletPrefsModalOpen) ? 
        <OutletWidgetModal
        isOpen={this.state.isOutletPrefsModalOpen}
        onSubmit={this.handleOutletPrefsFormSubmit}
        onClose={this.handleCloseOutletPrefsModal}
        OutletName={this.props.data.outletname}
        OutletID={this.props.data.outletid}
        ControlType={this.props.data.control_type}
        data={this.props.data}
        probearray={this.props.probearray}
        /> : null}
      </div>
    );
  }
}
