import React, { useState, useEffect } from "react";
import LoveSosaImage from './assets/image/Love Sosa.png';
import "./log-in-sign-up.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const LoginForm = () => {
  const [showLogin, setShowLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false); // manage login state
  const [loggedInUsername, setLoggedInUsername] = useState(""); // store and display username
  const [profileImage, setProfileImage] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const validateToken = async () => {
      try {
        const response = await axios.get("/api/validate_token", {
          withCredentials: true,
        });
        if (response.data && response.data.username) {
          setIsLoggedIn(true);
          setLoggedInUsername(response.data.username);
          setProfileImage(response.data.profileImage);  // Set profile image URL
        }
      } catch (error) {
        console.error("Token validation error:", error.response ? error.response.data : "No response");
        setIsLoggedIn(false);
        setLoggedInUsername("");
      }
    };

    validateToken();
  }, []);

  const toggleForm = () => {
    setShowLogin(!showLogin);
    setUsername("");
    setPassword("");
    setConfirmPassword("");
  };

  const handleLoginSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post(
        "/api/login",
        { username, password },
        { withCredentials: true }
      );
      setIsLoggedIn(true);
      setLoggedInUsername(username);
      setUsername("");
      setPassword("");
    } catch (error) {
      console.error("Login error:", error.response.data);
    }
  };

  const handleSignupSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post(
        "/api/signup",
        { username, password, confirmPassword }
      );
    } catch (error) {
      console.error("Sign up error:", error.response.data);
    }
  };

  const handleLogout = async (event) => {
    event.preventDefault();
    try {
      const response = await axios.post(
        "/api/logout",
        {},
        { withCredentials: true }
      );
      setIsLoggedIn(false);
      setLoggedInUsername("");
    } catch (error) {
      console.error(
        "Logout error:",
        error.response ? error.response.data : "No response"
      );
    }
  };

  const handlePosts = () => {
    navigate('/posts');
  };

  const navigateToEditProfile = () => {
    navigate('/EditProfile');
  };

  return (
    <div>
      <img src={profileImage || LoveSosaImage} alt="Profile" className="profile-pic" />
      {isLoggedIn ? (
        <div>
          <p>Welcome, {loggedInUsername}!</p>
          <button onClick={handleLogout}>Log Out</button>
          <button onClick={handlePosts}>Create a Post</button>
          <button onClick={navigateToEditProfile}>Edit Profile Picture</button>
        </div>
      ) : (
        showLogin ? (
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
        )
      )}
    </div>
  );
};

export default LoginForm;
