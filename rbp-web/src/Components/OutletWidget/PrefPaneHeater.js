import React, { Component } from "react";
import './OutletWidget.css';

class PrefPaneHeater extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someValue: 0,
    };
  }

  render() {
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
              <option value="0">Probe 1</option>
              <option value="1">Probe 2</option>
              <option value="2">Probe 3</option>
            </select>
        </div>




          <div className="form-row">
            <label htmlFor="heater">On Temperature</label>
          </div>

          <input type="number" id="temp_on" name="temp_on" min="0" max="212" step=".1" ></input>
          <div className="form-row">
            <label htmlFor="heater">Off Temperature</label>
          </div>

          <input type="number" id="temp_off" name="temp_off" min="0" max="212" step=".1" ></input>

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
