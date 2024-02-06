import React, { Component } from "react";
import "./Analytics.css";
import HighchartsWrapper from "./AnalyticsChart";

class Analytics extends Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedChart: 1,
      tempCharts: [{ chartname: "probe1" }, { chartname: "probe2" }],
      selectedTime: "1dy",
      chartTitle: null,
    };

    this.handleChartSelectorChange = this.handleChartSelectorChange.bind(this);
    this.handleChartSelectorChange2 =
      this.handleChartSelectorChange2.bind(this);
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

  // for a second series of data
  // need to convert timestamp to milliseconds to show up properly in HighCharts
  formatChartData2 = (chartdata) => {
    for (let datapoint in chartdata) {
      let newDate = new Date(chartdata[datapoint][0]).getTime();
      chartdata[datapoint][0] = newDate;
    }
    this.setState({ ChartData2: chartdata });
  };

  componentDidMount() {}

  componentWillReceiveProps() {
    // put a value at start of array for second dataset for no value if only want a single series graph
    let probeArray2 = [...this.props.probearray];
    probeArray2.unshift({ probeid: undefined });
    // probeArray2.push({ probeid: "int_outlet_1", probename: "outlet 1" });
    //probeArray2.push(this.props.outletarray)
    this.setState({ probearray2: probeArray2 });
    

  }

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
      probename: this.props.probearray[event.target.selectedIndex].probename,
    });
    this.setState({ selectedChart: event.target.selectedIndex });
  }

  handleChartSelectorChange2(event) {
    console.log(event.target.value);
    console.log(event.target.selectedIndex);
    console.log(this.state.probearray2[event.target.selectedIndex].probeid);

    let unit_type = "unknown";
    if (
      this.state.probearray2[event.target.selectedIndex].sensortype ===
      "humidity"
    ) {
      unit_type = "humidity";
    } else if (
      this.state.probearray2[event.target.selectedIndex].sensortype ===
      "temperature"
    ) {
      unit_type = "temperature";
    }
    // this.setState({ unitType2: unit_type });
    this.setState({
      selectedprobeid2:
        this.state.probearray2[event.target.selectedIndex].probeid,
      selectedprobename2:
        this.state.probearray2[event.target.selectedIndex].probename,
      selectedunitType2: unit_type,
      selectedChart2: event.target.selectedIndex,
    });
    // this.setState({ selectedChart2: event.target.selectedIndex });
  }

  handleOptionChange = (changeEvent) => {
    this.setState({
      selectedTime: changeEvent.target.value,
    });
  };

  handleFetchButtonRequest() {
    this.setState({ ChartData: [] });
    this.setState({ ChartData2: [] });

    this.setState({
      probeid2: this.state.selectedprobeid2,
      probename2: this.state.selectedprobename2,
      unitType2: this.state.selectedunitType2,
    });

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

    if (this.state.selectedprobeid2 === undefined) {
      let charttitle = this.state.probename + " - " + this.state.selectedTime;
      this.setState({ chartTitle: charttitle });
    } else {
      let charttitle =
        this.state.probename +
        " vs. " +
        this.state.selectedprobename2 +
        " - " +
        this.state.selectedTime;
      this.setState({ chartTitle: charttitle });
    }

    let apiURL = baseurl
      .concat(this.state.probeid)
      .concat("/")
      .concat(this.state.unitType);
    console.log(apiURL);
    this.apiCall(apiURL, this.formatChartData);

    let apiURL2 = baseurl
      .concat(this.state.selectedprobeid2)
      .concat("/")
      .concat(this.state.selectedunitType2);
    console.log(apiURL2);
    this.apiCall(apiURL2, this.formatChartData2);

    // let outletbaseurl = process.env.REACT_APP_API_GET_OUTLET_CHART_DATA
    // let apiURL2 = outletbaseurl
    //   .concat("int_outlet_1")
    //   .concat("/")
    //   .concat("24h");
    // console.log(apiURL2);
    // this.apiCall(apiURL2, this.formatChartData2);
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
        <div className="select-container">
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
            className="chartselector"
            id="chartselector2"
            name="chartselector2"
            required
            onChange={this.handleChartSelectorChange2}
            // value={this.state.selectedChart}
            selectedIndex={this.state.selectedChart2}
          >
            {this.state.probearray2?.map((chart, index) => (
              <option key={index} value={chart?.probename}>
                {chart?.probename}
              </option>
            ))}
          </select>

          <div>
            <label className="form-check-label">
              <input
                type="radio"
                name="react-tips"
                value="1dy"
                checked={this.state.selectedTime === "1dy"}
                onChange={this.handleOptionChange}
                className="form-check-input"
              />
              24 hour
            </label>
          </div>
          <div>
            <label className="form-check-label">
              <input
                type="radio"
                name="react-tips"
                value="1wk"
                checked={this.state.selectedTime === "1wk"}
                onChange={this.handleOptionChange}
                className="form-check-input"
              />
              1 week
            </label>
          </div>

          <div>
            <label className="form-check-label">
              <input
                type="radio"
                name="react-tips"
                value="1mo"
                checked={this.state.selectedTime === "1mo"}
                onChange={this.handleOptionChange}
                className="form-check-input"
              />
              1 month
            </label>
          </div>

          <button onClick={this.handleFetchButtonRequest} className="getbtn">
            Get Data
          </button>
        </div>
        <HighchartsWrapper
          probename={this.state.probename}
          probename2={this.state.probename2}
          chartdata={this.state.ChartData}
          chartdata2={this.state.ChartData2}
          unitType={this.state.unitType}
          unitType2={this.state.unitType2}
          oneToOne={true}
          chartTitle={this.state.chartTitle}
        />
      </div>
    );
  }
}

export default Analytics;
