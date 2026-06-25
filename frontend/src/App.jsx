import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div style={{ padding: "20px", flex: 1 }}>
        <Dashboard />
      </div>
    </div>
  );
}

export default App;