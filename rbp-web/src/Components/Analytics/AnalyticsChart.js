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
      text: "",
    },
    legend: {
      enabled: false,
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
    yAxis: { title: { enabled: false } },
    tooltip: {
      shared: true,
    },
    series: [{ name: props.probename, data: props.chartdata, color: "orange" }],

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
