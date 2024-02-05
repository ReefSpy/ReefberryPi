import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

const HighchartsWrapper = (props) => {
  /////////////////////////////

  ////////////////////////////

  // options for test chart
  let options = {
    chart: {
      type: "spline",
      //   height: 400,
      //   width: 720,
      borderColor: "#85868c",
      borderWidth: 2,
      borderRadius: 5,
      animation: false,
      zoomType: "x",
    },
    title: {
      text: props.chartTitle,
    },
    legend: {
      enabled: true,
    },
    credits: {
      enabled: false,
    },

    xAxis: {
      visible: true,
      type: "datetime",
      labels: {
        format: "{value:%Y-%m-%d %H:%M:%S}",
       // format: "{value:%H:%M:%S}",
      },
    },
    yAxis: [{ title: { enabled: true, text: props.unitType  } },{title: { enabled: true, text: props.unitType2,   },opposite: true} ],
    tooltip: {
      shared: true,
      valueDecimals:2,
    },
    series: [{ name: props.probename, data: props.chartdata, color: "orange", yAxis: 0  },{ name: props.probename2, data: props.chartdata2, color: "steelblue", yAxis: 1  }],

    plotOptions: {
      series: {
        animation: false,
      },
    },
    time: {
        useUTC: false
      },
  };

  return <HighchartsReact highcharts={Highcharts} options={options} />;
};

export default HighchartsWrapper;
