import React, { useRef, useEffect, useState } from "react";
import "./AddUserModal.css";
import closeCircle from "./close-circle.svg";

import ClipLoader from "react-spinners/ClipLoader";
import * as Api from "../Api/Api.js";

const AddUserModal = ({
  isOpen,
  hasCloseBtn = true,
  onClose,
  children,
  onRefreshRequest,
}) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);
  const focusInputRef = useRef(null);
  const [formState, setFormState] = useState({username: "",
                                              password: "",
                                              confirmpassord: ""});
 

 

  const modalRef = useRef(null);

  const handleCloseModal = () => {
    if (onClose) {
      onClose();
    }
    setModalOpen(false);
  };

  const handleKeyDown = (event) => {
    console.log(event.key)
    if (event.key === "Escape") {
       handleCloseModal();
    }
    if (event.code === 'Space') 
    {event.preventDefault()}
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

  let handleSubmitClick = () => {

    if(formState.username === ""){
      alert ("User name can not be empty.")
      return
    } 

    if(formState.password === ""){
        alert ("Password can not be empty.")
        return
      } 

    if(formState.password !== formState.confirmpassword){
      alert ("Password mismatch!")
      return
    } 


    let authtoken = JSON.parse(sessionStorage.getItem("token")).token;
    fetch(Api.API_SET_ADD_USER, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + authtoken,
      },
      body: JSON.stringify( {username: formState.username,
      password: formState.password,
    })
    })
      .then((response) => {
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error("Data not found");
          } else if (response.status === 500) {
            alert("Error adding user.")
            throw new Error("Server error");
          } else if (response.status === 401){
            alert("Unathorized.  Check password and try again.")
            throw new Error("Unauthorized access.")
          }
         else if (response.status === 5000) {
            throw new Error("Server error");
          }
          
           else {
            throw new Error("Network response was not ok");
          }
        }
        return response.json();
      })
      .then((data) => {
       alert("User added successfully.")
       handleCloseModal()
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  


  const handleInputChange = (event) => {


    const { name, value } = event.target;
    setFormState((prevFormData) => ({
      ...prevFormData,
      [name]: value.replace(" ", ""),
    }));
  };

  


  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className="addusermodal">
      {hasCloseBtn && (
        <button className="modal-close-btn" onClick={handleCloseModal}>
          <img src={closeCircle} alt="close" height="24px" width="24px"></img>
        </button>
      )}
      {children}
      <div className="addusercontainer">
      
        <label className="userNameLabel">User Name</label>
        <input 
        ref={focusInputRef}
        onChange={handleInputChange}
            className="userName"
          // type="password"
            id="username"
            name="username"
            autoComplete="off"
            onKeyDown={handleKeyDown}
          />

<label className="newPasswordLabel">New Password</label>
        <input 
        ref={focusInputRef}
        onChange={handleInputChange}
            className="newPassword"
            type="password"
            id="password"
            name="password"
            autoComplete="off"
          />

<label className="newPasswordConfirmLabel">Password Confirm</label>
        <input 
        ref={focusInputRef}
        onChange={handleInputChange}
            className="newPasswordConfirm"
            type="password"
            id="confirmpassword"
            name="confirmpassword"
            autoComplete="off"
          />

      </div>

      
      <div className="adduserbtncontainer">
      <button
          className="adduserbtncancel"
          onClick={handleCloseModal}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="adduserbtnsubmit"
          onClick={handleSubmitClick}
        >
          Submit
        </button>
      </div>
    </dialog>
  );
};

export default AddUserModal;
