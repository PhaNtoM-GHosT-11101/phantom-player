import React from 'react';
import { Home, Search, Library, Plus, Terminal } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { usePlaylists } from '../hooks/usePlaylists';

export default function Sidebar() {
    const location = useLocation();
    const { playlists, loading, createPlaylist } = usePlaylists();

    return (
        <aside className="sidebar">
            <div className="brand">
                <Terminal />
                <h2>Adi_Music_player</h2>
            </div>
            
            <nav className="main-nav">
                <Link to="/" className={`nav-item ${location.pathname === '/' ? 'active' : ''}`}>
                    <Home size={20} /> Home
                </Link>
                <Link to="/search" className={`nav-item ${location.pathname === '/search' ? 'active' : ''}`}>
                    <Search size={20} /> Search
                </Link>
                <Link to="/library" className={`nav-item ${location.pathname === '/library' ? 'active' : ''}`}>
                    <Library size={20} /> Your Library
                </Link>
            </nav>

            <div className="playlists" style={{ flex: 1, overflowY: 'auto' }}>
                <div className="playlists-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h3 style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>YOUR PLAYLISTS</h3>
                    <button className="icon-btn" onClick={() => {
                        const name = prompt("Enter playlist name:");
                        if (name) createPlaylist(name);
                    }}>
                        <Plus size={16} />
                    </button>
                </div>
                <div className="playlist-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {playlists.length === 0 && !loading && (
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No playlists yet.</p>
                    )}
                    {playlists.map(pl => (
                        <Link to={`/playlist/${pl.id}`} key={pl.id} className="nav-item" style={{ fontSize: '0.85rem' }}>
                            {pl.name}
                        </Link>
                    ))}
                </div>
            </div>
        </aside>
    );
}
