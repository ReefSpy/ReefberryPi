import React, { useRef, useEffect, useState } from "react";
import "./ProbePrefsModal.css";
import closeCircle from "./close-circle.svg";

const ProbePrefsModal = ({
  isOpen,
  hasCloseBtn = true,
  onClose,
  children,
   onSubmit,
}) => {
    const [isModalOpen, setModalOpen] = useState(isOpen);
    const [formState, setFormState] = useState({});
    const [adc_enable_channel_0, set_adc_enable_channel_0] = useState();
    const [adc_enable_channel_1, set_adc_enable_channel_1] = useState();
    const [adc_enable_channel_2, set_adc_enable_channel_2] = useState();
    const [adc_enable_channel_3, set_adc_enable_channel_3] = useState();
    const [adc_enable_channel_4, set_adc_enable_channel_4] = useState();
    const [adc_enable_channel_5, set_adc_enable_channel_5] = useState();
    const [adc_enable_channel_6, set_adc_enable_channel_6] = useState();
    const [adc_enable_channel_7, set_adc_enable_channel_7] = useState();

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

  useEffect(()=>{
    fetch(process.env.REACT_APP_API_GET_MCP3008_ENABLE_STATE)
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
      for (let channel in data){
        console.log(data[channel])
        if (data[channel].probeid === "mcp3008_ch0"){
          set_adc_enable_channel_0(data[channel].enabled  === "true" ? true : false)
        }else if (data[channel].probeid === "mcp3008_ch1"){
          set_adc_enable_channel_1(data[channel].enabled  === "true" ? true : false)
        }else if (data[channel].probeid === "mcp3008_ch2"){
          set_adc_enable_channel_2(data[channel].enabled  === "true" ? true : false)
        }else if (data[channel].probeid === "mcp3008_ch3"){
          set_adc_enable_channel_3(data[channel].enabled === "true" ? true : false)
        }else if (data[channel].probeid === "mcp3008_ch4"){
          set_adc_enable_channel_4(data[channel].enabled  === "true" ? true : false)
        }else if (data[channel].probeid === "mcp3008_ch5"){
          set_adc_enable_channel_5(data[channel].enabled  === "true" ? true : false)
        }else if (data[channel].probeid === "mcp3008_ch6"){
          set_adc_enable_channel_6(data[channel].enabled  === "true" ? true : false)
        }else if (data[channel].probeid === "mcp3008_ch7"){
          set_adc_enable_channel_7(data[channel].enabled  === "true" ? true : false)
        }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
  }, [])

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
    submitForm({adc_enable_channel_0,
      adc_enable_channel_1,
      adc_enable_channel_2,
      adc_enable_channel_3,
      adc_enable_channel_4,
      adc_enable_channel_5,
      adc_enable_channel_6,
      adc_enable_channel_7})
   
      onSubmit(formState);
  };

   function submitForm(probestates) {

   console.log( JSON.stringify(probestates))

    return fetch(process.env.REACT_APP_API_SET_MCP3008_ENABLE_STATE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(probestates),
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
        return data;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  const handleInputChange = (event) => {
   
    const { name, value } = event.target;
    setFormState((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));

  };


  const handleInputChange0 = (event) => {
    set_adc_enable_channel_0(event.target.checked);
  };

  const handleInputChange1 = (event) => {
    set_adc_enable_channel_1(event.target.checked);
  };

  const handleInputChange2 = (event) => {
    set_adc_enable_channel_2(event.target.checked);
  };

  const handleInputChange3 = (event) => {
    set_adc_enable_channel_3(event.target.checked);
  };

  const handleInputChange4 = (event) => {
    set_adc_enable_channel_4(event.target.checked);
  };

  const handleInputChange5 = (event) => {
    set_adc_enable_channel_5(event.target.checked);
  };

  const handleInputChange6 = (event) => {
    set_adc_enable_channel_6(event.target.checked);
  };

  const handleInputChange7 = (event) => {
    set_adc_enable_channel_7(event.target.checked);
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
       
      {/* <div className="form-row">
          <label htmlFor="enableDHT">Enable DHT Sensor</label>
        </div>
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
       <br></br>
       
        <div className="form-row">
          <label>Analog to Digital Probes</label>
          
        </div> */}

        <div class="adcgridcontainer">
          <div class="adctitlelabel adccol1">MCP3008 ADC</div>
          <div class="adcchannelrow adccol1 adcchannel0" grid-row-start="2">
            channel 0
          </div>
          <div class="adcchannelrow adccol1 adcchannel1" grid-row-start="3">
          channel 1
          </div>
          <div class="adcchannelrow adccol1 adcchannel2" grid-row-start="4">
          channel 2
          </div>
          <div class="adcchannelrow adccol1 adcchannel3" grid-row-start="5">
          channel 3
          </div>
          <div class="adcchannelrow adccol1 adcchannel4" grid-row-start="6">
            channel 4
          </div>
          <div class="adcchannelrow adccol1 adcchannel5" grid-row-start="7">
          channel 5
          </div>
          <div class="adcchannelrow adccol1 adcchannel6" grid-row-start="8">
          channel 6
          </div>
          <div class="adcchannelrow adccol1 adcchannel7" grid-row-start="9">
          channel 7
          </div>

          <div class="adctitlelabel adccol2">Enable</div>

          <div class="adcchannelrow adccol2 adcchannel0" grid-row-start="2">
            <input
              type="checkbox"
              onChange={(event) => handleInputChange0(event)}
              id="adc_enable_channel_0"
              name="adc_enable_channel_0"
              checked = {adc_enable_channel_0 === true ? true : false}
            />
          </div>
          <div class="adcchannelrow adccol2 adcchannel1" grid-row-start="3">
            <input
              type="checkbox"
              onChange={(event) => handleInputChange1(event)}
              id="adc_enable_channel_1"
              name="adc_enable_channel_1"
              checked = {adc_enable_channel_1 === true ? true : false}
            />
          </div>
          <div class="adcchannelrow adccol2 adcchannel2" grid-row-start="4">
            <input
              type="checkbox"
              onChange={(event) => handleInputChange2(event)}
              id="adc_enable_channel_2"
              name="adc_enable_channel_2"
              checked = {adc_enable_channel_2 === true ? true : false}
            />
          </div>
          <div class="adcchannelrow adccol2 adcchannel3" grid-row-start="5">
            <input
              type="checkbox"
              onChange={(event) => handleInputChange3(event)}
              id="adc_enable_channel_3"
              name="adc_enable_channel_3"
              checked = {adc_enable_channel_3 === true ? true : false}
            />
          </div>
          <div class="adcchannelrow adccol2 adcchannel4" grid-row-start="6">
            <input
              type="checkbox"
              onChange={(event) => handleInputChange4(event)}
              id="adc_enable_channel_4"
              name="adc_enable_channel_4"
              checked = {adc_enable_channel_4 === true ? true : false}
            />
          </div>

          <div class="adcchannelrow adccol2 adcchannel5" grid-row-start="7">
            <input
              type="checkbox"
              onChange={(event) => handleInputChange5(event)}
              id="adc_enable_channel_5"
              name="adc_enable_channel_5"
              checked = {adc_enable_channel_5 === true ? true : false}
            />
          </div>

          <div class="adcchannelrow adccol2 adcchannel6" grid-row-start="8">
            <input
              type="checkbox"
              onChange={(event) => handleInputChange6(event)}
              id="adc_enable_channel_6"
              name="adc_enable_channel_6"
              checked = {adc_enable_channel_6 === true ? true : false}
              
            />
          </div>
          <div class="adcchannelrow adccol2 adcchannel7" grid-row-start="9">
            <input
              type="checkbox"
              onChange={(event) => handleInputChange7(event)}
              id="adc_enable_channel_7"
              name="adc_enable_channel_7"
              checked = {adc_enable_channel_7 === true ? true : false}
            />
          </div>
        </div>



        <div className="submit_row">
          <button type="submit" className="submitbutton">
            Submit
          </button>
        </div>
      </form>
    </dialog>
  );
};

export default ProbePrefsModal;
