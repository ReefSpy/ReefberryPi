import React, { Component } from "react";
import "./Analytics.css";
import HighchartsWrapper from "./AnalyticsChart";

class Analytics extends Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedChart: 1,
      tempCharts: [{ chartname: "probe1" }, { chartname: "probe2" }],
    };

    this.handleChartSelectorChange = this.handleChartSelectorChange.bind(this);
    this.handleTimeSelectorChange = this.handleTimeSelectorChange.bind(this);
    this.handleFetchButtonRequest = this.handleFetchButtonRequest.bind(this);
  }

  // need to convert timestamp to milliseconds to show up properly in HighCharts
  formatChartData = (chartdata) => {
    for (let datapoint in chartdata) {
      // console.log(chartdata[datapoint])
      // console.log(chartdata[datapoint][0])
      // console.log(Date(chartdata[datapoint][0]))

      let newDate = new Date(chartdata[datapoint][0]).getTime();
      chartdata[datapoint][0] = newDate;
    }
    this.setState({ ChartData: chartdata });
  };

  componentDidMount() {}

  handleChartSelectorChange(event) {
    console.log(event.target.value);
    console.log(event.target.selectedIndex);
    console.log(this.props.probearray[event.target.selectedIndex].probeid);

    let unit_type = "unknown";
    if (
      this.props.probearray[event.target.selectedIndex].sensortype ===
      "humidity"
    ) {
      unit_type = "humidity";
    } else if (
      this.props.probearray[event.target.selectedIndex].sensortype ===
      "temperature"
    ) {
      unit_type = "temperature";
    }
    this.setState({ unitType: unit_type });
    this.setState({
      probeid: this.props.probearray[event.target.selectedIndex].probeid,
    });
    this.setState({ selectedChart: event.target.selectedIndex });
  }
  handleTimeSelectorChange(event) {
    console.log(event.target.value);
    console.log(event.target.selectedIndex);
    this.setState({ selectedTime: event.target.value });
  }

  handleFetchButtonRequest() {
    let baseurl = null;
    if (this.state.selectedTime === "1hr") {
      baseurl = process.env.REACT_APP_API_GET_CHART_DATA_1HR;
    } else if (this.state.selectedTime === "1dy") {
      baseurl = process.env.REACT_APP_API_GET_CHART_DATA_24HR;
    } else if (this.state.selectedTime === "1wk") {
      baseurl = process.env.REACT_APP_API_GET_CHART_DATA_1WK;
    } else if (this.state.selectedTime === "1mo") {
      baseurl = process.env.REACT_APP_API_GET_CHART_DATA_1MO;
    } else if (this.state.selectedTime === "3mo") {
      baseurl = process.env.REACT_APP_API_GET_CHART_DATA_3MO;
    }

    let apiURL = baseurl
      .concat(this.state.probeid)
      .concat("/")
      .concat(this.state.unitType);
      console.log(apiURL)
    this.apiCall(apiURL, this.formatChartData);
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
        callback(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
  render() {
    return (
      <div className="chartcontainer">
        <select
          className="chartselector"
          id="chartselector"
          name="chartselector"
          required
          onChange={this.handleChartSelectorChange}
          // value={this.state.selectedChart}
          selectedIndex={this.state.selectedChart}
        >
          {this.props.probearray.map((chart, index) => (
            <option key={index} value={chart.probename}>
              {chart.probename}
            </option>
          ))}
        </select>

        <select
          className="timeselector"
          id="timeselector"
          name="timeselector"
          required
          onChange={this.handleTimeSelectorChange}
          selectedIndex={this.state.selectedTime}
        >
          {/* <option key={0} value={"1hr"}>
            1 hour
          </option> */}
          <option key={1} value={"1dy"}>
            24 hour
          </option>
          <option key={2} value={"1wk"}>
            1 week
          </option>
          <option key={3} value={"1mo"}>
            1 month
          </option>
          {/* <option key={4} value={"3mo"}>
            3 month
          </option> */}
        </select>

        <button onClick={this.handleFetchButtonRequest}>Get Data</button>

        <HighchartsWrapper
          //  probename={this.props.data.probename}
          chartdata={this.state.ChartData}
          oneToOne={true}
        />
      </div>
    );
  }
}

export default Analytics;
