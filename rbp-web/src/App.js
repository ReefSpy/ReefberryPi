import React, { Component } from "react";
import { ProbeWidget } from "./Components/ProbeWidget/ProbeWidget";
import { OutletWidget } from "./Components/OutletWidget/OutletWidget";
import { FeedWidget } from "./Components/FeedWidget/FeedWidget";
import MainTabContainer from "./Components/MainTabContainer/MainTabContainer";

// there is a bug in react-beautiful-dnd where it wont work with strict mode
// in React 18.  Solution is repplace with fork @hello-pangea-dnd to fix it
// import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

// import { createRoot } from "react-dom/client";
import appicon from "./Images/reefberry-pi-logo.svg";
import preficon from "./Images/cog-white.svg";
import logouticon from "./Images/logout-white.svg"
import GlobalPrefsModal from "./Components/GlobalPrefs/GlobalPrefsModal";
import "./App.css";
//import useToken from "./useToken";
import Login from "./Components/Login/Login";

// a little function to help us with reordering the result
const reorder = (list, startIndex, endIndex) => {
  const result = Array.from(list);
  const [removed] = result.splice(startIndex, 1);
  result.splice(endIndex, 0, removed);

  return result;
};

/**
 * Moves an item from one list to another list.
 */
const move = (source, destination, droppableSource, droppableDestination) => {
  const sourceClone = Array.from(source);
  const destClone = Array.from(destination);
  const [removed] = sourceClone.splice(droppableSource.index, 1);

  destClone.splice(droppableDestination.index, 0, removed);

  const result = {};
  result[droppableSource.droppableId] = sourceClone;
  result[droppableDestination.droppableId] = destClone;

  return result;
};

const getItemStyle = (isDragging, draggableStyle) => ({
  // some basic styles to make the items look a bit nicer
  userSelect: "none",
  padding: "2px",
  borderRadius: 4,

  // change background colour if dragging
  background: isDragging ? "orange" : "steelblue",

  // styles we need to apply on draggables
  ...draggableStyle,
});

