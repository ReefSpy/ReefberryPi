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

  render() {
    return <div class="feedcontainer">
        Feed Widget
    </div>;
  }
}
