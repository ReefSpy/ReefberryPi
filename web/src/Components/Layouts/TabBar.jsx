import React from "react";
import Tab from "react-bootstrap/Tab";
import Nav from "react-bootstrap/Nav";
import Col from "react-bootstrap/Col";
import { Dashboard } from "../Dashboard";
import { GraphPage } from "../GraphPage/GraphPage";
import { AboutPage } from "../About/AboutPage";
import { tsPropertySignature } from "@babel/types";
import Button from "react-bootstrap/Button";

export default props => (
  <Tab.Container id="left-tabs-example" defaultActiveKey="dashboard">
    <style type="text/css">
      {`

            .nav-pills {
                padding: .5rem;
            }
            .nav-link  {
                color: black;
            }

            .nav-pills .nav-link.active,
            .nav-pills .show > .nav-link {
            color: black;
            background-color: orange; 
            }
           
          
      
            
            `}
    </style>

    <Col>
      <Nav variant="pills" className="flex-row">
        <Nav.Item>
          <Nav.Link eventKey="dashboard">
            <img
              src={require("./img/meter.svg")}
              alt="dashboard"
              height="24"
              width="24"
              align="center"
              hspace="8"
            />
            Dashboard
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="graphs">
            <img
              src={require("./img/chart.svg")}
              alt="dashboard"
              height="24"
              width="24"
              align="center"
              hspace="8"
            />
            Graphs
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="settings">
            <img
              src={require("./img/cog.svg")}
              alt="dashboard"
              height="24"
              width="24"
              align="center"
              hspace="8"
            />
            Settings
          </Nav.Link>
        </Nav.Item>
        <Nav.Item>
          <Nav.Link eventKey="about">
            <img
              src={require("./img/info.svg")}
              alt="dashboard"
              height="24"
              width="24"
              align="center"
              hspace="8"
            />
            About
          </Nav.Link>
        </Nav.Item>
      </Nav>
    </Col>
    <Col>
      <Tab.Content>
        <Tab.Pane eventKey="dashboard">
          <Dashboard
            probes={props.probes}
            probevals={props.probevals}
            outlets={props.outlets}
            feedmode={props.feedmode}
            onOutletWidgetClick={props.onOutletWidgetClick}
            onFeedWidgetClick={props.onFeedWidgetClick}
          />
        </Tab.Pane>
        <Tab.Pane eventKey="graphs">
          <GraphPage
            onPrimaryChartSelect={props.onPrimaryChartSelect}
            primaryChartData={props.primaryChartData}
          />
        </Tab.Pane>
        <Tab.Pane eventKey="settings">
          <h1>Settings coming soon</h1>
        </Tab.Pane>
        <Tab.Pane eventKey="about">
          <AboutPage />
        </Tab.Pane>
      </Tab.Content>
    </Col>
  </Tab.Container>
);