const getListStyle = (isDraggingOver) => ({
  background: isDraggingOver ? "lightblue" : "steelblue",
  padding: "1px",
  width: 320,
});

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      col2items: [],
      col1items: [],
      ProbeArray: [],
      DragDisabled: false,
      globalPrefs: null,
      col1rawitems: [],
    };
    this.setProbeData = this.setProbeData.bind(this);
    this.setOutletData = this.setOutletData.bind(this);
    this.setGlobalPrefs = this.setGlobalPrefs.bind(this);
    this.initCol1Items = this.initCol1Items.bind(this);
    this.addToCol1 = this.addToCol1.bind(this);
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

  /**
   * A semi-generic way to handle multiple lists. Matches
   * the IDs of the droppable container to the names of the
   * source arrays stored in the state.
   */
  id2List = {
    droppable: "col1items",
    droppable2: "col2items",
  };

  getList = (id) => this.state[this.id2List[id]];

  onDragEnd = (result) => {
    const { source, destination } = result;

    // dropped outside the list
    if (!destination) {
      return;
    }

    if (source.droppableId === destination.droppableId) {
      const col1items = reorder(
        this.getList(source.droppableId),
        source.index,
        destination.index
      );

      let state = { col1items };

      if (source.droppableId === "droppable2") {
        state = { col2items: col1items };
      }

      this.setState(state);
    } else {
      const result = move(
        this.getList(source.droppableId),
        this.getList(destination.droppableId),
        source,
        destination
      );

      this.setState({
        col1items: result.droppable,
        col2items: result.droppable2,
      });
    }
  };

  addToCol1(items) {
    let rawitems = [];
    let i = 0;
    for (let item in items) {
      items[item]["id"] = `item-${String(i++)}`;
      items[item]["widgetType"] = `probe`;
      rawitems.push(items[item]);
    }
    // lets add the feedwidget to this set
    let feeditem = { widgetType: "feed", id: `item-${String(i++)}` };
    rawitems.push(feeditem);
    this.setState({ col1items: rawitems });
  }

  initCol1Items() {
    // first get probes
    console.log(process.env.REACT_APP_API_GET_PROBE_LIST);
    this.apiCall(process.env.REACT_APP_API_GET_PROBE_LIST, this.addToCol1);

    return;
  }

  setProbeData(probedata) {
    let col1items = [];
    let i = 0;
    for (let probe in probedata) {
      probedata[probe]["id"] = `item-${String(i++)}`;
      probedata[probe]["widgetType"] = `probe`;
      col1items.push(probedata[probe]);
    }

    if (col1items.length > 0) {
      this.setState({ col1items });
    }
    this.setState({ ProbeArray: col1items });

    return col1items;
  }

  setOutletData(outletdata) {
    let col2items = [];
    let i = 0;
    for (let outlet in outletdata) {
      outletdata[outlet]["id"] = `item-${String(200 + i++)}`;
      outletdata[outlet]["widgetType"] = `outlet`;
      col2items.push(outletdata[outlet]);
    }

    if (col2items.length > 0) {
      this.setState({ col2items });
      this.setState({ OutletArray: col2items });
    }
    return col2items;
  }

  async componentDidMount() {
    this.apiCall(process.env.REACT_APP_API_GET_PROBE_LIST, this.setProbeData);

    this.apiCall(process.env.REACT_APP_API_GET_OUTLET_LIST, this.setOutletData);

    // global prefs
    this.apiCall(
      process.env.REACT_APP_API_GET_GLOBAL_PREFS,
      this.setGlobalPrefs
    );
    this.interval = setInterval(() => {
      this.apiCall(
        process.env.REACT_APP_API_GET_GLOBAL_PREFS,
        this.setGlobalPrefs
      );
    }, 3500);

    this.initCol1Items();
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  //   ///////
  handleOpenGlobalPrefsModal = () => {
    this.setState({ setGlobalPrefsModalOpen: true });
    this.setState({ isGlobalPrefsModalOpen: true });
  };

  handleCloseGlobalPrefsModal = () => {
    this.setState({ setGlobalPrefsModalOpen: false });
    this.setState({ isGlobalPrefsModalOpen: false });
  };

  handleGlobalPrefsFormSubmit = (data) => {
    let apiURL = process.env.REACT_APP_API_SET_GLOBAL_PREFS;
    console.log(data);
    let payload = {
      tempscale: data.tempScale,
      dht_enable: data.enableDHT,
      feed_a_time: data.feedA,
      feed_b_time: data.feedB,
      feed_c_time: data.feedC,
      feed_d_time: data.feedD,
    };
    this.apiCallPut(apiURL, payload);
    this.handleCloseGlobalPrefsModal();
  };

  setGlobalPrefs(data) {
    this.setState({ globalPrefs: data });
    this.setState({ globalTempScale: data.tempscale });
    this.setState({ globalEnableDHT: data.dht_enable });

    return;
  }

  // API call structure
  apiCallPut = (endpoint, newdata) => {
    fetch(endpoint, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newdata),
    })
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.log(error));
  };

  //   //////

  getWidget = (item) => {
    if (item.widgetType === "probe") {
      return (
        <ProbeWidget
          data={item}
          ProbeID={item.probeid}
          key={item.probeid}
        ></ProbeWidget>
      );
    } else if (item.widgetType === "outlet") {
      return (
        <OutletWidget
          data={item}
          OutletID={item.outletid}
          key={item.outletid}
          probearray={this.state.ProbeArray}
        ></OutletWidget>
      );
    } else if (item.widgetType === "feed") {
      return (
        <FeedWidget
          feedmode={this.state.globalPrefs.feed_CurrentMode}
        ></FeedWidget>
      );
    } else {
      return null;
    }
  };

  getToken = () => {
    const tokenString = sessionStorage.getItem("token");
    if (tokenString !== undefined) {
      const userToken = JSON.parse(tokenString);
      return userToken?.token;
    }
  };

  setToken(userToken) {
    console.log("settoken")
    if (userToken !== undefined){
    sessionStorage.setItem('token', JSON.stringify(userToken));}
    
  }

  logout(){
    sessionStorage.clear()
  }
  // Normally you would want to split things out into separate components.
  // But in this example everything is just done in one place for simplicity
  render() {
    if (!this.getToken()) {
      return <Login setToken={this.setToken}/>;
    }
    return (
      <div className="App">
        <div className="appheader">
          <img className="appicon" src={appicon} alt="logo" />

          <span>Reefberry Pi</span>

          <div className="header-right">
            <button className="headericonbtn">
              <img
                className="headericon"
                src={preficon}
                alt="preferences"
                onClick={this.handleOpenGlobalPrefsModal}
              ></img>
            </button>
            <button className = "headericonbtn"><img
                className="headericon"
                src={logouticon}
                alt="logout"
                onClick={this.logout}
              ></img></button>
          </div>
        </div>

        <div>
<MainTabContainer  feedmode={this.state.globalPrefs?.feed_CurrentMode} probearray={this.state.ProbeArray} outletarray={this.state.OutletArray}></MainTabContainer>
        </div>

        {/* <div className="maingridcontainer">
          <DragDropContext onDragEnd={this.onDragEnd}>
            <Droppable droppableId="droppable">
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  style={getListStyle(snapshot.isDraggingOver)}
                >
                  {this.state.col1items.map((item, index) => (
                    <Draggable
                      key={item.id}
                      draggableId={item.id}
                      index={index}
                      isDragDisabled={this.state.DragDisabled}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          style={getItemStyle(
                            snapshot.isDragging,
                            provided.draggableProps.style
                          )}
                        >
                          {this.getWidget(item)}
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
            <Droppable droppableId="droppable2">
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  style={getListStyle(snapshot.isDraggingOver)}
                >
                  {this.state.col2items.map((item, index) => (
                    <Draggable
                      key={item.id}
                      draggableId={item.id}
                      index={index}
                      isDragDisabled={this.state.DragDisabled}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          style={getItemStyle(
                            snapshot.isDragging,
                            provided.draggableProps.style
                          )}
                        >
                          {this.getWidget(item)}
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div> */}
        {this.state.globalPrefs && this.state.isGlobalPrefsModalOpen ? (
          <GlobalPrefsModal
            isOpen={this.state.isGlobalPrefsModalOpen}
            onSubmit={this.handleGlobalPrefsFormSubmit}
            onClose={this.handleCloseGlobalPrefsModal}
            globalTempScale={this.state.globalTempScale}
            globalPrefs={this.state.globalPrefs}
          />
        ) : null}
      </div>
    );
  }
}

export default App;
