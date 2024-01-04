import React, { Component } from "react";
import HighchartsWrapper from "./ProbeChart";

export class ProbeWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {
      LastTemp: "0.00",
      ProbeName: "Unkown",
    };
  }
  render() {


    return (
      <div>
        <h3 >{(this.props.data.probename)}</h3>
        <h1>{(this.props.data.lastTemperature)}</h1>
        {/* <h4>{this.props.data}</h4> */}
        <div>
              {/* <HighchartsReact highcharts={Highcharts} options={options} />*/}
              <HighchartsWrapper
                probename={this.props.probename}
                chartdata={this.props.chartdata}
                oneToOne={true}
              />
            </div>
      </div>
    );
      
  }
}
