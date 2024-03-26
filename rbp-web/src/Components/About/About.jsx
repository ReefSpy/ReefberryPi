import React, { Component } from "react";
import "./About.css";
import appicon from "../../Images/reefberry-pi-logo-reefspy.svg"


class About extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someState: 0,
    };
  }

  render() {
    


    return (
      <div>
        <img src = {appicon} alt="Reefberry Pi Logo" className="applogo"></img>
        <br></br>
        Open source aquarium controller running on Raspberry Pi.
        <br/>
         https://github.com/ReefSpy/ReefberryPi
      </div>
    );
  }
}

export default About;
