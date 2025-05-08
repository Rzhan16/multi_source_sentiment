import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
// frontend/src/components/Dashboard.tsx
import { useState } from "react";
import { useSentimentStream } from "../hooks";
import SentimentChart from "./SentimentChart";
export default function Dashboard() {
    const [input, setInput] = useState("");
    const [symbol, setSymbol] = useState("");
    const snap = useSentimentStream(symbol);
    return (_jsxs("div", { style: { maxWidth: 800, margin: "2rem auto", padding: 16 }, children: [_jsx("input", { style: { width: "100%", padding: 8, fontSize: 16 }, placeholder: "Ticker (e.g. AAPL)", value: input, onChange: e => setInput(e.target.value.toUpperCase()), onKeyDown: e => {
                    if (e.key === "Enter" && input.trim()) {
                        setSymbol(input.trim());
                    }
                } }), !symbol ? (_jsx("p", { className: "loading", children: "Press Enter to start streaming\u2026" })) : snap ? (_jsxs(_Fragment, { children: [_jsxs("h2", { style: { marginTop: 16 }, children: [symbol, " \u2014 ", snap.current_price, " ", snap.currency] }), _jsx(SentimentChart, { snap: snap })] })) : (_jsxs("p", { className: "loading", children: ["Loading data for \u201C", symbol, "\u201D\u2026"] }))] }));
}
