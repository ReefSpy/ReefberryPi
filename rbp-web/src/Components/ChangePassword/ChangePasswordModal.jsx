import React, { useRef, useEffect, useState } from "react";
import "./ChangePasswordModal.css";
import closeCircle from "./close-circle.svg";
import deleteIcon from "./delete.svg";
import userAddIcon from "./user-add.svg";
import keyIcon from "./key.svg";
import ClipLoader from "react-spinners/ClipLoader";
import * as Api from "../Api/Api.js";

const ChangePasswordModal = ({
  isOpen,
  hasCloseBtn = true,
  onClose,
  children,
  onRefreshRequest,
}) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);

  const [userList, setUserList] = useState();
  const [selectedUser, setSelectedUser] = useState();

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

  let handleSubmitClick = () => {};

  useEffect(() => {
    let authtoken = JSON.parse(sessionStorage.getItem("token")).token;
    fetch(Api.API_GET_USER_LIST, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + authtoken,
      },
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
        console.log(data.userlist);
        // setUserList(data.userlist);
        let userArray = [];
        for (let user in data.userlist) {
          userArray.push(data.userlist[user].username);
          console.log(data.userlist[user].username);
        }
        setUserList(userArray);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }, []);

  let handleUserChange = (event) => {
    setSelectedUser(event.target.value);
  };

  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className="passwordmodal">
      {hasCloseBtn && (
        <button className="modal-close-btn" onClick={handleCloseModal}>
          <img src={closeCircle} alt="close" height="24px" width="24px"></img>
        </button>
      )}
      {children}
      <div className="passwordcontainer">
      
        <label className="currentPasswordLabel">Current Password</label>
        <input 
            className="currentPassword"
            type="password"
            id="username"
            name="username"
            autoComplete="off"
          />

<label className="newPasswordLabel">New Password</label>
        <input 
            className="newPassword"
            type="password"
            id="username"
            name="username"
            autoComplete="off"
          />

<label className="newPasswordConfirmLabel">Password Confirm</label>
        <input 
            className="newPasswordConfirm"
            type="password"
            id="username"
            name="username"
            autoComplete="off"
          />

      </div>

      
      <div className="submit_row">
        <button
          type="submit"
          className="submitbutton"
          onClick={handleSubmitClick}
        >
          Submit
        </button>
      </div>
    </dialog>
  );
};

export default ChangePasswordModal;
