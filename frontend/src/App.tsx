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
