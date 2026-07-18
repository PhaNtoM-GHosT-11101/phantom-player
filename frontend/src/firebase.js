import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyDkzMiz5bScIlZQ-iW3svHLDzKXO59uaPQ",
  authDomain: "adityamusicplayer.firebaseapp.com",
  projectId: "adityamusicplayer",
  storageBucket: "adityamusicplayer.firebasestorage.app",
  messagingSenderId: "939045035466",
  appId: "1:939045035466:web:a0e37cb99347181ab34333",
  measurementId: "G-1PN8YS5YLG"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();
