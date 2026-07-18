import React from 'react';
import { usePlaylists } from '../hooks/usePlaylists';
import { Link } from 'react-router-dom';
import { Heart, ListMusic } from 'lucide-react';

export default function Library() {
    const { playlists, loading } = usePlaylists();

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="topbar"></div>
            <div className="content-area">
                <h1 className="section-title">Your Library</h1>
                
                {loading ? (
                    <p style={{ color: 'var(--text-muted)' }}>Loading library...</p>
                ) : (
                    <div className="results-grid">
                        <Link to="/playlist/liked-songs" className="track-card" style={{ textDecoration: 'none', background: 'linear-gradient(135deg, #450af5, #c4efd9)' }}>
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
                                <Heart size={64} fill="white" color="white" />
                                <h2 style={{ color: 'white', marginTop: '16px' }}>Liked Songs</h2>
                            </div>
                        </Link>
                        
                        {playlists.filter(p => p.id !== 'liked-songs').map((pl) => (
                            <Link to={`/playlist/${pl.id}`} className="track-card" key={pl.id} style={{ textDecoration: 'none', background: 'var(--bg-surface)' }}>
                                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', minHeight: '200px' }}>
                                    <ListMusic size={64} color="var(--primary)" />
                                    <h3 style={{ color: 'var(--text)', marginTop: '16px' }}>{pl.name}</h3>
                                    <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>{pl.tracks?.length || 0} tracks</p>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
