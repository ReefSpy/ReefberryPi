import React, { Component } from "react";
import "./OutletWidget.css";

class PrefPaneAlways extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someValue: 0,
      data: props.data,
      always_state: props.data.always_state,
    };
  }

  componentDidMount() {}

  componentWillUnmount(){

  }

  componentDidUpdate(prevProps, prevState) {

  }

  selectionChanged(event) {
     this.setState({ always_state: event.target.value });
    console.log(
      "select changed " + this.props.data.outletname + " " + event.target.value
    );
  }

  render() {


    return (
      <div>
        
          <div className="form-row">
            <label htmlFor="always_state">Always State</label>
          </div>
          <div onChange={(event) => this.selectionChanged(event)}>
            <input
              type="radio"
              id="always_state_on"
              name="always_state"
              value="ON"
              checked={this.state.always_state === "ON" ? true : null}
            />

            <label htmlFor="always_state_on">ON</label>

            <input
              type="radio"
              id="always_state_off"
              name="always_state"
              value="OFF"
              checked={this.state.always_state === "OFF" ? true : null}
            />
            <label htmlFor="always_state_off">OFF</label>
          </div>


         
        
      </div>
    );
  }
}

export default PrefPaneAlways;
