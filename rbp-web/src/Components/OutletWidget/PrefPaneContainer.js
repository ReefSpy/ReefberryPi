import React, { Component } from "react";
import "./OutletWidget.css";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import "react-tabs/style/react-tabs.css";
import PrefPaneAlways from "./PrefPaneAlways";
import PrefPaneLight from "./PrefPaneLight";
import PrefPaneHeater from "./PrefPaneHeater";
import PrefPaneSkimmer from "./PrefPaneSkimmer";
import PrefPaneReturn from "./PrefPaneReturn";
import PrefPanePh from "./PrefPanePh";

class PrefPaneContainer extends Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedIndex: 0,
    };
  }

  render() {
    const tabs = [];
    const tabPanels = [];

    const outletTypes = [
      { name: "Always", desc: <PrefPaneAlways data={this.props.data} isOpen={this.props.isOpen} onClose={this.props.onClose}/> },
      { name: "Light", desc: <PrefPaneLight data={this.props.data}/> },
      { name: "Heater", desc: <PrefPaneHeater data={this.props.data} probearray={this.props.probearray}/>} ,
      { name: "Skimmer", desc: <PrefPaneSkimmer data={this.props.data}/> },
      { name: "Return", desc: <PrefPaneReturn data={this.props.data}/> },
      { name: "PH", desc: <PrefPanePh data={this.props.data}/> },
    ];


    return (
      <div>
        <div>
          {outletTypes.forEach(({ name, desc }) => {
            tabs.push(
              <Tab className="outlet-tab" key={name}>
                {name}
              </Tab>
            );
            tabPanels.push(
              <TabPanel className="outlet-tab-panel" key={name}>
                {desc}
              </TabPanel>
            );
          })}

          <div>
            <Tabs
              selectedIndex={this.props.selectedTab}
              onSelect={(selectedIndex) => this.setState({ selectedIndex })}
              selectedTabClassName="outlet-tab--selected"
              selectedTabPanelClassName="outlet-tab-panel--selected"
            >
              {/* <TabList className="outlet-tab-list">{tabs}</TabList> */}
              {tabPanels}
            </Tabs>
          </div>
        </div>
      </div>
    );
  }
}

export default PrefPaneContainer;
