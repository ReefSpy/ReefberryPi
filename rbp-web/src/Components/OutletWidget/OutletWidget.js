import React, { Component } from "react";
import MultiToggle from "react-multi-toggle";
import "./togglestyle.css";
import "./OutletWidget.css";
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

    // console.log("I'm handling the button click " + outletid + " " + val);
    const newOutLetData = { ...this.state.OutletData };
    newOutLetData.ischanged = true;
    this.setState({ OutletData: newOutLetData });

    let apiURL = process.env.REACT_APP_API_PUT_OUTLET_BUTTONSTATE.concat(
      outletid
    )
      .concat("/")
      .concat(val);
    //console.log(apiURL)
    this.apiCall(apiURL, this.handleOutletButtonClick);
  }

  handleOutletButtonClick(retData) {
    console.log(retData);
  }

  // handleOutletButtonClick(outletid, buttonval) {
  //   console.log("I'm handling the button click " + outletid + " " + buttonval);
  //   var outletListArrayClone = this.state.OutletArray.slice(0);
  //   for (var outletClone in outletListArrayClone) {
  //     if (outletListArrayClone[outletClone]["outletid"] === outletid) {
  //       console.log("Found a match");
  //       // console.log(outletdata[outlet].outletid);
  //       // console.log(outletListArrayClone[outletClone]["outletid"]);
  //       outletListArrayClone[outletClone]["button_state"] = buttonval;
  //       outletListArrayClone[outletClone]["ischanged"] = true;
  //     }
  //   }
  //   //console.log(this.state.OutletArray)
  //   this.setState({ OutletArray: outletListArrayClone });
  //   console.log(this.state.OutletArray);

  //   let apiURL = process.env.REACT_APP_API_PUT_OUTLET_BUTTONSTATE.concat(
  //     outletid
  //   )
  //     .concat("/")
  //     .concat(buttonval);
  //   //console.log(apiURL)
  //   this.apiCall(apiURL);
  // }

  componentDidMount() {
    this.setState({ buttonstateidx: this.props.data.button_state });

    // update stats
    let ApiGetStats = process.env.REACT_APP_API_GET_CURRENT_OUTLET_STATS.concat(
      this.props.data.outletid
    );
    this.apiCall(ApiGetStats, this.SetOutletData);

    this.interval2 = setInterval(() => {
      this.apiCall(ApiGetStats, this.SetOutletData);
    }, 2000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
    clearInterval(this.interval2);
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
    console.log(data);
  };

  SetOutletData = (data) => {
    this.setState({ OutletName: data.outletname });
    this.setState({ OutletStatus: data.outletstatus });
    this.setState({ OutletData: data });
    this.setState({ buttonstateidx: data.button_state });
  };

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

  render() {
    return (
      <div class="outletcontainer">
        <div class="outletitem outletname">{this.state.OutletName}</div>
        <div class="outletitem multitoggle">
          <MultiToggle
            options={groupOptions}
            label={this.state.OutletStatus}
            onSelectOption={this.onToggleSelect}
            selectedOption={this.state.buttonstateidx}
            className={"outletSlider"}
          />
        </div>
        <div class="outletitem outletseticon">
          <button class="outletsetbtn">
            <img
              src={cogicon}
              alt="settings"
              height="14"
              width="14"
              onClick={this.handleOpenOutletPrefsModal}
            />
          </button>
        </div>

        {this.state.isOutletPrefsModalOpen ? (
          <OutletWidgetModal
            isOpen={this.state.isOutletPrefsModalOpen}
            onSubmit={this.handleOutletPrefsFormSubmit}
            onClose={this.handleCloseOutletPrefsModal}
            OutletName={this.state.OutletName}
            OutletID={this.props.data.outletid}
            ControlType={this.props.data.control_type}
            data={this.state.OutletData}
            probearray={this.props.probearray}
          />
        ) : null}
      </div>
    );
  }
}
