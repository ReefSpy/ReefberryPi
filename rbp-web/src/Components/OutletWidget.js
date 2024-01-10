import React, { Component } from "react";
import MultiToggle from "react-multi-toggle";
import "./togglestyle.css";
import "./OutletWidget.css"

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

  render() {
    const widgetstyle = {
      color: "black",
      backgroundColor: "white",
      padding: "10px",
      border: "1px solid black",
      width: "300px",
      display: "block",
    };


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
        {/* <h1>{(this.props.data.outletname)}</h1> */}
        {/* <h4>{this.props.data.control_type}</h4> */}
      </div>
    );
  }
}
