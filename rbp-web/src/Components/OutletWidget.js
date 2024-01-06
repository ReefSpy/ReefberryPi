import React, { Component } from "react";
import MultiToggle from "react-multi-toggle";
import "./togglestyle.css";

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
    this.state = {buttonstateidx: undefined};
  }

  onToggleSelect = (value) => {
    console.log(value);

    this.handleClick(value, this.props.data.outletid);
  };

  handleClick(val, outletid) {
    console.log("Click detected! " + val + " " + outletid);
    console.log(this.props.data)
    
    this.setState({buttonstateidx: val})
    //this.props.onOutletWidgetClick(val, outletid);
    this.props.onButtonStateChange( outletid, val)
  }
componentDidMount(){
  this.setState({buttonstateidx: this.props.data.button_state})
}

  render() {
    
    return (
      <div>
        <h3>
          {this.props.data.outletid} : {this.props.data.outletname} :{" "}
          {this.props.data.control_type} : {this.props.data.button_state} :{" "}
          {this.props.data.outletstatus}{" "}
        </h3>
        <MultiToggle
          options={groupOptions}
          label={this.props.data.outletstatus}
          onSelectOption={this.onToggleSelect}
          selectedOption={this.props.data.button_state}
          className={"outletSlider"}
        />
        {/* <h1>{(this.props.data.outletname)}</h1> */}
        {/* <h4>{this.props.data.control_type}</h4> */}
      </div>
    );
  }
}
