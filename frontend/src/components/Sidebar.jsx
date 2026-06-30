import { Link } from "react-router-dom";

function Sidebar() {
  return (
    <div
      style={{
        width: "250px",
        height: "100vh",
        background: "#1f2937",
        color: "white",
        padding: "20px",
      }}
    >
      <h2>ERIDSS</h2>

      <hr />

      <p>
        <Link to="/dashboard" style={{ color: "white", textDecoration: "none" }}>
          📊 Dashboard
        </Link>
      </p>

      <p>
        <Link
          to="/documents"
          style={{ color: "white", textDecoration: "none" }}
        >
          📄 Documents
        </Link>
      </p>

      <p>
        <Link
          to="/knowledge-graph"
          style={{ color: "white", textDecoration: "none" }}
        >
          🕸 Knowledge Graph
        </Link>
      </p>

      <p>
        <Link
          to="/risk-analysis"
          style={{ color: "white", textDecoration: "none" }}
        >
          ⚠ Risk Analysis
        </Link>
      </p>

      <p>
        <Link
          to="/settings"
          style={{ color: "white", textDecoration: "none" }}
        >
          ⚙ Settings
        </Link>
      </p>
    </div>
  );
}

export default Sidebar;