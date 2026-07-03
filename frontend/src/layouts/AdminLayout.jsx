import { Outlet } from "react-router-dom";
import AdminSidebar from "../components/Admin/AdminSidebar";

function AdminLayout() {
  return (
    <div style={{ display: "flex" }}>
      <AdminSidebar />

      <div
        style={{
          marginLeft: "250px",
          width: "100%",
          padding: "30px"
        }}
      >
        <Outlet />
      </div>
    </div>
  );
}

export default AdminLayout;