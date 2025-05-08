// frontend/src/components/Dashboard.tsx
import { useState } from "react";
import { useSentimentStream } from "../hooks";
import SentimentChart from "./SentimentChart";

export default function Dashboard() {
  const [input, setInput]   = useState("");
  const [symbol, setSymbol] = useState("");
  const snap = useSentimentStream(symbol);

  return (
    <div style={{ maxWidth: 800, margin: "2rem auto", padding: 16 }}>
      <input
        style={{ width: "100%", padding: 8, fontSize: 16 }}
        placeholder="Ticker (e.g. AAPL)"
        value={input}
        onChange={e => setInput(e.target.value.toUpperCase())}
        onKeyDown={e => {
          if (e.key === "Enter" && input.trim()) {
            setSymbol(input.trim());
          }
        }}
      />

      {!symbol ? (
        <p className="loading">
          Press Enter to start streaming…
        </p>
      ) : snap ? (
        <>
          <h2 style={{ marginTop: 16 }}>
            {symbol} — {snap.current_price} {snap.currency}
          </h2>
          <SentimentChart snap={snap} />
        </>
      ) : (
        <p className="loading">
          Loading data for “{symbol}”…
        </p>
      )}
    </div>
  );
}
