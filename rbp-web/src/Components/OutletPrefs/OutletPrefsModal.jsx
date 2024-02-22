import React, { useRef, useEffect, useState } from "react";
import "./OutletPrefsModal.css";
import closeCircle from "./close-circle.svg";

const OutletPrefsModal = ({
  isOpen,
  hasCloseBtn = true,
  onClose,
  children,
  onSubmit,
}) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);
  const [formState, setFormState] = useState({});
  const [enable_int_outlet_1, set_enable_int_outlet_1] = useState();
  const [enable_int_outlet_2, set_enable_int_outlet_2] = useState();
  const [enable_int_outlet_3, set_enable_int_outlet_3] = useState();
  const [enable_int_outlet_4, set_enable_int_outlet_4] = useState();
  const [enable_int_outlet_5, set_enable_int_outlet_5] = useState();
  const [enable_int_outlet_6, set_enable_int_outlet_6] = useState();
  const [enable_int_outlet_7, set_enable_int_outlet_7] = useState();
  const [enable_int_outlet_8, set_enable_int_outlet_8] = useState();

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
    fetch(process.env.REACT_APP_API_GET_OUTLET_ENABLE_STATE)
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
        for (let outlet in data) {
          console.log(data[outlet]);
          if (data[outlet].outletid === "int_outlet_1") {
            set_enable_int_outlet_1(
              data[outlet].enabled === "true" ? true : false
            );
          } else if (data[outlet].outletid === "int_outlet_2") {
            set_enable_int_outlet_2(
              data[outlet].enabled === "true" ? true : false
            );
          } else if (data[outlet].outletid === "int_outlet_3") {
            set_enable_int_outlet_3(
              data[outlet].enabled === "true" ? true : false
            );
          } else if (data[outlet].outletid === "int_outlet_4") {
            set_enable_int_outlet_4(
              data[outlet].enabled === "true" ? true : false
            );
          } else if (data[outlet].outletid === "int_outlet_5") {
            set_enable_int_outlet_5(
              data[outlet].enabled === "true" ? true : false
            );
          } else if (data[outlet].outletid === "int_outlet_6") {
            set_enable_int_outlet_6(
              data[outlet].enabled === "true" ? true : false
            );
          } else if (data[outlet].outletid === "int_outlet_7") {
            set_enable_int_outlet_7(
              data[outlet].enabled === "true" ? true : false
            );
          } else if (data[outlet].outletid === "int_outlet_8") {
            set_enable_int_outlet_8(
              data[outlet].enabled === "true" ? true : false
            );
          }
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }, []);

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
    submitForm({
      enable_int_outlet_1,
      enable_int_outlet_2,
      enable_int_outlet_3,
      enable_int_outlet_4,
      enable_int_outlet_5,
      enable_int_outlet_6,
      enable_int_outlet_7,
      enable_int_outlet_8,
    });

    onSubmit(formState);
  };

  function submitForm(outletstates) {
    console.log(JSON.stringify(outletstates));

    return fetch(process.env.REACT_APP_API_SET_OUTLET_ENABLE_STATE, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(outletstates),
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

//   const handleInputChange = (event) => {
//     const { name, value } = event.target;
//     setFormState((prevFormData) => ({
//       ...prevFormData,
//       [name]: value,
//     }));
//   };

  const handleInputChange1 = (event) => {
    set_enable_int_outlet_1(event.target.checked);
  };

  const handleInputChange2 = (event) => {
    set_enable_int_outlet_2(event.target.checked);
  };

  const handleInputChange3 = (event) => {
    set_enable_int_outlet_3(event.target.checked);
  };

  const handleInputChange4 = (event) => {
    set_enable_int_outlet_4(event.target.checked);
  };

  const handleInputChange5 = (event) => {
    set_enable_int_outlet_5(event.target.checked);
  };

  const handleInputChange6 = (event) => {
    set_enable_int_outlet_6(event.target.checked);
  };

  const handleInputChange7 = (event) => {
    set_enable_int_outlet_7(event.target.checked);
  };

  const handleInputChange8 = (event) => {
    set_enable_int_outlet_8(event.target.checked);
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
        <div class="outletgridcontainer">
          <div class="outlettitlelabel outletcol1">Outlet Number</div>
          <div
            class="outletchannelrow outletcol1 outletchannel1"
            grid-row-start="2"
          >
            Outlet 1
          </div>
          <div
            class="outletchannelrow outletcol1 outletchannel2"
            grid-row-start="3"
          >
            Outlet 2
          </div>
          <div
            class="outletchannelrow outletcol1 outletchannel3"
            grid-row-start="4"
          >
            Outlet 3
          </div>
          <div
            class="outletchannelrow outletcol1 outletchannel4"
            grid-row-start="5"
          >
            Outlet 4
          </div>
          <div
            class="outletchannelrow outletcol1 outletchannel5"
            grid-row-start="6"
          >
            Outlet 5
          </div>
          <div
            class="outletchannelrow outletcol1 outletchannel6"
            grid-row-start="7"
          >
            Outlet 6
          </div>
          <div
            class="outletchannelrow outletcol1 outletchannel7"
            grid-row-start="8"
          >
            Outlet 7
          </div>
          <div
            class="outletchannelrow outletcol1 outletchannel8"
            grid-row-start="9"
          >
            Outlet 8
          </div>

          <div class="outlettitlelabel outletcol2">Enable</div>

          <div
            class="outletchannelrow outletcol2 outletchannel1"
            grid-row-start="2"
          >
            <input
              type="checkbox"
              onChange={(event) => handleInputChange1(event)}
              id="enable_int_outlet_1"
              name="enable_int_outlet_1"
              checked={enable_int_outlet_1 === true ? true : false}
            />
          </div>
          <div
            class="outletchannelrow outletcol2 outletchannel2"
            grid-row-start="3"
          >
            <input
              type="checkbox"
              onChange={(event) => handleInputChange2(event)}
              id="enable_int_outlet_2"
              name="enable_int_outlet_2"
              checked={enable_int_outlet_2 === true ? true : false}
            />
          </div>
          <div
            class="outletchannelrow outletcol2 outletchannel3"
            grid-row-start="4"
          >
            <input
              type="checkbox"
              onChange={(event) => handleInputChange3(event)}
              id="enable_int_outlet_3"
              name="enable_int_outlet_3"
              checked={enable_int_outlet_3 === true ? true : false}
            />
          </div>
          <div
            class="outletchannelrow outletcol2 outletchannel4"
            grid-row-start="5"
          >
            <input
              type="checkbox"
              onChange={(event) => handleInputChange4(event)}
              id="enable_int_outlet_4"
              name="enable_int_outlet_4"
              checked={enable_int_outlet_4 === true ? true : false}
            />
          </div>
          <div
            class="outletchannelrow outletcol2 outletchannel5"
            grid-row-start="6"
          >
            <input
              type="checkbox"
              onChange={(event) => handleInputChange5(event)}
              id="enable_int_outlet_5"
              name="enable_int_outlet_5"
              checked={enable_int_outlet_5 === true ? true : false}
            />
          </div>

          <div
            class="outletchannelrow outletcol2 outletchannel6"
            grid-row-start="7"
          >
            <input
              type="checkbox"
              onChange={(event) => handleInputChange6(event)}
              id="enable_int_outlet_6"
              name="enable_int_outlet_6"
              checked={enable_int_outlet_6 === true ? true : false}
            />
          </div>

          <div
            class="outletchannelrow outletcol2 outletchannel7"
            grid-row-start="8"
          >
            <input
              type="checkbox"
              onChange={(event) => handleInputChange7(event)}
              id="enable_int_outlet_7"
              name="enable_int_outlet_7"
              checked={enable_int_outlet_7 === true ? true : false}
            />
          </div>
          <div
            class="outletchannelrow outletcol2 outletchannel8"
            grid-row-start="9"
          >
            <input
              type="checkbox"
              onChange={(event) => handleInputChange8(event)}
              id="enable_int_outlet_8"
              name="enable_int_outlet_8"
              checked={enable_int_outlet_8 === true ? true : false}
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

export default OutletPrefsModal;
