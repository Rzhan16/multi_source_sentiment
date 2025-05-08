import Dashboard from "./components/Dashboard";

export default function App() {
  return (
    <main>
      <header style={{ textAlign: "center", margin: "2rem 0" }}>
        <h1>Stock Sentiment Dashboard</h1>
      </header>
      <Dashboard />
    </main>
  );
}