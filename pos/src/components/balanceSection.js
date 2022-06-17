import '@picocss/pico';
import { myFirebase, db } from "../firebase/firebase";
import React, { useState, useEffect, useReducer } from "react";


function BalanceSection({ reader, handleResetUi, handleSetAction, handleUpdateReader }) {

    const [loading, setLoading] = useState(true);
    const [reader_data, setReaderData] = useState(0);

    useEffect(() => {
        async function updateReader() {
            handleUpdateReader(reader, "balance", 0);
            db.collection("readers").doc(reader)
            .onSnapshot((data) => {
                setReaderData(data.data());
            });
        }
        updateReader();
    }, []);

    useEffect(() => {
        if (reader_data.action == "success" || reader_data.action == "failed") {
            setLoading(false);
        }
    }, [reader_data]);


    return (
        <section className="container">
            { loading ? ( <span>Loading...</span> ) : ( <span>Balance: {reader_data?.amount}</span> ) }
            <br />
            <br />
            <button onClick={() => {handleSetAction(false)}} key="back" className="outline">Back</button>
            <button onClick={() => {handleResetUi()}} key="home" className="secondary">Home</button>
        </section>
    );
}

export default BalanceSection;