import '@picocss/pico';
import { myFirebase, db } from "../firebase/firebase";
import React, { useState, useEffect, useReducer } from "react";

function ReaderSection({ handleSetReader }) {

    const [readers, setReaders] = useState([]);

    useEffect(() => {
        async function fetchReaders() {
            try {
                db.collection("readers").get().then((querySnapshot) => {
                    console.log(querySnapshot)
                    querySnapshot.forEach((reader) => {
                        setReaders(current => [...current, reader]);
                    })
                })
            } catch (err) {
                console.log(err);
            }
        }
        fetchReaders();
    }, []);


    return (
        <section className="container">
            {
                readers.length == 0 ? (
                    <h4>Loading...</h4>
                ) : (
                    readers.map((reader) => (
                        <button onClick={() => {handleSetReader(reader.id)}} key={reader.id}>{reader.id}</button>
                    ))
                )
                
            }
        </section>
    );
}

export default ReaderSection;
