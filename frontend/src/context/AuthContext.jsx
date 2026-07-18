import React, { createContext, useState, useEffect } from 'react';
import { auth, googleProvider } from '../firebase';
import { signInWithPopup, signOut, onAuthStateChanged } from 'firebase/auth';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
            setUser(currentUser);
            setLoading(false);
        });
        return unsubscribe;
    }, []);

    const loginWithGoogle = async () => {
        try {
            await signInWithPopup(auth, googleProvider);
        } catch (error) {
            console.error("Login failed", error);
        }
    };

    const logout = () => {
        signOut(auth);
    };

    return (
        <AuthContext.Provider value={{ user, loading, loginWithGoogle, logout }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
