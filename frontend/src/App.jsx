
import React from 'react';
import LoginForm from './log-in-sign-up';
import LoveSosaImage from './assets/image/Love Sosa.png';

function App() {
  return (
    <div>
      <img src={LoveSosaImage} alt="Love Sosa" />
      <LoginForm />
    </div>
  );
}

export default App;

