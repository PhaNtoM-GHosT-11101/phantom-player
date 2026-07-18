import React, { useContext } from 'react';
import { Home, Search, Library, Plus, LogOut } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { usePlaylists } from '../hooks/usePlaylists';
import { AuthContext } from '../context/AuthContext';

export default function Sidebar() {
    const location = useLocation();
    const { playlists, loading, createPlaylist } = usePlaylists();
    const { user, loginWithGoogle, logout } = useContext(AuthContext);

    return (
        <aside className="sidebar">
            <div className="brand">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="10" width="4" height="10" rx="2" fill="currentColor">
                        <animate attributeName="height" values="10;4;14;10" dur="1s" repeatCount="indefinite" />
                        <animate attributeName="y" values="10;16;6;10" dur="1s" repeatCount="indefinite" />
                    </rect>
                    <rect x="10" y="6" width="4" height="14" rx="2" fill="currentColor">
                        <animate attributeName="height" values="14;18;8;14" dur="1.2s" repeatCount="indefinite" />
                        <animate attributeName="y" values="6;2;12;6" dur="1.2s" repeatCount="indefinite" />
                    </rect>
                    <rect x="17" y="12" width="4" height="8" rx="2" fill="currentColor">
                        <animate attributeName="height" values="8;12;4;8" dur="0.8s" repeatCount="indefinite" />
                        <animate attributeName="y" values="12;8;16;12" dur="0.8s" repeatCount="indefinite" />
                    </rect>
                </svg>
                <h2>Phantom V2</h2>
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
                <div className="playlists-header">
                    <h3>Your Playlists</h3>
                    <button className="icon-btn" onClick={() => {
                        const name = prompt("Enter playlist name:");
                        if (name) createPlaylist(name);
                    }}>
                        <Plus size={16} />
                    </button>
                </div>
                <div className="playlist-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {!user && <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Log in to view playlists.</p>}
                    {user && playlists?.length === 0 && !loading && (
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No playlists yet.</p>
                    )}
                    {playlists?.map(pl => (
                        <Link to={`/playlist/${pl.id}`} key={pl.id} className="nav-item">
                            {pl.name}
                        </Link>
                    ))}
                </div>
            </div>

            <div className="auth-section">
                {!user ? (
                    <button className="btn primary-btn" onClick={loginWithGoogle} style={{ width: '100%' }}>
                        Login with Google
                    </button>
                ) : (
                    <div className="user-profile">
                        <img 
                            src={user.photoURL || 'https://placehold.co/32x32/1e1e2e/ffffff?text=U'} 
                            alt="Avatar" 
                        />
                        <span>{user.displayName}</span>
                        <button className="icon-btn" onClick={logout} title="Logout">
                            <LogOut size={18} />
                        </button>
                    </div>
                )}
            </div>
        </aside>
    );
}
