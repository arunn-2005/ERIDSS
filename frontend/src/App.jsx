import "./App.css";

import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import KnowledgeGraph from "./pages/KnowledgeGraph";
import RiskAnalysis from "./pages/RiskAnalysis";
import Settings from "./pages/Settings";

import { Routes, Route, useLocation } from "react-router-dom";

function App() {
  const location = useLocation();

  // Hide sidebar on Login and Register pages
  const hideSidebar =
    location.pathname === "/" ||
    location.pathname === "/login" ||
    location.pathname === "/register";

  return (
    <div className="app-container">
      {!hideSidebar && <Sidebar />}

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
          <Route path="/risk-analysis" element={<RiskAnalysis />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;