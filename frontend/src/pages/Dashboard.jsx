import { useNavigate } from "react-router-dom";
import "../styles/Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
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
          <button className="upload-btn">
            + Upload Documents
          </button>

          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="stats-grid">

        <div className="stat-card">
          <span className="stat-title">Documents</span>
          <h2>5</h2>
          <p>Uploaded Documents</p>
        </div>

        <div className="stat-card">
          <span className="stat-title">Entities</span>
          <h2>118</h2>
          <p>Entities Extracted</p>
        </div>

        <div className="stat-card">
          <span className="stat-title">Relationships</span>
          <h2>0</h2>
          <p>Graph Connections</p>
        </div>

        <div className="stat-card">
          <span className="stat-title">Risk Alerts</span>
          <h2>0</h2>
          <p>Detected Risks</p>
        </div>

      </div>

      <div className="dashboard-content">

        <div className="panel large-panel">
          <h3>Recent Activity</h3>

          <div className="empty-state">
            No documents processed yet.
          </div>
        </div>

        <div className="panel">
          <h3>Knowledge Graph</h3>

          <div className="empty-state">
            Graph visualization will appear here.
          </div>
        </div>

      </div>

    </div>
  );
}

export default Dashboard;