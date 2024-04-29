import React, { useRef, useEffect, useState } from "react";
import "./ProbeWidget.css";
import closeCircle from "./close-circle.svg";
import CalChartWrapper from "./ProbeCalChart";
import * as Api from "../Api/Api.js";

const ProbeWidgetPhCal = ({
  onSubmit,
  isOpen,
  hasCloseBtn = true,
  onClose,
  ProbeName,
  ProbeID,
  SensorType,
  Model,
}) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);
  const [dvList, setDvList] = useState();
  const [stdDev, setStdDev] = useState();
  const [formState, setFormState] = useState({dvList: []});
  const modalRef = useRef(null);

  const formRef = useRef(null);

  const handleCloseModal = () => {
    if (onClose) {
      onClose();
    }
    setModalOpen(false);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Escape") {
      handleCloseModal();
    }
  };

  useEffect(() => {
    setModalOpen(isOpen);
  }, [isOpen]);

  useEffect(() => {
    const modalElement = modalRef.current;

    if (modalElement) {
      if (isModalOpen) {
        modalElement.showModal();
      } else {
        modalElement.close();
      }
    }
  }, [isModalOpen]);

  let getCalData = () => {
    let authtoken = JSON.parse(sessionStorage.getItem("token")).token;
    fetch(Api.API_GET_ANALOG_CAL_STATS + "0", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + authtoken,
      },
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
        console.log(data);
        setFormState({
          stdDev: data.std_deviation,
          dvList: data.datapoints,
          meanVal: data.meanvalue,
        });
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };

  useEffect(() => {
    getCalData();
    const interval = setInterval(() => {
      getCalData();
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className="modalcal">
      {hasCloseBtn && (
        <button className="modal-close-btn" onClick={handleCloseModal}>
          <img src={closeCircle} alt="close" height="24px" width="24px"></img>
        </button>
      )}
      Calibrate: {ProbeName} <br></br>
      {ProbeID} <br></br>
      {SensorType} <br/>
      MeanVal: {formState.meanVal} <br/>
      StdDev: {formState.stdDev} <br/>
      <br></br>
      <CalChartWrapper probename={ProbeName}
       stdDev={formState.stdDev} 
       mean={formState.meanVal} 
       chartdata={formState.dvList}>

       </CalChartWrapper>
    </dialog>
  );
};

export default ProbeWidgetPhCal;
