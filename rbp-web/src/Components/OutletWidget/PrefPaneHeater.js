import React, { Component } from "react";
import "./OutletWidget.css";

class PrefPaneHeater extends Component {
  constructor(props) {
    super(props);

    this.state = {
      tempProbes: this.props.probearray,
      selectedTempProbe: "",
    };
  }

  render() {
    const { tempProbes, selectedTempProbe } = this.state;
    return (
      <div>
        <form>
          <div className="form-row">
            <label htmlFor="heater">Temperature Probe</label>
            <select
              className="tempProbe"
              id="tempProbe"
              name="tempProbe"
              required
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
            value={this.props.data.heater_on}
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
            value={this.props.data.heater_off}
          ></input>

          <div className="submit_row">
            <button type="submit" className="submitbutton">
              Submit
            </button>
          </div>
        </form>
      </div>
    );
  }
}

export default PrefPaneHeater;
