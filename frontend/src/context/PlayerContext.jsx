import React, { createContext, useState, useRef, useEffect } from 'react';
import ReactPlayer from 'react-player/youtube';

export const PlayerContext = createContext();

export const PlayerProvider = ({ children }) => {
    const [currentTrack, setCurrentTrack] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    
    const playerRef = useRef(null);

    const playTrack = (track) => {
        setCurrentTrack(track);
        setIsPlaying(true);
    };

    const togglePlay = () => {
        if (!currentTrack) return;
        setIsPlaying(!isPlaying);
    };

    const seek = (time) => {
        if (playerRef.current) {
            playerRef.current.seekTo(time, 'seconds');
            setProgress(time);
        }
    };

    const handleProgress = (state) => {
        setProgress(state.playedSeconds);
    };

    const handleDuration = (dur) => {
        setDuration(dur);
    };

    const handleEnded = () => {
        setIsPlaying(false);
        // Handle queue logic here later
    };

    return (
        <PlayerContext.Provider value={{
            currentTrack,
            isPlaying,
            progress,
            duration,
            volume,
            setVolume,
            playTrack,
            togglePlay,
            seek
        }}>
            {children}
            {/* Hidden ReactPlayer for audio playback directly from YouTube */}
            {currentTrack && (
                <div style={{ display: 'none' }}>
                    <ReactPlayer
                        ref={playerRef}
                        url={`https://www.youtube.com/watch?v=${currentTrack.videoId}`}
                        playing={isPlaying}
                        volume={volume}
                        onProgress={handleProgress}
                        onDuration={handleDuration}
                        onEnded={handleEnded}
                        width="0"
                        height="0"
                        config={{
                            youtube: {
                                playerVars: { 
                                    autoplay: 1, 
                                    controls: 0,
                                    disablekb: 1,
                                    fs: 0,
                                    modestbranding: 1
                                }
                            }
                        }}
                    />
                </div>
            )}
        </PlayerContext.Provider>
    );
};
