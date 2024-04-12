import React, { Component } from "react";
import "./Analytics.css";
import HighchartsWrapper from "./AnalyticsChart";
import probeIcon from "./probe.svg";
import outletIcon from "./outlet.svg";
import * as Api from "../Api/Api.js"

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

    this.authtoken = JSON.parse(sessionStorage.getItem("token")).token;
    this.payload = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + this.authtoken,
      },
    };
  }

  // need to convert timestamp to milliseconds to show up properly in HighCharts
  formatChartData1 = (chartdata) => {
    let valueArray1 = [];
    let ValueTotal1 = 0;
    for (let datapoint in chartdata) {
      let newDate = new Date(chartdata[datapoint][0]).getTime();
      chartdata[datapoint][0] = newDate;
      valueArray1.push(chartdata[datapoint][1]);
      ValueTotal1 = ValueTotal1 + chartdata[datapoint][1];
    }
    // if outlet is on, extend the line to end of graph by adding an extra "ON" point
    if (this.state.selectedwidgettype1 === "outlet") {
      console.log(chartdata.slice(-1)[0][1]);
      if (chartdata.slice(-1)[0][1] === 1) {
        chartdata.push([new Date().getTime(), 1]);
      }
    }
    this.setState({ ChartData: chartdata });
    if (this.state.selectedwidgettype1 === "probe") {
      this.setState({
        ProbeIcn1: "probe",
        ProbeMax1: Math.max(...valueArray1).toFixed(2),
        ProbeMin1: Math.min(...valueArray1).toFixed(2),
        ProbeAvg1: (ValueTotal1 / valueArray1.length).toFixed(2),
        
      });
    } else {
      this.setState({
        ProbeIcn1: "outlet",
        ProbeMax1: "--",
        ProbeMin1: "--",
        ProbeAvg1: "--",
        
      });
    }
  };

  // for a second series of data
  // need to convert timestamp to milliseconds to show up properly in HighCharts
  formatChartData2 = (chartdata) => {
    let valueArray2 = [];
    let ValueTotal2 = 0;
    for (let datapoint in chartdata) {
      let newDate = new Date(chartdata[datapoint][0]).getTime();
      chartdata[datapoint][0] = newDate;
      valueArray2.push(chartdata[datapoint][1]);
      ValueTotal2 = ValueTotal2 + chartdata[datapoint][1];
    }
    // if outlet is on, extend the lione to end of graph by adding an extra "ON" point
    if (this.state.selectedwidgettype2 === "outlet") {
      console.log(chartdata.slice(-1)[0][1]);
      if (chartdata.slice(-1)[0][1] === 1) {
        chartdata.push([new Date().getTime(), 1]);
      }
    }
    this.setState({ ChartData2: chartdata });
    if (this.state.selectedwidgettype2 === "probe") {
      this.setState({
        ProbeIcn2: "probe",
        ProbeMax2: Math.max(...valueArray2).toFixed(2),
        ProbeMin2: Math.min(...valueArray2).toFixed(2),
        ProbeAvg2: (ValueTotal2 / valueArray2.length).toFixed(2),
        
      });
    } else {
      this.setState({
        ProbeIcn2: "outlet",
        ProbeMax2: "--",
        ProbeMin2: "--",
        ProbeAvg2: "--",
        
      });
    }
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
      ProbeMax1: "--",
      ProbeMin1: "--",
      ProbeAvg1: "--",
      ProbeMax2: "--",
      ProbeMin2: "--",
      ProbeAvg2: "--",
      ProbeIcn1: null,
      ProbeIcn2: null,
    });

    let baseurl = null;
    if (this.state.selectedTime === "1hr") {
      baseurl = Api.API_GET_CHART_DATA_1HR;
    } else if (this.state.selectedTime === "1dy") {
      baseurl = Api.API_GET_CHART_DATA_24HR;
    } else if (this.state.selectedTime === "1wk") {
      baseurl = Api.API_GET_CHART_DATA_1WK;
    } else if (this.state.selectedTime === "1mo") {
      baseurl = Api.API_GET_CHART_DATA_1MO;
    } else if (this.state.selectedTime === "3mo") {
      baseurl = Api.API_GET_CHART_DATA_3MO;
    }

    if (this.state.selectedprobeid2 === undefined) {
      let charttitle =
        this.state.selectedprobename1 + " - " + this.state.selectedTime;
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
      this.apiCall(apiURL1, this.payload, this.formatChartData1);
    } else if (this.state.selectedwidgettype1 === "outlet") {
      let outletbaseurl = Api.API_GET_OUTLET_CHART_DATA;
      let apiURL1 = outletbaseurl
        .concat(this.state.selectedprobeid1)
        .concat("/")
        .concat(outlettime);
      console.log(apiURL1);
      this.apiCall(apiURL1, this.payload, this.formatChartData1);
    }

    if (this.state.selectedwidgettype2 === "probe") {
      let apiURL2 = baseurl
        .concat(this.state.selectedprobeid2)
        .concat("/")
        .concat(this.state.selectedunitType2);
      console.log(apiURL2);
      this.apiCall(apiURL2,this.payload, this.formatChartData2);
    } else if (this.state.selectedwidgettype2 === "outlet") {
      let outletbaseurl = Api.API_GET_OUTLET_CHART_DATA;
      let apiURL2 = outletbaseurl
        .concat(this.state.selectedprobeid2)
        .concat("/")
        .concat(outlettime);
      console.log(apiURL2);
      this.apiCall(apiURL2, this.payload, this.formatChartData2);
    }
  }

  // generic API call structure
  apiCall(endpoint, payload, callback) {
    fetch(endpoint, payload)
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
        <br></br>
        <div className="result-container">
          <label className="result-title">Type</label>
          <label className="result-title">Name</label>
          <label className="result-title">High</label>
          <label className="result-title">Low</label>
          <label className="result-title">Mean</label>

          {this.state.ProbeIcn1 === "probe" ? <div className="result-row1">
            <img src={probeIcon} alt="Probe" className="result-icon"></img>
          </div> : <div></div>}
          {this.state.ProbeIcn1 === "outlet" ? <div className="result-row1">
            <img src={outletIcon} alt="Outlet" className="result-icon"></img>
          </div> : <div></div>}
          {this.state.ProbeIcn1 === null ? <div className="result-row1">
            --</div> : <div></div>}
          {/* <div className="result-row1">
            <img src={probeIcon} alt="Probe" className="result-icon"></img>
          </div> */}
          <label className="result-row1">{this.state.probename1}</label>
          <label className="result-row1">{this.state.ProbeMax1}</label>
          <label className="result-row1">{this.state.ProbeMin1}</label>
          <label className="result-row1">{this.state.ProbeAvg1}</label>
          
          {this.state.ProbeIcn2 === "probe" ? <div className="result-row2">
            <img src={probeIcon} alt="Probe" className="result-icon"></img>
          </div> : <div></div>}
          {this.state.ProbeIcn2 === "outlet" ? <div className="result-row2">
            <img src={outletIcon} alt="Outlet" className="result-icon"></img>
          </div> : <div></div>}
          {this.state.ProbeIcn2 === null ? <div className="result-row2">
            --</div> : <div></div>}
          {/* <div className="result-row2">
            <img src={probeIcon} alt="P>robe" className="result-icon"></img>
          </div> */}
          <label className="result-row2">{this.state.probename2}</label>
          <label className="result-row2">{this.state.ProbeMax2}</label>
          <label className="result-row2">{this.state.ProbeMin2}</label>
          <label className="result-row2">{this.state.ProbeAvg2}</label>
        </div>
      </div>
    );
  }
}

export default Analytics;
