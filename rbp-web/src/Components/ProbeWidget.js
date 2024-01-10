import React, { Component } from "react";
import HighchartsWrapper from "./ProbeChart";
import "./ProbeWidget.css";
export class ProbeWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {
      LastTemp: "0.00",
      ProbeName: "Unkown",
      apiResponse: null,
      ChartData: null,
    };
  }

  // generic API call structure
  apiCall(endpoint, callback) {
    fetch(endpoint)
      .then((response) => {
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Data not found");
          } else if (response.status === 500) {
            throw new Error("Server error");
          } else {
            throw new Error("Network response was not ok");
          }
        }
        return response.json();
      })
      .then((data) => {
        this.setState({ ChartData: data });
        callback(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  componentDidMount() {
    //console.log(this.props.probename)
    let apiURL = "http://xpi01.local:5000/get_chartdata_24hr/QV3BIZZV/".concat(
      this.props.data.probeid
    );
    this.apiCall(apiURL, this.GetChartData);

    // outlet list
    this.interval = setInterval(() => {
      this.apiCall(apiURL, this.GetChartData);
    }, 600000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  GetChartData(chartdata) {
    console.log(chartdata);
  }

  render() {
   
    return (
      <div class="probecontainer">
        <div class="item probename">{this.props.data.probename}</div>
        <div class="item probevalue">{this.props.data.lastTemperature} </div>
        <div class="item chartdata">
          <div>
            <HighchartsWrapper
              probename={this.props.probename}
              chartdata={this.state.ChartData}
              oneToOne={true}
            />
          </div>
        </div>
      </div>
    );
  }
}
