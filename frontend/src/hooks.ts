import { useEffect, useRef, useState } from "react";

export interface Snapshot {
  ts: string;
  current_price: number;
  currency: string;
  daily_sentiment: Record<string, number>;
  rolling_mean: Record<string, number>;
  ci_lower: Record<string, number>;
  ci_upper: Record<string, number>;
  stock_history: Record<string, { Close: number }>;
}

export function useSentimentStream(symbol: string) {
  const [snap, setSnap] = useState<Snapshot | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!symbol) return;
    const ws = new WebSocket(`${import.meta.env.VITE_WS_URL}/ws/${symbol}`);
    ws.onmessage = (e) => setSnap(JSON.parse(e.data));
    wsRef.current = ws;
    return () => ws.close();
  }, [symbol]);

  return snap;
}
