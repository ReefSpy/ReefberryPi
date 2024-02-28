import React, { useRef, useEffect, useState } from "react";
import "./TempPrefsModal.css";
import closeCircle from "./close-circle.svg";
import rightArrow from "./right-arrow.svg"
import deleteIcon from "./delete.svg"

const TempPrefsModal = ({ isOpen, hasCloseBtn = true, onClose, children }) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);
  const [selectedConnectedProbe, setSelectedConnectedProbe] = useState();
  const [connectedProbesList, setConnectedProbesList] = useState([]);
  const [probeID1, setProbeID1] = useState("Unassigned");
  const [probeID2, setProbeID2] = useState("Unassigned");
  const [probeID3, setProbeID3] = useState("Unassigned");
  const [probeID4, setProbeID4] = useState("Unassigned");

  const modalRef = useRef(null);

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

  let handleConnectedProbesChange = (event) => {
    setSelectedConnectedProbe(event.target.value);
  };

  useEffect(() => {
    fetch(process.env.REACT_APP_API_GET_CONNECTED_TEMP_PROBES)
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
        setConnectedProbesList(data);
        for (let probe in data) {
          console.log(data[probe]);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }, []);

  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className="tempmodal">
      {hasCloseBtn && (
        <button className="modal-close-btn" onClick={handleCloseModal}>
          <img src={closeCircle} alt="close" height="24px" width="24px"></img>
        </button>
      )}
      {children}
      <div className="probescontainer">
        <label htmlFor="connectedprobes" classname = "detectedlabel">Detected Probes</label>
        <select
          className="connectedProbes"
          id="connectedProbes"
          name="connectedProbes"
          required
          onChange={handleConnectedProbesChange}
          value={selectedConnectedProbe}
          size="6"
          
        >
          {connectedProbesList.map((tempProbe, index) => (
            <option key={index} value={tempProbe}>
              {tempProbe}
            </option>
          ))}
        </select>

        <button className="probe1btn">Assign Probe 1 <img src={rightArrow} alt="arrow" className="righticon"></img></button>
        <button className="probe2btn">Assign Probe 2 <img src={rightArrow} alt="arrow" className="righticon"></img></button>
        <button className="probe3btn">Assign Probe 3 <img src={rightArrow} alt="arrow" className="righticon"></img></button>
        <button className="probe4btn">Assign Probe 4 <img src={rightArrow} alt="arrow" className="righticon"></img></button>

        <label className="probe1lbl">{probeID1}</label>
        <label className="probe2lbl">{probeID2}</label>
        <label className="probe3lbl">{probeID3}</label>
        <label className="probe4lbl">{probeID4}</label>

        <button className="del1btn"><img src={deleteIcon} alt="delete" className="delicon"></img></button>
        <button className="del2btn"><img src={deleteIcon} alt="delete" className="delicon"></img></button>
        <button className="del3btn"><img src={deleteIcon} alt="delete" className="delicon"></img></button>
        <button className="del4btn"><img src={deleteIcon} alt="delete" className="delicon"></img></button>

      </div>
    </dialog>
  );
};

export default TempPrefsModal;
