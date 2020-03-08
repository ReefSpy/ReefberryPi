import React from "react";
//import Grid from "@material-ui/core/Grid";
import { LeftPane } from "./LeftPane";
import { RightPane } from "./RightPane";
import { CenterPane } from "./CenterPane";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const styles = {
  Paper: {
    backgroundColor: "#D9DBE0",
    padding: 20,
    marginTop: 10,
    marginBottom: 10,

    border: "1px solid #85868c",
    borderRadius: 15,
    width: 400
  },
  Columns: {
    top: "0",
    right: "0",
    bottom: "0",
    left: "0",
    width: "360px"
  },
  ProbeWidget: {
    backgroundColor: "#D9DBE0"
  },
  PageBackground: {}
};

export class Dashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  handleOutletWidgetClick(val, outletid) {
    console.log("Dashboard got the click! " + val + " " + outletid);
    this.props.onOutletWidgetClick(val, outletid);
  }

  render() {
    return (
      <div container className="dashLayout">
        <Row className="dashRow">
          <LeftPane
            item
            styles={styles}
            probes={this.props.probes}
            probevals={this.props.probevals}
            feedmode={this.props.feedmode}
          />
          <RightPane
            item
            styles={styles}
            outlets={this.props.outlets}
            feedmode={this.props.feedmode}
            onOutletWidgetClick={this.handleOutletWidgetClick.bind(this)}
          />
          <CenterPane
            item
            styles={styles}
            feedmode={this.props.feedmode}
            onOutletWidgetClick={this.handleOutletWidgetClick.bind(this)}
            onFeedWidgetClick={this.props.onFeedWidgetClick}
            handleConfigSave={this.props.handleConfigSave}
            handleConfigLoad={this.props.handleConfigLoad}
            appConfig={this.props.appConfig}
          />
        </Row>
      </div>
    );
  }
}
const Modal = ({ handleClose, show, children }) => {
  const showHideClassName = show ? "modal display-block" : "modal display-none";

  return (
    <div className={showHideClassName}>
      <section className="modal-main">
        {children}
        <button onClick={handleClose}>Close</button>
      </section>
    </div>
  );
};
