import React, { Component } from "react";
import "./OutletWidget.css";

class PrefPaneAlways extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someValue: 0,
    };
  }


  componentDidMount() {

  }


  render() {
    return (
      <div>
        <form>
          <div className="form-row">
            <label htmlFor="always_state">Always State</label>
          </div>
          <input
            type="radio"
            id="always_state_on"
            name="always_state"
            value="ON"
            checked={this.props.data.always_state === "ON" ? true: null}
          />

          <label htmlFor="always_state_on">ON</label>

          <input
            type="radio"
            id="always_state_off"
            name="always_state"
            value="OFF"
            checked={this.props.data.always_state === "OFF" ? true: null}
          />
          <label htmlFor="always_state_off">OFF</label>

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

export default PrefPaneAlways;
