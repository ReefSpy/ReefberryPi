import React from "react";
import MultiSwitch from "react-multi-switch-toggle";

export class OutletSwitch extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedSwitchColor: "lightblue",
      texts: ["OFF", "AUTO", "ON"],
      selectedSwitch: 1,
      bgColor: "gray",
      onToggleCallback: this.onToggle,
      fontColor: "white",
      selectedFontColor: "#1e311b",
      eachSwitchWidth: 80,
      height: "25px",
      fontSize: "12px",
      selectedSwitchColor: "lightblue"
    };
    this.onToggle = this.onToggle.bind(this);
  }

  render() {
    return (
      <div className="App">
        <MultiSwitch
          texts={this.state.texts}
          selectedSwitch={this.state.selectedSwitch}
          bgColor={this.state.bgColor}
          onToggleCallback={this.state.onToggleCallback}
          fontColor={this.state.fontColor}
          selectedFontColor={this.state.selectedFontColor}
          eachSwitchWidth={this.state.eachSwitchWidth}
          height={this.state.height}
          fontSize={this.state.fontSize}
          selectedSwitchColor={this.state.selectedSwitchColor}
        ></MultiSwitch>
      </div>
    );
  }

  onToggle(selectedItem) {
    console.log(selectedItem);
  }
}
