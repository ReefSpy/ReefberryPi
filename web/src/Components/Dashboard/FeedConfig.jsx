import React from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import InputGroup from "react-bootstrap/InputGroup";
import Table from "react-bootstrap/Table";

export default class OutletConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: this.props.show,
      feed_a: null,
      feed_b: null,
      feed_c: null,
      feed_d: null
    };
    this.handleInputChange = this.handleInputChange.bind(this);
  }
  handleInputChange(event) {
    const target = event.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;

    this.setState({
      [name]: value
    });
  }

  getInitialState = () => {
    return { showModal: false };
  };

  close = () => {
    this.setState({ showModal: false });
    this.props.onClose();
  };

  show = () => {
    /* this.setState({ feed_a: this.getValue("feed_timers", "feed_a", "60") });
    this.setState({ feed_b: this.getValue("feed_timers", "feed_b", "60") });
    this.setState({ feed_c: this.getValue("feed_timers", "feed_c", "60") });
    this.setState({ feed_d: this.getValue("feed_timers", "feed_d", "60") }); */
    console.log("load feed config form");
    console.log(this.props.appConfig);
    //this.getValue();

    this.props.handleConfigLoad();
    this.setState({ feed_a: this.props.appConfig["feed_a_time"] });
    this.setState({ feed_b: this.props.appConfig["feed_b_time"] });
    this.setState({ feed_c: this.props.appConfig["feed_c_time"] });
    this.setState({ feed_d: this.props.appConfig["feed_d_time"] });
    this.props.onShow();
  };

  open = () => {
    this.setState({ showModal: true });
  };

  save = () => {
    this.setState({ showModal: false });
    this.props.onSave("feed_timers", "feed_a", this.state.feed_a);
    this.props.onSave("feed_timers", "feed_b", this.state.feed_b);
    this.props.onSave("feed_timers", "feed_c", this.state.feed_c);
    this.props.onSave("feed_timers", "feed_d", this.state.feed_d);
    console.log(
      "save feed config form",
      this.state.feed_a,
      this.state.feed_b,
      this.state.feed_c,
      this.state.feed_d
    );
  };

  //getValue = () => {
  //  console.log("getValue");
  //  this.props.handleConfigLoad();
  //};

  componentWillUpdate() {
    //console.log("componentWillUpdate", this.props.appConfig["feed_a_time"]);
  }

  render() {
    return (
      <Modal
        show={this.props.show}
        onHide={this.close}
        onShow={this.show}
        backdrop={"static"}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Feed Timers</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Table striped bordered size="sm">
            <thead>
              <tr>
                <th>Timer</th>
                <th>Duration (seconds)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>A</td>
                <td>
                  <InputGroup>
                    <Form.Control
                      name="feed_a"
                      as="input"
                      type="number"
                      min="0"
                      max="3600"
                      step="1"
                      defaultValue={this.state.feed_a}
                      onChange={this.handleInputChange}
                    />
                  </InputGroup>
                </td>
              </tr>
              <tr>
                <td>B</td>
                <td>
                  <InputGroup>
                    <Form.Control
                      name="feed_b"
                      as="input"
                      type="number"
                      min="0"
                      max="3600"
                      step="1"
                      defaultValue={this.state.feed_b}
                      onChange={this.handleInputChange}
                    />
                  </InputGroup>
                </td>
              </tr>
              <tr>
                <td>C</td>
                <td>
                  <InputGroup>
                    <Form.Control
                      name="feed_c"
                      as="input"
                      type="number"
                      min="0"
                      max="3600"
                      step="1"
                      defaultValue={this.state.feed_c}
                      onChange={this.handleInputChange}
                    />
                  </InputGroup>
                </td>
              </tr>
              <tr>
                <td>D</td>
                <td>
                  <InputGroup>
                    <Form.Control
                      name="feed_d"
                      as="input"
                      type="number"
                      min="0"
                      max="3600"
                      step="1"
                      defaultValue={this.state.feed_d}
                      onChange={this.handleInputChange}
                    />
                  </InputGroup>
                </td>
              </tr>
            </tbody>
          </Table>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={this.close}>
            Cancel
          </Button>
          <Button variant="primary" type="submit" onClick={this.save}>
            Save
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }
}
