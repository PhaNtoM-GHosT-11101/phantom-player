import React from 'react';
import { X, Plus } from 'lucide-react';
import { usePlaylists } from '../hooks/usePlaylists';

export default function SaveTrackModal({ track, onClose }) {
    const { playlists, addTrackToPlaylist, createPlaylist } = usePlaylists();

    const handleSave = (playlistId) => {
        addTrackToPlaylist(playlistId, track);
        onClose();
    };

    const handleCreateNew = () => {
        const name = prompt("Enter new playlist name:");
        if (name) {
            // Note: Since createPlaylist is async and might take a moment to reflect in the UI,
            // we just create it. The user will see it appear in the modal if it's kept open,
            // or they can close and re-open.
            createPlaylist(name);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Save to Playlist</h3>
                    <button className="icon-btn" onClick={onClose}><X size={20} /></button>
                </div>
                
                <div className="modal-track-info">
                    <img src={track.thumbnails?.[track.thumbnails.length - 1]?.url || 'https://placehold.co/60x60'} alt={track.title} />
                    <div>
                        <h4>{track.title}</h4>
                        <p>{track.artist}</p>
                    </div>
                </div>

                <div className="modal-playlists">
                    {playlists.length === 0 ? (
                        <p className="no-playlists">You don't have any playlists yet.</p>
                    ) : (
                        playlists.map(pl => (
                            <button 
                                key={pl.id} 
                                className="playlist-select-btn"
                                onClick={() => handleSave(pl.id)}
                            >
                                {pl.name}
                            </button>
                        ))
                    )}
                </div>

                <button className="btn secondary-btn create-new-btn" onClick={handleCreateNew}>
                    <Plus size={16} style={{ marginRight: '8px' }} /> Create New Playlist
                </button>
            </div>
        </div>
    );
}
