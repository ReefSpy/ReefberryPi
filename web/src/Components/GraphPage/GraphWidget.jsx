import React from "react";
import Highcharts from "highcharts/highstock";
import HighchartsReact from "highcharts-react-official";
import Button from "react-bootstrap/Button";

export class GraphWidget extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  componentDidMount() {
    // console.log("from the graphwidget componentdidmount:");
    // console.log(this.props.primaryChartData);
  }

  componentDidUpdate(prevProps) {
    // console.log("graphWidgetcomponentdidUpdate");
  }

  render() {
    var options = {
      title: {
        text: "testchart"
      },
      xAxis: { visible: true, type: "datetime" },
      chart: {
        type: "spline",
        height: 500,
        animation: false
      },
      rangeSelector: {
        allButtonsEnabled: true,
        buttons: [
          {
            type: "day",
            count: 1,
            text: "1D",
            dataGrouping: {
              forced: true,
              units: [["minute", [1]]]
            }
          },
          {
            type: "day",
            count: 3,
            text: "3D",
            dataGrouping: {
              forced: true,
              units: [["minute", [1]]]
            }
          },
          {
            type: "day",
            count: 7,
            text: "1W",
            dataGrouping: {
              forced: true,
              units: [["hour", [1]]]
            }
          },
          {
            type: "all",
            text: "1M",
            dataGrouping: {
              forced: true,
              units: [["hour", [1]]]
            }
          }
        ]
      },
      series: [
        {
          name: "nothing yet",
          data: this.props.primaryChartData,
          color: "orange",
          turboThreshold: 100000,
          tooltip: {
            valueDecimals: 1
          }
        }
      ]
    };
    //console.log("from the graphWidget render:");
    //console.log(this.props.primaryChartData);

    return (
      <div>
        <HighchartsReact
          highcharts={Highcharts}
          constructorType={"stockChart"}
          options={options}
        />
      </div>
    );
  }

  onPrimaryChartSelect = value => {
    console.log("Click graph page");

    this.props.onPrimaryChartSelect(value);
  };
}
