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
        <h3 >{(this.props.data.outletid)}</h3>
        <h1>{(this.props.data.outletname)}</h1>
        {/* <h4>{this.props.data}</h4> */}
      </div>
    );
      
  }
}