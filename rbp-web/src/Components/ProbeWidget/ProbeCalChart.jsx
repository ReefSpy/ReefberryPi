import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import React from "react";

const CalChartWrapper = (props) => {


  // options for test chart
  let options = {
    chart: {
       type: "spline",
      //type: "area",
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

    // xAxis: {
    //   visible: true,
    //  // type: "datetime",
    //   labels: {
    //    // format: "{value:%Y-%m-%d %H:%M:%S}",
    //    // format: "{value:%H:%M:%S}",
    //   },
    // },
    yAxis: [{ title: { enabled: true, text: props.unitType  }, 
    

          
        plotLines: [{
            color: '#FF0000',
            width: 2,
            value: props.mean,

            label: { 
                text: "mean: " + props.mean, // Content of the label. 
                align: 'left', // Positioning of the label. Default to center.
                x: +10, // Amount of pixels the label will be repositioned according to the alignment. 
                zIndex: 99
              }
        },
        {
            color: 'steelblue',
            width: 2,
            value: parseFloat(props.mean) + parseFloat(props.stdDev),
            dashStyle: "dash",
            label: { 
                text: "+1σ", // Content of the label. 
                align: 'left', // Positioning of the label. Default to center.
                x: +10, // Amount of pixels the label will be repositioned according to the alignment. 
              }
        },
       
        {
            color: 'steelblue',
            width: 2,
            value: parseFloat(props.mean) - parseFloat(props.stdDev),
            dashStyle: "dash",
            label: { 
                text: "-1σ", // Content of the label. 
                align: 'left', // Positioning of the label. Default to center.
                x: +10, // Amount of pixels the label will be repositioned according to the alignment. 
              },
              
        },
    ],

    
    }  ],
    tooltip: {
      shared: true,
      //valueDecimals:2,
    },

    plotLines: [{
        color: '#FF0000',
        width: 2,
        value: props.mean
    
    }],

    series: [{ name: props.probename, data: props.chartdata, color: "orange", yAxis: 0, zIndex: 1}, ],

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

export default CalChartWrapper;
