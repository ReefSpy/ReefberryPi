import React from "react";

// there is a bug in react-beautiful-dnd where it wont work with strict mode
// in React 18.  Solution is repplace with fork @hello-pangea-dnd to fix it
// import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { DragDropContext } from "@hello-pangea/dnd";

// import { FeedWidget } from "../FeedWidget/FeedWidget";
// import { ProbeWidget } from "../ProbeWidget/ProbeWidget";
// import { OutletWidget } from "../OutletWidget/OutletWidget";

import Column from "./Column";
import "./Dashboard2.css";
import * as Api from "../Api/Api.js"

class Dashboard2 extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      // Facilitate reordering of the columns
      columnOrder: ["column-1", "column-2", "column-3"],

      collist1: [],
      collist2: [],
      collist3: [],

      Col1SaveOrder: [],
      Col2SaveOrder: [],
      Col3SaveOrder: [],

      widgets: {},

      columns: {
        "column-1": {
          id: "column-1",
          title: "Column 1",
          widgetIds: [],
        },
        "column-2": {
          id: "column-2",
          title: "Column 2",
          widgetIds: [],
        },
        "column-3": {
          id: "column-3",
          title: "Column 3",
          widgetIds: [],
        },
        // 'column-4': {
        //   id: 'column-4',
        //   title: 'Column 4',
        //   widgetIds: [],
        // },
      },
    };

    this.reorderWidgets = this.reorderWidgets.bind(this);
  }

  onDragEnd = (result) => {
    const { destination, source, draggableId } = result;

    if (!destination) {
      return;
    }

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const start = this.state.columns[source.droppableId];
    const finish = this.state.columns[destination.droppableId];

    if (start === finish) {
      const newWidgetIds = Array.from(start.widgetIds);
      newWidgetIds.splice(source.index, 1);
      newWidgetIds.splice(destination.index, 0, draggableId);

      const newColumn = {
        ...start,
        widgetIds: newWidgetIds,
      };

      const newState = {
        ...this.state,
        columns: {
          ...this.state.columns,
          [newColumn.id]: newColumn,
        },
      };

      this.setState(newState);
      return;
    }

    // Moving from one list to another
    const startWidgetIds = Array.from(start.widgetIds);
    startWidgetIds.splice(source.index, 1);
    const newStart = {
      ...start,
      widgetIds: startWidgetIds,
    };

    const finishWidgetIds = Array.from(finish.widgetIds);
    finishWidgetIds.splice(destination.index, 0, draggableId);
    const newFinish = {
      ...finish,
      widgetIds: finishWidgetIds,
    };

    const newState = {
      ...this.state,
      columns: {
        ...this.state.columns,
        [newStart.id]: newStart,
        [newFinish.id]: newFinish,
      },
    };
    this.setState(newState);
  };

  async getSavedWidgetOrder() {
    // first add probe widgets
    fetch(Api.API_GET_COLUMN_WIDGET_ORDER)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        // console.log(data);
        this.setState({ Col1SaveOrder: data["column1"] });
        this.setState({ Col2SaveOrder: data["column2"] });
        this.setState({ Col3SaveOrder: data["column3"] });
        // for (let column in data) {
        //   console.log(data[column]);
        // }
      })
      .then((data) => {
        let newcol = this.state.columns;
        newcol["column-1"].widgetIds = this.state.Col1SaveOrder;
        newcol["column-2"].widgetIds = this.state.Col2SaveOrder;
        newcol["column-3"].widgetIds = this.state.Col3SaveOrder;
        // this.setState({columns: newcol}) ;
        // console.log(newcol["column-1"].widgetIds);
        // console.log(newcol["column-2"].widgetIds);
        // console.log(newcol["column-3"].widgetIds);
        // console.log(this.state.WidgetArray);
        
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  async initWidgets() {
    console.log("initWidgets")
    let collist1 = [];
    let collist2 = [];
    let collist3 = [];
    let items = {};
    let probeitems = [];
    // let i = 1;
    let newcol = this.state.columns;

    // first add probe widgets
    fetch(Api.API_GET_PROBE_LIST)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        // i = 100;
        for (let probe in data) {
          // let idnum = String(i++);
          // data[probe]["id"] = `item-${idnum}`;
          data[probe]["id"] = probe;
          data[probe]["widgetType"] = `probe`;
          data[probe]["content"] = "Probe Widget";

          // items[`item-${idnum}`] = data[probe];
          items[probe] = data[probe];

          //  collist1.push(`item-${idnum}`);
          collist1.push(probe);

          probeitems.push(data[probe]);
        }
      })
      .then(() => {
        this.setState({ ProbeArray: probeitems });
        this.setState({ collist1: collist1 });

        // console.log(newcol["column-1"])
        // console.log(collist1)
        newcol["column-1"].widgetIds = collist1;

        // this.setState({columns2: newcol })
      })
      .catch((error) => {
        console.error("Error:", error);
      });

    // now add outlet widgets
    let outletitems = [];
    // fetch(process.env.REACT_APP_API_GET_OUTLET_LIST)
    fetch(Api.API_GET_OUTLET_LIST)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        // i = 200;
        for (let outlet in data) {
          // let idnum = String(i++);
          //  data[outlet]["id"] = `item-${idnum}`;
          data[outlet]["id"] = outlet;

          data[outlet]["widgetType"] = `outlet`;
          data[outlet]["content"] = "Outlet Widget";

          //items[`item-${idnum}`] = data[outlet];
          //items[outlet] = data[outlet];

          if (data[outlet]["enabled"] === "true") {
            // collist2.push(`item-${idnum}`);
            collist2.push(outlet);

            outletitems.push(data[outlet]);
            items[outlet] = data[outlet];
          }
        }
      })
      .then(() => {
        this.setState({ OutletArray: outletitems });
        this.setState({ collist2: collist2 });

        newcol["column-2"].widgetIds = collist2;
      })

      .catch((error) => {
        console.error("Error:", error);
      });

    // now add other widgets
    // lets add the feedwidget to this set
    // i = 300;
    // let idnum = String(i++);
    let feeditem = {
      widgetType: "feed",
      // id: `item-${idnum}`,
      id: "feed",
      content: "Feed Widget",
    };
    items[feeditem.id] = feeditem;
    // collist3.push(`item-${idnum}`);
    collist3.push("feed");

    newcol["column-3"].widgetIds = collist3;

    this.setState({ collist3: collist3 });
    this.setState({ WidgetArray: items });
    //this.setState({ columns: newcol, widgets: items });
     this.setState({ widgets: items });
 
  }

  initColumns() {
    console.log("initColumns")
    // now assign widgets to columns
    let columns = {
      "column-1": {
        id: "column-1",
        title: "Column 1",
        widgetIds: [],
      },
      "column-2": {
        id: "column-2",
        title: "Column 2",
        widgetIds: [],
      },
      "column-3": {
        id: "column-3",
        title: "Column 3",
        widgetIds: [],
      },
      // 'column-4': {
      //   id: 'column-4',
      //   title: 'Again',
      //   widgetIds: [],
      // },
    };

    this.setState({ columns: columns });
  }

  componentDidUpdate(prevProps, prevState) {
    if (this.props.ShouldRefreshDashboard === true) {
      // console.log("from the dashboard");
      // console.log(this.props.ShouldRefreshDashboard);
      this.reloadDashboard();
      this.props.RefreshCompleted();
    }

    if (this.props.shouldSaveWidgetOrder === true) {
      // console.log(this.state.columns);
      // for (const column in this.state.columns) {
      //   this.saveColumnOrder1(this.state.columns[column]["widgetIds"]);
      // }
      this.saveColumnOrder1(this.state.columns["column-1"]["widgetIds"]);
      this.saveColumnOrder2(this.state.columns["column-2"]["widgetIds"]);
      this.saveColumnOrder3(this.state.columns["column-3"]["widgetIds"]);
      this.props.onWidgetSaveComplete();
    }
  }

  saveColumnOrder1 = (widgets) => {
    console.log(JSON.stringify(widgets));
    return fetch(Api.API_SET_COLUMN_WIDGET_ORDER, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ column1: widgets }),
    })
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
        return data;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  saveColumnOrder2 = (widgets) => {
    console.log(JSON.stringify(widgets));
    return fetch(Api.API_SET_COLUMN_WIDGET_ORDER, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ column2: widgets }),
    })
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
        return data;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  saveColumnOrder3 = (widgets) => {
    console.log(JSON.stringify(widgets));
    return fetch(Api.API_SET_COLUMN_WIDGET_ORDER, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ column3: widgets }),
    })
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
        return data;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  reorderWidgets() {
    let columnOrder = this.state.columns;
    columnOrder["column-1"].widgetIds = this.state.Col1SaveOrder;
    columnOrder["column-2"].widgetIds = this.state.Col2SaveOrder;
    columnOrder["column-3"].widgetIds = this.state.Col3SaveOrder;

    for (let widget in this.state.WidgetArray) {
      console.log(widget);
      if (!columnOrder["column-1"].widgetIds.includes(widget)) {
        if (!columnOrder["column-2"].widgetIds.includes(widget)) {
          if (!columnOrder["column-3"].widgetIds.includes(widget)) {
            columnOrder["column-1"].widgetIds.push(widget);
          }
        }
      }
    }
    this.setState({ columns: columnOrder });
  }

  async reloadDashboard() {
    this.getSavedWidgetOrder()
      .then(this.initColumns())
      .then(this.initWidgets())
  }

  async componentDidMount() {
    console.log("Dashboard componentDidMount")
    this.getSavedWidgetOrder()
      .then(this.initColumns())
      .then(this.initWidgets())
      .then(this.reloadDashboard()) // when compiled for prod, dash was empty until it reloaded 2nd time
  }

  render() {
    return (
      <div className="colcontainer">
        <DragDropContext onDragEnd={this.onDragEnd}>
          {this.state.columnOrder.map((columnId) => {
            const column = this.state.columns[columnId];

            const widgets = column.widgetIds.map(
              (widgetId) => this.state.widgets[widgetId]
            );

            return (
              <Column
                key={column.id}
                column={column}
                widgets={widgets}
                globalPrefs={this.props.globalPrefs}
                feedmode={this.props.feedmode}
                probearray={this.state.ProbeArray}
                dragDisabled={this.props.dragDisabled}
              />
            );
          })}
        </DragDropContext>
      </div>
    );
  }
}

export default Dashboard2;
