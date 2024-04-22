import React, { useState } from "react";
import "./Login.css";
import PropTypes from "prop-types";
import applogo from "../../Images/reefberry-pi-logo.svg";
import * as Api from "../Api/Api.js"

async function loginUser(credentials) {

  // return fetch(process.env.REACT_APP_API_GET_TOKEN, {
  return fetch(Api.API_GET_TOKEN, {  
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
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

export default function Login({ setToken, setUser }) {
  const [username, setUserName] = useState();
  const [password, setPassword] = useState();
  const [isInvalidLogin, setIsInvalidLogin] = useState();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsInvalidLogin(false);
    const token = await loginUser({
      username,
      password,
    });
    console.log(token);
    if (token === undefined) {
      console.log("invalid login");
      setIsInvalidLogin(true);
    }

    setUser(username)
    setToken(token);
    
  };

  const updateUserCredentials = (e) => {
    setUserName(e.target.value);
    setIsInvalidLogin(false);
  };

  const updatePWCredentials = (e) => {
    setPassword(e.target.value);
    setIsInvalidLogin(false);
  };


  return (
    <div>
      <div className="login-wrapper">
        <table className={!isInvalidLogin ? "login-sheet" : "login-sheet-fail"}>
          <td className="login-logo">
            <div>
              <img src={applogo} alt="Reefberry Pi Logo" width="140"></img>
            </div>{" "}
          </td>
          <td>
            <div className="login-fields">
              <h1 className="h1">Reefberry Pi</h1>
              <h3 className="h3">Aquarium Controller</h3>
              <form onSubmit={handleSubmit}>
                <label className="field-style">
                  <div>Username</div>
                  <input
                    type="text"
                    // onChange={e => setUserName(e.target.value)}
                    onChange={(e) => updateUserCredentials(e)}
                  />
                </label>
                <br></br>
                <label className="field-style">
                  <div>Password</div>
                  <input
                    type="password"
                    // onChange={(e) => setPassword(e.target.value)}
                    onChange={(e) => updatePWCredentials(e)}
                  />
                </label>

                {isInvalidLogin ? (
                  <div className="fail-style"><label >Invalid Login</label></div>
                ) : <div className="fail-style"></div>}

                <div>
                  <button type="submit" className="button-style">
                    Login
                  </button>
                </div>
              </form>
            </div>
          </td>
        </table>
      </div>
    </div>
  );
}

Login.propTypes = {
  setToken: PropTypes.func.isRequired,
};
