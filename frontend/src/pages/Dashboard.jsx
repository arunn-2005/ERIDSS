import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getDashboardStats } from "../services/documentService";
import "../styles/Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const [stats, setStats] = useState({
    documents: 0,
    entities: 0,
    relationships: 0,
    riskAlerts: 0,
  });
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const data = await getDashboardStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to load dashboard stats:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    
    // Auto-refresh stats when window regains focus or every 15 seconds
    // const interval = setInterval(fetchStats, 15000);
    // return () => clearInterval(interval);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    navigate("/"); // Redirects to Login page
  };

  return (
    <div className="dashboard">

      <div className="dashboard-header">
        <div>
          <h1>Enterprise Risk Dashboard</h1>
          <p>
            Monitor document processing, knowledge graph generation and risk
            intelligence from a single workspace.
          </p>
        </div>

        <div className="header-actions">
          <button className="eridss-btn-primary" onClick={() => navigate("/documents")}>
            + Upload Documents
          </button>

          <button className="eridss-btn-danger" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="stats-grid">

        <div className="stat-card">
          <span className="stat-title">Documents</span>
          <h2>{loading ? "..." : stats.documents}</h2>
          <p>Uploaded Documents</p>
        </div>

        <div className="stat-card">
          <span className="stat-title">Entities</span>
          <h2>{loading ? "..." : stats.entities}</h2>
          <p>Entities Extracted</p>
        </div>

        <div className="stat-card">
          <span className="stat-title">Relationships</span>
          <h2>{loading ? "..." : stats.relationships}</h2>
          <p>Graph Connections</p>
        </div>

        <div className="stat-card">
          <span className="stat-title">Risk Alerts</span>
          <h2>{loading ? "..." : stats.riskAlerts}</h2>
          <p>Detected Risks</p>
        </div>

      </div>

      <div className="dashboard-content">

        <div className="panel large-panel">
          <h3>Recent Activity</h3>

          <div className="empty-state">
            {stats.documents === 0 ? "No documents processed yet." : "Recent document activity updated."}
          </div>
        </div>

        <div className="panel">
          <h3>Knowledge Graph</h3>

          <div className="empty-state">
            {stats.relationships === 0 ? "Graph visualization will appear here." : "Knowledge graph connected."}
          </div>
        </div>

      </div>

    </div>
  );
}

export default Dashboard;