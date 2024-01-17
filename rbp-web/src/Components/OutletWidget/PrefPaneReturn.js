import React, { Component } from "react";
import './OutletWidget.css';

class PrefPaneReturn extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someValue: 0,
    };
  }

  render() {
    return (
      <div>
        The Return Pane
        <button>Return Button</button> <button>Return Button 2</button>
      </div>
    );
  }
}

export default PrefPaneReturn;
