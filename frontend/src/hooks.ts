import { useState, useEffect } from 'react';

// Adjust the API URL based on environment
const API_URL = import.meta.env.VITE_API_URL || '/api';
const WS_URL = import.meta.env.VITE_WS_URL || window.location.origin.replace('http', 'ws');

export const useSentimentData = (symbol: string, includeTwitter: boolean = true) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`${API_URL}/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            stock_symbol: symbol,
            window: 5,
            twitter: includeTwitter
          })
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        setData({
          ...result,
          symbol
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };
    
    if (symbol) {
      fetchData();
    }
  }, [symbol, includeTwitter]);
  
  return { data, loading, error };
};
