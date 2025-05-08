import { useState } from "react";
import { useSentimentStream } from "../hooks";
import SentimentChart from "./SentimentChart";

export default function Dashboard() {
  const [symbol, setSymbol] = useState("");
  const snap = useSentimentStream(symbol);

  return (
    <div style={{ maxWidth: 800, margin: "2rem auto", padding: 16 }}>
      <input
        style={{ width: "100%", padding: 8, fontSize: 16 }}
        placeholder="Ticker (e.g. AAPL)"
        value={symbol}
        onChange={e => setSymbol(e.target.value.toUpperCase())}
      />

      {snap ? (
        <>
          <h2 style={{ marginTop: 16 }}>
            {symbol} — {snap.current_price} {snap.currency}
          </h2>
          <SentimentChart snap={snap} />
        </>
      ) : (
        <p style={{ color: "#666", fontStyle: "italic", marginTop: 16 }}>
          Enter a ticker to start streaming…
        </p>
      )}
    </div>
  );
}
