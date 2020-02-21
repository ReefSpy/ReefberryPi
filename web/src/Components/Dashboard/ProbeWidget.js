import React from "react";
import { Fragment } from "react";
import HighchartsWrapper from "./ProbeChart";
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";

export default function(props) {
  //console.log("Render Probewidget " + props.probename);
  return (
    <Fragment>
      <Row>
        <Col>
          <div class="container">
            <h6>{props.probename}</h6>
            <h1>{props.probeval}</h1>
          </div>
        </Col>
        <Col>
          <div>
            {/* <HighchartsReact highcharts={Highcharts} options={options} />*/}
            <HighchartsWrapper
              probename={props.probename}
              chartdata={props.chartdata}
              oneToOne={true}
            />
          </div>
        </Col>
      </Row>
    </Fragment>
  );
}
