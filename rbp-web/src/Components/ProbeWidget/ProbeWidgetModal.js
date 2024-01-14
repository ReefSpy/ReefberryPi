import React, { useRef, useEffect, useState } from "react";
import "./ProbeWidgetModal.css";
import closeCircle from "./close-circle.svg";

const initialProbePrefsModalData = {
  probename: "",
  probeid: "",
};

const ProbeWidgetModal = ({
  onSubmit,
  isOpen,
  hasCloseBtn = true,
  onClose,
  ProbeName,
  ProbeID,
  SensorType,
}) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);
  const modalRef = useRef(null);
  const [formState, setFormState] = useState(initialProbePrefsModalData);
  const focusInputRef = useRef(null);
  const formRef = useRef(null);


  const handleCloseModal = () => {
    if (onClose) {
      onClose();
      formRef.current.reset();
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

  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(formState);
    setFormState(initialProbePrefsModalData);
    formRef.current.reset();
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormState((prevFormData) => ({
      ...prevFormData,
      [name]: value, probeid: ProbeID,
    }));

  };

  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className="modal">
      {hasCloseBtn && (
        <button className="modal-close-btn" onClick={handleCloseModal}>
          <img src={closeCircle} alt="close" height="24px" width="24px"></img>
        </button>
      )}
      <form onSubmit={handleSubmit} ref={formRef}>
        <div className="form-row">
          <label htmlFor="probename">Probe Name</label>
          <input
            ref={focusInputRef}
            type="text"
            id="probename"
            name="probename"
            Value={ProbeName}
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
    </dialog>
  );
};

export default ProbeWidgetModal;
