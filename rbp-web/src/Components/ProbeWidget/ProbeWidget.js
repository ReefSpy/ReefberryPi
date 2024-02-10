import React, { Component } from "react";
import HighchartsWrapper from "./ProbeChart";
import "./ProbeWidget.css";
import cogicon from "./cog.svg";
import ProbeWidgetModal from "./ProbeWidgetModal";

export class ProbeWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {
      ProbeName: "",
      apiResponse: null,
      ChartData: null,
      isProbePrefsModalOpen: false,
      setProbePrefsModalOpen: false,
      probeprefsFormData: null,
      setProbePrefsFormData: null,
      LastValue: "--",
    };
  }

  handleOpenProbePrefsModal = () => {
    this.setState({ setProbePrefsModalOpen: true });
    this.setState({ isProbePrefsModalOpen: true });
  };

  handleCloseProbePrefsModal = () => {
    this.setState({ setProbePrefsModalOpen: false });
    this.setState({ isProbePrefsModalOpen: false });
  };

  handleProbePrefsFormSubmit = (data) => {
    this.setState({ setProbePrefsFormData: data });
    this.handleCloseProbePrefsModal();
    console.log(data);

    let updateApiURL = process.env.REACT_APP_API_SET_PROBE_NAME.concat(
      data.probeid
    )
      .concat("/")
      .concat(data.probename);
    this.apiCall(updateApiURL, this.setNameCallback);
  };

  setNameCallback() {
    return;
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

  componentDidMount() {
    let unit_type = "unknown";
    if (this.props.data.sensortype === "humidity") {
      unit_type = "humidity";
    } else if (this.props.data.sensortype === "temperature") {
      unit_type = "temperature";
    } else if (this.props.data.sensortype === "ph") {
      unit_type = "ph";
    }

    //console.log(this.props.probename)
    let apiURL = process.env.REACT_APP_API_GET_CHART_DATA_24HR.concat(
      this.props.data.probeid
    )
      .concat("/")
      .concat(unit_type);
    this.apiCall(apiURL, this.GetChartData);

    // chart data
    this.interval = setInterval(() => {
      this.apiCall(apiURL, this.GetChartData);
    }, 600000);

    // update stats
    let ApiGetStats = process.env.REACT_APP_API_GET_CURRENT_PROBE_STATS.concat(
      this.props.data.probeid
    );
    this.apiCall(ApiGetStats, this.SetProbeData);

    this.interval2 = setInterval(() => {
      this.apiCall(ApiGetStats, this.SetProbeData);
    }, 2000);
  }

  componentWillUnmount() {
    clearInterval(this.interval);
    clearInterval(this.interval2);
  }

  GetChartData = (chartdata) => {
    this.setState({ ChartData: chartdata });
  };

  SetProbeData = (data) => {
    this.setState({ LastValue: data.lastValue });
    this.setState({ ProbeName: data.probename });
  };

  render() {
    return (
      <div className="probecontainer">
        <div className="item probename">{this.state.ProbeName}</div>
        <div className="item probevalue">{this.state.LastValue} </div>
        <div className="item chartdata">
          <div>
            <HighchartsWrapper
              probename={this.props.data.probename}
              chartdata={this.state.ChartData}
              oneToOne={true}
            />
          </div>
        </div>
        <div className="probeseticon">
          <button className="probesetbtn">
            <img
              src={cogicon}
              alt="settings"
              height="14"
              width="14"
              onClick={this.handleOpenProbePrefsModal}
            />
          </button>
        </div>

        <ProbeWidgetModal
          isOpen={this.state.isProbePrefsModalOpen}
          onSubmit={this.handleProbePrefsFormSubmit}
          onClose={this.handleCloseProbePrefsModal}
          ProbeName={this.state.ProbeName}
          ProbeID={this.props.data.probeid}
          SensorType={this.props.data.sensortype}
          Model={this.props.data.probetype}
        />
      </div>
    );
  }
}
