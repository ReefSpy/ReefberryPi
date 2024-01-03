import React, { Component } from "react";
import { ProbeWidget } from "./Components/ProbeWidget";
import "./App.css";

const apiUrl = "http://xpi01.local:5000/get_tempprobe_list/";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      apiResponse: null,
    };
  }

  async componentDidMount() {
    this.interval = setInterval(() => {
      this.apiCall(apiUrl, this.setProbeData);
    }, 2000);
  }

  // componentDidMount() {
  //   this.interval = setInterval(() => {
  //     fetch("http://xpi01.local:5000/get_tempprobe_list/")
  //       .then((response) => response.json())
  //       .then((apiResponse) => this.setState({ apiResponse }));
  //   }, 2000);
  // }

  // generic API call structure
  apiCall(endpoint, callback) {
    // let returnVal = "";
    fetch(endpoint)
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
        //console.log(JSON.stringify(data, null, 2));
        // returnVal = JSON.stringify(data, null, 2);
        this.setState({ apiResponse: data });
        // console.log(returnVal);
        callback(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  setProbeData(probedata) {
    console.log(probedata);
    const arr = [];
    // console.log(json)

    for (let probe in probedata) {
      let probename = probedata[probe]["probename"];
      let lastTemp = probedata[probe]["lastTemperature"];
      console.log(probedata[probe]);
      console.log(probename + " = " + lastTemp);
      arr.push(probedata[probe]);
    }
    //this.setState({ apiResponse: arr });

    console.log(arr);
    return arr;
  }

  componentWillUnmount() {
    clearInterval(this.interval);
  }
  render() {
    var probeArray = this.setProbeData(this.state.apiResponse);

    return (
      <div className="App">
        <h1>Welcome</h1>
        {/* <ProbeWidget
          data={this.state.apiResponse}
        ></ProbeWidget> */}
        <ProbeWidget data = {probeArray}></ProbeWidget>
      </div>
    );
  }
}
export default App;

// import React, { Component } from 'react';

// class App extends Component {
//   constructor(props) {
//     super(props);

//     this.state = {
//       data: [],
//     };
//   }

//   componentDidMount() {
//     this.interval = setInterval(() => {
//       fetch("http://xpi01.local:5000/get_tempprobe_list/")
//         .then(response => response.json())
//         .then(data => this.setState({ data }));
//     }, 2000);
//   }

//   componentWillUnmount() {
//     clearInterval(this.interval);
//   }

//   processData(data) {
//     // Process the data here
//     return data;
//   }

//   render() {
//     return (
//       <div>
//         <ChildComponent data={this.processData(this.state.data)} />
//       </div>
//     );
//   }
// }

// function ChildComponent(props) {
//   console.log(props.data)
//   return (
//     <div>
//      {JSON.stringify(props.data)}
//     </div>
//   );
// }
// export default App;
