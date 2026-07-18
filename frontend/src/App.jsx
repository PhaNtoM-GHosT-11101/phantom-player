import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import BottomPlayer from './components/BottomPlayer';
import Search from './pages/Search';
import Home from './pages/Home';

function App() {
    return (
        <div className="app-container">
            <Sidebar />
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/search" element={<Search />} />
                    <Route path="/library" element={
                        <div className="content-area">
                            <h1 className="section-title">Your Library</h1>
                            <p style={{ color: 'var(--text-muted)' }}>Login to view your saved playlists.</p>
                        </div>
                    } />
                </Routes>
            </main>
            <BottomPlayer />
        </div>
    );
}

export default App;
