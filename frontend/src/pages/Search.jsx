import React, { useState, useEffect, useContext } from 'react';
import { Search as SearchIcon, Plus } from 'lucide-react';
import { PlayerContext } from '../context/PlayerContext';
import { usePlaylists } from '../hooks/usePlaylists';

export default function Search() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    
    const { playQueue } = useContext(PlayerContext);
    const { playlists, addTrackToPlaylist } = usePlaylists();

    useEffect(() => {
        const delayDebounceFn = setTimeout(() => {
            if (query.trim()) {
                performSearch(query);
            } else {
                setResults([]);
            }
        }, 500);

        return () => clearTimeout(delayDebounceFn);
    }, [query]);

    const performSearch = async (q) => {
        setLoading(true);
        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
            const res = await fetch(`${API_URL}/search?query=${encodeURIComponent(q)}`);
            const data = await res.json();
            setResults(data.results || []);
        } catch (error) {
            console.error('Search failed', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSaveTrack = (e, track) => {
        e.stopPropagation(); // prevent playing when clicking save
        if (playlists.length === 0) {
            alert('Create a playlist first from the sidebar!');
            return;
        }
        
        // Very simple implementation: always add to the first playlist for now
        // In a full production app, this would open a modal to select the playlist
        const pl = playlists[0];
        addTrackToPlaylist(pl.id, track);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div className="topbar">
                <div className="search-bar">
                    <SearchIcon size={20} color="var(--text-muted)" />
                    <input 
                        type="text" 
                        placeholder="Search for songs..." 
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        autoFocus
                    />
                </div>
            </div>

            <div className="content-area">
                <h1 className="section-title">
                    {query ? (loading ? `Searching for "${query}"...` : 'Search Results') : 'Browse All'}
                </h1>
                
                <div className="results-grid">
                    {results.map((track, index) => {
                        const thumbUrl = track.thumbnails?.[track.thumbnails.length - 1]?.url 
                            || 'https://placehold.co/200x200/1e1e2e/9ece6a?text=No+Image';
                            
                        return (
                            <div className="track-card" key={track.videoId} onClick={() => playQueue(results, index)}>
                                <img src={thumbUrl} alt={track.title} />
                                <h4>{track.title}</h4>
                                <p>{track.artist}</p>
                                <button 
                                    onClick={(e) => handleSaveTrack(e, track)}
                                    className="btn secondary-btn" 
                                    style={{ marginTop: '12px', padding: '8px' }}
                                >
                                    <Plus size={16} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> Save
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
