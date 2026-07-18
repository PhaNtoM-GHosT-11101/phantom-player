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
                // Fetch from the backend API if running
                const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
                const res = await fetch(`${API_URL}/search?query=top+trending+music+2024`);
                const data = await res.json();
                setTrending(data.results || []);
            } catch (error) {
                console.error('Failed to fetch trending', error);
                // Fallback mock data for minimalist UI testing
                setTrending([
                    { videoId: '1', title: 'Midnight City', artist: 'M83', thumbnails: [{url: 'https://placehold.co/200x200/1e1e2e/ffffff?text=M83'}] },
                    { videoId: '2', title: 'Blinding Lights', artist: 'The Weeknd', thumbnails: [{url: 'https://placehold.co/200x200/1e1e2e/ffffff?text=TW'}] },
                    { videoId: '3', title: 'Levitating', artist: 'Dua Lipa', thumbnails: [{url: 'https://placehold.co/200x200/1e1e2e/ffffff?text=DL'}] },
                    { videoId: '4', title: 'As It Was', artist: 'Harry Styles', thumbnails: [{url: 'https://placehold.co/200x200/1e1e2e/ffffff?text=HS'}] },
                ]);
            } finally {
                setLoading(false);
            }
        };
        fetchTrending();
    }, []);

    return (
        <div style={{ height: '100%' }}>
            <h1 className="section-title">Trending Now</h1>
            
            {loading ? (
                <p style={{ color: 'var(--text-muted)' }}>Loading trending tracks...</p>
            ) : (
                <div className="grid">
                    {trending.map((track, index) => {
                        const thumbUrl = track.thumbnails?.[track.thumbnails.length - 1]?.url 
                            || 'https://placehold.co/200x200/1e1e2e/ffffff?text=No+Image';
                            
                        return (
                            <div className="card" key={track.videoId} onClick={() => playQueue(trending, index)}>
                                <div className="card-img-wrapper">
                                    <img src={thumbUrl} alt={track.title} />
                                </div>
                                <h4 className="card-title">{track.title}</h4>
                                <p className="card-subtitle">{track.artist}</p>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
