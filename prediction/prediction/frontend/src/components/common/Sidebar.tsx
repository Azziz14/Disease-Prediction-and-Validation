import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, History, Activity, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar: React.FC = () => {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const linkClass = (isActive: boolean) =>
    `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
      isActive
        ? 'bg-brand/5 text-brand border border-brand/10'
        : 'text-text-secondary hover:bg-surface-hover hover:text-text-primary border border-transparent'
    }`;

  return (
    <div className="flex flex-col w-60 bg-white border-r border-border-subtle min-h-screen fixed left-0 top-0 pt-6 z-40">
      
      {/* Brand */}
      <div className="px-5 mb-8 flex items-center gap-2.5">
        <div className="flex justify-center items-center h-9 w-9 bg-brand text-white rounded-xl">
          <Activity size={20} strokeWidth={2.5} />
        </div>
        <div className="flex flex-col">
          <span className="font-display font-bold text-sm text-text-primary tracking-tight">CarePredict</span>
          <span className="text-[10px] text-text-muted tracking-wide font-medium uppercase">
            {isAdmin ? 'Admin' : 'Clinical'}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1">
        <NavLink
          to={isAdmin ? '/admin' : '/dashboard'}
          className={({ isActive }) => linkClass(isActive)}
        >
          <LayoutDashboard size={18} />
          Dashboard
        </NavLink>

        {!isAdmin && (
          <NavLink to="/diagnosis" className={({ isActive }) => linkClass(isActive)}>
            <Activity size={18} />
            New Diagnosis
          </NavLink>
        )}

        <NavLink to="/history" className={({ isActive }) => linkClass(isActive)}>
          <History size={18} />
          {isAdmin ? 'All Records' : 'History'}
        </NavLink>
      </nav>

      {/* Profile Footer */}
      <div className="p-4 mt-auto border-t border-border-subtle">
        <div className="flex items-center gap-3 mb-3 px-1">
          <div className="h-8 w-8 rounded-full bg-brand-light flex items-center justify-center text-brand font-bold text-xs">
            {user?.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-medium text-text-primary truncate">{user?.name}</span>
            <span className="text-[10px] text-text-muted uppercase tracking-wider font-medium">{user?.role}</span>
          </div>
        </div>
        
        <button 
          onClick={handleLogout}
          className="flex items-center gap-2 w-full px-3 py-2 text-sm font-medium text-text-muted hover:text-health-danger hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut size={15} /> Sign Out
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
