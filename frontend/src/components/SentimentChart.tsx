import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { useMemo } from 'react';

type ChartData = {
  date: string;
  sentiment: number;
  price: number;
}

type SentimentChartProps = {
  data: any;
}

const SentimentChart = ({ data }: SentimentChartProps) => {
  const chartData = useMemo(() => {
    if (!data || !data.sentiment) return [];
    
    // Transform the data for Recharts
    const dailySentiment = data.sentiment.daily_sentiment || {};
    const stockHistory = data.sentiment.stock_history || {};
    
    return Object.keys(dailySentiment).map(date => ({
      date,
      sentiment: dailySentiment[date],
      price: stockHistory[date]
    }));
  }, [data]);

  if (!data) return null;

  return (
    <div className="sentiment-chart">
      <h2>{data.symbol} Sentiment Analysis</h2>
      <div className="metrics">
        <div>
          <span>Average Sentiment: </span>
          <strong>{data.sentiment?.average_sentiment?.toFixed(2)}</strong>
        </div>
        <div>
          <span>Trend: </span>
          <strong>{data.sentiment?.trend}</strong>
        </div>
        <div>
          <span>Current Price: </span>
          <strong>{data.current_price} {data.currency}</strong>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line yAxisId="left" type="monotone" dataKey="sentiment" stroke="#8884d8" />
          <Line yAxisId="right" type="monotone" dataKey="price" stroke="#82ca9d" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SentimentChart;
