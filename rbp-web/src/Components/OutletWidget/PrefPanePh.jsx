import React, { Component } from "react";
import "./OutletWidget.css";

class PrefPanePh extends Component {
  constructor(props) {
    super(props);

    this.state = {
      Probes: this.props.probearray,
      selectedProbe: "",
      data: props.data,
      ph_low: props.data.ph_low,
      ph_high: props.data.ph_high,
      ph_probe: props.data.ph_probe,
      onWhen: props.data.ph_onwhen
    };
  }

  handleProbeChange = (event) => {
    this.setState({ selectedProbe: event.target.value });
    this.setState({ selectedProbeIndex: event.target.selectedIndex });
    this.setState({
      selectedProbeID:
        this.state.Probes[event.target.selectedIndex].probeid,
    });
  };

  handleWhenChange = (event) => {
    this.setState({ onWhen: event.target.value });
  };

  phLowChanged(event) {
    this.setState({ ph_low: event.target.value });
  }

  phHighChanged(event) {
    this.setState({ ph_high: event.target.value });
  }
  componentDidMount() {
    console.log(this.state.Probes);

    for (let probe in this.state.Probes) {
      console.log(this.state.Probes[probe].probeid);
      if (this.state.Probes[probe].probeid === this.state.ph_probe) {
        this.setState({ selectedProbeIndex: probe });
        this.setState({
          selectedProbe: this.state.Probes[probe].probename,
        });
        return;
      }
    }
  }

  render() {
    const { Probes, selectedProbe } = this.state;
    return (
      <div>
        <div className="form-row">
          <label htmlFor="phProbe">PH Probe</label>
          <select
            className="phProbe"
            id="phProbe"
            name="phProbe"
            required
            onChange={this.handleProbeChange}
            value={this.state.selectedProbe}
          >
            {Probes.map((Probe, index) => (
              <option key={index} value={Probe.probename}>
                {Probe.probename}
              </option>
            ))}
          </select>
        </div>

        <div className="form-row">
          <label htmlFor="phProbe">High PH</label>
        </div>

        <input
          type="number"
          id="ph_high"
          name="ph_high"
          min="0"
          max="14.0"
          step=".1"
          value={this.state.ph_high}
          onChange={(event) => this.phHighChanged(event)}
        ></input>
        <div className="form-row">
          <label htmlFor="phProbe">Low PH</label>
        </div>

        <input
          type="number"
          id="ph_low"
          name="ph_low"
          min="0"
          max="14.0"
          step=".1"
          value={this.state.ph_low}
          onChange={(event) => this.phLowChanged(event)}
        ></input>
         <div className="form-row">
          <label htmlFor="phProbe">On When</label>
          <select
            className="onWhen"
            id="onWhen"
            name="onWhen"
            required
            onChange={this.handleWhenChange}
            value={this.state.onWhen}>

              <option key="0" value="HIGH">
                HIGH
              </option>
              <option key="1" value="LOW">
                LOW
              </option>

          </select>
        </div>
      </div>
    );
  }
}

export default PrefPanePh;
