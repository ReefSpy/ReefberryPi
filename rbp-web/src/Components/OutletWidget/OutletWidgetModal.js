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
    // formRef.current.reset();
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
      let apiURL =
        process.env.REACT_APP_API_SET_OUTLET_PARAMS_HEATER.concat(OutletID);

      console.log(probearray[event.target.tempProbe.selectedIndex].probeid);
      console.log(event.target.tempProbe.selectedIndex);
      let payload = {
        outletname: event.target.outletname.value,
        outletid: OutletID,
        control_type: formState.controlType,
        heater_on: event.target.temp_on.value,
        heater_off: event.target.temp_off.value,
        heater_probe: probearray[event.target.tempProbe.selectedIndex].probeid,
      };
      apiCall(apiURL, payload);
    }
    // skimmer
    else if (formState.controlType === "Skimmer") {
      let apiURL =
      process.env.REACT_APP_API_SET_OUTLET_PARAMS_SKIMMER.concat(OutletID);

    let payload = {
      outletname: event.target.outletname.value,
      outletid: OutletID,
      control_type: formState.controlType,
      skimmer_enable_feed_a: String(event.target.skimmer_enable_feed_a.checked),
      skimmer_enable_feed_b: String(event.target.skimmer_enable_feed_b.checked),
      skimmer_enable_feed_c: String(event.target.skimmer_enable_feed_c.checked),
      skimmer_enable_feed_d: String(event.target.skimmer_enable_feed_d.checked),
      skimmer_feed_delay_a: event.target.skimmer_feed_delay_a.value,
      skimmer_feed_delay_b: event.target.skimmer_feed_delay_b.value,
      skimmer_feed_delay_c: event.target.skimmer_feed_delay_c.value,
      skimmer_feed_delay_d: event.target.skimmer_feed_delay_d.value,

    };
    apiCall(apiURL, payload);
    }
    // return
    else if (formState.controlType === "Return") {
      let apiURL =
        process.env.REACT_APP_API_SET_OUTLET_PARAMS_RETURN.concat(OutletID);

      let payload = {
        outletname: event.target.outletname.value,
        outletid: OutletID,
        control_type: formState.controlType,
        return_enable_feed_a: String(event.target.return_enable_feed_a.checked),
        return_enable_feed_b: String(event.target.return_enable_feed_b.checked),
        return_enable_feed_c: String(event.target.return_enable_feed_c.checked),
        return_enable_feed_d: String(event.target.return_enable_feed_d.checked),
        return_feed_delay_a: event.target.return_feed_delay_a.value,
        return_feed_delay_b: event.target.return_feed_delay_b.value,
        return_feed_delay_c: event.target.return_feed_delay_c.value,
        return_feed_delay_d: event.target.return_feed_delay_d.value,

      };
      apiCall(apiURL, payload);
    }
    // PH
    else if (formState.controlType === "PH") {
      let apiURL =
        process.env.REACT_APP_API_SET_OUTLET_PARAMS_PH.concat(OutletID);

      let payload = {
        outletname: event.target.outletname.value,
        outletid: OutletID,
        control_type: formState.controlType,
        ph_low: event.target.ph_low.value,
        ph_high: event.target.ph_high.value,
        ph_onwhen: event.target.onWhen.value,
        ph_probe: probearray[event.target.phProbe.selectedIndex].probeid,

      }
      console.log(payload)
      apiCall(apiURL, payload);
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

    </dialog>
  );
};

export default OutletWidgetModal;
