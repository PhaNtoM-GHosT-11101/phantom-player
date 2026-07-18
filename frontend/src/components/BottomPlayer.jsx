import React, { useContext, useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, Shuffle, Repeat, Volume2, ListMusic, Heart } from 'lucide-react';
import { PlayerContext } from '../context/PlayerContext';
import { usePlaylists } from '../hooks/usePlaylists';
import { AuthContext } from '../context/AuthContext';

function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function BottomPlayer() {
    const { currentTrack, isPlaying, progress, duration, volume, setVolume, togglePlay, seek, nextTrack, prevTrack, queue, currentIndex, playQueue } = useContext(PlayerContext);
    const { toggleLikeTrack, playlists } = usePlaylists();
    const { user } = useContext(AuthContext);
    const [showQueue, setShowQueue] = useState(false);

    const handleSeek = (e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        seek(pos * duration);
    };

    const progressPercent = duration ? (progress / duration) * 100 : 0;
    
    const thumbUrl = currentTrack?.thumbnails?.[currentTrack.thumbnails.length - 1]?.url 
        || 'https://placehold.co/60x60/1e1e2e/ffffff?text=?';

    const likedPlaylist = playlists?.find(p => p.id === 'liked-songs');
    const isLiked = currentTrack && likedPlaylist?.tracks?.some(t => t.videoId === currentTrack.videoId);

    return (
        <footer className="bottom-player">
            {showQueue && (
                <div style={{ position: 'absolute', bottom: '100%', right: '32px', width: '300px', backgroundColor: 'var(--bg-surface-elevated)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-lg)', padding: '16px', zIndex: 100, maxHeight: '400px', overflowY: 'auto' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>Up Next</h3>
                        <button className="icon-btn" onClick={() => setShowQueue(false)}>&times;</button>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {queue.map((track, idx) => (
                            <div 
                                key={idx} 
                                style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px', borderRadius: 'var(--radius-md)', backgroundColor: idx === currentIndex ? 'var(--bg-hover)' : 'transparent', cursor: 'pointer' }}
                                onClick={() => playQueue(queue, idx)}
                            >
                                <img src={track.thumbnails?.[0]?.url || 'https://placehold.co/40x40'} alt="thumb" style={{ width: '40px', height: '40px', borderRadius: '4px', objectFit: 'cover' }} />
                                <div style={{ flex: 1, overflow: 'hidden' }}>
                                    <p style={{ fontSize: '0.9rem', fontWeight: 500, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>{track.title}</p>
                                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{track.artist}</p>
                                </div>
                            </div>
                        ))}
                        {queue.length === 0 && <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Queue is empty</p>}
                    </div>
                </div>
            )}

            <div className="player-left">
                <img src={thumbUrl} alt="Thumbnail" className="track-cover" />
                <div className="track-info">
                    <span className="track-title">{currentTrack ? currentTrack.title : 'No Track'}</span>
                    <span className="track-artist">{currentTrack ? currentTrack.artist : '--'}</span>
                </div>
                {currentTrack && (
                    <button 
                        className="icon-btn" 
                        onClick={() => toggleLikeTrack(currentTrack)}
                        style={{ marginLeft: '12px', color: isLiked ? 'var(--text-main)' : 'var(--text-muted)' }}
                    >
                        <Heart size={20} fill={isLiked ? 'currentColor' : 'none'} />
                    </button>
                )}
            </div>
            
            <div className="player-center">
                <div className="player-controls">
                    <button className="icon-btn"><Shuffle size={18} /></button>
                    <button className="icon-btn" onClick={prevTrack}><SkipBack size={20} /></button>
                    <button className="play-pause-btn" onClick={togglePlay}>
                        {isPlaying ? <Pause fill="currentColor" size={20} /> : <Play fill="currentColor" size={20} style={{ marginLeft: '2px' }} />}
                    </button>
                    <button className="icon-btn" onClick={nextTrack}><SkipForward size={20} /></button>
                    <button className="icon-btn"><Repeat size={18} /></button>
                </div>
                <div className="progress-container">
                    <span className="time">{formatTime(progress)}</span>
                    <div className="progress-bar" onClick={handleSeek}>
                        <div className="progress-fill" style={{ width: `${progressPercent}%` }}></div>
                    </div>
                    <span className="time">{formatTime(duration)}</span>
                </div>
            </div>
            
            <div className="player-right">
                <button className={`icon-btn ${showQueue ? 'active' : ''}`} onClick={() => setShowQueue(!showQueue)} title="Queue">
                    <ListMusic size={20} />
                </button>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <Volume2 size={20} color="var(--text-muted)" />
                    <input 
                        type="range" 
                        min="0" max="100" 
                        value={volume * 100} 
                        onChange={(e) => setVolume(e.target.value / 100)} 
                        style={{ width: '80px', accentColor: 'var(--text-main)' }}
                    />
                </div>
            </div>
        </footer>
    );
}
