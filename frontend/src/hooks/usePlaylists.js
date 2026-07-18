import { useState, useEffect, useContext } from 'react';
import { db } from '../firebase';
import { collection, query, onSnapshot, addDoc, updateDoc, doc, arrayUnion } from 'firebase/firestore';
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
        });

        return unsubscribe;
    }, [user]);

    const createPlaylist = async (name) => {
        if (!user) return;
        try {
            await addDoc(collection(db, `users/${user.uid}/playlists`), {
                name,
                tracks: [],
                createdAt: new Date().toISOString()
            });
        } catch (error) {
            console.error("Error creating playlist", error);
        }
    };

    const addTrackToPlaylist = async (playlistId, track) => {
        if (!user) return;
        try {
            const playlistRef = doc(db, `users/${user.uid}/playlists`, playlistId);
            await updateDoc(playlistRef, {
                tracks: arrayUnion(track)
            });
            alert(`Added to playlist!`);
        } catch (error) {
            console.error("Error adding track", error);
        }
    };

    return { playlists, loading, createPlaylist, addTrackToPlaylist };
}
