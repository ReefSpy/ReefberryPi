import React from "react";
//import Paper from "@material-ui/core/Paper";
import ProbeWidget from "./ProbeWidget";

const columnStyle = {
  color: "#2E3B55"
};
export class LeftPane extends React.Component {
  render() {
    //console.log(this.props.probevals);
    //onsole.log(this.props);
    //console.log("Render Left Pane");

    return (
      <div class="container" style={this.props.styles.Paper}>
        <h2 style={columnStyle}>Probes</h2>
        <div style={this.props.styles.Columns}>
          {this.props.probes.map(probe => (
            <ProbeWidget
              key={probe.probeid}
              probeid={probe.probeid}
              probename={probe.probename}
              probetype={probe.probetype}
              sensortype={probe.sensortype}
              probeval={probe.probeval}
              chartdata={probe.chartdata}
              style={this.props.styles.ProbeWidget}
            />
          ))}
        </div>
      </div>
    );
  }
}
