import { useState, useEffect } from 'react';
import SentimentChart from './SentimentChart';
import { useSentimentData } from '../hooks';

type StockData = {
  symbol: string;
  sentiment: number;
  trend: string;
  price: number;
}

const Dashboard = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [includeTwitter, setIncludeTwitter] = useState(true);
  const { data, loading, error } = useSentimentData(symbol, includeTwitter);

  const handleSymbolChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSymbol(e.target.value.toUpperCase());
  };

  const handleTwitterToggle = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIncludeTwitter(e.target.checked);
  };

  return (
    <div className="dashboard">
      <div className="controls">
        <label>
          Stock Symbol:
          <input type="text" value={symbol} onChange={handleSymbolChange} />
        </label>
        <label>
          Include Twitter:
          <input type="checkbox" checked={includeTwitter} onChange={handleTwitterToggle} />
        </label>
      </div>
      
      {loading && <div>Loading...</div>}
      {error && <div className="error">{error}</div>}
      
      {data && <SentimentChart data={data} />}
    </div>
  );
};

export default Dashboard;
