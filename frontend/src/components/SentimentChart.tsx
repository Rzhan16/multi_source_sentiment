import {
    LineChart, Line, Area, XAxis, YAxis,
    CartesianGrid, Tooltip, ResponsiveContainer
  } from "recharts";
  import { Snapshot } from "../hooks";
  import { useMemo } from "react";
  
  export default function SentimentChart({ snap }: { snap: Snapshot }) {
    const data = useMemo(() => {
      if (!snap) return [];
      return Object.keys(snap.daily_sentiment).map(date => ({
        date,
        sentiment: snap.daily_sentiment[date],
        mean:      snap.rolling_mean[date],
        ciLo:      snap.ci_lower[date],
        ciHi:      snap.ci_upper[date],
        price:     snap.stock_history[date]?.Close
      }));
    }, [snap]);
  
    return (
      <ResponsiveContainer width="100%" height={450}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" domain={[-1, 1]} />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Area
            yAxisId="left"
            dataKey="ciHi"
            stroke="none"
            fill="rgba(128,128,128,0.2)"
            isAnimationActive={false}
          />
          <Area
            yAxisId="left"
            dataKey="ciLo"
            stroke="none"
            fill="#ffffff"
            isAnimationActive={false}
          />
          <Line yAxisId="left" dataKey="sentiment" stroke="#8884d8" dot={false} />
          <Line yAxisId="left" dataKey="mean"      stroke="#0044aa" dot={false} />
          <Line yAxisId="right" dataKey="price"    stroke="#d62728" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    );
  }
  