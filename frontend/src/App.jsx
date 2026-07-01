import { Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import KnowledgeGraph from "./pages/KnowledgeGraph";
import RiskAnalysis from "./pages/RiskAnalysis";
import Settings from "./pages/Settings";

import MainLayout from "./layouts/MainLayout"; 

function App() {
  return (
    <Routes>
      {/* Public Routes (No Sidebar) */}
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Routes (With Sidebar) */}
      <Route element={<MainLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/knowledge-graph" element={<KnowledgeGraph />} />
        <Route path="/risk-analysis" element={<RiskAnalysis />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}

export default App;s