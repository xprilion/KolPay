import '@picocss/pico';
import { myFirebase, db } from "../firebase/firebase";
import React, { useState, useEffect, useReducer } from "react";


function TransactionSection({ reader, action, handleResetUi, handleSetAction, handleUpdateReader }) {

    const [loading, setLoading] = useState(false);
    const [submit, setSubmit] = useState(false);
    const [reader_data, setReaderData] = useState(0);
    const [amount, setAmount] = useState(0);

    useEffect(() => {
        if (submit) {
            async function updateReader() {
                handleUpdateReader(reader, action, parseInt(amount));
                setLoading(true);
                db.collection("readers").doc(reader)
                    .onSnapshot((data) => {
                        setReaderData(data.data());
                    });
            }
            updateReader();
        }
    }, [submit]);

    useEffect(() => {
        if (reader_data.action == "success") {
            setLoading(false);
        }
    }, [reader_data]);

    return (
        <section className="container">
            {
                reader_data?.action == "success" ? (
                    <span>{reader_data.action}</span>
                ) : (
                    <section id="loading">
                        <input
                            aria-disabled={loading ? "true" : "false"}
                            value={amount}
                            onInput={e => setAmount(e.target.value)}
                            type="text"
                            id="amount"
                            name="amount"
                            placeholder="00.00"
                            required />
                        <button aria-busy={loading ? "true" : "false"} onClick={() => { setSubmit(true) }}>{action}</button>
                    </section>
                )

            }

            <br />
            <br />
            <button onClick={() => { handleSetAction(false) }} key="back" className="outline">Back</button>
            <button onClick={() => { handleResetUi() }} key="home" className="secondary">Home</button>
        </section >
    );
}

export default TransactionSection;