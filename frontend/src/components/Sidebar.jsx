import { Link, useLocation } from "react-router-dom";
import "../styles/ERIDSSTheme.css";

function Sidebar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="eridss-sidebar">
      <div className="eridss-sidebar-brand">ERIDSS</div>
      <p style={{ color: "#94a3b8", fontSize: "13px", marginBottom: "15px" }}>
        Enterprise Risk Intelligence
      </p>

      <hr />

      <div className="eridss-sidebar-links">
        <Link
          to="/dashboard"
          className={`eridss-sidebar-link ${isActive("/dashboard") ? "active" : ""}`}
        >
          📊 Dashboard
        </Link>

        <Link
          to="/documents"
          className={`eridss-sidebar-link ${isActive("/documents") ? "active" : ""}`}
        >
          📄 Documents
        </Link>

        <Link
          to="/knowledge-graph"
          className={`eridss-sidebar-link ${isActive("/knowledge-graph") ? "active" : ""}`}
        >
          🕸 Knowledge Graph
        </Link>

        <Link
          to="/risk-analysis"
          className={`eridss-sidebar-link ${isActive("/risk-analysis") ? "active" : ""}`}
        >
          ⚠ Risk Analysis
        </Link>

        <Link
          to="/settings"
          className={`eridss-sidebar-link ${isActive("/settings") ? "active" : ""}`}
        >
          ⚙ Settings
        </Link>
      </div>
    </div>
  );
}

export default Sidebar;