import React from "react";
//import Paper from "@material-ui/core/Paper";
import { FeedWidget } from "./FeedWidget";

const columnStyle = {
  color: "#2E3B55"
};

export class CenterPane extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return (
      <div class="container" style={this.props.styles.Paper}>
        <h2 style={columnStyle}>Extras</h2>
        <div style={this.props.styles.Columns}></div>
        <FeedWidget
          onClick={this.handleClick.bind(this)}
          feedmode={this.props.feedmode}
        ></FeedWidget>
      </div>
    );
  }
  handleClick(val) {
    console.log("Feed Click detected! " + val);
    this.props.onFeedWidgetClick(val);
  }
}
