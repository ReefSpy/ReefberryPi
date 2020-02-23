import React from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import Form from "react-bootstrap/Form";
import InputGroup from "react-bootstrap/InputGroup";
import Table from "react-bootstrap/Table";

export default class OutletConfig extends React.Component {
  constructor(props) {
    super(props);
    this.state = { showModal: this.props.show };
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

  render() {
    return (
      <Modal
        show={this.props.show}
        onHide={this.close}
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
