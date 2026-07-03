import { NavLink, useNavigate } from "react-router-dom";
import "../../styles/AdminSidebar.css";

function AdminSidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/");
  };

  return (
    <div className="admin-sidebar">
      <div className="admin-logo">
        <h2>ERIDSS</h2>
        <span>Admin Panel</span>
      </div>

      <nav className="admin-nav">

        <NavLink to="/admin/dashboard">
          Dashboard
        </NavLink>

        <NavLink to="/admin/users">
          Users
        </NavLink>

        <NavLink to="/admin/documents">
          Documents
        </NavLink>

        <NavLink to="/admin/system-logs">
          System Logs
        </NavLink>

        <NavLink to="/admin/settings">
          Settings
        </NavLink>

      </nav>

      <button className="logout-button" onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}

export default AdminSidebar;