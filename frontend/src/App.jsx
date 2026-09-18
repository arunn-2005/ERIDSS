import { Routes, Route } from "react-router-dom";

// Public Pages
import Login from "./pages/Login";
import Register from "./pages/Register";

// User Pages
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import KnowledgeGraph from "./pages/KnowledgeGraph";
import RiskAnalysis from "./pages/RiskAnalysis";
import Settings from "./pages/Settings";

// Admin Pages
import AdminDashboard from "./pages/AdminDashboard";
import UserManagement from "./pages/UserManagement";
import AdminDocuments from "./pages/AdminDocuments";
import SystemLogs from "./pages/SystemLogs";
import AdminSettings from "./pages/AdminSettings";
import AdminDocumentDashboard from "./pages/AdminDocumentDashboard";

// Layouts
import MainLayout from "./layouts/MainLayout";
import AdminLayout from "./layouts/AdminLayout";

function App() {
  return (
    <Routes>

      {/* ---------- Public ---------- */}
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* ---------- User ---------- */}
      <Route element={<MainLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/documents" element={<Documents />} />
        {/* Supports /knowledge-graph and /knowledge-graph/:documentId */}
        <Route path="/knowledge-graph/:documentId?" element={<KnowledgeGraph />} />
        <Route path="/risk-analysis" element={<RiskAnalysis />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      {/* ---------- Admin ---------- */}
      <Route element={<AdminLayout />}>
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<UserManagement />} />
        <Route path="/admin/documents" element={<AdminDocuments />} />
        <Route path="/admin/system-logs" element={<SystemLogs />} />
        <Route path="/admin/documents/dashboard" element={<AdminDocumentDashboard />} />
        <Route path="/admin/settings" element={<AdminSettings />} />
      </Route>

    </Routes>
  );
}

export default App;