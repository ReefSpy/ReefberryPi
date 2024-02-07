import React, { Component } from "react";
import "./Analytics.css";
import HighchartsWrapper from "./AnalyticsChart";

class Analytics extends Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedChart1: 0,
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
  formatChartData1 = (chartdata) => {
    for (let datapoint in chartdata) {
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
    this.setState({ probearray2: probeArray2 });

   
// build the second lists
    let dropdownlist1 = [];
    let dropdownlist2 = [];
    dropdownlist2.push({ id: undefined, name: undefined });
    for (let probe in this.props.probearray) {
      dropdownlist1.push({
        id: this.props.probearray[probe].probeid,
        name: this.props.probearray[probe].probename,
        displayname: "Probe: " + this.props.probearray[probe].probename,
        unit: this.props.probearray[probe].sensortype,
        widgettype: this.props.probearray[probe].widgetType,
      });
      dropdownlist2.push({
        id: this.props.probearray[probe].probeid,
        name: this.props.probearray[probe].probename,
        displayname: "Probe: " + this.props.probearray[probe].probename,
        unit: this.props.probearray[probe].sensortype,
        widgettype: this.props.probearray[probe].widgetType,
      });
    }

    for (let outlet in this.props.outletarray) {
      dropdownlist1.push({
        id: this.props.outletarray[outlet].outletid,
        name: this.props.outletarray[outlet].outletname,
        displayname: "Outlet: " + this.props.outletarray[outlet].outletname,
        unit: "on-off",
        widgettype: this.props.outletarray[outlet].widgetType,
      });
      dropdownlist2.push({
        id: this.props.outletarray[outlet].outletid,
        name: this.props.outletarray[outlet].outletname,
        displayname: "Outlet: " + this.props.outletarray[outlet].outletname,
        unit: "on-off",
        widgettype: this.props.outletarray[outlet].widgetType,
      });
    }
    this.setState({ dropdownlist1: dropdownlist1 });
    this.setState({ dropdownlist2: dropdownlist2 });
  }

  handleChartSelectorChange(event) {
    console.log(event.target.value);
    console.log(event.target.selectedIndex);
    console.log(this.state.dropdownlist1[event.target.selectedIndex].id);

    this.setState({
      selectedprobeid1: this.state.dropdownlist1[event.target.selectedIndex].id,
      selectedprobename1:
        this.state.dropdownlist1[event.target.selectedIndex].name,
      selectedunitType1:
        this.state.dropdownlist1[event.target.selectedIndex].unit,
      selectedChart1: event.target.selectedIndex,
      selectedwidgettype1:
        this.state.dropdownlist1[event.target.selectedIndex].widgettype,
    });
  }

  handleChartSelectorChange2(event) {
    console.log(event.target.value);
    console.log(event.target.selectedIndex);
    console.log(this.state.dropdownlist2[event.target.selectedIndex].id);

    this.setState({
      selectedprobeid2: this.state.dropdownlist2[event.target.selectedIndex].id,
      selectedprobename2:
        this.state.dropdownlist2[event.target.selectedIndex].name,
      selectedunitType2:
        this.state.dropdownlist2[event.target.selectedIndex].unit,
      selectedChart2: event.target.selectedIndex,
      selectedwidgettype2:
        this.state.dropdownlist2[event.target.selectedIndex].widgettype,
    });
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
      probeid1: this.state.selectedprobeid1,
      probeid2: this.state.selectedprobeid2,
      probename1: this.state.selectedprobename1,
      probename2: this.state.selectedprobename2,
      unitType1: this.state.selectedunitType1,
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
      let charttitle = this.state.selectedprobename1 + " - " + this.state.selectedTime;
      this.setState({ chartTitle: charttitle });
    } else {
      let charttitle =
        this.state.selectedprobename1 +
        " vs. " +
        this.state.selectedprobename2 +
        " - " +
        this.state.selectedTime;
      this.setState({ chartTitle: charttitle });
    }

    // let apiURL = baseurl
    //   .concat(this.state.probeid)
    //   .concat("/")
    //   .concat(this.state.unitType);
    // console.log(apiURL);
    // this.apiCall(apiURL, this.formatChartData);

    let outlettime = "";
    if (this.state.selectedTime === "1dy") {
      outlettime = "24h";
    } else if (this.state.selectedTime === "1wk") {
      outlettime = "7d";
    } else if (this.state.selectedTime === "1mo") {
      outlettime = "30d";
    }

    if (this.state.selectedwidgettype1 === "probe") {
      let apiURL1 = baseurl
        .concat(this.state.selectedprobeid1)
        .concat("/")
        .concat(this.state.selectedunitType1);
      console.log(apiURL1);
      this.apiCall(apiURL1, this.formatChartData1);
    } else if (this.state.selectedwidgettype1 === "outlet") {
      let outletbaseurl = process.env.REACT_APP_API_GET_OUTLET_CHART_DATA;
      let apiURL1 = outletbaseurl
        .concat(this.state.selectedprobeid1)
        .concat("/")
        .concat(outlettime);
      console.log(apiURL1);
      this.apiCall(apiURL1, this.formatChartData1);
    }

    if (this.state.selectedwidgettype2 === "probe") {
      let apiURL2 = baseurl
        .concat(this.state.selectedprobeid2)
        .concat("/")
        .concat(this.state.selectedunitType2);
      console.log(apiURL2);
      this.apiCall(apiURL2, this.formatChartData2);
    } else if (this.state.selectedwidgettype2 === "outlet") {
      let outletbaseurl = process.env.REACT_APP_API_GET_OUTLET_CHART_DATA;
      let apiURL2 = outletbaseurl
        .concat(this.state.selectedprobeid2)
        .concat("/")
        .concat(outlettime);
      console.log(apiURL2);
      this.apiCall(apiURL2, this.formatChartData2);
    }
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
            selectedIndex={this.state.selectedChart}
          >
            {/* {this.props.probearray.map((chart, index) => (
              <option key={index} value={chart.probename}>
                {chart.probename}
              </option>
            ))} */}
             {this.state.dropdownlist1?.map((chart, index) => (
              <option key={index} value={chart?.id}>
                {chart?.displayname}
              </option>
            ))}
          </select>
          <select
            className="chartselector"
            id="chartselector2"
            name="chartselector2"
            required
            onChange={this.handleChartSelectorChange2}
            selectedIndex={this.state.selectedChart2}
          >
            {this.state.dropdownlist2?.map((chart, index) => (
              <option key={index} value={chart?.id}>
                {chart?.displayname}
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
          probename={this.state.probename1}
          probename2={this.state.probename2}
          chartdata={this.state.ChartData}
          chartdata2={this.state.ChartData2}
          unitType={this.state.unitType1}
          unitType2={this.state.unitType2}
          oneToOne={true}
          chartTitle={this.state.chartTitle}
        />
      </div>
    );
  }
}

export default Analytics;
