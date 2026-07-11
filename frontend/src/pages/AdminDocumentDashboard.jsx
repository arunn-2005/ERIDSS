import { useEffect, useState } from "react";
import { getDocumentDashboard } from "../services/adminService";
import "../styles/AdminDashboard.css";

function AdminDocumentDashboard() {

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const data = await getDocumentDashboard();
      console.log(data);
      setDashboard(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <h2>Loading...</h2>;
  }

  return (
    <div className="admin-dashboard">

      <div className="dashboard-header">
        <div>
          <h1>Document Dashboard</h1>
          <p>Enterprise Risk Intelligence & Decision Support System</p>
        </div>
      </div>

      <div className="stats-grid">

        <div className="stat-card">
          <h3>Total Documents</h3>
          <h2>{dashboard.total_documents}</h2>
        </div>

        <div className="stat-card">
          <h3>Uploaded</h3>
          <h2>{dashboard.uploaded_documents}</h2>
        </div>

        <div className="stat-card">
          <h3>Processing</h3>
          <h2>{dashboard.processing_documents}</h2>
        </div>

        <div className="stat-card">
          <h3>Processed</h3>
          <h2>{dashboard.processed_documents}</h2>
        </div>

        <div className="stat-card">
          <h3>Failed</h3>
          <h2>{dashboard.failed_documents}</h2>
        </div>

      </div>

      <div className="recent-users">

        <h2>Recent Documents</h2>

        <table>

          <thead>
            <tr>
              <th>Filename</th>
              <th>User</th>
              <th>Status</th>
              <th>Uploaded</th>
            </tr>
          </thead>

          <tbody>

            {dashboard.recent_documents.map((doc) => (

              <tr key={doc.id}>

                <td>{doc.filename}</td>

                <td>{doc.username}</td>

                <td>{doc.status}</td>

                <td>
                  {new Date(doc.uploaded_at).toLocaleString()}
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default AdminDocumentDashboard;