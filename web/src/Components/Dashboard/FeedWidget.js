import React from "react";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import FeedConfig from "./FeedConfig";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";

const styles = {
  Button: {
    backgroundColor: "#747c8e",
    margin: 4,
    color: "#FFFFFF",
    borderRadius: 15,
    fontSize: "10px",
    fontWeight: "bold",
    size: "small",
    maxWidth: "30px",
    minWidth: "30px",
    width: "30px",
    height: "30px"
  },
  activeButton: {
    backgroundColor: "#99e34f",
    margin: 4,
    color: "#000000",
    borderRadius: 15,
    fontSize: "10px",
    fontWeight: "bold",
    size: "small",
    maxWidth: "30px",
    minWidth: "30px",
    width: "30px",
    height: "30px",
    border: "2px solid #747c8e"
  },
  CancelButton: {
    backgroundColor: "#747c8e",
    margin: 4,
    color: "#FFFFFF",
    borderRadius: 15,
    fontSize: "10px",
    fontWeight: "bold",
    size: "small",
    height: "30px"
  }
};

export class FeedWidget extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      buttonStyles: {
        A: styles.Button,
        B: styles.Button,
        C: styles.Button,
        D: styles.Button
      }
    };
  }
  timeConvert(time) {
    // console.log(this.props.feedmode["timeremaining"]);
    var measuredTime = new Date(null);
    measuredTime.setSeconds(time); // specify value of SECONDS
    var MHSTime = measuredTime.toISOString().substr(11, 8);
    if (time > 0) {
      return MHSTime;
    } else return <br></br>;
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
    // console.log(this.props.feedmode);
    var buttonStylesClone = this.state.buttonStyles;
    if (this.props.feedmode["feedtimer"] === "A") {
      buttonStylesClone["A"] = styles.activeButton;
      //this.setState({ buttonStyles: buttonStylesClone });
    } else if (this.props.feedmode["feedtimer"] === "B") {
      buttonStylesClone["B"] = styles.activeButton;
    } else if (this.props.feedmode["feedtimer"] === "C") {
      buttonStylesClone["C"] = styles.activeButton;
    } else if (this.props.feedmode["feedtimer"] === "D") {
      buttonStylesClone["D"] = styles.activeButton;
    } else {
      buttonStylesClone["A"] = styles.Button;
      buttonStylesClone["B"] = styles.Button;
      buttonStylesClone["C"] = styles.Button;
      buttonStylesClone["D"] = styles.Button;
    }

    return (
      <div style={{ maxWidth: "300px", minWidth: "300px" }}>
        <Container>
          <Col container>Feed Mode</Col>
          <Row>
            <Col>{this.timeConvert(this.props.feedmode["timeremaining"])}</Col>
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
            </Col>
          </Row>
          <Row>
            <Col container>
              <Button
                style={this.state.buttonStyles["A"]}
                onClick={() => this.props.onClick("A")}
                variant="outline-dark"
              >
                A
              </Button>
              <Button
                style={this.state.buttonStyles["B"]}
                onClick={() => this.props.onClick("B")}
                variant="outline-dark"
              >
                B
              </Button>
              <Button
                style={this.state.buttonStyles["C"]}
                onClick={() => this.props.onClick("C")}
                variant="outline-dark"
              >
                C
              </Button>
              <Button
                style={this.state.buttonStyles["D"]}
                onClick={() => this.props.onClick("D")}
                variant="outline-dark"
              >
                D
              </Button>
              <Button
                style={styles.CancelButton}
                onClick={() => this.props.onClick("CANCEL")}
                variant="outline-dark"
              >
                Cancel
              </Button>
            </Col>
          </Row>
        </Container>

        <FeedConfig
          show={this.state.showModal}
          onHide={this.close}
          backdrop={"static"}
          onClose={this.handleClose.bind(this)}
        ></FeedConfig>
      </div>
    );
  }

  handleClose() {
    console.log("Close detected!");
    this.close();
  }
}
