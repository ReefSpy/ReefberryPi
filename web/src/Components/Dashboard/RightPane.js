import React from "react";
//import Paper from "@material-ui/core/Paper";
import { OutletWidget } from "./OutletWidget";

const columnStyle = {
  color: "#2E3B55"
};
export class RightPane extends React.Component {
  render() {
    //console.log(this.props.probevals);
    //onsole.log(this.props);
    //console.log("Render Right Pane");
    return (
      <div class="container" style={this.props.styles.Paper}>
        <h2 style={columnStyle}>Outlets</h2>
        <div style={this.props.styles.Columns}>
          {this.props.outlets.map(outlet => (
            <OutletWidget
              key={outlet.outletid}
              outlet={outlet}
              outletid={outlet.outletid}
              outletname={outlet.outletname}
              statusmsg={outlet.statusmsg}
              onClick={this.handleClick.bind(this)}
              buttonstate={outlet.buttonstate}
              buttonstateidx={outlet.buttonstateidx}
              appConfig={this.props.appConfig}
            />
          ))}
        </div>
      </div>
    );
  }
  handleClick(val, outletid) {
    console.log("Click detected! " + val + " " + outletid);
    //console.log(this.props)
    this.props.onOutletWidgetClick(val, outletid);
  }
}
