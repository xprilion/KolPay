import '@picocss/pico';

function MenuSection({handleSetAction}) {
    return (
        <section className="container">           
            <button onClick={() => {handleSetAction("debit")}} key="debit" >Debit</button>
            <button onClick={() => {handleSetAction("credit")}} key="credit" className="outline">Credit</button>
            <button onClick={() => {handleSetAction("balance")}} key="balance" className="outline">Balance</button>
        </section>
    );
}

export default MenuSection;
