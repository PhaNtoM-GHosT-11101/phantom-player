import React, { useState, useEffect, useContext } from 'react';
import { PlayerContext } from '../context/PlayerContext';
import { Play } from 'lucide-react';

export default function Home() {
    const [trending, setTrending] = useState([]);
    const [loading, setLoading] = useState(true);
    const { playQueue } = useContext(PlayerContext);

    useEffect(() => {
        const fetchTrending = async () => {
            try {
                const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
                const res = await fetch(`${API_URL}/search?query=top+trending+music+2024`);
                const data = await res.json();
                setTrending(data.results || []);
            } catch (error) {
                console.error('Failed to fetch trending', error);
            } finally {
                setLoading(false);
            }
        };
        fetchTrending();
    }, []);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="topbar"></div>
            <div className="content-area">
                <h1 className="section-title">Trending Now</h1>
                
                {loading ? (
                    <p style={{ color: 'var(--text-muted)' }}>Loading trending tracks...</p>
                ) : (
                    <div className="results-grid">
                        {trending.map((track, index) => {
                            const thumbUrl = track.thumbnails?.[track.thumbnails.length - 1]?.url 
                                || 'https://placehold.co/200x200/1e1e2e/9ece6a?text=No+Image';
                                
                            return (
                                <div className="track-card" key={track.videoId} onClick={() => playQueue(trending, index)}>
                                    <img src={thumbUrl} alt={track.title} />
                                    <h4>{track.title}</h4>
                                    <p>{track.artist}</p>
                                    <button 
                                        className="btn primary-btn" 
                                        style={{ marginTop: '12px', padding: '8px', display: 'flex', justifyContent: 'center' }}
                                    >
                                        <Play size={16} fill="currentColor" /> Play
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
