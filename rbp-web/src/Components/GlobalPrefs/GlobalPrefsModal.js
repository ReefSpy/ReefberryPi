import React, { useRef, useEffect, useState } from "react";
import "./GlobalPrefsModal.css";
import closeCircle from "./close-circle.svg";

const GlobalPrefsModal = ({
  isOpen,
  hasCloseBtn = true,
  onClose,
  children,
  onSubmit,
  globalTempScale,
  globalPrefs,
}) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);
  const [formState, setFormState] = useState({enableDHT: globalPrefs.dht_enable, tempScale: globalPrefs.tempscale});

  const modalRef = useRef(null);

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


  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormState((prevFormData) => ({
        ...prevFormData,
        [name]: value
    }))
  };


  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(formState);

  };

  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className="modal">
      {hasCloseBtn && (
        <button className="modal-close-btn" onClick={handleCloseModal}>
          <img src={closeCircle} alt="close" height="24px" width="24px"></img>
        </button>
      )}
      {children}
      <form onSubmit={handleSubmit} ref={modalRef}>
        <div className="form-row">
          <label htmlFor="appuid">Application UID</label>
          <span className="plainlabel">{globalPrefs.appuid}</span>
        </div>

        <div className="form-row">
          <label htmlFor="tempScale">Temperature Scale</label>
        </div>
        <div onChange={(event) => handleInputChange(event)} >
          <input
            type="radio"
            id="tempScale"
            name="tempScale"
            value="F"
            checked={formState.tempScale === "F" ? true : null}
          />

          <label htmlFor="tempscale">F</label>

          <input
            type="radio"
            id="tempScale"
            name="tempScale"
            value="C"
            checked={formState.tempScale === "C" ? true : null}
          />
          <label htmlFor="tempscale">C</label>
        </div>

        <div className="form-row"> <label htmlFor="enableDHT">Enable DHT Sensor</label></div>
        <div onChange={(event) => handleInputChange(event)}>
          <input
            type="radio"
            id="enableDHT"
            name="enableDHT"
            value="true"
             checked={formState.enableDHT === "true" ? true : null}
          />

          <label htmlFor="enableDHT">ON</label>

          <input
            type="radio"
            id="enableDHT"
            name="enableDHT"
            value="false"
             checked={formState.enableDHT === "false" ? true : null}
          />
          <label htmlFor="enableDHT">OFF</label>
        </div>

        <div className="submit_row" >
          <button type="submit" className="submitbutton">
            Submit
          </button>
        </div>
      </form>

    </dialog>
  );
};

export default GlobalPrefsModal;
