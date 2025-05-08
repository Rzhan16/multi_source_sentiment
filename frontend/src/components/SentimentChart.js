import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { LineChart, Line, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useMemo } from "react";
export default function SentimentChart({ snap }) {
    const data = useMemo(() => {
        if (!snap)
            return [];
        return Object.keys(snap.daily_sentiment).map(date => ({
            date,
            sentiment: snap.daily_sentiment[date],
            mean: snap.rolling_mean[date],
            ciLo: snap.ci_lower[date],
            ciHi: snap.ci_upper[date],
            price: snap.stock_history[date]?.Close
        }));
    }, [snap]);
    return (_jsx(ResponsiveContainer, { width: "100%", height: 450, children: _jsxs(LineChart, { data: data, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3" }), _jsx(XAxis, { dataKey: "date" }), _jsx(YAxis, { yAxisId: "left", domain: [-1, 1] }), _jsx(YAxis, { yAxisId: "right", orientation: "right" }), _jsx(Tooltip, {}), _jsx(Area, { yAxisId: "left", dataKey: "ciHi", stroke: "none", fill: "rgba(128,128,128,0.2)", isAnimationActive: false }), _jsx(Area, { yAxisId: "left", dataKey: "ciLo", stroke: "none", fill: "#ffffff", isAnimationActive: false }), _jsx(Line, { yAxisId: "left", dataKey: "sentiment", stroke: "#8884d8", dot: false }), _jsx(Line, { yAxisId: "left", dataKey: "mean", stroke: "#0044aa", dot: false }), _jsx(Line, { yAxisId: "right", dataKey: "price", stroke: "#d62728", dot: false })] }) }));
}
