import React, { useRef, useEffect, useState } from "react";
import "./OutletWidget.css";
import closeCircle from "./close-circle.svg";
import PrefPaneContainer from "./PrefPaneContainer";

const initialOutletPrefsModalData = {
  outletname: "",
  outletid: "",
  controlType: "",
  selectedIndex: 0
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

  const handleSelectionChange = (event) => {
    console.log("Selection changed");
    console.log(event.target.value);
    // this.setState({ selectedIndex: Number(event.target.value) });
    setFormState((prevFormData) => ({
      ...prevFormData,
      selectedIndex: Number(event.target.value)
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
              onChange={handleSelectionChange}
              required
            >
              <option value="0">Always</option>
              <option value="1">Light</option>
              <option value="2">Heater</option>
              <option value="3">Skimmer</option>
              <option value="4">Return</option>
              <option value="5">PH</option>
            </select>
        </div>

      
        
      </form>

      <PrefPaneContainer data = {formState}></PrefPaneContainer>
    </dialog>
  );
};

export default OutletWidgetModal;
