import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import BottomPlayer from './components/BottomPlayer';
import Home from './pages/Home';
import Search from './pages/Search';
import PlaylistView from './pages/PlaylistView';
import Library from './pages/Library';

function App() {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search" element={<Search />} />
          <Route path="/playlist/:id" element={<PlaylistView />} />
          <Route path="/library" element={<Library />} />
        </Routes>
      </main>
      <BottomPlayer />
    </div>
  );
}

export default App;
