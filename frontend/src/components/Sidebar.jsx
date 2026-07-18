import React, { useContext } from 'react';
import { Home, Search, Library, Plus, Terminal, LogOut } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { usePlaylists } from '../hooks/usePlaylists';
import { AuthContext } from '../context/AuthContext';

export default function Sidebar() {
    const location = useLocation();
    const { playlists, loading, createPlaylist } = usePlaylists();
    const { user, loginWithGoogle, logout } = useContext(AuthContext);

    return (
        <aside className="sidebar">
            <div className="brand" style={{ gap: '12px' }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ filter: 'drop-shadow(0 0 8px #9ece6a)' }}>
                    <rect x="3" y="10" width="4" height="10" rx="2" fill="#9ece6a">
                        <animate attributeName="height" values="10;4;14;10" dur="1s" repeatCount="indefinite" />
                        <animate attributeName="y" values="10;16;6;10" dur="1s" repeatCount="indefinite" />
                    </rect>
                    <rect x="10" y="6" width="4" height="14" rx="2" fill="#9ece6a">
                        <animate attributeName="height" values="14;18;8;14" dur="1.2s" repeatCount="indefinite" />
                        <animate attributeName="y" values="6;2;12;6" dur="1.2s" repeatCount="indefinite" />
                    </rect>
                    <rect x="17" y="12" width="4" height="8" rx="2" fill="#9ece6a">
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
                <div className="playlists-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '24px 0 16px' }}>
                    <h3 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', letterSpacing: '1px' }}>YOUR PLAYLISTS</h3>
                    <button className="icon-btn" onClick={() => {
                        const name = prompt("Enter playlist name:");
                        if (name) createPlaylist(name);
                    }}>
                        <Plus size={16} />
                    </button>
                </div>
                <div className="playlist-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {!user && <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Log in to view playlists.</p>}
                    {user && playlists.length === 0 && !loading && (
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No playlists yet.</p>
                    )}
                    {playlists.map(pl => (
                        <Link to={`/playlist/${pl.id}`} key={pl.id} className="nav-item" style={{ fontSize: '0.9rem' }}>
                            {pl.name}
                        </Link>
                    ))}
                </div>
            </div>

            <div className="auth-section" style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                {!user ? (
                    <button className="btn primary-btn" onClick={loginWithGoogle} style={{ width: '100%', display: 'block' }}>Login with Google</button>
                ) : (
                    <div className="user-profile" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <img 
                            src={user.photoURL || 'https://placehold.co/32x32/1e1e2e/9ece6a?text=U'} 
                            alt="Avatar" 
                            style={{ width: '36px', height: '36px', borderRadius: '50%' }}
                        />
                        <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontSize: '0.9rem' }}>
                            {user.displayName}
                        </span>
                        <button className="icon-btn" onClick={logout} title="Logout">
                            <LogOut size={18} />
                        </button>
                    </div>
                )}
            </div>
        </aside>
    );
}
