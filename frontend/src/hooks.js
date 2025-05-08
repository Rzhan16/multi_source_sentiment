// frontend/src/hooks.ts
import { useEffect, useRef, useState } from "react";
export function useSentimentStream(symbol) {
    const [snap, setSnap] = useState(null);
    const wsRef = useRef(null);
    useEffect(() => {
        // if we clear the symbol, close any existing socket & reset
        if (!symbol) {
            wsRef.current?.close();
            setSnap(null);
            return;
        }
        // close previous socket before opening a new one
        wsRef.current?.close();
        // 1) pick up VITE_WS_URL at build time, else default to same host
        const base = import.meta.env.VITE_WS_URL
            ? // transform http:// → ws://, https:// → wss://
                import.meta.env.VITE_WS_URL.replace(/^http/, "ws")
            : window.location.origin.replace(/^http/, "ws");
        const url = `${base}/ws/${symbol}`;
        console.log("Connecting to WS:", url);
        const ws = new WebSocket(url);
        ws.onopen = () => console.log("WS open");
        ws.onmessage = (e) => setSnap(JSON.parse(e.data));
        ws.onerror = (err) => console.error("WS error", err);
        ws.onclose = () => console.log("WS closed");
        wsRef.current = ws;
        return () => { ws.close(); };
    }, [symbol]);
    return snap;
}
