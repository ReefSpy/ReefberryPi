import React, { Component } from "react";
import "./OutletWidget.css";

class PrefPaneReturn extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: props.data,
      return_enable_feed_a: props.data.return_enable_feed_a,
      return_enable_feed_b: props.data.return_enable_feed_b,
      return_enable_feed_c: props.data.return_enable_feed_c,
      return_enable_feed_d: props.data.return_enable_feed_d,
      return_feed_delay_a: props.data.return_feed_delay_a,
      return_feed_delay_b: props.data.return_feed_delay_b,
      return_feed_delay_c: props.data.return_feed_delay_c,
      return_feed_delay_d: props.data.return_feed_delay_d,
    };
  }

  handleInputChangeA(event) {
    this.setState({ return_enable_feed_a: event.target.checked });
  }

  handleInputChangeB(event) {
    this.setState({ return_enable_feed_b: event.target.checked });
  }

  handleInputChangeC(event) {
    this.setState({ return_enable_feed_c: event.target.checked });
  }

  handleInputChangeD(event) {
    this.setState({ return_enable_feed_d: event.target.checked });
  }

  handleNumChangeA(event) {
    this.setState({ return_feed_delay_a: event.target.value });
  }

  handleNumChangeB(event) {
    this.setState({ return_feed_delay_b: event.target.value });
  }

  handleNumChangeC(event) {
    this.setState({ return_feed_delay_c: event.target.value });
  }

  handleNumChangeD(event) {
    this.setState({ return_feed_delay_d: event.target.value });
  }

//  validateNumberA(event){
//   const keyCode = event.keyCode || event.which;
//   const keyValue = String.fromCharCode(keyCode);
//   const currentValue = event.target.value + keyValue;
//   const max = event.target.max;

//   if (currentValue > max) {
//     event.target.value = max
//     this.setState({ return_feed_delay_a: max});
//   }
//   }

//   validateNumberB(event){
//     const keyCode = event.keyCode || event.which;
//     const keyValue = String.fromCharCode(keyCode);
//     const currentValue = event.target.value + keyValue;
//     const max = event.target.max;
  
//     if (currentValue > max) {
//       event.target.value = max
//       this.setState({ return_feed_delay_b: max});
//     }
//     }

//     validateNumberC(event){
//       const keyCode = event.keyCode || event.which;
//       const keyValue = String.fromCharCode(keyCode);
//       const currentValue = event.target.value + keyValue;
//       const max = event.target.max;
    
//       if (currentValue > max) {
//         event.target.value = max
//         this.setState({ return_feed_delay_c: max});
//       }
//       }

//       validateNumberD(event){
//         const keyCode = event.keyCode || event.which;
//         const keyValue = String.fromCharCode(keyCode);
//         const currentValue = event.target.value + keyValue;
//         const max = event.target.max;
      
//         if (currentValue > max) {
//           event.target.value = max
//           this.setState({ return_feed_delay_d: max});
//         }
//         }

      

  render() {
    return (
      <div>
        <div class="feedgridcontainer">
          <div class="feedtimerlabel feedcol1">Feed Timer</div>
          <div class="feedmoderow feedcol1 feedrowA" grid-row-start="2">
            A
          </div>
          <div class="feedmoderow feedcol1 feedrowB" grid-row-start="3">
            B
          </div>
          <div class="feedmoderow feedcol1 feedrowC" grid-row-start="4">
            C
          </div>
          <div class="feedmoderow feedcol1 feedrowD" grid-row-start="5">
            D
          </div>

          <div class="feedtimerlabel feedcol2">Enable</div>

          <div class="feedmoderow feedcol2 feedrowA" grid-row-start="2">
            <input
              type="checkbox"
              onChange={(event) => this.handleInputChangeA(event)}
              id="return_enable_feed_a"
              name="return_enable_feed_a"
              checked={this.state.return_enable_feed_a}
            />
          </div>
          <div class="feedmoderow feedcol2 feedrowB" grid-row-start="3">
            <input
              type="checkbox"
              onChange={(event) => this.handleInputChangeB(event)}
              id="return_enable_feed_b"
              name="return_enable_feed_b"
              checked={this.state.return_enable_feed_b}
            />
          </div>
          <div class="feedmoderow feedcol2 feedrowC" grid-row-start="4">
            <input
              type="checkbox"
              onChange={(event) => this.handleInputChangeC(event)}
              id="return_enable_feed_c"
              name="return_enable_feed_c"
              checked={this.state.return_enable_feed_c}
            />
          </div>
          <div class="feedmoderow feedcol2 feedrowD" grid-row-start="5">
            <input
              type="checkbox"
              onChange={(event) => this.handleInputChangeD(event)}
              id="return_enable_feed_d"
              name="return_enable_feed_d"
              checked={this.state.return_enable_feed_d}
            />
          </div>

          <div class="feedtimerlabel feedcol3" grid-row-start="1">
            Additional Feed Timer Delay (seconds)
          </div>
          <div class="feedmoderow feedcol3 feedrowA" grid-row-start="2">
            <input
              type="number"
              name="return_feed_delay_a"
              value={this.state.return_feed_delay_a}
              min="0"
              max="3600"
              // defaultValue={0}
              onChange={(event) => this.handleNumChangeA(event)}
              // onKeyUp={(event) => this.validateNumberA(event)}
              
              
            />
          </div>
          <div class="feedmoderow feedcol3 feedrowB" grid-row-start="3">
            <input
              type="number"
              name="return_feed_delay_b"
              value={this.state.return_feed_delay_b}
              min="0"
              max="3600"
              // defaultValue={0}
              onChange={(event) => this.handleNumChangeB(event)}
              // onKeyUp={(event) => this.validateNumberB(event)}
            />
          </div>
          <div class="feedmoderow feedcol3 feedrowC" grid-row-start="4">
            <input
              type="number"
              name="return_feed_delay_c"
              value={this.state.return_feed_delay_c}
              min="0"
              max="3600"
              // defaultValue={0}
              onChange={(event) => this.handleNumChangeC(event)}
              // onKeyUp={(event) => this.validateNumberC(event)}
            />
          </div>
          <div class="feedmoderow feedcol3 feedrowD" grid-row-start="5">
            <input
              type="number"
              name="return_feed_delay_d"
              value={this.state.return_feed_delay_d}
              min="0"
              max="3600"
              // defaultValue={0}
              onChange={(event) => this.handleNumChangeD(event)}
              // onKeyUp={(event) => this.validateNumberD(event)}
            />
          </div>
        </div>
      </div>
    );
  }
}

export default PrefPaneReturn;
