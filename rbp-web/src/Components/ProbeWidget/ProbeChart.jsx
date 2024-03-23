import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

const HighchartsWrapper = props => {

/////////////////////////////

////////////////////////////


  //console.log(props.chartdata); // this is always correct)
  //console.log(props.probename);

  /*constructor(props) {
    super(props);
    this.state = {
     chartData : []
    };
  }*/

  /*let options = {
    title: { text: "My chart" },
    series: props.chartData
  };*/

  // options for test chart
  let options = {
    chart: {
      type: "spline",
      height: 100,
      width: 180,
      borderColor: "#85868c",
      borderWidth: 2,
      borderRadius: 5,
      animation: false
    },
    title: {
      text: ""
    },
    legend: {
      enabled: false
    },
    credits: {
      enabled: false
    },

    xAxis: { visible: false, type: "datetime" },
    yAxis: { title: { enabled: false } },
    tooltip: {
      shared: true,
      valueDecimals: 2,
    },
    series: [{ name: props.probename, data: props.chartdata, color: "orange" }],
    
    plotOptions: {
      series: {
          animation: false
      }
  },
  time: {
    useUTC: false
  },
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default HighchartsWrapper;
