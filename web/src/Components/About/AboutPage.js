import React from "react";

export class AboutPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return (
      <div>
        <body>Reefberry Pi DIY aquarium controller</body>
        <br></br>
        <img
          src={require("../Layouts/img/reefberry-pi-logo-reefspy.svg")}
          alt="logo"
          hspace="8"
        />
      </div>
    );
  }
}
