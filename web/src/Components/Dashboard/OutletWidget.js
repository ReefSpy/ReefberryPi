import React from "react";
import MultiToggle from "react-multi-toggle";
import { Fragment } from "react";
import "./togglestyle.css";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Button from "react-bootstrap/Button";
import Modal from "react-bootstrap/Modal";
import OutletConfig from "./OutletConfig";
import "../Layouts/rbp.css";

const styles = {
  cfgButton: {
    position: "absolute",
    left: 10,
    bottom: 5,
    height: 24
  },
  outletLabel: {
    marginTop: 4,
    right: 10,
    textAlign: "left"
  },
  outletStyle: {
    border: "1px solid black",

    borderRadius: 15,
    margin: 2,
    backgroundColor: "white"
  }
};

const groupOptions = [
  {
    displayName: "OFF",
    value: 0,
    optionClass: "styleOff"
  },
  {
    displayName: "AUTO",
    value: 1,
    optionClass: "styleAuto"
  },
  {
    displayName: "ON",
    value: 2,
    optionClass: "styleOn"
  }
];

export class OutletWidget extends React.Component {
  //const [index, onChange] = useState(0);
  constructor(props) {
    super(props);
    this.state = {
      showModal: false
    };
  }
  getInitialState = () => {
    return { showModal: false };
  };

  close = () => {
    this.setState({ showModal: false });
  };

  open = () => {
    this.setState({ showModal: true });
  };
  render() {
    var outletStatusStyle = "outletStatus";
    if (!this.props.statusmsg.search("OFF")) {
      outletStatusStyle = "outletStatusOff";
    } else if (!this.props.statusmsg.search("ON")) {
      outletStatusStyle = "outletStatusOn";
    }

    return (
      <Fragment>
        <Col style={styles.outletStyle}>
          <MultiToggle
            options={groupOptions}
            label={this.props.outletname}
            onSelectOption={this.onToggleSelect}
            selectedOption={this.props.buttonstateidx}
            className={"outletSlider"}
          />
          <Row>
            <Col>
              <Button
                style={styles.cfgButton}
                variant="outline-light"
                onClick={this.open}
              >
                <img
                  src={require("../Layouts/img/cog.svg")}
                  alt="settings"
                  height="12"
                  width="12"
                  align="left"
                />
              </Button>
              <OutletConfig
                show={this.state.showModal}
                onHide={this.close}
                backdrop={"static"}
                onClose={this.handleClose.bind(this)}
                outletname={this.props.outletname}
                outletid={this.props.outletid}
                outlettype={this.props.outlettype}
                outlet={this.props.outlet}
                appConfig={this.props.appConfig}
              ></OutletConfig>

              <body className={outletStatusStyle}>{this.props.statusmsg}</body>
            </Col>
          </Row>
        </Col>
      </Fragment>
    );
  }
  handleClose() {
    console.log("Close detected!");
    this.close();
  }

  onToggleSelect = value => {
    console.log(value);

    this.props.onClick(value, this.props.outletid);
  };
}
