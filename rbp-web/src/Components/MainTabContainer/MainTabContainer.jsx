import React, { Component } from "react";
import Dashboard from "../Dashboard/Dashboard";
import Dashboard2 from "../Dashboard2/Dashboard2";
import Analytics from "../Analytics/Analytics";
import About from "../About/About";
import Settings from "../Settings/Settings";
import "./MainTabContainer.css";
import { Tab, Tabs, TabList, TabPanel } from "react-tabs";
import "react-tabs/style/react-tabs.css";
import dashicon from "../../Images/meter.svg";
import charticon from "../../Images/chart.svg";
import infoicon from "../../Images/info.svg";
import notepadicon from "../../Images/notepad.svg";
import testtubeicon from "../../Images/test-tube.svg";
import cogicon from "../../Images/cog.svg";
import alarmicon from "../../Images/bell-ringing.svg";

class MainTabContainer extends Component {
  constructor(props) {
    super(props);

    this.state = {
      selectedIndex: 0,
    };
  }

  handleRefreshRequest = () => {
    console.log("refresh request at setting container");
    this.setState({ RefreshDashboard: true });
  };

  onRefreshFinished = () => {
    console.log("refresh complete");
    this.setState({ RefreshDashboard: false });
  };
  render() {
    const tabs = [];
    const tabPanels = [];

    const tabTypes = [
      // { name: "Dashboard", desc: <Dashboard feedmode={this.props.feedmode} globalPrefs={this.props.globalPrefs}/>, img: dashicon},
      {
        name: "Dashboard",
        desc: (
          <Dashboard2
            feedmode={this.props.feedmode}
            globalPrefs={this.props.globalPrefs}
            dragDisabled={this.props.dragDisabled}
            ShouldRefreshDashboard={this.state.RefreshDashboard}
            RefreshCompleted={this.onRefreshFinished}
            shouldSaveWidgetOrder={this.props.shouldSaveWidgetOrder}
            onWidgetSaveComplete={this.props.onWidgetSaveComplete}
          />
        ),
        img: dashicon,
      },
      {
        name: "Analytics",
        desc: (
          <Analytics
            probearray={this.props.probearray}
            outletarray={this.props.outletarray}
          />
        ),
        img: charticon,
      },
      // { name: "Testing", desc: "Testing Parameters coming soon", img: testtubeicon},
      // { name: "Alarms", desc: "Alarms", img: alarmicon},
      // { name: "Journal", desc: "Journal coming soon", img: notepadicon},
      {
        name: "Settings",
        desc: (
          <Settings
            openGlobalPrefs={this.props.openGlobalPrefs}
            onRefreshRequest={this.handleRefreshRequest}
            globalPrefs={this.props.globalPrefs}
          />
        ),
        img: cogicon,
      },
      // { name: "About", desc: <About />, img: infoicon}
    ];

    return (
      <div display="block">
        <div>
          {tabTypes.forEach(({ name, desc, img }) => {
            tabs.push(
              <Tab className="rbp-tab" key={name}>
                <img src={img} alt={name} className="tabicon" />
                {name}
              </Tab>
            );
            tabPanels.push(
              <TabPanel className="rbp-tab-panel" key={name} forceRender={true}>
                {desc}
              </TabPanel>
            );
          })}

          <div>
            <Tabs
              selectedIndex={this.state.selectedIndex}
              onSelect={(selectedIndex) => this.setState({ selectedIndex })}
              selectedTabClassName="rbp-tab--selected"
              selectedTabPanelClassName="rbp-tab-panel--selected"
            >
              <TabList className="rbp-tab-list">{tabs}</TabList>
              {tabPanels}
            </Tabs>
          </div>
        </div>
      </div>
    );
  }
}

export default MainTabContainer;
