import React, { Component } from "react";
import "./FeedWidget.css";

export class FeedWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {
      SomeState: null,
      shouldFeedChange: false,
      feedmode: "CANCEL",
    };
  }

  // generic API call structure
  apiCall(endpoint, callback) {
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
        callback(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

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
    let apiURL = process.env.REACT_APP_API_SET_FEEDMODE.concat(mode);
    this.apiCall(apiURL ,() => this.setFeedState(mode));
  };

setFeedState(mode){
  console.log(mode)
return
}

  render() {
    return (
      <div className="feedcontainer">
        <span className="feedmodelbl">Feed Mode</span>
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
