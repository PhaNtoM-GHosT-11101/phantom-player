import React, { useContext } from 'react';
import { Play, Pause, SkipBack, SkipForward, Shuffle, Repeat, Volume2, Loader } from 'lucide-react';
import { PlayerContext } from '../context/PlayerContext';

function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
}

export default function BottomPlayer() {
    const { currentTrack, isPlaying, progress, duration, volume, setVolume, togglePlay, seek, nextTrack, prevTrack } = useContext(PlayerContext);

    const handleSeek = (e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const pos = (e.clientX - rect.left) / rect.width;
        seek(pos * duration);
    };

    const progressPercent = duration ? (progress / duration) * 100 : 0;
    
    const thumbUrl = currentTrack?.thumbnails?.[currentTrack.thumbnails.length - 1]?.url 
        || 'https://placehold.co/60x60/1e1e2e/9ece6a?text=?';

    return (
        <footer className={`bottom-player ${!currentTrack ? 'empty' : ''}`}>
            <div className={`now-playing ${isPlaying ? 'playing' : ''}`}>
                <img src={thumbUrl} alt="Thumbnail" />
                <div className="track-info">
                    <h4>{currentTrack ? currentTrack.title : 'No Track Playing'}</h4>
                    <p>{currentTrack ? currentTrack.artist : '--'}</p>
                </div>
            </div>
            
            <div className="player-controls-container">
                <div className="player-controls">
                    <button className="icon-btn"><Shuffle size={20} /></button>
                    <button className="icon-btn" onClick={prevTrack}><SkipBack size={20} /></button>
                    <button className="icon-btn play-btn" onClick={togglePlay}>
                        {isPlaying ? <Pause fill="currentColor" size={20} /> : <Play fill="currentColor" size={24} style={{ marginLeft: '2px' }} />}
                    </button>
                    <button className="icon-btn" onClick={nextTrack}><SkipForward size={20} /></button>
                    <button className="icon-btn"><Repeat size={20} /></button>
                </div>
                <div className="progress-container">
                    <span>{formatTime(progress)}</span>
                    <div className="progress-bar-bg" onClick={handleSeek}>
                        <div className="progress-bar-fill" style={{ width: `${progressPercent}%` }}></div>
                    </div>
                    <span>{formatTime(duration)}</span>
                </div>
            </div>
            
            <div className="volume-controls">
                <Volume2 size={20} />
                <input 
                    type="range" 
                    min="0" max="100" 
                    value={volume * 100} 
                    onChange={(e) => setVolume(e.target.value / 100)} 
                />
            </div>
        </footer>
    );
}
