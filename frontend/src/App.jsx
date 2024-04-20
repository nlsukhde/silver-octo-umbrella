
import React from 'react';
import {BrowserRouter, Routes, Route} from "react-router-dom";
import LoginForm from './log-in-sign-up';
import Posts from './post' ;
import EditProfile from './EditProfile';


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path ="/" element={<LoginForm />}></Route>
        <Route path ="/posts" element={<Posts />}></Route>
        <Route path ="/editprofile" element={<EditProfile />}></Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

