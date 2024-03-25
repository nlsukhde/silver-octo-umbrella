
import React from 'react';
import {BrowserRouter, Routes, Route} from "react-router-dom";
import LoginForm from './log-in-sign-up';
import Posts from './post' ;


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path ="/" element={<LoginForm />}></Route>
        <Route path ="/posts" element={<Posts />}></Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;

