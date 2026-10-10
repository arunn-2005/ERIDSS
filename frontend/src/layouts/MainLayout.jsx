import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import "../styles/ERIDSSTheme.css";

function MainLayout() {
  return (
    <div className="eridss-app-layout">
      <Sidebar />
      <div className="eridss-main-content fade-in">
        <Outlet />
      </div>
    </div>
  );
}

export default MainLayout;