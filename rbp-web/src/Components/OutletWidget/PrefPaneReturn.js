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
            <input type="checkbox" id="return_enable_feed_a" name="return_enable_feed_a" checked={this.state.return_enable_feed_a==="true"}  />
          </div>
          <div class="feedmoderow feedcol2 feedrowB" grid-row-start="3">
            <input type="checkbox" id="return_enable_feed_b" name="return_enable_feed_b" checked={this.state.return_enable_feed_b==="true"} />
          </div>
          <div class="feedmoderow feedcol2 feedrowC" grid-row-start="4">
            <input type="checkbox" id="return_enable_feed_c" name="return_enable_feed_c" checked={this.state.return_enable_feed_c==="true"}  />
          </div>
          <div class="feedmoderow feedcol2 feedrowD" grid-row-start="5">
            <input type="checkbox" id="return_enable_feed_d" name="return_enable_feed_d" checked={this.state.return_enable_feed_d==="true"}  />
          </div>

          <div class="feedtimerlabel feedcol3" grid-row-start="1">
            Additional Feed Timer Delay (seconds)
          </div>
          <div class="feedmoderow feedcol3 feedrowA" grid-row-start="2">
            <input type="number" name="return_feed_delay_a" value={this.state.return_feed_delay_a} min="0" max="3600" defaultValue={0}/>
          </div>
          <div class="feedmoderow feedcol3 feedrowB" grid-row-start="3">
            <input type="number" name="return_feed_delay_b" value={this.state.return_feed_delay_b} min="0" max="3600" defaultValue={0}/>
          </div>
          <div class="feedmoderow feedcol3 feedrowC" grid-row-start="4">
            <input type="number" name="return_feed_delay_c" value={this.state.return_feed_delay_c} min="0" max="3600" defaultValue={0}/>
          </div>
          <div class="feedmoderow feedcol3 feedrowD" grid-row-start="5">
            <input type="number" name="return_feed_delay_d" value={this.state.return_feed_delay_d} min="0" max="3600" defaultValue={0}/>
          </div>
        </div>

      </div>
    );
  }
}

export default PrefPaneReturn;
