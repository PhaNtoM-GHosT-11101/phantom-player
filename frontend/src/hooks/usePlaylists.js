import { useState, useEffect } from 'react';

const STORAGE_KEY = 'phantom_playlists_v2';

export function usePlaylists() {
    const [playlists, setPlaylists] = useState([]);
    const [loading, setLoading] = useState(true);

    // Load from local storage on mount
    useEffect(() => {
        try {
            const data = localStorage.getItem(STORAGE_KEY);
            if (data) {
                setPlaylists(JSON.parse(data));
            } else {
                // Initialize with empty liked songs if nothing exists
                const initial = [{
                    id: 'liked-songs',
                    name: 'Liked Songs',
                    tracks: [],
                    createdAt: new Date().toISOString()
                }];
                localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
                setPlaylists(initial);
            }
        } catch (e) {
            console.error("Failed to parse playlists from localStorage", e);
            setPlaylists([]);
        } finally {
            setLoading(false);
        }
    }, []);

    // Helper to save and update state
    const saveToStorage = (newPlaylists) => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newPlaylists));
        setPlaylists(newPlaylists);
    };

    const createPlaylist = async (name) => {
        const newPlaylist = {
            id: `pl_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            name,
            tracks: [],
            createdAt: new Date().toISOString()
        };
        const newPlaylists = [...playlists, newPlaylist];
        saveToStorage(newPlaylists);
    };

    const addTrackToPlaylist = async (playlistId, track) => {
        const newPlaylists = playlists.map(pl => {
            if (pl.id === playlistId) {
                // Prevent duplicates
                if (!pl.tracks.some(t => t.videoId === track.videoId)) {
                    return { ...pl, tracks: [...pl.tracks, track] };
                }
            }
            return pl;
        });
        saveToStorage(newPlaylists);
        console.log(`Added to playlist!`);
    };

    const removeTrackFromPlaylist = async (playlistId, track) => {
        const newPlaylists = playlists.map(pl => {
            if (pl.id === playlistId) {
                return {
                    ...pl,
                    tracks: pl.tracks.filter(t => t.videoId !== track.videoId)
                };
            }
            return pl;
        });
        saveToStorage(newPlaylists);
    };

    const deletePlaylist = async (playlistId) => {
        // Prevent deleting Liked Songs
        if (playlistId === 'liked-songs') {
            alert("You cannot delete the Liked Songs playlist.");
            return;
        }
        const newPlaylists = playlists.filter(pl => pl.id !== playlistId);
        saveToStorage(newPlaylists);
    };

    const toggleLikeTrack = async (track) => {
        const likedPlaylist = playlists.find(p => p.id === 'liked-songs');
        
        let newPlaylists;
        if (!likedPlaylist) {
            // Re-create liked songs if it somehow got deleted
            const newLiked = {
                id: 'liked-songs',
                name: 'Liked Songs',
                tracks: [track],
                createdAt: new Date().toISOString()
            };
            newPlaylists = [...playlists, newLiked];
        } else {
            const isLiked = likedPlaylist.tracks.some(t => t.videoId === track.videoId);
            newPlaylists = playlists.map(pl => {
                if (pl.id === 'liked-songs') {
                    if (isLiked) {
                        return { ...pl, tracks: pl.tracks.filter(t => t.videoId !== track.videoId) };
                    } else {
                        return { ...pl, tracks: [...pl.tracks, track] };
                    }
                }
                return pl;
            });
        }
        
        saveToStorage(newPlaylists);
    };

    return { playlists, loading, createPlaylist, addTrackToPlaylist, removeTrackFromPlaylist, deletePlaylist, toggleLikeTrack };
}
