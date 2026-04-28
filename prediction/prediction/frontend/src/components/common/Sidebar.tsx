import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, History, Activity, LogOut, Shield, Sparkles } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar: React.FC = () => {
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const linkClass = (isActive: boolean) =>
    `flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all duration-200 ${
      isActive
        ? 'bg-[linear-gradient(90deg,rgba(0,243,255,0.18),rgba(176,91,255,0.10))] text-white border border-[rgba(0,243,255,0.28)] shadow-[0_0_20px_rgba(0,243,255,0.08)]'
        : 'text-white/68 hover:bg-white/[0.06] hover:text-white border border-transparent'
    }`;

  return (
    <div className="hidden lg:flex flex-col w-72 min-h-screen fixed left-0 top-0 p-4 z-40">
      <div className="flex flex-col h-full rounded-[28px] border border-[rgba(0,243,255,0.14)] bg-[linear-gradient(180deg,rgba(5,8,18,0.92),rgba(7,10,20,0.84))] backdrop-blur-xl shadow-[0_0_40px_rgba(0,243,255,0.05)] pt-6">
        <div className="px-5 mb-8 flex items-center gap-3">
          <div className="flex justify-center items-center h-11 w-11 rounded-2xl border border-[rgba(0,243,255,0.28)] bg-[rgba(0,243,255,0.10)] text-[var(--neon-blue)] shadow-[0_0_22px_rgba(0,243,255,0.12)]">
            <Shield size={20} strokeWidth={2.5} />
          </div>
          <div className="flex flex-col">
            <span className="font-display font-bold text-base text-white tracking-tight">CarePredict</span>
            <span className="text-[10px] text-white/45 tracking-[0.22em] font-medium uppercase">
              {isAdmin ? 'System Command' : 'Clinical Interface'}
            </span>
          </div>
        </div>

        <div className="mx-5 mb-6 rounded-3xl border border-[rgba(255,255,255,0.08)] bg-white/[0.04] p-4">
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.24em] text-cyan-300/75 font-bold">
            <Sparkles size={12} />
            Active Workspace
          </div>
          <p className="mt-3 text-sm text-white/72 leading-relaxed">
            {isAdmin ? 'Oversee platform intelligence, patient traffic, and risk signals.' : 'Launch diagnoses, inspect history, and use the upgraded voice workflow.'}
          </p>
        </div>

        <nav className="flex-1 px-3 space-y-2">
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

        <div className="p-4 mt-auto border-t border-white/10">
          <div className="flex items-center gap-3 mb-3 px-1">
            <div className="h-10 w-10 rounded-2xl bg-[rgba(0,243,255,0.10)] border border-[rgba(0,243,255,0.16)] flex items-center justify-center text-cyan-200 font-bold text-sm">
              {user?.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-medium text-white truncate">{user?.name}</span>
              <span className="text-[10px] text-white/45 uppercase tracking-[0.22em] font-medium">{user?.role}</span>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 w-full px-3 py-3 text-sm font-medium text-white/60 hover:text-red-300 hover:bg-red-500/10 rounded-2xl transition-colors"
          >
            <LogOut size={15} /> Sign Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
