import React, { useRef, useEffect, useState } from "react";
import "./TempPrefsModal.css";
import closeCircle from "./close-circle.svg";
import rightArrow from "./right-arrow.svg";
import deleteIcon from "./delete.svg";
import ClipLoader from "react-spinners/ClipLoader";

const TempPrefsModal = ({ isOpen, hasCloseBtn = true, onClose, children }) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);
  const [selectedConnectedProbe, setSelectedConnectedProbe] = useState();
  const [connectedProbesList, setConnectedProbesList] = useState([]);
  const [probeID1, setProbeID1] = useState();
  const [probeID2, setProbeID2] = useState();
  const [probeID3, setProbeID3] = useState();
  const [probeID4, setProbeID4] = useState();

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

  let handleProbeID1Click = () => {
    if (selectedConnectedProbe !== undefined) {
      setProbeID1(selectedConnectedProbe);
      // const index = connectedProbesList.indexOf(selectedConnectedProbe);
      // const x = connectedProbesList.splice(index, 1);
      // console.log(index)
      // console.log (index)
    }
  };

  let handleProbeID2Click = () => {
    if (selectedConnectedProbe !== undefined) {
      setProbeID2(selectedConnectedProbe);
    }
  };

  let handleProbeID3Click = () => {
    if (selectedConnectedProbe !== undefined) {
      setProbeID3(selectedConnectedProbe);
    }
  };

  let handleProbeID4Click = () => {
    if (selectedConnectedProbe !== undefined) {
      setProbeID4(selectedConnectedProbe);
    }
  };

  let deleteProbeID1Click = () => {
    setProbeID1("");
  };

  let deleteProbeID2Click = () => {
    setProbeID2("");
  };

  let deleteProbeID3Click = () => {
    setProbeID3("");
  };

  let deleteProbeID4Click = () => {
    setProbeID4("");
  };

  let handleSubmitClick = () => {
    let probeList = { probeID1, probeID2, probeID3, probeID4 };
    console.log(probeList);

    console.log(JSON.stringify(probeList));
    if (window.confirm("Are you sure you want to save changes?")){
    return fetch(process.env.REACT_APP_API_SET_CONNECTED_TEMP_PROBE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(probeList),
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
        alert("Settings saved successfully");
        // window.location.reload(false);
        return data;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
    }
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

  useEffect(() => {
    fetch(process.env.REACT_APP_API_GET_ASSIGNED_TEMP_PROBES)
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
        for (let probe in data) {
          console.log(data[probe]);
          if (data[probe].temp_probe_1 && data[probe].temp_probe_1 !== "none") {
            console.log(data[probe].temp_probe_1);
            setProbeID1(data[probe].temp_probe_1);
          }
          if (data[probe].temp_probe_2 && data[probe].temp_probe_2 !== "none") {
            console.log(data[probe].temp_probe_2);
            setProbeID2(data[probe].temp_probe_2);
          }
          if (data[probe].temp_probe_3 && data[probe].temp_probe_3 !== "none") {
            console.log(data[probe].temp_probe_3);
            setProbeID3(data[probe].temp_probe_3);
          }
          if (data[probe].temp_probe_4 && data[probe].temp_probe_4 !== "none") {
            console.log(data[probe].temp_probe_4);
            setProbeID4(data[probe].temp_probe_4);
          }
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
        <label htmlFor="connectedprobes" className="detectedlabel">
          Detected Probes
        </label>
        <label htmlFor="connectedprobes2" className="detectedlabel2">
          Assigned Probes
        </label>
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

        <button className="probe1btn" onClick={handleProbeID1Click}>
          Assign Probe 1{" "}
          <img src={rightArrow} alt="arrow" className="righticon"></img>
        </button>
        <button className="probe2btn" onClick={handleProbeID2Click}>
          Assign Probe 2{" "}
          <img src={rightArrow} alt="arrow" className="righticon"></img>
        </button>
        <button className="probe3btn" onClick={handleProbeID3Click}>
          Assign Probe 3{" "}
          <img src={rightArrow} alt="arrow" className="righticon"></img>
        </button>
        <button className="probe4btn" onClick={handleProbeID4Click}>
          Assign Probe 4{" "}
          <img src={rightArrow} alt="arrow" className="righticon"></img>
        </button>

        <label className="probe1lbl">{probeID1 ? probeID1 : "Undefined"}</label>
        <label className="probe2lbl">{probeID2 ? probeID2 : "Undefined"}</label>
        <label className="probe3lbl">{probeID3 ? probeID3 : "Undefined"}</label>
        <label className="probe4lbl">{probeID4 ? probeID4 : "Undefined"}</label>

        <button className="del1btn delbtn" onClick={deleteProbeID1Click}>
          <img src={deleteIcon} alt="delete" className="delicon"></img>
        </button>
        <button className="del2btn delbtn" onClick={deleteProbeID2Click}>
          <img src={deleteIcon} alt="delete" className="delicon"></img>
        </button>
        <button className="del3btn delbtn" onClick={deleteProbeID3Click}>
          <img src={deleteIcon} alt="delete" className="delicon"></img>
        </button>
        <button className="del4btn delbtn" onClick={deleteProbeID4Click}>
          <img src={deleteIcon} alt="delete" className="delicon"></img>
        </button>
      </div>
      <div className="submit_row">
        <button
          type="submit"
          className="submitbutton"
          onClick={handleSubmitClick}
        >
          Submit
        </button>
      </div>
    </dialog>
  );
};

export default TempPrefsModal;
