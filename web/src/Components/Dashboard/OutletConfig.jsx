import React from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Datetime from "react-datetime";
import InputGroup from "react-bootstrap/InputGroup";
import Table from "react-bootstrap/Table";
import "../Layouts/rbp.css";
import "../Layouts/datetime.css";

export default class OutletConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = { showModal: this.props.show, controlType: null };
  }
  getInitialState = () => {
    return { showModal: false };
  };

  close = () => {
    this.setState({ showModal: false });
    this.props.onClose();
  };

  open = () => {
    this.setState({ showModal: true });
  };

  onChangeControlType(e) {
    //console.log("Control type changed");
    //console.log(e.target.value);
    this.setState({ controlType: e.target.value });

    if (e.target.value === "always") {
      this.setState({ controlType: <AlwaysConfig /> });
    } else if (e.target.value === "heater") {
      this.setState({ controlType: <HeaterConfig /> });
    } else if (e.target.value === "light") {
      this.setState({ controlType: <LightConfig /> });
    } else if (e.target.value === "skimmer") {
      this.setState({ controlType: <SkimmerConfig /> });
    } else if (e.target.value === "returnpump") {
      this.setState({ controlType: <ReturnConfig /> });
    } else if (e.target.value === "phcontrol") {
      this.setState({ controlType: <PhConfig /> });
    }
  }

  render() {
    //console.log("config click");
    //console.log(this.props.show);
    return (
      <Modal
        show={this.props.show}
        onHide={this.close}
        backdrop={"static"}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>
            Outlet {this.props.outletid.split("_", 3).reverse()[0]}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group controlId="formOutletName">
              <Form.Label>Name</Form.Label>
              <Form.Control type="text" placeholder={this.props.outletname} />
            </Form.Group>

            <Form.Group controlId="formControlType">
              <Form.Label>Control type</Form.Label>
              <Form.Control
                as="select"
                onChange={this.onChangeControlType.bind(this)}
              >
                <option value="always">Always</option>
                <option value="heater">Heater</option>
                <option value="light">Light</option>
                <option value="returnpump">Return Pump</option>
                <option value="skimmer">Skimmer</option>
                <option value="phcontrol">pH Control</option>
              </Form.Control>
            </Form.Group>

            <Form.Group controlId="formEnableLogging">
              <Form.Check type="checkbox" label="Enable Logging" />
            </Form.Group>
            <hr />
            <Form.Group controlId="formConfiguration">
              <Form.Label>
                <b>Configuration</b>
              </Form.Label>
              <br></br>
              {this.state.controlType}
            </Form.Group>
          </Form>
          <hr />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={this.close}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Save
          </Button>
        </Modal.Footer>
      </Modal>
    );
  }
}

class AlwaysConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return (
      <fieldset>
        <Form.Group as={Row}>
          <Form.Label as="legend" column sm={2}>
            State
          </Form.Label>
          <Col sm={10}>
            <Form.Check
              type="radio"
              label="OFF"
              name="formHorizontalRadios"
              id="formHorizontalRadiosOff"
            />
            <Form.Check
              type="radio"
              label="ON"
              name="formHorizontalRadios"
              id="formHorizontalRadiosOn"
            />
          </Col>
        </Form.Group>
      </fieldset>
    );
  }
}

class LightConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return (
      <div>
        <Form.Label>ON Time</Form.Label>
        <InputGroup>
          <Datetime
            dateFormat={false}
            timeFormat="HH:mm"
            defaultValue="08:00"
          />
          <InputGroup.Append>
            <InputGroup.Text>
              <img
                src={require("../Layouts/img/time.svg")}
                alt="time"
                height="24"
                width="24"
                align="center"
                hspace="8"
              />
            </InputGroup.Text>
          </InputGroup.Append>
        </InputGroup>
        <br></br>
        <Form.Label>OFF Time</Form.Label>
        <InputGroup>
          <Datetime
            dateFormat={false}
            timeFormat="HH:mm"
            defaultValue="17:00"
          />
          <InputGroup.Append>
            <InputGroup.Text>
              <img
                src={require("../Layouts/img/time.svg")}
                alt="time"
                height="24"
                width="24"
                align="center"
                hspace="8"
              />
            </InputGroup.Text>
          </InputGroup.Append>
        </InputGroup>
      </div>
    );
  }
}

class HeaterConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return (
      <div>
        <Form.Group controlId="formHeaterTempProbe">
          <Form.Label>Temperature Probe</Form.Label>
          <Form.Control as="select">
            <option value="one">one</option>
            <option value="two">two</option>
            <option value="three">three</option>
            <option value="four">four</option>
          </Form.Control>
        </Form.Group>
        <Form.Group controlId="formHeaterOnTemp">
          <Form.Label>On Temperature</Form.Label>
          <InputGroup>
            <InputGroup.Prepend>
              <Button variant="secondary">-</Button>
            </InputGroup.Prepend>
            <Form.Control
              as="input"
              type="number"
              min="0"
              max="300"
              step=".1"
            />
            <InputGroup.Append>
              <InputGroup.Text>°F</InputGroup.Text>
            </InputGroup.Append>
            <InputGroup.Append>
              <Button variant="secondary">+</Button>
            </InputGroup.Append>
          </InputGroup>
        </Form.Group>
        <Form.Group controlId="formHeaterOffTemp">
          <Form.Label>Off Temperature</Form.Label>
          <InputGroup>
            <InputGroup.Prepend>
              <Button variant="secondary">-</Button>
            </InputGroup.Prepend>
            <Form.Control
              as="input"
              type="number"
              min="0"
              max="300"
              step=".1"
            />
            <InputGroup.Append>
              <InputGroup.Text>°F</InputGroup.Text>
            </InputGroup.Append>
            <InputGroup.Append>
              <Button variant="secondary">+</Button>
            </InputGroup.Append>
          </InputGroup>
        </Form.Group>
      </div>
    );
  }
}

class ReturnConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return <FeedTimerConfig></FeedTimerConfig>;
  }
}

class SkimmerConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return <FeedTimerConfig></FeedTimerConfig>;
  }
}

class PhConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return (
      <div>
        <Form.Group controlId="formPhProbe">
          <Form.Label>Probe Name</Form.Label>
          <Form.Control as="select">
            <option value="chone">channel one</option>
            <option value="chtwo">channel two</option>
            <option value="chthree">channel three</option>
            <option value="chfour">channel four</option>
          </Form.Control>
        </Form.Group>
        <Form.Group controlId="formPhHigh">
          <Form.Label>High Value</Form.Label>
          <InputGroup>
            <InputGroup.Prepend>
              <Button variant="secondary">-</Button>
            </InputGroup.Prepend>
            <Form.Control as="input" type="number" min="0" max="14" step=".1" />
            <InputGroup.Append>
              <InputGroup.Text>pH</InputGroup.Text>
            </InputGroup.Append>
            <InputGroup.Append>
              <Button variant="secondary">+</Button>
            </InputGroup.Append>
          </InputGroup>
        </Form.Group>
        <Form.Group controlId="formPhLow">
          <Form.Label>Low Vaue</Form.Label>
          <InputGroup>
            <InputGroup.Prepend>
              <Button variant="secondary">-</Button>
            </InputGroup.Prepend>
            <Form.Control as="input" type="number" min="0" max="14" step=".1" />
            <InputGroup.Append>
              <InputGroup.Text>pH</InputGroup.Text>
            </InputGroup.Append>
            <InputGroup.Append>
              <Button variant="secondary">+</Button>
            </InputGroup.Append>
          </InputGroup>
        </Form.Group>
        <Form.Group controlId="formPhOnWhen">
          <Form.Label>On When</Form.Label>
          <Form.Control as="select">
            <option value="low">LOW</option>
            <option value="high">HIGH</option>
          </Form.Control>
        </Form.Group>
      </div>
    );
  }
}

class FeedTimerConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }
  render() {
    return (
      <div>
        <Table striped bordered size="sm">
          <thead>
            <tr>
              <th>Feed Mode</th>
              <th>Enable</th>
              <th>Additional Feed Timer Delay (seconds)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>A</td>
              <td>
                <Form.Check type="checkbox" />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>B</td>
              <td>
                <Form.Check type="checkbox" />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>C</td>
              <td>
                {" "}
                <Form.Check type="checkbox" />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>D</td>
              <td>
                <Form.Check type="checkbox" />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                  />
                </InputGroup>
              </td>
            </tr>
          </tbody>
        </Table>
      </div>
    );
  }
}
