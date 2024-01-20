import React, { useRef, useEffect, useState } from "react";
import "./OutletWidget.css";
import closeCircle from "./close-circle.svg";
import PrefPaneContainer from "./PrefPaneContainer";

const initialOutletPrefsModalData = {
  outletname: "",
  outletid: "",
  controlType: "",
  selectedIndex: 0,
};

const OutletWidgetModal = ({
  onSubmit,
  isOpen,
  hasCloseBtn = true,
  onClose,
  OutletName,
  OutletID,
  ControlType,
  data,
  probearray,
}) => {
  initialOutletPrefsModalData.controlType = ControlType;
  initialOutletPrefsModalData.outletid = OutletID;
  initialOutletPrefsModalData.outletname = OutletName;

  const getIndex = () => {
    if (ControlType === "Always") {
      initialOutletPrefsModalData.selectedIndex = 0;
    } else if (ControlType === "Light") {
      initialOutletPrefsModalData.selectedIndex = 1;
    } else if (ControlType === "Heater") {
      initialOutletPrefsModalData.selectedIndex = 2;
    } else if (ControlType === "Skimmer") {
      initialOutletPrefsModalData.selectedIndex = 3;
    } else if (ControlType === "Return") {
      initialOutletPrefsModalData.selectedIndex = 4;
    } else if (ControlType === "PH") {
      initialOutletPrefsModalData.selectedIndex = 5;
    }
  };

  getIndex();

  const [isModalOpen, setModalOpen] = useState(isOpen);
  const modalRef = useRef(null);
  const [formState, setFormState] = useState(initialOutletPrefsModalData);
  const focusInputRef = useRef(null);
  const formRef = useRef(null);

  const handleCloseModal = () => {
    if (onClose) {
      onClose();
      getIndex();
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
    console.log("Modal Open: ".concat(OutletID).concat(" ").concat(OutletName));
    setFormState(initialOutletPrefsModalData);
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
    console.log(formState.controlType);
    // setFormState(initialOutletPrefsModalData);
    //formRef.current.reset();
    console.log("Form Submit");
    console.log(event.target.outletname.value);
    console.log(OutletID);
    // always
    if (formState.controlType === "Always") {
      // console.log(event.target.always_state.value);
      let apiURL =
        process.env.REACT_APP_API_SET_OUTLET_PARAMS_ALWAYS.concat(OutletID);
      let payload = {
        outletname: event.target.outletname.value,
        control_type: formState.controlType,
        outletid: OutletID,
        always_state: event.target.always_state.value,
      };
      apiCall(apiURL, payload);
    }
    // light
    else if (formState.controlType === "Light") {
      let apiURL =
        process.env.REACT_APP_API_SET_OUTLET_PARAMS_LIGHT.concat(OutletID);
      let payload = {
        outletname: event.target.outletname.value,
        outletid: OutletID,
        control_type: formState.controlType,
        light_on: event.target.time_on.value,
        light_off: event.target.time_off.value,
      };
      apiCall(apiURL, payload);
    }
    // heater
    else if (formState.controlType === "Heater") {
    }
    // skimmer
    else if (formState.controlType === "Skimmer") {
    }
    // return
    else if (formState.controlType === "Return") {
    }
    // PH
    else if (formState.controlType === "PH") {
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormState((prevFormData) => ({
      ...prevFormData,
      [name]: value,
      outletid: OutletID,
    }));
  };

  const handleSelectionChange = (event) => {
    console.log("Selection changed");
    console.log(event.target.value);
    // this.setState({ selectedIndex: Number(event.target.value) });
    setFormState((prevFormData) => ({
      ...prevFormData,
      selectedIndex: Number(event.target.value),
      controlType: event.target[event.target.value].text,
    }));
  };

  // API call structure
  const apiCall = (endpoint, newdata) => {
    fetch(endpoint, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newdata),
    })
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.log(error));
  };

  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className="outletmodal">
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
            value={formState.selectedIndex}
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
        <PrefPaneContainer
          data={data}
          selectedTab={formState.selectedIndex}
          probearray={probearray}
          isOpen={isOpen}
        ></PrefPaneContainer>
        <div className="submit_row">
          <button type="submit" className="submitbutton">
            Submit
          </button>
        </div>
      </form>

      {/* <PrefPaneContainer data={formState}></PrefPaneContainer> */}
    </dialog>
  );
};

export default OutletWidgetModal;
