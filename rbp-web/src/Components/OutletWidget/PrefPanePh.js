import React, { Component } from "react";
import './OutletWidget.css';

class PrefPanePh extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someValue: 0,
    };
  }

  render() {
    return (
      <div>
        PH Control Coming soon
        <button>PH Button</button> 
      </div>
    );
  }
}

export default PrefPanePh;
