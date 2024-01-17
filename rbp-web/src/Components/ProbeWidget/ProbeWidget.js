import React, { Component } from "react";
import HighchartsWrapper from "./ProbeChart";
import "./ProbeWidget.css";
import cogicon from "./cog.svg";
import ProbeWidgetModal from "./ProbeWidgetModal";


export class ProbeWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {
      LastTemp: "--",
      ProbeName: "Unknown",
      apiResponse: null,
      ChartData: null,
      isProbePrefsModalOpen: false,
      setProbePrefsModalOpen: false,
      probeprefsFormData: null,
      setProbePrefsFormData: null,
    };
  }

  ///////
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
    console.log(data)

    let updateApiURL = "http://xpi01.local:5000/set_probe_name/"
      .concat(data.probeid)
      .concat("/")
      .concat(data.probename);
    this.apiCall(updateApiURL, );
  };
  //////

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
    let unit_type = "unknown";
    if (this.props.data.sensortype === "humidity") {
      unit_type = "humidity";
    } else if (this.props.data.sensortype === "temperature") {
      unit_type = "temperature_c";
    }

    //console.log(this.props.probename)
    let apiURL = "http://xpi01.local:5000/get_chartdata_24hr/QV3BIZZV/"
      .concat(this.props.data.probeid)
      .concat("/")
      .concat(unit_type);
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
        <div class="item probevalue">{this.props.data.lastValue} </div>
        <div class="item chartdata">
          <div>
            <HighchartsWrapper
              probename={this.props.data.probename}
              chartdata={this.state.ChartData}
              oneToOne={true}
            />
          </div>
        </div>
        <div class="probeseticon">
          <button class="probesetbtn">
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
        ProbeName={this.props.data.probename}
        ProbeID={this.props.data.probeid}
        SensorType={this.props.data.sensortype}
        Model={this.props.data.probetype}
        />
      </div>
    );
  }
}
