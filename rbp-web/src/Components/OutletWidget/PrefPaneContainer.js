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

    this.outletTypes = [
      { name: "Always", desc: <PrefPaneAlways /> },
      { name: "Light", desc: <PrefPaneLight /> },
      { name: "Heater", desc: <PrefPaneHeater /> },
      { name: "Skimmer", desc: <PrefPaneSkimmer /> },
      { name: "Return", desc: <PrefPaneReturn /> },
      { name: "PH", desc: <PrefPanePh /> },
    ];

    this.state = {
      selectedIndex: 0,
    };
  }

  render() {
    const tabs = [];
    const tabPanels = [];

    return (
      <div>
        <div>
          {this.outletTypes.forEach(({ name, desc }) => {
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
              selectedIndex={this.props.data.selectedIndex}
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
