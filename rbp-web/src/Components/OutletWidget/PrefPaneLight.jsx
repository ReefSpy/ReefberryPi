import React, { Component } from "react";
import "./OutletWidget.css";

class PrefPaneLight extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someValue: 0,
      data: props.data,
      light_on: props.data.light_on,
      light_off: props.data.light_off,
    };
  }

  lightOnChanged(event) {
    this.setState({ light_on: event.target.value });
    console.log(
      "light on changed " +
        this.props.data.outletname +
        " " +
        event.target.value
    );
  }

  lightOffChanged(event) {
    this.setState({ light_off: event.target.value });
    console.log(
      "light off changed " +
        this.props.data.outletname +
        " " +
        event.target.value
    );
  }

  render() {
    return (
      <div>
        <div
          className="form-row"
          onChange={(event) => this.lightOnChanged(event)}
        >
          <label htmlFor="light">On Time</label>
        </div>
        <div onChange={(event) => this.lightOnChanged(event)}>
          <input
            type="time"
            id="time_on"
            name="light_on"
            value={this.state.light_on}
          ></input>
        </div>

        <div className="form-row">
          <label htmlFor="light">Off Time</label>
        </div>
        <div onChange={(event) => this.lightOffChanged(event)}>
          <input
            type="time"
            id="time_off"
            name="light_off"
            value={this.state.light_off}
          ></input>
        </div>

       
      </div>
    );
  }
}

export default PrefPaneLight;
