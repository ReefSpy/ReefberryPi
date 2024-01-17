import React, { Component } from "react";
import "./OutletWidget.css";

class PrefPaneLight extends Component {
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
            <label htmlFor="light">On Time</label>
          </div>

          <input type="time" id="time_on" name="time_on"></input>
          <div className="form-row">
            <label htmlFor="light">Off Time</label>
          </div>

          <input type="time" id="time_off" name="time_off"></input>

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

export default PrefPaneLight;
