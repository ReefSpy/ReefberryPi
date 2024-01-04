import React, { Component } from "react";

export class OutletWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {

    };
  }
  render() {


    return (
      <div>
        <h3 >{(this.props.data.outletid)} : {(this.props.data.outletname)} : {this.props.data.control_type}</h3>
        {/* <h1>{(this.props.data.outletname)}</h1> */}
        {/* <h4>{this.props.data.control_type}</h4> */}
      </div>
    );
      
  }
}