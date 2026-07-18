import { useState, useEffect, useContext } from 'react';
import { db } from '../firebase';
import { collection, query, onSnapshot, addDoc, updateDoc, doc, arrayUnion, arrayRemove, deleteDoc, getDoc, setDoc } from 'firebase/firestore';
import { AuthContext } from '../context/AuthContext';

export function usePlaylists() {
    const { user } = useContext(AuthContext);
    const [playlists, setPlaylists] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!user) {
            setPlaylists([]);
            setLoading(false);
            return;
        }

        const q = query(collection(db, `users/${user.uid}/playlists`));
        const unsubscribe = onSnapshot(q, (snapshot) => {
            const list = [];
            snapshot.forEach((doc) => {
                list.push({ id: doc.id, ...doc.data() });
            });
            setPlaylists(list);
            setLoading(false);
        }, (error) => {
            console.error("Firestore permission denied or error:", error);
            setLoading(false);
        });

        return unsubscribe;
    }, [user]);

    const createPlaylist = async (name) => {
        if (!user) {
            alert("Please login to create a playlist!");
            return;
        }
        try {
            await addDoc(collection(db, `users/${user.uid}/playlists`), {
                name,
                tracks: [],
                createdAt: new Date().toISOString()
            });
        } catch (error) {
            console.error("Error creating playlist", error);
            alert("Error: Firestore Security Rules are likely blocking the write. Please allow writes in Firebase Console.");
        }
    };

    const addTrackToPlaylist = async (playlistId, track) => {
        if (!user) return;
        try {
            const playlistRef = doc(db, `users/${user.uid}/playlists`, playlistId);
            await updateDoc(playlistRef, {
                tracks: arrayUnion(track)
            });
            console.log(`Added to playlist!`);
        } catch (error) {
            console.error("Error adding track", error);
            alert("Error: Firestore Security Rules are likely blocking the write.");
        }
    };

    const removeTrackFromPlaylist = async (playlistId, track) => {
        if (!user) return;
        try {
            const playlistRef = doc(db, `users/${user.uid}/playlists`, playlistId);
            await updateDoc(playlistRef, {
                tracks: arrayRemove(track)
            });
        } catch (error) {
            console.error("Error removing track", error);
            alert("Error: Firestore Security Rules are likely blocking the write.");
        }
    };

    const deletePlaylist = async (playlistId) => {
        if (!user) return;
        try {
            const playlistRef = doc(db, `users/${user.uid}/playlists`, playlistId);
            await deleteDoc(playlistRef);
        } catch (error) {
            console.error("Error deleting playlist", error);
            alert("Error: Firestore Security Rules are likely blocking the write.");
        }
    };

    const toggleLikeTrack = async (track) => {
        if (!user) {
            alert("Please login to like tracks!");
            return;
        }
        try {
            const playlistRef = doc(db, `users/${user.uid}/playlists`, 'liked-songs');
            const snap = await getDoc(playlistRef);
            if (!snap.exists()) {
                await setDoc(playlistRef, { name: 'Liked Songs', tracks: [track], createdAt: new Date().toISOString() });
            } else {
                const data = snap.data();
                const isLiked = data.tracks?.some(t => t.videoId === track.videoId);
                if (isLiked) {
                    // Because arrayRemove needs deep equality, we find the exact track object in DB
                    const exactTrack = data.tracks.find(t => t.videoId === track.videoId);
                    await updateDoc(playlistRef, { tracks: arrayRemove(exactTrack) });
                } else {
                    await updateDoc(playlistRef, { tracks: arrayUnion(track) });
                }
            }
        } catch (error) {
            console.error("Error toggling like", error);
        }
    };

    return { playlists, loading, createPlaylist, addTrackToPlaylist, removeTrackFromPlaylist, deletePlaylist, toggleLikeTrack };
}
