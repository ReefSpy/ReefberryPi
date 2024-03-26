import React from 'react';
// import styled from 'styled-components';
// there is a bug in react-beautiful-dnd where it wont work with strict mode
// in React 18.  Solution is repplace with fork @hello-pangea-dnd to fix it
// import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { Draggable } from "@hello-pangea/dnd";

import { FeedWidget } from "../FeedWidget/FeedWidget";
import { ProbeWidget } from "../ProbeWidget/ProbeWidget";
import { OutletWidget } from "../OutletWidget/OutletWidget";
import "./Dashboard2.css";

// const Container = styled.div`
//   border: 1px solid lightgrey;
//   border-radius: 2px;
//   padding: 8px;
//   margin-bottom: 8px;
//   background-color: ${props => (props.isDragging ? 'lightgreen' : 'white')};
// `;

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

  

export default class Widget extends React.Component {

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
          probearray={this.props.probearray}
        ></OutletWidget>
      );
    } else if (item.widgetType === "feed") {
      return <FeedWidget feedmode={this.props.feedmode} globalPrefs={this.props.globalPrefs}></FeedWidget>;
    } else {
      return null;
    }
  };
  render() {
    return (
      <Draggable draggableId={this.props.widget.id} index={this.props.index}  isDragDisabled={this.props.dragDisabled}>
        {(provided, snapshot) => (
          <div className = "widget"
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            ref={provided.innerRef}
            isDragging={snapshot.isDragging}
            style={getItemStyle(
                snapshot.isDragging,
                provided.draggableProps.style
              )}
          >
            {/* {this.props.widget.content} */}
            {this.getWidget(this.props.widget)}
          </div>
        )}
      </Draggable>
    );
  }
}
