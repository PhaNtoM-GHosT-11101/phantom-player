import React, { useContext, useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PlayerContext } from '../context/PlayerContext';
import { usePlaylists } from '../hooks/usePlaylists';
import { Play, Trash2, X } from 'lucide-react';

export default function PlaylistView() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { playlists, loading, deletePlaylist, removeTrackFromPlaylist } = usePlaylists();
    const { playQueue } = useContext(PlayerContext);
    const [playlist, setPlaylist] = useState(null);

    useEffect(() => {
        if (playlists.length > 0) {
            const found = playlists.find(p => p.id === id);
            setPlaylist(found);
        }
    }, [id, playlists]);

    if (loading) {
        return <div className="content-area"><h1 className="section-title">Loading Playlist...</h1></div>;
    }

    if (!playlist) {
        return <div className="content-area"><h1 className="section-title">Playlist Not Found</h1></div>;
    }

    const handlePlayAll = () => {
        if (playlist.tracks && playlist.tracks.length > 0) {
            playQueue(playlist.tracks, 0);
        }
    };

    const handleDeletePlaylist = async () => {
        if (window.confirm('Are you sure you want to delete this playlist?')) {
            await deletePlaylist(playlist.id);
            navigate('/');
        }
    };

    const handleRemoveTrack = async (e, track) => {
        e.stopPropagation();
        await removeTrackFromPlaylist(playlist.id, track);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="content-area">
                <div style={{ display: 'flex', alignItems: 'center', gap: '24px', marginBottom: '32px' }}>
                    <div style={{ 
                        width: '150px', height: '150px', 
                        background: 'linear-gradient(135deg, var(--accent), var(--accent-secondary))',
                        borderRadius: '16px',
                        boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                        <h1 style={{ color: 'var(--bg-base)', fontSize: '4rem' }}>{playlist.name.charAt(0).toUpperCase()}</h1>
                    </div>
                    <div>
                        <p style={{ color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '2px', fontSize: '0.8rem', marginBottom: '8px' }}>Playlist</p>
                        <h1 className="section-title" style={{ marginBottom: '16px', fontSize: '3rem' }}>{playlist.name}</h1>
                        <p style={{ color: 'var(--text-muted)' }}>{playlist.tracks?.length || 0} tracks</p>
                        <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                            <button className="btn primary-btn" onClick={handlePlayAll} style={{ width: 'auto', display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 32px', borderRadius: '30px' }}>
                                <Play size={20} fill="currentColor" /> Play All
                            </button>
                            <button className="btn secondary-btn" onClick={handleDeletePlaylist} style={{ width: 'auto', display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px', borderRadius: '30px', color: '#ff6b6b' }}>
                                <Trash2 size={20} /> Delete
                            </button>
                        </div>
                    </div>
                </div>
                
                <div className="results-grid" style={{ gridTemplateColumns: '1fr' }}>
                    {playlist.tracks && playlist.tracks.map((track, index) => {
                        const thumbUrl = track.thumbnails?.[track.thumbnails.length - 1]?.url 
                            || 'https://placehold.co/60x60/1e1e2e/9ece6a?text=No+Image';
                            
                        return (
                            <div className="track-card" key={`${track.videoId}-${index}`} onClick={() => playQueue(playlist.tracks, index)} style={{ flexDirection: 'row', alignItems: 'center', gap: '16px', padding: '12px', position: 'relative' }}>
                                <span style={{ width: '24px', textAlign: 'right', color: 'var(--text-muted)', fontWeight: 'bold' }}>{index + 1}</span>
                                <img src={thumbUrl} alt={track.title} style={{ width: '48px', height: '48px', marginBottom: '0', borderRadius: '8px' }} />
                                <div style={{ flex: 1 }}>
                                    <h4 style={{ fontSize: '1rem' }}>{track.title}</h4>
                                    <p style={{ fontSize: '0.85rem' }}>{track.artist}</p>
                                </div>
                                <button className="icon-btn" onClick={(e) => handleRemoveTrack(e, track)} style={{ color: 'var(--text-muted)', opacity: 0.5 }}>
                                    <X size={20} />
                                </button>
                            </div>
                        );
                    })}
                    {(!playlist.tracks || playlist.tracks.length === 0) && (
                        <p style={{ color: 'var(--text-muted)' }}>This playlist is empty. Search for songs to add them.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
