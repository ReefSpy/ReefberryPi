import React, { Component } from "react";
import "./FeedWidget.css";

export class FeedWidget extends Component {
  constructor(props) {
    super(props);
    this.state = {
      SomeState: null,
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

  clickFeedMode = (mode) => {

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
              this.props.feedmode === "A" ? "feedmodebtnon" : "feedmodebtn"
            }
            onClick={() => this.clickFeedMode("A")}
          >
            A
          </button>
          <button
            className={
              this.props.feedmode === "B" ? "feedmodebtnon" : "feedmodebtn"
            }
            onClick={() => this.clickFeedMode("B")}
          >
            B
          </button>
          <button
            className={
              this.props.feedmode === "C" ? "feedmodebtnon" : "feedmodebtn"
            }
            onClick={() => this.clickFeedMode("C")}
          >
            C
          </button>
          <button
            className={
              this.props.feedmode === "D" ? "feedmodebtnon" : "feedmodebtn"
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
