import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/common/Sidebar';

const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex relative overflow-hidden" style={{ background: 'transparent' }}>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(0,243,255,0.10),transparent_26%),radial-gradient(circle_at_bottom_right,rgba(176,91,255,0.10),transparent_22%)]" />
      <Sidebar />
      <div className="flex-1 lg:ml-72 p-4 md:p-6 lg:p-8 overflow-y-auto relative z-10">
        <div className="rounded-[30px] border border-[rgba(255,255,255,0.08)] bg-[rgba(7,10,18,0.45)] backdrop-blur-sm min-h-[calc(100vh-2rem)] p-4 md:p-6 lg:p-8 shadow-[inset_0_0_40px_rgba(255,255,255,0.02)]">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;
