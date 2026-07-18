import { useState, useEffect } from 'react';

export function usePlaylists() {
    const [playlists, setPlaylists] = useState([]);
    const [loading, setLoading] = useState(true);

    // Load from localStorage on mount
    useEffect(() => {
        const stored = localStorage.getItem('phantom_playlists');
        if (stored) {
            try {
                setPlaylists(JSON.parse(stored));
            } catch (e) {
                console.error("Failed to parse playlists", e);
            }
        }
        setLoading(false);
    }, []);

    // Save to localStorage whenever playlists change
    useEffect(() => {
        if (!loading) {
            localStorage.setItem('phantom_playlists', JSON.stringify(playlists));
        }
    }, [playlists, loading]);

    const createPlaylist = (name) => {
        const newPlaylist = {
            id: Date.now().toString(),
            name,
            tracks: [],
            createdAt: new Date().toISOString()
        };
        setPlaylists(prev => [...prev, newPlaylist]);
    };

    const addTrackToPlaylist = (playlistId, track) => {
        setPlaylists(prev => prev.map(pl => {
            if (pl.id === playlistId) {
                // Check if track already exists to avoid duplicates
                const exists = pl.tracks.find(t => t.videoId === track.videoId);
                if (exists) return pl;
                
                return {
                    ...pl,
                    tracks: [...pl.tracks, track]
                };
            }
            return pl;
        }));
        alert(`Added to playlist!`);
    };

    return { playlists, loading, createPlaylist, addTrackToPlaylist };
}
