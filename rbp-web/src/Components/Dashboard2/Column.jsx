import React from 'react';
// import styled from 'styled-components';
// there is a bug in react-beautiful-dnd where it wont work with strict mode
// in React 18.  Solution is repplace with fork @hello-pangea-dnd to fix it
// import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { Droppable } from "@hello-pangea/dnd";

import Widget from './Widget';
import "./Dashboard2.css";

// const Container = styled.div`
//   margin: 8px;
//   border: 1px solid lightgrey;
//   border-radius: 2px;
//   width: 220px;

//   display: flex;
//   flex-direction: column;
// `;
// const Title = styled.h3`
//   padding: 8px;
// `;
// const WidgetList = styled.div`
//   padding: 8px;
//   transition: background-color 0.2s ease;
//   background-color: ${props => (props.isDraggingOver ? 'skyblue' : 'white')};
//   flex-grow: 1;
//   min-height: 100px;
// `;
const getListStyle = (isDraggingOver) => ({
    background: isDraggingOver ? "lightblue" : "steelblue",
    padding: "1px",
    width: 320,
  });

export default class Column extends React.Component {
  render() {
    return (
      <div className="column">
        {/* <div className = "title">{this.props.column.title}</div> */}
        <Droppable droppableId={this.props.column.id}>
          {(provided, snapshot) => (
          
            <div className="widgetlist"
              ref={provided.innerRef}
              {...provided.droppableProps}
              isDraggingOver={snapshot.isDraggingOver}
              style={getListStyle(snapshot.isDraggingOver)}
            > 
              {this.props.widgets.map((widget, index) => (  
                
               (widget ? <Widget key={widget.id} widget={widget} index={index} probearray={this.props.probearray} globalPrefs={this.props.globalPrefs} feedmode={this.props.feedmode} /> : null)
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </div>
    );
  }
}
