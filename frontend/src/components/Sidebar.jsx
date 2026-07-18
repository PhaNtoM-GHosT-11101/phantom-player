import React, { useContext } from 'react';
import { Home, Search, Library, Plus, LogOut, Terminal } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { usePlaylists } from '../hooks/usePlaylists';

export default function Sidebar() {
    const location = useLocation();
    const { user, loginWithGoogle, logout } = useContext(AuthContext);
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

            <div className="playlists">
                <div className="playlists-header">
                    <h3>YOUR PLAYLISTS</h3>
                    {user && (
                        <button className="icon-btn" onClick={() => {
                            const name = prompt("Enter playlist name:");
                            if (name) createPlaylist(name);
                        }}>
                            <Plus size={16} />
                        </button>
                    )}
                </div>
                <div className="playlist-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {!user && <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Log in to create playlists.</p>}
                    {user && playlists.length === 0 && !loading && (
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No playlists yet.</p>
                    )}
                    {playlists.map(pl => (
                        <Link to={`/playlist/${pl.id}`} key={pl.id} className="nav-item" style={{ fontSize: '0.85rem' }}>
                            {pl.name}
                        </Link>
                    ))}
                </div>
            </div>

            <div className="auth-section">
                {!user ? (
                    <button className="btn primary-btn" onClick={loginWithGoogle}>Login to Save</button>
                ) : (
                    <div className="user-profile" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <img 
                            src={user.photoURL || 'https://placehold.co/32x32/1e1e2e/9ece6a?text=U'} 
                            alt="Avatar" 
                            style={{ width: '32px', height: '32px', borderRadius: '50%' }}
                        />
                        <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
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
