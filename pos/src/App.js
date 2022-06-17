import '@picocss/pico';
import React, { useState, useEffect, useReducer } from "react";
import TopSection from './components/topSection';
import FooterSection from './components/footerSection';
import ReaderSection from './components/readerSection';
import MenuSection from './components/menuSection';
import TransactionSection from './components/transactionSection';
import BalanceSection from './components/balanceSection';

import { myFirebase, db } from "./firebase/firebase";

function App() {

  const [reader, setReader] = useState(false);
  const [action, setAction] = useState(false);

  const handleSetReader = (reader_id) => { setReader(reader_id); }
  const handleSetAction = (action_name) => { setAction(action_name); }
  const handleResetUi = () => { setReader(false); setAction(false); }

  const handleUpdateReader = (reader_id, action_name, amount = false) => {
    try {
      db.collection("readers").doc(reader_id).set({
        action: action_name,
        card: false,
        amount: amount
      });
    } catch (err) {
      console.log(err);
    }
  }

  useEffect(() => {
    console.log(reader);
  }, [reader]);

  useEffect(() => {
    console.log(action);
  }, [action]);

  return (
    <div>
      <TopSection />
      {
        reader ? (
          action ? (
            action == "balance" ? (
              <BalanceSection
                reader={reader}
                handleResetUi={handleResetUi}
                handleSetAction={handleSetAction}
                handleUpdateReader={handleUpdateReader}
              />
            ) : (
              <TransactionSection
                reader={reader}
                action={action}
                handleResetUi={handleResetUi}
                handleSetAction={handleSetAction}
                handleUpdateReader={handleUpdateReader}
              />
            )
          ) : (
            <MenuSection handleSetAction={handleSetAction} />
          )
        ) : (
          <ReaderSection handleSetReader={handleSetReader} />
        )
      }
      <FooterSection />
    </div>
  );
}

export default App;
