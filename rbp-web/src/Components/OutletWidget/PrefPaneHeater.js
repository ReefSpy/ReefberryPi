import React, { Component } from "react";
import "./OutletWidget.css";

class PrefPaneHeater extends Component {
  constructor(props) {
    super(props);

    this.state = {
      tempProbes: this.props.probearray,
      selectedTempProbe: "",
      data: props.data,
      heater_on: props.data.heater_on,
      heater_off: props.data.heater_off,
      heater_probe: props.data.heater_probe,
    };
  }

  handleProbeChange = (event) => {
    this.setState({ selectedTempProbe: event.target.value });
    this.setState({ selectedTempProbeIndex: event.target.selectedIndex });
    this.setState({ selectedTempProbeID: this.state.tempProbes[event.target.selectedIndex].probeid });

  }

  tempOffChanged(event) {
    this.setState({ heater_off: event.target.value });
    console.log(
      "heater off changed " +
        this.props.data.outletname +
        " " +
        event.target.value
    );
  }

  tempOnChanged(event) {
    this.setState({ heater_on: event.target.value });
    console.log(
      "heater on changed " +
        this.props.data.outletname +
        " " +
        event.target.value
    );
  }

  render() {
    const { tempProbes, selectedTempProbe } = this.state;
    return (
      <div>
    
          <div className="form-row">
            <label htmlFor="heater">Temperature Probe</label>
            <select
              className="tempProbe"
              id="tempProbe"
              name="tempProbe"
              required
              onChange={this.handleProbeChange}
            >
              {tempProbes.map((tempProbe, index) => (
                <option key={index} value={tempProbe.probename}>
                  {tempProbe.probename}
                </option>
              ))}
            </select>
          </div>

          <div className="form-row">
            <label htmlFor="heater">On Temperature</label>
          </div>

          <input
            type="number"
            id="temp_on"
            name="temp_on"
            min="0"
            max="212"
            step=".1"
            value={this.state.heater_on}
            onChange={(event) => this.tempOnChanged(event)}
          ></input>
          <div className="form-row">
            <label htmlFor="heater">Off Temperature</label>
          </div>

          <input
            type="number"
            id="temp_off"
            name="temp_off"
            min="0"
            max="212"
            step=".1"
            value={this.state.heater_off}
            onChange={(event) => this.tempOffChanged(event)}
          ></input>


      </div>
    );
  }
}

export default PrefPaneHeater;
