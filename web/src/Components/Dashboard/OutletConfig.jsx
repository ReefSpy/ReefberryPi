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

var getTrueFalse = val => {
  if (val === "True") {
    return true;
  } else {
    return false;
  }
};

export default class OutletConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: this.props.show,
      controlType: null,
      control_type: null,
      enable_log: null
    };
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

  show = () => {
    console.log("Outlet Config Show");
    console.log("props", this.props.appConfig);
    console.log(
      "enable log",
      this.props.outletid,
      this.props.appConfig["outletDict"][this.props.outletid]["enable_log"]
    );

    this.setState({
      enable_log: this.props.appConfig["outletDict"][this.props.outletid][
        "enable_log"
      ]
    });
    this.setState({
      control_type: this.props.appConfig["outletDict"][this.props.outletid][
        "control_type"
      ]
    });
    this.selectFromDropDownList(
      this.props.appConfig["outletDict"][this.props.outletid]["control_type"]
    );
  };

  onChangeControlType(e) {
    //console.log("Control type changed");
    //console.log(e.target.value);
    this.selectFromDropDownList(e.target.value);
  }

  onChangeEnableLog() {
    this.setState(this.setEnableLog);
  }

  setEnableLog(state, props) {
    if (state.enable_log === "True") {
      state.enable_log = "False";
      console.log(this.props.outletid, "enable_log set to", state.enable_log);
    } else {
      state.enable_log = "True";
      console.log(this.props.outletid, "enable_log set to", state.enable_log);
    }
    return { ...state, enable_log: state.enable_log };
  }

  selectFromDropDownList(selection) {
    if (selection === "Always") {
      this.setState({
        controlType: (
          <AlwaysConfig
            appConfig={this.props.appConfig}
            outletid={this.props.outletid}
          />
        )
      });
      this.setState({ control_type: "Always" });
    } else if (selection === "Heater") {
      this.setState({
        controlType: (
          <HeaterConfig
            appConfig={this.props.appConfig}
            outletid={this.props.outletid}
            probes={this.props.probes}
          />
        )
      });
      this.setState({ control_type: "Heater" });
    } else if (selection === "Light") {
      this.setState({
        controlType: (
          <LightConfig
            appConfig={this.props.appConfig}
            outletid={this.props.outletid}
          />
        )
      });
      this.setState({ control_type: "Light" });
    } else if (selection === "Skimmer") {
      this.setState({
        controlType: (
          <SkimmerConfig
            appConfig={this.props.appConfig}
            outletid={this.props.outletid}
          />
        )
      });
      this.setState({ control_type: "Skimmer" });
    } else if (selection === "Return Pump") {
      this.setState({
        controlType: (
          <ReturnConfig
            appConfig={this.props.appConfig}
            outletid={this.props.outletid}
          />
        )
      });
      this.setState({ control_type: "Return Pump" });
    } else if (selection === "pH Control") {
      this.setState({
        controlType: (
          <PhConfig
            appConfig={this.props.appConfig}
            outletid={this.props.outletid}
            probes={this.props.probes}
          />
        )
      });
      this.setState({ control_type: "pH Control" });
    }
  }
  componentDidMount() {
    console.log(
      "The outlet control type is:",
      this.props.outlet["control_type"],
      this.props.outletid
    );
    console.log(this.props);
    this.setState({ control_type: this.props.outlet.control_type });
  }
  render() {
    //console.log("config click");
    //console.log(this.props.show);
    return (
      <Modal
        show={this.props.show}
        onShow={this.show}
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
              <Form.Control
                type="text"
                defaultValue={this.props.outletname}
                placeholder="Unnamed"
              />
            </Form.Group>

            <Form.Group controlId="formControlType">
              <Form.Label>Control type</Form.Label>
              <Form.Control
                as="select"
                onChange={this.onChangeControlType.bind(this)}
                value={this.state.control_type}
              >
                <option value="Always">Always</option>
                <option value="Heater">Heater</option>
                <option value="Light">Light</option>
                <option value="Return Pump">Return Pump</option>
                <option value="Skimmer">Skimmer</option>
                <option value="pH Control">pH Control</option>
              </Form.Control>
            </Form.Group>

            <Form.Group controlId="formEnableLogging">
              <Form.Check
                type="checkbox"
                label="Enable Logging"
                checked={getTrueFalse(this.state.enable_log)}
                onChange={this.onChangeEnableLog.bind(this)}
              />
            </Form.Group>
            <hr />
            <Form.Group>
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
    this.state = {
      option: this.props.appConfig["outletDict"][this.props.outletid][
        "always_state"
      ]
    };

    console.log("Always config construct", this.props.appConfig);
  }
  handleOnCheck(option) {
    console.log(option);
    this.setState({
      option: option
    });
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
              onChange={this.handleOnCheck.bind(this, "OFF")}
              checked={this.state.option === "OFF"}
            />
            <Form.Check
              type="radio"
              label="ON"
              name="formHorizontalRadios"
              id="formHorizontalRadiosOn"
              onChange={this.handleOnCheck.bind(this, "ON")}
              checked={this.state.option === "ON"}
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
            defaultValue={
              this.props.appConfig["outletDict"][this.props.outletid][
                "light_on"
              ]
            }
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
            defaultValue={
              this.props.appConfig["outletDict"][this.props.outletid][
                "light_off"
              ]
            }
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
    this.state = {
      tempProbes: [],
      selectedProbe: "",
      onVal: "",
      offVal: "",
      scale: ""
    };
  }

  componentDidMount() {
    let items = [];
    console.log("Heater Config Probe List:", this.props.probes);

    var tempProbeList = this.props.probes.slice(0);
    console.log(tempProbeList);
    for (var tempProbe in tempProbeList) {
      console.log(tempProbe, tempProbeList[tempProbe]["probetype"]);
      if (tempProbeList[tempProbe]["probetype"] === "ds18b20") {
        console.log(
          tempProbeList[tempProbe]["probeid"],
          tempProbeList[tempProbe]["probename"]
        );
        items.push(
          <option key={tempProbe} value={tempProbeList[tempProbe]["probeid"]}>
            {tempProbeList[tempProbe]["probename"]} [
            {tempProbeList[tempProbe]["probeid"].split("_", 2)[1]}]
          </option>
        );
      }
    }

    this.setState({ tempProbes: items });
    this.setState({
      selectedProbe: this.props.appConfig["outletDict"][this.props.outletid][
        "heater_probe"
      ]
    });

    if (this.props.appConfig["temperaturescale"] == "1") {
      console.log("Temperature scale is Fahrenheit");
      this.setState({ scale: "°F" });

      var onTempF =
        1.8 *
          this.props.appConfig["outletDict"][this.props.outletid]["heater_on"] +
        32;
      this.setState({
        onVal: onTempF.toFixed(1)
      });

      var offTempF =
        1.8 *
          this.props.appConfig["outletDict"][this.props.outletid][
            "heater_off"
          ] +
        32;
      this.setState({
        offVal: offTempF.toFixed(1)
      });
    } else {
      console.log(
        "Temperature scale is Celcius",
        this.props.appConfig["temperaturescale"]
      );
      this.setState({ scale: "°C" });
      this.setState({
        onVal: this.props.appConfig["outletDict"][this.props.outletid][
          "heater_on"
        ]
      });
      this.setState({
        offVal: this.props.appConfig["outletDict"][this.props.outletid][
          "heater_off"
        ]
      });
    }
  }

  onChangeProbe(e) {
    console.log("onChangeProbe", e.target.value);
    this.setState({ selectedProbe: e.target.value });
  }

  onOnValChange(e) {
    console.log("On Val Change", e.target.value);
    this.setState({
      onVal: e.target.value
    });
  }

  onOffValChange(e) {
    console.log("Off Val Change", e.target.value);
    this.setState({
      offVal: e.target.value
    });
  }

  increaseOnTemp() {
    this.setState({
      onVal: (parseFloat(this.state.onVal) + 0.1).toFixed(1)
    });
    console.log("on click +", this.state.onVal);
  }
  decreaseOnTemp() {
    this.setState({
      onVal: (parseFloat(this.state.onVal) - 0.1).toFixed(1)
    });
    console.log("on click -", this.state.onVal);
  }

  increaseOffTemp() {
    this.setState({
      offVal: (parseFloat(this.state.offVal) + 0.1).toFixed(1)
    });
    console.log("low click +", this.state.offVal);
  }

  decreaseOffTemp() {
    this.setState({
      offVal: (parseFloat(this.state.offVal) - 0.1).toFixed(1)
    });
    console.log("low click -", this.state.offVal);
  }

  render() {
    return (
      <div>
        <Form.Group controlId="formHeaterTempProbe">
          <Form.Label>Temperature Probe</Form.Label>
          <Form.Control
            as="select"
            value={this.state.selectedProbe}
            onChange={this.onChangeProbe.bind(this)}
          >
            {this.state.tempProbes}
          </Form.Control>
        </Form.Group>
        <Form.Group controlId="formHeaterOnTemp">
          <Form.Label>On Temperature</Form.Label>
          <InputGroup>
            <InputGroup.Prepend>
              <Button
                variant="secondary"
                onClick={this.decreaseOnTemp.bind(this)}
              >
                -
              </Button>
            </InputGroup.Prepend>
            <Form.Control
              as="input"
              type="number"
              min="0"
              max="300"
              step=".1"
              value={this.state.onVal}
              onChange={this.onOnValChange.bind(this)}
            />
            <InputGroup.Append>
              <InputGroup.Text>{this.state.scale}</InputGroup.Text>
            </InputGroup.Append>
            <InputGroup.Append>
              <Button
                variant="secondary"
                onClick={this.increaseOnTemp.bind(this)}
              >
                +
              </Button>
            </InputGroup.Append>
          </InputGroup>
        </Form.Group>
        <Form.Group controlId="formHeaterOffTemp">
          <Form.Label>Off Temperature</Form.Label>
          <InputGroup>
            <InputGroup.Prepend>
              <Button
                variant="secondary"
                onClick={this.decreaseOffTemp.bind(this)}
              >
                -
              </Button>
            </InputGroup.Prepend>
            <Form.Control
              as="input"
              type="number"
              min="0"
              max="300"
              step=".1"
              value={this.state.offVal}
              onChange={this.onOffValChange.bind(this)}
            />
            <InputGroup.Append>
              <InputGroup.Text>{this.state.scale}</InputGroup.Text>
            </InputGroup.Append>
            <InputGroup.Append>
              <Button
                variant="secondary"
                onClick={this.increaseOffTemp.bind(this)}
              >
                +
              </Button>
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
    console.log("return config construct", this.props.appConfig);
  }

  render() {
    return (
      <FeedTimerReturnConfig
        appConfig={this.props.appConfig}
        outletid={this.props.outletid}
      ></FeedTimerReturnConfig>
    );
  }
}

class SkimmerConfig extends React.Component {
  constructor(props) {
    super(props);
    console.log("skimmer config construct", this.props.appConfig);
  }
  render() {
    return (
      <FeedTimerSkimmerConfig
        appConfig={this.props.appConfig}
        outletid={this.props.outletid}
      ></FeedTimerSkimmerConfig>
    );
  }
}

class PhConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      phProbes: [],
      selectedProbe: "",
      onWhen: "",
      highVal: "",
      lowVal: ""
    };
  }
  componentDidMount() {
    let items = [];
    console.log("PH Config Probe List:", this.props.probes);

    var phProbeList = this.props.probes.slice(0);
    console.log(phProbeList);
    for (var phProbe in phProbeList) {
      console.log(phProbe, phProbeList[phProbe]["probetype"]);
      if (phProbeList[phProbe]["probetype"] === "mcp3008") {
        console.log(
          phProbeList[phProbe]["probeid"],
          phProbeList[phProbe]["probename"]
        );
        items.push(
          <option key={phProbe} value={phProbeList[phProbe]["probeid"]}>
            {phProbeList[phProbe]["probename"]} [
            {phProbeList[phProbe]["probeid"]}]
          </option>
        );
      }
    }

    this.setState({ phProbes: items });
    this.setState({
      selectedProbe: this.props.appConfig["outletDict"][this.props.outletid][
        "ph_probe"
      ]
    });

    this.setState({
      onWhen: this.props.appConfig["outletDict"][this.props.outletid][
        "ph_onwhen"
      ]
    });

    this.setState({
      highVal: this.props.appConfig["outletDict"][this.props.outletid][
        "ph_high"
      ]
    });

    this.setState({
      lowVal: this.props.appConfig["outletDict"][this.props.outletid]["ph_low"]
    });
  }

  onChangeProbe(e) {
    console.log("onChangeProbe", e.target.value);
    this.setState({ selectedProbe: e.target.value });
  }

  onChangeWhen(e) {
    console.log("onChangeWhen", e.target.value);
    this.setState({ onWhen: e.target.value });
  }

  increaseHighVal() {
    this.setState({
      highVal: (parseFloat(this.state.highVal) + 0.1).toFixed(1)
    });
    console.log("high click +", this.state.highVal);
  }
  decreaseHighVal() {
    this.setState({
      highVal: (parseFloat(this.state.highVal) - 0.1).toFixed(1)
    });
    console.log("high click -", this.state.highVal);
  }

  increaseLowVal() {
    this.setState({
      lowVal: (parseFloat(this.state.lowVal) + 0.1).toFixed(1)
    });
    console.log("low click +", this.state.lowVal);
  }

  decreaseLowVal() {
    this.setState({
      lowVal: (parseFloat(this.state.lowVal) - 0.1).toFixed(1)
    });
    console.log("low click -", this.state.lowVal);
  }

  onHighValChange(e) {
    console.log("High Val Change", e.target.value);
    this.setState({
      highVal: e.target.value
    });
  }

  onLowValChange(e) {
    console.log("Low Val Change", e.target.value);
    this.setState({
      lowVal: e.target.value
    });
  }

  render() {
    return (
      <div>
        <Form.Group controlId="formPhProbe">
          <Form.Label>Probe Name</Form.Label>
          <Form.Control
            as="select"
            value={this.state.selectedProbe}
            onChange={this.onChangeProbe.bind(this)}
          >
            {this.state.phProbes}
          </Form.Control>
        </Form.Group>
        <Form.Group controlId="formPhHigh">
          <Form.Label>High Value</Form.Label>
          <InputGroup>
            <InputGroup.Prepend>
              <Button
                variant="secondary"
                onClick={this.decreaseHighVal.bind(this)}
              >
                -
              </Button>
            </InputGroup.Prepend>
            <Form.Control
              as="input"
              type="number"
              min="0"
              max="14"
              step=".1"
              value={this.state.highVal}
              onChange={this.onHighValChange.bind(this)}
            />
            <InputGroup.Append>
              <InputGroup.Text>pH</InputGroup.Text>
            </InputGroup.Append>
            <InputGroup.Append>
              <Button
                variant="secondary"
                onClick={this.increaseHighVal.bind(this)}
              >
                +
              </Button>
            </InputGroup.Append>
          </InputGroup>
        </Form.Group>
        <Form.Group controlId="formPhLow">
          <Form.Label>Low Vaue</Form.Label>
          <InputGroup>
            <InputGroup.Prepend>
              <Button
                variant="secondary"
                onClick={this.decreaseLowVal.bind(this)}
              >
                -
              </Button>
            </InputGroup.Prepend>
            <Form.Control
              as="input"
              type="number"
              min="0"
              max="14"
              step=".1"
              value={this.state.lowVal}
              onChange={this.onLowValChange.bind(this)}
            />
            <InputGroup.Append>
              <InputGroup.Text>pH</InputGroup.Text>
            </InputGroup.Append>
            <InputGroup.Append>
              <Button
                variant="secondary"
                onClick={this.increaseLowVal.bind(this)}
              >
                +
              </Button>
            </InputGroup.Append>
          </InputGroup>
        </Form.Group>
        <Form.Group controlId="formPhOnWhen">
          <Form.Label>On When</Form.Label>
          <Form.Control
            as="select"
            value={this.state.onWhen}
            onChange={this.onChangeWhen.bind(this)}
          >
            <option value="LOW">LOW</option>
            <option value="HIGH">HIGH</option>
          </Form.Control>
        </Form.Group>
      </div>
    );
  }
}

class FeedTimerReturnConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      return_enable_feed_a: null,
      return_feed_delay_a: null,
      return_enable_feed_b: null,
      return_feed_delay_b: null,
      return_enable_feed_c: null,
      return_feed_delay_c: null,
      return_enable_feed_d: null,
      return_feed_delay_d: null
    };
    console.log("construvtor");
    console.log(this.props.appConfig);
  }
  componentDidMount() {
    this.loadvals();
  }

  loadvals() {
    console.log("loadvals");
    try {
      this.setState({
        return_enable_feed_a: getTrueFalse(
          this.props.appConfig["outletDict"][this.props.outletid][
            "return_enable_feed_a"
          ]
        )
      });

      this.setState({
        return_feed_delay_a: this.props.appConfig["outletDict"][
          this.props.outletid
        ]["return_feed_delay_a"]
      });

      this.setState({
        return_enable_feed_b: getTrueFalse(
          this.props.appConfig["outletDict"][this.props.outletid][
            "return_enable_feed_b"
          ]
        )
      });

      this.setState({
        return_feed_delay_b: this.props.appConfig["outletDict"][
          this.props.outletid
        ]["return_feed_delay_b"]
      });

      this.setState({
        return_enable_feed_c: getTrueFalse(
          this.props.appConfig["outletDict"][this.props.outletid][
            "return_enable_feed_c"
          ]
        )
      });

      this.setState({
        return_feed_delay_c: this.props.appConfig["outletDict"][
          this.props.outletid
        ]["return_feed_delay_c"]
      });

      this.setState({
        return_enable_feed_d: getTrueFalse(
          this.props.appConfig["outletDict"][this.props.outletid][
            "return_enable_feed_d"
          ]
        )
      });

      this.setState({
        return_feed_delay_d: this.props.appConfig["outletDict"][
          this.props.outletid
        ]["return_feed_delay_d"]
      });
    } catch (err) {
      console.log(err);
    }
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
                <Form.Check
                  name="return_enable_feed_a"
                  type="checkbox"
                  defaultChecked={this.state.return_enable_feed_a}
                />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    name="return_feed_delay_a"
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                    defaultValue={this.state.return_feed_delay_a}
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>B</td>
              <td>
                <Form.Check
                  name="return_enable_feed_b"
                  type="checkbox"
                  defaultChecked={this.state.return_enable_feed_b}
                />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    name="return_feed_delay_b"
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                    defaultValue={this.state.return_feed_delay_b}
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>C</td>
              <td>
                {" "}
                <Form.Check
                  name="return_enable_feed_c"
                  type="checkbox"
                  defaultChecked={this.state.return_enable_feed_c}
                />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    name="return_feed_delay_c"
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                    defaultValue={this.state.return_feed_delay_c}
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>D</td>
              <td>
                <Form.Check
                  name="return_enable_feed_d"
                  type="checkbox"
                  defaultChecked={this.state.return_enable_feed_d}
                />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    name="return_feed_delay_d"
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                    defaultValue={this.state.return_feed_delay_d}
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

class FeedTimerSkimmerConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      skimmer_enable_feed_a: null,
      skimmer_feed_delay_a: null,
      skimmer_enable_feed_b: null,
      skimmer_feed_delay_b: null,
      skimmer_enable_feed_c: null,
      skimmer_feed_delay_c: null,
      skimmer_enable_feed_d: null,
      skimmer_feed_delay_d: null
    };
    //console.log("constructor");
    console.log(this.props.appConfig);
  }
  componentDidMount() {
    this.loadvals();
  }

  loadvals() {
    console.log("loadvals");
    try {
      this.setState({
        skimmer_enable_feed_a: getTrueFalse(
          this.props.appConfig["outletDict"][this.props.outletid][
            "skimmer_enable_feed_a"
          ]
        )
      });

      this.setState({
        skimmer_feed_delay_a: this.props.appConfig["outletDict"][
          this.props.outletid
        ]["skimmer_feed_delay_a"]
      });

      this.setState({
        skimmer_enable_feed_b: getTrueFalse(
          this.props.appConfig["outletDict"][this.props.outletid][
            "skimmer_enable_feed_b"
          ]
        )
      });

      this.setState({
        skimmer_feed_delay_b: this.props.appConfig["outletDict"][
          this.props.outletid
        ]["skimmer_feed_delay_b"]
      });

      this.setState({
        skimmer_enable_feed_c: getTrueFalse(
          this.props.appConfig["outletDict"][this.props.outletid][
            "skimmer_enable_feed_c"
          ]
        )
      });

      this.setState({
        skimmer_feed_delay_c: this.props.appConfig["outletDict"][
          this.props.outletid
        ]["skimmer_feed_delay_c"]
      });

      this.setState({
        skimmer_enable_feed_d: getTrueFalse(
          this.props.appConfig["outletDict"][this.props.outletid][
            "skimmer_enable_feed_d"
          ]
        )
      });

      this.setState({
        skimmer_feed_delay_d: this.props.appConfig["outletDict"][
          this.props.outletid
        ]["skimmer_feed_delay_d"]
      });
    } catch (err) {
      console.log(err);
    }
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
                <Form.Check
                  name="skimmer_enable_feed_a"
                  type="checkbox"
                  defaultChecked={this.state.skimmer_enable_feed_a}
                />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    name="skimmer_feed_delay_a"
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                    defaultValue={this.state.skimmer_feed_delay_a}
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>B</td>
              <td>
                <Form.Check
                  name="skimmer_enable_feed_b"
                  type="checkbox"
                  defaultChecked={this.state.skimmer_enable_feed_b}
                />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    name="skimmer_feed_delay_b"
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                    defaultValue={this.state.skimmer_feed_delay_b}
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>C</td>
              <td>
                {" "}
                <Form.Check
                  name="skimmer_enable_feed_c"
                  type="checkbox"
                  defaultChecked={this.state.skimmer_enable_feed_c}
                />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    name="skimmer_feed_delay_c"
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                    defaultValue={this.state.skimmer_feed_delay_c}
                  />
                </InputGroup>
              </td>
            </tr>
            <tr>
              <td>D</td>
              <td>
                <Form.Check
                  name="skimmer_enable_feed_d"
                  type="checkbox"
                  defaultChecked={this.state.skimmer_enable_feed_d}
                />
              </td>
              <td>
                <InputGroup>
                  <Form.Control
                    name="skimmer_feed_delay_d"
                    as="input"
                    type="number"
                    min="0"
                    max="3600"
                    step="1"
                    defaultValue={this.state.skimmer_feed_delay_d}
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
