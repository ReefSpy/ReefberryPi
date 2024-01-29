import React, { Component } from "react";
import { ProbeWidget } from "./Components/ProbeWidget/ProbeWidget";
import { OutletWidget } from "./Components/OutletWidget/OutletWidget";
import { FeedWidget } from "./Components/FeedWidget/FeedWidget";

// there is a bug in react-beautiful-dnd where it wont work with strict mode
// in React 18.  Solution is repplace with fork @hello-pangea-dnd to fix it
// import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";

// import { createRoot } from "react-dom/client";
import appicon from "./Images/reefberry-pi-logo.svg";
import preficon from "./Images/cog-white.svg";
import GlobalPrefsModal from "./Components/GlobalPrefs/GlobalPrefsModal";
import "./App.css";

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
      //  items: getItems(10),
      //   col2items: getItems(5, 10),
      col2items: [],
      col1items: [],
      ProbeArray: [],
      DragDisabled: false,
      globalPrefs: null,
    };
    this.setProbeData = this.setProbeData.bind(this);
    this.setOutletData = this.setOutletData.bind(this);
    this.setGlobalPrefs = this.setGlobalPrefs.bind(this);
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
  setProbeData(probedata) {
    console.log(probedata);

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
    console.log(outletdata);

    let col2items = [];
    let i = 0;
    for (let outlet in outletdata) {
      outletdata[outlet]["id"] = `item-${String(200 + i++)}`;
      outletdata[outlet]["widgetType"] = `outlet`;
      col2items.push(outletdata[outlet]);
    }

    if (col2items.length > 0) {
      this.setState({ col2items });
    }

    return col2items;
  }

  async componentDidMount() {
    this.apiCall(process.env.REACT_APP_API_GET_PROBE_LIST, this.setProbeData);
    console.log(process.env.REACT_APP_API_GET_PROBE_LIST);

    this.apiCall(process.env.REACT_APP_API_GET_OUTLET_LIST, this.setOutletData);
    console.log(process.env.REACT_APP_API_GET_OUTLET_LIST);

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
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }

  //   ///////
  handleOpenGlobalPrefsModal = () => {
    console.log("global prefs button click");
    this.setState({ setGlobalPrefsModalOpen: true });
    this.setState({ isGlobalPrefsModalOpen: true });
  };

  handleCloseGlobalPrefsModal = () => {
    this.setState({ setGlobalPrefsModalOpen: false });
    this.setState({ isGlobalPrefsModalOpen: false });
  };

  handleGlobalPrefsFormSubmit = (data) => {
    let apiURL = process.env.REACT_APP_API_SET_GLOBAL_PREFS;
    let payload = {
      tempscale: data.tempScale,
      dht_enable: data.enableDHT,
      feed_a_time: "0",
      feed_b_time: "0",
      feed_c_time: "0",
      feed_d_time: "0",
    };
    this.apiCallPut(apiURL, payload);
    this.handleCloseGlobalPrefsModal();
  };

  setGlobalPrefs(data) {
    console.log(data);
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
      <FeedWidget></FeedWidget>
    } else {
      return null;
    }
  };

  //   {
  //     item.widgetType === "probe" ? (
  //       <ProbeWidget
  //         data={item}
  //         ProbeID={item.probeid}
  //         key={item.probeid}
  //       ></ProbeWidget>
  //     ) : (
  //       <OutletWidget
  //         data={item}
  //         OutletID={item.outletid}
  //         key={item.outletid}
  //         probearray={this.state.ProbeArray}
  //       ></OutletWidget>
  //     );
  //   }
  // };

  // Normally you would want to split things out into separate components.
  // But in this example everything is just done in one place for simplicity
  render() {
    return (
      <div className="App">
        <div class="appheader">
          <img className="appicon" src={appicon} alt="logo" />

          <span>Reefberry Pi</span>

          <div class="header-right">
            <button className="preficonbtn">
              <img
                className="preficon"
                src={preficon}
                alt="preferences"
                onClick={this.handleOpenGlobalPrefsModal}
              ></img>
            </button>
          </div>
        </div>
        <div className="maingridcontainer">
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
                          {/* {item.widgetType === "probe" ? (
                            <ProbeWidget
                              data={item}
                              ProbeID={item.probeid}
                              key={item.probeid}
                            ></ProbeWidget>
                          ) : (
                            <OutletWidget
                              data={item}
                              OutletID={item.outletid}
                              key={item.outletid}
                              probearray={this.state.ProbeArray}
                            ></OutletWidget>
                          )} */}
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
                          {/* {item.widgetType === "probe" ? (
                            <ProbeWidget
                              data={item}
                              ProbeID={item.probeid}
                              key={item.probeid}
                            ></ProbeWidget>
                          ) : (
                            <OutletWidget
                              data={item}
                              OutletID={item.outletid}
                              key={item.outletid}
                              probearray={this.state.ProbeArray}
                            ></OutletWidget>
                          )} */}
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div>
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
// Put the things into the DOM!
// const container = document.getElementById("root");
// const root = createRoot(container);
// root.render(<App />);

// class App extends Component {
//   constructor(props) {
//     super(props);
//     this.state = {
//       apiResponse: null,
//       ProbeArray: [],
//       OutletArray: [],
//       DHTArray: [],
//       AppUID: "",
//       globalPrefs: null,
//     };

//     this.setProbeData = this.setProbeData.bind(this);
//     this.setOutletData = this.setOutletData.bind(this);
//     this.createOutletSet = this.createOutletSet.bind(this);
//     this.handleOutletButtonClick = this.handleOutletButtonClick.bind(this);
//     this.handleCurrentOutletState = this.handleCurrentOutletState.bind(this);
//     this.setDHTData = this.setDHTData.bind(this);
//     this.setGlobalPrefs = this.setGlobalPrefs.bind(this);
//   }

//   async componentDidMount() {
//     document.title = "Reefberry Pi";
//     // probe list
//     console.log(process.env.REACT_APP_API_GET_TEMPPROBE_LIST);
//     this.apiCall(
//       process.env.REACT_APP_API_GET_TEMPPROBE_LIST,
//       this.setProbeData
//     );
//     this.interval = setInterval(() => {
//       this.apiCall(
//         process.env.REACT_APP_API_GET_TEMPPROBE_LIST,
//         this.setProbeData
//       );
//     }, 2000);
//     // outlet list
//     this.apiCall(
//       process.env.REACT_APP_API_GET_OUTLET_LIST,
//       this.createOutletSet
//     );
//     this.interval2 = setInterval(() => {
//       this.apiCall(
//         process.env.REACT_APP_API_GET_OUTLET_LIST,
//         this.handleCurrentOutletState
//       );
//     }, 2000);
//     // dht sensor list
//     this.apiCall(process.env.REACT_APP_API_GET_DHT_SENSOR, this.setDHTData);
//     this.interval3 = setInterval(() => {
//       this.apiCall(process.env.REACT_APP_API_GET_DHT_SENSOR, this.setDHTData);
//     }, 2000);
//     // global prefs
//     this.apiCall(
//       process.env.REACT_APP_API_GET_GLOBAL_PREFS,
//       this.setGlobalPrefs
//     );
//     this.interval4 = setInterval(() => {
//       this.apiCall(
//         process.env.REACT_APP_API_GET_GLOBAL_PREFS,
//         this.setGlobalPrefs
//       );
//     }, 3500);
//   }

//   // generic API call structure
//   apiCall(endpoint, callback) {
//     fetch(endpoint)
//       .then((response) => {
//         if (!response.ok) {
//           if (response.status === 404) {
//             throw new Error("Data not found");
//           } else if (response.status === 500) {
//             throw new Error("Server error");
//           } else {
//             throw new Error("Network response was not ok");
//           }
//         }
//         return response.json();
//       })
//       .then((data) => {
//         // this.setState({ apiResponse: data });
//         callback(data);
//       })
//       .catch((error) => {
//         console.error("Error:", error);
//       });
//   }

//   // API call structure
//   apiCallPut = (endpoint, newdata) => {
//     fetch(endpoint, {
//       method: "PUT",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify(newdata),
//     })
//       .then((response) => response.json())
//       .then((data) => console.log(data))
//       .catch((error) => console.log(error));
//   };

//   setDHTData(probedata) {
//     console.log(probedata);
//     let DHTArray = [];

//     if (probedata.dht_enable === "false") {
//       return DHTArray;
//     }

//     for (let probe in probedata) {
//       DHTArray.push(probedata[probe]);
//     }
//     if (DHTArray.length > 0) {
//       this.setState({ DHTArray });
//     }
//     // console.log(ProbeArray);
//     return DHTArray;
//   }

//   setGlobalPrefs(data) {
//     console.log(data);
//     this.setState({ globalPrefs: data });
//     this.setState({ globalTempScale: data.tempscale });
//     this.setState({ globalEnableDHT: data.dht_enable });

//     return;
//   }

//   setProbeData(probedata) {
//     console.log(probedata);

//     let ProbeArray = [];
//     for (let probe in probedata) {
//       // let probename = probedata[probe]["probename"];
//       // let lastTemp = probedata[probe]["lastTemperature"];
//       // console.log(probedata[probe]);
//       // console.log(probename + " = " + lastTemp);
//       ProbeArray.push(probedata[probe]);
//     }
//     if (ProbeArray.length > 0) {
//       this.setState({ ProbeArray });
//     }

//     // console.log(ProbeArray);

//     return ProbeArray;
//   }
//   createOutletSet(outletdata) {
//     console.log("Create Outlet Set");
//     console.log(outletdata);

//     let OutletArray = [];
//     for (let outlet in outletdata) {
//       OutletArray.push(outletdata[outlet]);
//     }
//     if (OutletArray.length > 0) {
//       this.setState({ OutletArray });
//     }

//     console.log(OutletArray);

//     return OutletArray;
//   }
//   handleCurrentOutletState(outletdata) {
//     var outletListArrayClone = this.state.OutletArray.slice(0);
//     console.log(outletdata);

//     for (var outlet in outletdata) {
//       for (var outletClone in outletListArrayClone) {
//         if (
//           outletListArrayClone[outletClone]["outletid"] ===
//           outletdata[outlet].outletid
//         ) {
//           outletListArrayClone[outletClone]["always_state"] =
//             outletdata[outlet].always_state;
//           outletListArrayClone[outletClone]["button_state"] =
//             outletdata[outlet].button_state;
//           outletListArrayClone[outletClone]["control_type"] =
//             outletdata[outlet].control_type;
//           outletListArrayClone[outletClone]["heater_off"] =
//             outletdata[outlet].heater_off;
//           outletListArrayClone[outletClone]["heater_on"] =
//             outletdata[outlet].heater_on;
//           outletListArrayClone[outletClone]["heater_probe"] =
//             outletdata[outlet].heater_probe;
//           outletListArrayClone[outletClone]["light_off"] =
//             outletdata[outlet].light_off;
//           outletListArrayClone[outletClone]["light_on"] =
//             outletdata[outlet].light_on;
//           outletListArrayClone[outletClone]["outletid"] =
//             outletdata[outlet].outletid;
//           outletListArrayClone[outletClone]["outletname"] =
//             outletdata[outlet].outletname;
//           outletListArrayClone[outletClone]["outletstatus"] =
//             outletdata[outlet].outletstatus;
//           outletListArrayClone[outletClone]["return_enable_feed_a"] =
//             outletdata[outlet].return_enable_feed_a;
//           outletListArrayClone[outletClone]["return_enable_feed_b"] =
//             outletdata[outlet].return_enable_feed_b;
//           outletListArrayClone[outletClone]["return_enable_feed_c"] =
//             outletdata[outlet].return_enable_feed_c;
//           outletListArrayClone[outletClone]["return_enable_feed_d"] =
//             outletdata[outlet].return_enable_feed_d;
//           outletListArrayClone[outletClone]["return_feed_delay_a"] =
//             outletdata[outlet].return_feed_delay_a;
//           outletListArrayClone[outletClone]["return_feed_delay_b"] =
//             outletdata[outlet].return_feed_delay_b;
//           outletListArrayClone[outletClone]["return_feed_delay_c"] =
//             outletdata[outlet].return_feed_delay_c;
//           outletListArrayClone[outletClone]["return_feed_delay_d"] =
//             outletdata[outlet].return_feed_delay_d;
//           outletListArrayClone[outletClone]["skimmer_enable_feed_a"] =
//             outletdata[outlet].skimmer_enable_feed_a;
//           outletListArrayClone[outletClone]["skimmer_enable_feed_b"] =
//             outletdata[outlet].skimmer_enable_feed_b;
//           outletListArrayClone[outletClone]["skimmer_enable_feed_c"] =
//             outletdata[outlet].skimmer_enable_feed_c;
//           outletListArrayClone[outletClone]["skimmer_enable_feed_d"] =
//             outletdata[outlet].skimmer_enable_feed_d;
//           outletListArrayClone[outletClone]["skimmer_feed_delay_a"] =
//             outletdata[outlet].skimmer_feed_delay_a;
//           outletListArrayClone[outletClone]["skimmer_feed_delay_b"] =
//             outletdata[outlet].skimmer_feed_delay_b;
//           outletListArrayClone[outletClone]["skimmer_feed_delay_c"] =
//             outletdata[outlet].skimmer_feed_delay_c;
//           outletListArrayClone[outletClone]["skimmer_feed_delay_d"] =
//             outletdata[outlet].skimmer_feed_delay_d;

//         }
//       }
//       this.setState({ OutletArray: outletListArrayClone });
//     }
//   }

//   setOutletData(outletdata) {
//     console.log(outletdata);

//     let OutletArray = [];
//     for (let outlet in outletdata) {
//       OutletArray.push(outletdata[outlet]);
//     }
//     if (OutletArray.length > 0) {
//       this.setState({ OutletArray });
//     }

//     console.log(OutletArray);

//     return OutletArray;
//   }

//   handleOutletButtonClick(outletid, buttonval) {
//     console.log("I'm handling the button click " + outletid + " " + buttonval);
//     var outletListArrayClone = this.state.OutletArray.slice(0);
//     for (var outletClone in outletListArrayClone) {
//       if (outletListArrayClone[outletClone]["outletid"] === outletid) {
//         console.log("Found a match");
//         // console.log(outletdata[outlet].outletid);
//         // console.log(outletListArrayClone[outletClone]["outletid"]);
//         outletListArrayClone[outletClone]["button_state"] = buttonval;
//         outletListArrayClone[outletClone]["ischanged"] = true;
//       }
//     }
//     //console.log(this.state.OutletArray)
//     this.setState({ OutletArray: outletListArrayClone });
//     console.log(this.state.OutletArray);

//     let apiURL = process.env.REACT_APP_API_PUT_OUTLET_BUTTONSTATE.concat(
//       outletid
//     )
//       .concat("/")
//       .concat(buttonval);
//     //console.log(apiURL)
//     this.apiCall(apiURL);
//   }

//   buttonClickCallback() {
//     console.log();
//   }

//   componentWillUnmount() {
//     clearInterval(this.interval);
//     clearInterval(this.interval2);
//     clearInterval(this.interval3);
//     clearInterval(this.interval4);
//   }

//   ///////
//   handleOpenGlobalPrefsModal = () => {
//     console.log("global prefs button click");
//     this.setState({ setGlobalPrefsModalOpen: true });
//     this.setState({ isGlobalPrefsModalOpen: true });
//   };

//   handleCloseGlobalPrefsModal = () => {
//     this.setState({ setGlobalPrefsModalOpen: false });
//     this.setState({ isGlobalPrefsModalOpen: false });
//   };

//   handleGlobalPrefsFormSubmit = (data) => {
//     let apiURL = process.env.REACT_APP_API_SET_GLOBAL_PREFS;
//     let payload = {
//       tempscale: data.tempScale,
//       dht_enable: data.enableDHT,
//       feed_a_time: "0",
//       feed_b_time: "0",
//       feed_c_time: "0",
//       feed_d_time: "0"
//     };
//     this.apiCallPut(apiURL, payload);
//     this.handleCloseGlobalPrefsModal()
//   };

//   //////

//   render() {
//     return (
//       <div className="App">
//         <div class="appheader">
//           <img className="appicon" src={appicon} alt="logo" />

//           <span>Reefberry Pi</span>

//           <div class="header-right">
//             <button className="preficonbtn">
//               <img
//                 className="preficon"
//                 src={preficon}
//                 alt="preferences"
//                 onClick={this.handleOpenGlobalPrefsModal}
//               ></img>
//             </button>
//           </div>
//         </div>
//         <div class="maingridcontainer">
//           <div class="maincol1">
//             {this.state.ProbeArray.map((probe, index) => (
//               <div class="col1items" >
//                 <ProbeWidget data={probe} key={probe.probeid} index={index}></ProbeWidget>
//               </div>
//             ))}

//             {this.state.DHTArray.map((probe) => (
//               <div class="col1items" >
//                 <ProbeWidget data={probe} key={probe.probeid}></ProbeWidget>
//               </div>
//             ))}
//           </div>
//           <div class="maincol2">
//             {this.state.OutletArray.map((outlet) => (
//               <div class="col2items">
//                 <OutletWidget
//                   data={outlet}
//                   onButtonStateChange={this.handleOutletButtonClick}
//                   probearray={this.state.ProbeArray}
//                   key={outlet.outletid}
//                 ></OutletWidget>
//               </div>
//             ))}
//           </div>
//         </div>

//         {this.state.globalPrefs && this.state.isGlobalPrefsModalOpen ? (
//           <GlobalPrefsModal
//             isOpen={this.state.isGlobalPrefsModalOpen}
//             onSubmit={this.handleGlobalPrefsFormSubmit}
//             onClose={this.handleCloseGlobalPrefsModal}
//             globalTempScale={this.state.globalTempScale}
//             globalPrefs={this.state.globalPrefs}
//           />
//         ) : null}
//       </div>
//     );
//   }
// }
// export default App;
