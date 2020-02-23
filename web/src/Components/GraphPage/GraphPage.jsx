import React from "react";
import Button from "react-bootstrap/Button";
import { GraphWidget } from "./GraphWidget";

export class GraphPage extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      graphArray: []
    };
  }

  createGraph() {
    this.props.onPrimaryChartSelect();
    console.log("button press");
    console.log(this.props.primaryChartData);
    const graph = [];
    graph.push(
      <GraphWidget
        primaryChartData={this.props.primaryChartData}
        onPrimaryChartSelect={this.props.onPrimaryChartSelect}
        oneToOne={true}
      ></GraphWidget>
    );
    this.setState({ graphArray: graph });
    //console.log(this.state)
  }

  render() {
    //console.log("graphPage Render");
    //console.log(this.props.primaryChartData);
    return (
      <div>
        {this.props.primaryChartData.length}
        <Button onClick={this.props.onPrimaryChartSelect}>load data</Button>
        <Button onClick={this.createGraph.bind(this)}>create graph</Button>
        <GraphWidget
        primaryChartData={this.props.primaryChartData}
        onPrimaryChartSelect={this.props.onPrimaryChartSelect}
        oneToOne={true}
      ></GraphWidget>
        <div>
          {this.state.graphArray.map((graph, index) => {
            return (
              <div className="box" key={index}>
                {graph}
              </div>
            );
          })}
        </div>
      </div>
    );
  }
}
