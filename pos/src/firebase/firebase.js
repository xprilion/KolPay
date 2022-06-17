// Import the functions you need from the SDKs you need
import firebase from "firebase/compat/app";
import "firebase/compat/firestore";


// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAwSGloihyrfW_9NQwbU5jsM4-eCqifk7s",
  authDomain: "niyoproject-306620.firebaseapp.com",
  projectId: "niyoproject-306620",
  storageBucket: "niyoproject-306620.appspot.com",
  messagingSenderId: "1065240776308",
  appId: "1:1065240776308:web:a05a0a53d6cd08e18d4b21"
};

export const myFirebase = firebase.initializeApp(firebaseConfig);
const baseDb = myFirebase.firestore();
export const db = baseDb;
export default myFirebase;