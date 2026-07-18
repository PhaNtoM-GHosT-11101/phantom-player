import React, { createContext, useState, useRef, useEffect } from 'react';
import ReactPlayer from 'react-player/youtube';

export const PlayerContext = createContext();

export const PlayerProvider = ({ children }) => {
    const [currentTrack, setCurrentTrack] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    
    // Play Queue state
    const [queue, setQueue] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(-1);
    
    const playerRef = useRef(null);

    // Legacy method for single tracks, safely wrap it in a queue of 1
    const playTrack = (track) => {
        setQueue([track]);
        setCurrentIndex(0);
        setCurrentTrack(track);
        setIsPlaying(true);
    };

    // New method for playing from a list (e.g. search results, playlist)
    const playQueue = (tracks, startIndex = 0) => {
        if (!tracks || tracks.length === 0) return;
        setQueue(tracks);
        setCurrentIndex(startIndex);
        setCurrentTrack(tracks[startIndex]);
        setIsPlaying(true);
    };

    const nextTrack = () => {
        if (queue.length === 0 || currentIndex === -1) return;
        const nextIdx = (currentIndex + 1) % queue.length; // Loop back to start
        setCurrentIndex(nextIdx);
        setCurrentTrack(queue[nextIdx]);
        setIsPlaying(true);
    };

    const prevTrack = () => {
        if (queue.length === 0 || currentIndex === -1) return;
        if (progress > 3) {
            // If we are more than 3 seconds in, just restart the current track
            seek(0);
            return;
        }
        const prevIdx = (currentIndex - 1 + queue.length) % queue.length;
        setCurrentIndex(prevIdx);
        setCurrentTrack(queue[prevIdx]);
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
        // Automatically play next track when current ends
        nextTrack();
    };

    return (
        <PlayerContext.Provider value={{
            currentTrack,
            isPlaying,
            progress,
            duration,
            volume,
            queue,
            setVolume,
            playTrack,
            playQueue,
            nextTrack,
            prevTrack,
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
                                    modestbranding: 1,
                                    vq: 'tiny'
                                }
                            }
                        }}
                    />
                </div>
            )}
        </PlayerContext.Provider>
    );
};
