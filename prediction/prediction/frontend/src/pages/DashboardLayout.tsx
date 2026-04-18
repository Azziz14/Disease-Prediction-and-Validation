import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/common/Sidebar';

const DashboardLayout: React.FC = () => {
  return (
    <div className="min-h-screen flex relative" style={{ background: 'transparent' }}>
      <Sidebar />
      <div className="flex-1 ml-60 p-8 overflow-y-auto">
        <Outlet />
      </div>
    </div>
  );
};

export default DashboardLayout;
