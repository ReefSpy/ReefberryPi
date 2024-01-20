import React, { Component } from "react";
import './OutletWidget.css';

class PrefPaneSkimmer extends Component {
  constructor(props) {
    super(props);

    this.state = {
      someValue: 0,
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
            <input type="checkbox" />
          </div>
          <div class="feedmoderow feedcol2 feedrowB" grid-row-start="3">
            <input type="checkbox" />
          </div>
          <div class="feedmoderow feedcol2 feedrowC" grid-row-start="4">
            <input type="checkbox" />
          </div>
          <div class="feedmoderow feedcol2 feedrowD" grid-row-start="5">
            <input type="checkbox" />
          </div>

          <div class="feedtimerlabel feedcol3" grid-row-start="1">
            Additional Feed Timer Delay (seconds)
          </div>
          <div class="feedmoderow feedcol3 feedrowA" grid-row-start="2">
            <input type="number" min="0" max="3600" defaultValue={0}/>
          </div>
          <div class="feedmoderow feedcol3 feedrowB" grid-row-start="3">
            <input type="number" min="0" max="3600" defaultValue={0}/>
          </div>
          <div class="feedmoderow feedcol3 feedrowC" grid-row-start="4">
            <input type="number" min="0" max="3600" defaultValue={0}/>
          </div>
          <div class="feedmoderow feedcol3 feedrowD" grid-row-start="5">
            <input type="number" min="0" max="3600" defaultValue={0}/>
          </div>
        </div>
        <div className="submit_row">
          <button type="submit" className="submitbutton">
            Submit
          </button>
        </div>
      </div>
    );
  }
}

export default PrefPaneSkimmer;
