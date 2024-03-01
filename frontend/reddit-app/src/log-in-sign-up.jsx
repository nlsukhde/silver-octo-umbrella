import React, { useState } from 'react';
import './log-in-sign-up.css'; 

const LoginForm = () => {
  const [showLogin, setShowLogin] = useState(true);

  const toggleForm = () => {
    setShowLogin(!showLogin);
  };

  return (
    <div>
      {showLogin ? (
        <div id="login-form">
          <h2>Log in</h2>
          <input type="text" placeholder="username" />
          <input type="password" placeholder="password" />
          <button id="login-btn">LOG IN</button>
          <p>Forgot your username or password?</p>
          <p>New to [app name]? <span onClick={toggleForm} style={{cursor: 'pointer'}}>Sign up</span></p>
        </div>
      ) : (
        <div id="signup-form">
          <h2>Sign up</h2>
          <input type="text" placeholder="username" />
          <input type="password" placeholder="password" />
          <input type="password" placeholder="confirm password" />
          <button id="signup-btn">SIGN UP</button>
          <p>Already have an account? <span onClick={toggleForm} style={{cursor: 'pointer'}}>Log in</span></p>
        </div>
      )}
    </div>
  );
};

export default LoginForm;
