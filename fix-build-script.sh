#!/bin/bash
# Fix for the build issues found in the stock sentiment analysis app

# 1. Create a root package.json if it doesn't exist
if [ ! -f package.json ]; then
  echo "Creating root package.json"
  cat > package.json << 'EOF'
{
  "name": "stock-sentiment-analysis",
  "version": "1.0.0",
  "description": "Stock sentiment analysis application",
  "scripts": {
    "build": "cd frontend && npm install && npm run build",
    "start": "node server.js"
  },
  "engines": {
    "node": ">=16.0.0"
  }
}
EOF
fi

# 2. Fix the TypeScript configuration in the frontend
cd frontend || exit 1

# Install required React type dependencies
npm install --save-dev @types/react @types/react-dom typescript

# Create proper tsconfig.json if it doesn't exist or has issues
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    
    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    
    /* Linting */
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF

# Ensure basic tsconfig.node.json exists
cat > tsconfig.node.json << 'EOF'
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
EOF

# Update package.json to ensure React types are correctly specified
if [ -f package.json ]; then
  # Check if React is already in dependencies
  if ! grep -q '"react"' package.json; then
    # Add react and react-dom if missing
    npx -y json -I -f package.json -e "this.dependencies=this.dependencies||{};this.dependencies.react='^18.2.0';this.dependencies['react-dom']='^18.2.0'"
  fi
  
  # Add TypeScript dependencies if missing
  npx -y json -I -f package.json -e "this.devDependencies=this.devDependencies||{};this.devDependencies.typescript='^5.0.0';this.devDependencies['@types/react']='^18.2.0';this.devDependencies['@types/react-dom']='^18.2.0'"
fi

# Create a proper vite.config.ts file
cat > vite.config.ts << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true
      }
    }
  }
})
EOF

# Ensure React imports are correct in App.tsx
if [ -f src/App.tsx ]; then
  cat > src/App.tsx.tmp << 'EOF'
import { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Stock Sentiment Analyzer</h1>
      </header>
      <Dashboard />
    </div>
  );
}

export default App;
EOF
  mv src/App.tsx.tmp src/App.tsx
fi

# Fix main.tsx
if [ -f src/main.tsx ]; then
  cat > src/main.tsx.tmp << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
EOF
  mv src/main.tsx.tmp src/main.tsx
fi

# Fix Dashboard component
if [ -f src/components/Dashboard.tsx ]; then
  cat > src/components/Dashboard.tsx.tmp << 'EOF'
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
EOF
  mv src/components/Dashboard.tsx.tmp src/components/Dashboard.tsx
fi

# Fix SentimentChart component
if [ -f src/components/SentimentChart.tsx ]; then
  cat > src/components/SentimentChart.tsx.tmp << 'EOF'
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
EOF
  mv src/components/SentimentChart.tsx.tmp src/components/SentimentChart.tsx
fi

# Fix hooks.ts
if [ -f src/hooks.ts ]; then
  cat > src/hooks.ts.tmp << 'EOF'
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
EOF
  mv src/hooks.ts.tmp src/hooks.ts
fi

echo "Build fix script completed!"chmod +x fix-build-script.sh


