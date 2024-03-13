import React, { useState } from "react";
import "./log-in-sign-up.css";
import axios from "axios";

const LoginForm = () => {
  const [showLogin, setShowLogin] = useState(true);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const toggleForm = () => {
    setShowLogin(!showLogin);
    setUsername("");
    setPassword("");
    setConfirmPassword("");
  };

  // Example submit handlers
  const handleLoginSubmit = (event) => {
    event.preventDefault(); //
    //logic for logging in goes here
    console.log("Logging in with:", username, password);
  };

  const handleSignupSubmit = async (event) => {
    print("button");
    event.preventDefault();
    console.log("Signing up with:", username, password, confirmPassword);
    try {
      const response = await axios.post("http://127.0.0.1:8080/api/signup", {
        username,
        password,
        confirmPassword,
      });
      console.log("Login response:", response.data);
    } catch (error) {
      console.error("Login error:", error.response.data);
    }
  };

  return (
    <div>
      {showLogin ? (
        <form id="login-form" onSubmit={handleLoginSubmit}>
          <h2>Log in</h2>
          <input
            type="text"
            placeholder="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit" id="login-btn">
            LOG IN
          </button>
          <p>Forgot your username or password?</p>
          <p>
            New to Love Sosa Reddit?{" "}
            <span onClick={toggleForm} style={{ cursor: "pointer" }}>
              Sign up
            </span>
          </p>
        </form>
      ) : (
        <form id="signup-form" onSubmit={handleSignupSubmit}>
          <h2>Sign up</h2>
          <input
            type="text"
            placeholder="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            type="password"
            placeholder="confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <button type="submit" id="signup-btn">
            SIGN UP
          </button>
          <p>
            Already have an account?{" "}
            <span onClick={toggleForm} style={{ cursor: "pointer" }}>
              Log in
            </span>
          </p>
        </form>
      )}
    </div>
  );
};

export default LoginForm;
