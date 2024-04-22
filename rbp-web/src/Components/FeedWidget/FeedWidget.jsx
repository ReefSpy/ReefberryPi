import React, { Component } from "react";
import "./FeedWidget.css";
import CountdownTimer  from "./CountDownTimer";
import * as Api from "../Api/Api.js"

export class FeedWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {
      SomeState: null,
      shouldFeedChange: false,
      feedmode: "CANCEL",
    };
  }

  // // generic API call structure
  // apiCall(endpoint, callback) {
  //   fetch(endpoint)
  //     .then((response) => {
  //       if (!response.ok) {
  //         if (response.status === 404) {
  //           throw new Error("Data not found");
  //         } else if (response.status === 500) {
  //           throw new Error("Server error");
  //         } else {
  //           throw new Error("Network response was not ok");
  //         }
  //       }
  //       return response.json();
  //     })
  //     .then((data) => {
  //       callback(data);
  //     })
  //     .catch((error) => {
  //       console.error("Error:", error);
  //     });
  // }

  componentDidMount() {}

  componentWillUnmount() {}

  componentWillReceiveProps() {
    // to prevent button state from changing prematurely, 
    // ensure you get two consecutive statuses that are the same
    if (this.state.shouldFeedChange === true){
      this.setState({ feedmode: this.props.feedmode });
      this.setState({ shouldFeedChange: false });
      }
    
    if (this.props.feedmode !== this.state.feedmode){
      this.setState({ shouldFeedChange: true });
    }else{
      this.setState({ shouldFeedChange: false });
    }


  }

  clickFeedMode = (mode) => {
    this.setState({ feedmode: mode });
    this.setState({ shouldFeedChange: false });
    if(mode === "A"){
      this.setState({feedtimer: this.props.globalPrefs.feed_a_time})
    } else if (mode === "B"){
      this.setState({feedtimer: this.props.globalPrefs.feed_b_time})
    }else if (mode === "C"){
      this.setState({feedtimer: this.props.globalPrefs.feed_c_time})
    } else if (mode === "D"){
      this.setState({feedtimer: this.props.globalPrefs.feed_d_time})
    } else { this.setState({feedtimer: "0"})}
    
    // let apiURL = Api.API_SET_FEEDMODE.concat(mode);
    // this.apiCall(apiURL ,() => this.setFeedState(mode));

    this.setFeedMode(mode)
  };

// setFeedState(mode){
//   console.log(mode)
// return
// }

setFeedMode = (feedmode) => {
  console.log(JSON.stringify(feedmode));
  let authtoken = JSON.parse(sessionStorage.getItem("token")).token
  return fetch(Api.API_SET_FEEDMODE, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + authtoken
    },
    body: JSON.stringify({ feedmode: feedmode }),
  })
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
      return data;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

  render() {
    return (
      <div className="feedcontainer">
        <div className="feedmodelbl">Feed Mode</div>
       {this.state.feedmode !== "CANCEL" ? (<div className="feedtimer"><CountdownTimer time = {this.state.feedtimer} /></div>) : null }
        
    
        <div className="btncontainer">
          <button
            className={
              this.state.feedmode === "A" ? "feedmodebtnon" : "feedmodebtn"
            }
            onClick={() => this.clickFeedMode("A")}
          >
            A
          </button>
          <button
            className={
              this.state.feedmode === "B" ? "feedmodebtnon" : "feedmodebtn"
            }
            onClick={() => this.clickFeedMode("B")}
          >
            B
          </button>
          <button
            className={
              this.state.feedmode === "C" ? "feedmodebtnon" : "feedmodebtn"
            }
            onClick={() => this.clickFeedMode("C")}
          >
            C
          </button>
          <button
            className={
              this.state.feedmode === "D" ? "feedmodebtnon" : "feedmodebtn"
            }
            onClick={() => this.clickFeedMode("D")}
          >
            D
          </button>
          <button
            className="feedcancelbtn"
            onClick={() => this.clickFeedMode("CANCEL")}
          >
            Cancel
          </button>
       
        </div>
      </div>
    );
  }
}
