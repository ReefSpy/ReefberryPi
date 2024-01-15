import React, { useRef, useEffect, useState } from "react";
import "./OutletWidget.css";
import closeCircle from "./close-circle.svg";

const initialOutletPrefsModalData = {
  outletname: "",
  outletid: "",
  controlType: ""
};

const OutletWidgetModal = ({
  onSubmit,
  isOpen,
  hasCloseBtn = true,
  onClose,
  OutletName,
  OutletID,
  ControlType

}) => {
  initialOutletPrefsModalData.controlType = ControlType
  initialOutletPrefsModalData.outletid = OutletID
  initialOutletPrefsModalData.outletname = OutletName
  
  const [isModalOpen, setModalOpen] = useState(isOpen);
  const modalRef = useRef(null);
  const [formState, setFormState] = useState(initialOutletPrefsModalData);
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
    setFormState(initialOutletPrefsModalData);
    formRef.current.reset();
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormState((prevFormData) => ({
      ...prevFormData,
      [name]: value, outletid: OutletID,
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
          <label htmlFor="outletname">Outlet Name</label>
          <input
            ref={focusInputRef}
            type="text"
            id="outletname"
            name="outletname"
            Value={OutletName}
            autocomplete="off"
            onChange={handleInputChange}
            required
            placeholder="Unnamed"
          />
        </div>

        <div className="form-row">
          <label htmlFor="outletid">Outlet ID</label>
          <span className="plainlabel">{OutletID}</span>
        </div>

        <div className="form-row">
          <label htmlFor="controlType">Control Type</label>
          <select
            className="controltype"
            id="controlType"
            name="controlType"
            value={formState.controlType}
            onChange={handleInputChange}
            required
          >
            <option value="Always">Always</option>
            <option value="Light">Light</option>
            <option value="Heater">Heater</option>
            <option value="Skimmer">Skimmer</option>
            <option value="Return">Return</option>
            <option value="PH">PH</option>
          </select>
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

export default OutletWidgetModal;
