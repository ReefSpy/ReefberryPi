import React from "react";

// there is a bug in react-beautiful-dnd where it wont work with strict mode
// in React 18.  Solution is repplace with fork @hello-pangea-dnd to fix it
// import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { DragDropContext } from "@hello-pangea/dnd";

import { FeedWidget } from "../FeedWidget/FeedWidget";
import { ProbeWidget } from "../ProbeWidget/ProbeWidget";
import { OutletWidget } from "../OutletWidget/OutletWidget";

import Column from "./Column";
import "./Dashboard2.css";

class Dashboard2 extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      // Facilitate reordering of the columns
      columnOrder: ["column-1", "column-2", "column-3"],

      collist1: [],
      collist2: [],
      collist3: [],

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

  async initWidgets() {
    let collist1 = [];
    let collist2 = [];
    let collist3 = [];
    let items = {};
    let probeitems = [];
    let i = 1;
    let newcol = this.state.columns;

    // first add probe widgets
    fetch(process.env.REACT_APP_API_GET_PROBE_LIST)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        i = 100;
        for (let probe in data) {
          let idnum = String(i++);
          data[probe]["id"] = `item-${idnum}`;
          data[probe]["widgetType"] = `probe`;
          data[probe]["content"] = "Probe Widget";

          items[`item-${idnum}`] = data[probe];
          collist1.push(`item-${idnum}`);
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
    fetch(process.env.REACT_APP_API_GET_OUTLET_LIST)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        i = 200;
        for (let outlet in data) {
          let idnum = String(i++);
          data[outlet]["id"] = `item-${idnum}`;
          data[outlet]["widgetType"] = `outlet`;
          data[outlet]["content"] = "Outlet Widget";

          items[`item-${idnum}`] = data[outlet];


          if (data[outlet]["enabled"] === "true") {
            collist2.push(`item-${idnum}`);
            outletitems.push(data[outlet]);
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
    i = 300;
    let idnum = String(i++);
    let feeditem = {
      widgetType: "feed",
      id: `item-${idnum}`,
      content: "Feed Widget",
    };
    items[feeditem.id] = feeditem;
    collist3.push(`item-${idnum}`);

    newcol["column-3"].widgetIds = collist3;

    this.setState({ collist3: collist3 });
    this.setState({ WidgetArray: items });
    this.setState({ columns: newcol, widgets: items });
    // this.setState({ widgets: items });

    // let cols = this.state.columns
    // cols["column-1"].widgetIds = collist3
    // this.setState({columns: cols})
    // console.log(cols)
    // console.log(this.state.columns["column-1"].widgetIds)
  }

  initColumns() {
    // now assign widgets to columns
    let columns = {
      "column-1": {
        id: "column-1",
        title: "Column 1",
        //  widgetIds: ["widget-1", "widget-2", "widget-3"],
        widgetIds: [],
      },
      "column-2": {
        id: "column-2",
        title: "Column 2",
        //  widgetIds: ["widget-5"],
        widgetIds: [],
      },
      "column-3": {
        id: "column-3",
        title: "Column 3",
        // widgetIds: ["widget-4"],
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

async reloadDashboard() {
  this.initColumns();
  this.initWidgets();
}

  async componentDidMount() {
    this.initColumns();
    this.initWidgets();
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
