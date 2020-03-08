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
          onClick={this.props.onFeedWidgetClick}
          feedmode={this.props.feedmode}
          handleConfigSave={this.props.handleConfigSave}
          handleConfigLoad={this.props.handleConfigLoad}
          appConfig={this.props.appConfig}
        ></FeedWidget>
      </div>
    );
  }
}
