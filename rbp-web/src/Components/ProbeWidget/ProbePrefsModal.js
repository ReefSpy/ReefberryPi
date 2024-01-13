import React, { useState, useEffect, useRef } from "react";
import "./ProbeWidget.css";
import Modal from "../Modal/Modal";

const initialProbePrefsModalData = {
  probename: "Hello",
  probeid: "123456",
};

const ProbePrefsModal = ({ onSubmit, isOpen, onClose, ProbeName, ProbeID, SensorType }) => {
  const focusInputRef = useRef(null);
  const [formState, setFormState] = useState(initialProbePrefsModalData);
  const [prefsProbeName, setPrefsProbeName] = useState(ProbeName);

  useEffect(() => {
    if (isOpen && focusInputRef.current) {
      setTimeout(() => {
        focusInputRef.current.focus();
      }, 0);
    }
  }, [isOpen]);

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormState((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(formState);
    setFormState(initialProbePrefsModalData);
  };

  return (
    <Modal hasCloseBtn={true} isOpen={isOpen} onClose={onClose}>
      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <label htmlFor="probename">Probe Name</label>
          <input
            ref={focusInputRef}
            type="text"
            id="probename"
            name="probename"
            defaultValue={prefsProbeName}
            autocomplete="off"
            onChange={handleInputChange}
            required
            placeholder="Unnamed"
          />
        </div>

        <div className="form-row">
          <label htmlFor="probeid">Probe ID</label>
          <span className="plainlabel">{ProbeID}</span>
        </div>

        <div className="form-row">
          <label htmlFor="probeid">Sensor Type</label>
          <span className="plainlabel">{SensorType}</span>
        </div>

        <div className="form-row">
          <button type="submit" className="submitbutton">
            Submit
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default ProbePrefsModal;
