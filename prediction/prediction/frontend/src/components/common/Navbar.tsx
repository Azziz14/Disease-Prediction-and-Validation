import React, { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { LogOut, User, Zap } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Navbar: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const linkClass = (isActive: boolean) =>
    `relative text-sm font-bold uppercase tracking-wider transition-all duration-300 py-1 ${
      isActive
        ? 'text-[var(--neon-blue)] neon-text-blue'
        : 'text-gray-400 hover:text-white'
    }`;

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 w-full transition-all duration-500 ${
        scrolled
          ? 'bg-[var(--cyber-dark)]/90 backdrop-blur-xl border-b border-[var(--cyber-border)] shadow-[0_4px_30px_rgba(0,243,255,0.1)] py-3'
          : 'bg-transparent py-5'
      }`}
    >
      <div className="container mx-auto px-6 max-w-6xl flex items-center justify-between">
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-3 group">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-black border border-[var(--neon-blue)] text-[var(--neon-blue)] group-hover:shadow-[0_0_15px_var(--neon-blue)] transition-all duration-300">
            <Zap size={18} strokeWidth={2.5} />
          </div>
          <span className="text-lg font-extrabold text-white tracking-tight uppercase">
            Care<span className="text-[var(--neon-blue)]">Predict</span>
          </span>
        </NavLink>

        {/* Navigation */}
        <div className="flex items-center gap-8">
          <nav className="hidden md:flex items-center gap-7" aria-label="Main navigation">
            <NavLink to="/" end className={({ isActive }) => linkClass(isActive)}>
              Home
            </NavLink>

            {isAuthenticated && (
              <NavLink
                to={user?.role === 'admin' ? '/admin' : '/dashboard'}
                className={({ isActive }) => linkClass(isActive)}
              >
                Dashboard
              </NavLink>
            )}

            <NavLink to="/diagnosis" className={({ isActive }) => linkClass(isActive)}>
              Diagnosis
            </NavLink>
          </nav>

          {/* Auth */}
          <div className="flex items-center gap-4 ml-4">
            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <div className="hidden sm:flex items-center gap-2 text-sm text-gray-400">
                  <div className="h-7 w-7 rounded-full border border-[var(--neon-purple)] flex items-center justify-center">
                    <User size={14} className="text-[var(--neon-purple)]" />
                  </div>
                  <span className="font-medium">{user?.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-red-400 transition-colors"
                >
                  <LogOut size={15} />
                </button>
              </div>
            ) : (
              <>
                <NavLink
                  to="/login"
                  className="text-sm font-bold text-gray-400 hover:text-white transition-colors uppercase tracking-wider"
                >
                  Log in
                </NavLink>
                <NavLink
                  to="/register"
                  className="text-sm font-extrabold px-6 py-2.5 bg-[var(--neon-blue)] text-black rounded-full hover:bg-white hover:shadow-[0_0_20px_var(--neon-blue)] transition-all duration-300 uppercase tracking-wider"
                >
                  Get Started
                </NavLink>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
