import React, { useState, useEffect, useRef } from 'react';
import './ProbeWidget.css';
import Modal from '../Modal/Modal';

const initialProbePrefsModalData = {
    probename: 'Hello',
    probeid: '123456'
  };
  
  const ProbePrefsModal = ({ onSubmit, isOpen, onClose, ProbeName, ProbeID }) => {
    const focusInputRef = useRef(null);
    const [formState, setFormState] = useState(initialProbePrefsModalData);

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
              value={ProbeName}
              onChange={handleInputChange}
              required
              placeholder="Unnamed"
            />
          </div>
          
          <div className="form-row">
          <label htmlFor="probeid">Probe ID</label>
           
            <input
              ref={focusInputRef}
              type="text"
              id="probeid"
              name="probeid"
              value={ProbeID}
              onChange={handleInputChange}
              required
              placeholder="Unnamed"
            />
             </div>
          <div className="form-row">
            <button type="submit" className="submitbutton">Submit</button>
          </div>
        </form>
      </Modal>

    );
  };
  
  export default ProbePrefsModal;