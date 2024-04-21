import React, { useRef, useEffect, useState } from "react";
import "./UserPrefsModal.css";
import closeCircle from "./close-circle.svg";
import deleteIcon from "./delete.svg";
import userAddIcon from "./user-add.svg";
import keyIcon from "./key.svg";
import ClipLoader from "react-spinners/ClipLoader";
import * as Api from "../Api/Api.js";

const UserPrefsModal = ({
  isOpen,
  hasCloseBtn = true,
  onClose,
  children,
  onAddUser,
  onChangePW,
  onRefreshRequest,
}) => {
  const [isModalOpen, setModalOpen] = useState(isOpen);

  const [userList, setUserList] = useState();
  const [selectedUser, setSelectedUser] = useState();
  const [pwButtonDisabled, setPwButtonDisabled] = useState(true);
  const [delUserButtonDisabled, setDelUserButtonDisabled] = useState(true);
  const [loggedInUser, setLoggedInUser] = useState(sessionStorage.getItem("userName"));

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

    if(selectedUser===undefined){
     
      setDelUserButtonDisabled(true);
      setPwButtonDisabled(true);
      return
    }
    if (selectedUser === loggedInUser) {
      setDelUserButtonDisabled(true);
      setPwButtonDisabled(false);

    } else {
      setDelUserButtonDisabled(false);
      setPwButtonDisabled(true);
    }
  }, [selectedUser]);

  let handleUserChange = (event) => {

    setSelectedUser(event.target.value);

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

  return (
    <dialog ref={modalRef} onKeyDown={handleKeyDown} className="usermodal">
      {hasCloseBtn && (
        <button className="modal-close-btn" onClick={handleCloseModal}>
          <img src={closeCircle} alt="close" height="24px" width="24px"></img>
        </button>
      )}
      {children}
      <div className="userscontainer">
        <label htmlFor="userlist" className="userlistlabel">
          Users
        </label>
        {!userList == "" ? (
          <select
            className="userslistbox"
            id="userslistbox"
            name="userslistbox"
            required
            onChange={handleUserChange}
            value={selectedUser}
            size="6"
          >
            {userList?.map((user, index) => (
              <option key={index} value={user}>
                {user}
              </option>
            ))}
          </select>
        ) : (
          <ClipLoader
            className="userSpinner"
            color="#000000"
            loading={true}
            size={48}
            aria-label="Loading Spinner"
            data-testid="loader"
          />
        )}{" "}
        <div className="userBtnRow">
          <button className="adduserbtn" title="Add User" onClick={onAddUser}>
            <img src={userAddIcon} alt="Add" height="24px" width="24px"></img>
          </button>
          <button
            className={!delUserButtonDisabled ? "deluserbtn" : "pwbtndisabled"}
            title="Delete User"
          >
            <img src={deleteIcon} alt="Delete" height="24px" width="24px"></img>
          </button>
          <button
            className={!pwButtonDisabled ? "chgpwbtn" : "pwbtndisabled"}
            title="Change Password"
            onClick={onChangePW}
            disabled={pwButtonDisabled}
          >
            <img src={keyIcon} alt="Password" height="24px" width="24px"></img>
          </button>
        </div>
      </div>

      <div className="submit_row">
        <button
         // type="submit"
          className="submitbutton"
          onClick={handleCloseModal}
        >
          Close
        </button>
      </div>
    </dialog>
  );
};

export default UserPrefsModal;
