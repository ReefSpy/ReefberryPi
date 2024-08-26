import React from "react";
import "./PhCal.css";
import * as Api from "../Api/Api.js";

const PhCal = ({
  phCalLowCurrent,
  phCalMidCurrent,
  phCalHighCurrent,
  stdDev,
  mean,
  probeid,
  onSubmitCal
}) => {

    let handlePHSubmitClick = (type) => {
        if (window.confirm("Are you sure you want to calibrate with this value? " + mean)) {
          let authtoken = JSON.parse(sessionStorage.getItem("token")).token;
          fetch(Api.API_SET_ANALOG_PH_CAL, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + authtoken,
            },
            body: JSON.stringify({
              caltype: type,
              targetval: mean,
              probeid: probeid,
            }),
          })
            .then((response) => {
              if (!response.ok) {
                if (response.status === 404) {
                  throw new Error("Data not found");
                } else if (response.status === 500) {
                  alert("Error saving value.");
                  throw new Error("Server error");
                } else if (response.status === 401) {
                  alert("Unauthorized!");
                  throw new Error("Unauthorized access.");
                } else if (response.status === 5000) {
                  throw new Error("Server error");
                } else {
                  throw new Error("Network response was not ok");
                }
              }
              alert("Value saved succesfully!")
              onSubmitCal();
              return response.json();
            })
            .catch((error) => {
              console.error("Error:", error);
            });
        }
      };

  return (
    <div className="phcalcontainer">
      <div className="phrefcontainer phref4">
        <div gridColumnStart="1">
          Reference PH <br />
          <label className="phRefval">4.0</label>
        </div>
        <button
          className="phcalbutton"
          gridColumnStart="1"
          onClick={()=>handlePHSubmitClick("low")}
        >
          Save Low Cal
        </button>
        <label classname="phtargetlabel">Stored Value: {phCalLowCurrent}</label>
      </div>

      <div className="phrefcontainer phref7">
        <div gridColumnStart="2">
          Reference PH <br />
          <label className="phRefval">7.0</label>
        </div>
        <button
          className="phcalbutton"
          gridColumnStart="2"
          onClick={()=>handlePHSubmitClick("mid")}
        >
          Save Mid Cal
        </button>
        <label classname="phtargetlabel">Stored Value: {phCalMidCurrent}</label>
      </div>

      <div className="phrefcontainer phref10">
        <div gridColumnStart="3">
          <label> Reference PH</label> <br />
          <label className="phRefval">10.0</label>
        </div>
        <button
          className="phcalbutton"
          gridColumnStart="3"
          onClick={()=>handlePHSubmitClick("high")}
        >
          Save High Cal
        </button>
        <label classname="phtargetlabel">
          Stored Value: {phCalHighCurrent}
        </label>
      </div>
    </div>
  );
};
export default PhCal;
