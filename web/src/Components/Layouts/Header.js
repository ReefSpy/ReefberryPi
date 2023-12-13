import React from "react";
import Navbar from "react-bootstrap/Navbar";

export default props => (
  <Navbar bg="dark" variant="dark">
    <img
      src={require("./img/reefberry-pi-logo.svg")}
      alt="logo"
      height="48"
      width="48"
      align="center"
      hspace="8"
    />
    <Navbar.Brand>Reefberry Pi Web</Navbar.Brand>
  </Navbar>
);
