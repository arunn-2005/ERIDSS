import { useEffect, useState } from "react";
import { getDashboard } from "../services/adminService";
import "../styles/AdminDashboard.css";

function AdminDashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
  try {
    const data = await getDashboard();

    console.log(data);          // Add this
    console.log(data.recent_users);

    setDashboard(data);
  } catch (error) {
    console.error("Failed to fetch dashboard:", error);
  } finally {
    setLoading(false);
  }
};

  if (loading) {
    return <h2>Loading Dashboard...</h2>;
  }

  return (
    <div className="admin-dashboard">

      <div className="dashboard-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p>Enterprise Risk Intelligence & Decision Support System</p>
        </div>
      </div>

      <div className="stats-grid">

        <div className="stat-card">
    <h3>Total Users</h3>
    <h2>{dashboard.total_users}</h2>
    <span>Registered Accounts</span>
</div>

        <div className="stat-card">
    <h3>Admin Users</h3>
    <h2>{dashboard.total_admins}</h2>
    <span>System Administrators</span>
</div>

        <div className="stat-card">
    <h3>Normal Users</h3>
    <h2>{dashboard.total_normal_users}</h2>
    <span>Standard Accounts</span>
</div>
<div className="stat-card">
    <h3>System Status</h3>
    <h2>Online</h2>
    <span>All Services Operational</span>
</div>
      </div>

      <div className="recent-users">

        <h2>Recently Registered Users</h2>

        <table>

          <thead>
            <tr>
              <th>Username</th>
              <th>Email</th>
              <th>Role</th>
              <th>Joined</th>
            </tr>
          </thead>

          <tbody>

            {dashboard.recent_users.map((user) => (
              <tr key={user.id}>
                <td>{user.username}</td>
                <td>{user.email}</td>
                <td>
  <span
    className={
      user.role === "Admin"
        ? "role admin"
        : "role user"
    }
  >
    {user.role}
  </span>
</td>
                <td>
                  {new Date(user.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default AdminDashboard;