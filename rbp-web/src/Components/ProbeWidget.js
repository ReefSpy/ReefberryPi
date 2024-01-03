import React, { Component } from "react";

export class ProbeWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {
      LastTemp: "0.00",
      ProbeName: "Unkown",
    };
  }
  render() {
  if (this.props.data.length > 0 ){

    return (
      <div>
        <h3 >{(this.props.data[1].probename)}</h3>
        <h1>{(this.props.data[1].lastTemperature)}</h1>
        {/* <h4>{this.props.data}</h4> */}
      </div>
    );
      }
  }
}
