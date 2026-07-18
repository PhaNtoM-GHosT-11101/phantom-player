import React, { createContext, useState, useRef, useEffect } from 'react';

export const PlayerContext = createContext();

export const PlayerProvider = ({ children }) => {
    const [currentTrack, setCurrentTrack] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    
    const audioRef = useRef(new Audio());

    useEffect(() => {
        const audio = audioRef.current;
        
        const handleTimeUpdate = () => {
            setProgress(audio.currentTime);
            setDuration(audio.duration || 0);
        };
        
        const handleEnded = () => {
            setIsPlaying(false);
            // Handle queue logic here later
        };

        audio.addEventListener('timeupdate', handleTimeUpdate);
        audio.addEventListener('ended', handleEnded);
        
        return () => {
            audio.removeEventListener('timeupdate', handleTimeUpdate);
            audio.removeEventListener('ended', handleEnded);
        };
    }, []);

    useEffect(() => {
        audioRef.current.volume = volume;
    }, [volume]);

    const playTrack = async (track) => {
        setCurrentTrack(track);
        setIsPlaying(true);
        // Playback logic will interact with backend here
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
            const res = await fetch(`${API_URL}/stream/${track.videoId}`);
            if (!res.ok) throw new Error('Stream fetch failed');
            const data = await res.json();
            
            audioRef.current.src = data.streamUrl;
            audioRef.current.play();
        } catch (error) {
            console.error('Playback error:', error);
            setIsPlaying(false);
        }
    };

    const togglePlay = () => {
        if (!audioRef.current.src) return;
        if (isPlaying) {
            audioRef.current.pause();
        } else {
            audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    const seek = (time) => {
        audioRef.current.currentTime = time;
        setProgress(time);
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
        </PlayerContext.Provider>
    );
};
