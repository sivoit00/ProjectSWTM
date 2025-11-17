import { Outlet } from "react-router-dom";
import Sidebar from "../components/common/Sidebar";

export default function MainLayout() {
  return (
    <div className="flex h-screen bg-gray-900">
      <Sidebar />
      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  );
}
