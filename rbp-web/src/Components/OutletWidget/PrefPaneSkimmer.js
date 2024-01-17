import React, { Component } from "react";
import './OutletWidget.css';

class PrefPaneSkimmer extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someValue: 0,
    };
  }

  render() {
    return (
      <div>
        The Skimmer Pane
        <button>Skimmer Button</button> <button>Skimmer Button 2</button>
      </div>
    );
  }
}

export default PrefPaneSkimmer;
