import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation, NavLink } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth, Role } from '../context/AuthContext';
import { Zap, Mail, Lock, User as UserIcon, ChevronDown, ArrowLeft } from 'lucide-react';

const genZMorphVariants = {
  enter: (isLogin: boolean) => ({
    opacity: 0,
    scale: 1.1,
    x: isLogin ? -40 : 40,
    filter: 'blur(15px)'
  }),
  center: {
    opacity: 1,
    scale: 1,
    x: 0,
    filter: 'blur(0px)'
  },
  exit: (isLogin: boolean) => ({
    opacity: 0,
    scale: 0.9,
    x: isLogin ? 40 : -40,
    filter: 'blur(15px)'
  })
};

const Auth: React.FC = () => {
  const location = useLocation();
  const [isLogin, setIsLogin] = useState(!location.pathname.includes('register'));
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState<Role>('doctor');
  const [error, setError] = useState('');
  const [focusedField, setFocusedField] = useState('');

  const { register, loginWithPassword } = useAuth();
  const navigate = useNavigate();

  // Optimized bending/parallax effect for smooth input tracking
  const containerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let animationFrameId: number;
    const handleMouse = (e: MouseEvent) => {
      animationFrameId = requestAnimationFrame(() => {
        if (!containerRef.current) return;
        const x = (e.clientX / window.innerWidth) * 2 - 1;
        const y = (e.clientY / window.innerHeight) * 2 - 1;
        containerRef.current.style.transform = `translateZ(0) rotateX(${-y * 1.5}deg) rotateY(${x * 1.5}deg)`;
      });
    };
    window.addEventListener('mousemove', handleMouse);
    return () => {
      window.removeEventListener('mousemove', handleMouse);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!email || !password || (!isLogin && !name)) { setError('ALL FIELDS REQUIRED FOR CLEARANCE.'); return; }
    if (password.length < 6) { setError('MINIMUM 6-CHAR PASSPHRASE REQUIRED.'); return; }
    
    if (isLogin) {
      const result = await loginWithPassword(email, password);
      if (!result.success) {
        setError(result.error || 'Authentication failed.');
        return;
      }
      const stored = localStorage.getItem('carepredict_user');
      const parsed = stored ? JSON.parse(stored) : null;
      navigate(parsed?.role === 'admin' ? '/admin' : '/dashboard');
    } else {
      // Register mode — stores password hash
      const result = await register(email, password, role, name);
      if (!result.success) {
        setError(result.error || 'Registration failed.');
        return;
      }
      navigate(role === 'admin' ? '/admin' : '/dashboard');
    }
  };

  const inputClasses = (field: string) => 
    `w-full pl-11 pr-4 py-3.5 bg-black/80 border border-white/20 hover:border-[var(--neon-blue)] rounded-xl text-sm font-bold text-white placeholder:text-gray-500 transition-all duration-300 ${
      focusedField === field ? 'scale-[1.02] border-[var(--neon-blue)] shadow-[0_0_15px_rgba(0,243,255,0.3)]' : ''
    }`;

  const toggleAuthMode = () => {
    setError('');
    setIsLogin((prev) => !prev);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden" style={{ perspective: '1200px' }}>
      <motion.div
        ref={containerRef}
        initial={{ opacity: 0, y: 30, filter: 'blur(10px)' }}
        animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
        transition={{ duration: 0.6, ease: [0.33, 1, 0.68, 1] }}
        className="w-full max-w-md relative z-10"
        style={{
          transition: 'transform 0.1s linear',
          willChange: 'transform',
          transformStyle: 'preserve-3d',
          backfaceVisibility: 'hidden'
        }}
      >
        {/* Back to home */}
        <NavLink 
          to="/" 
          className="flex items-center gap-2 text-gray-500 hover:text-[var(--neon-blue)] transition-colors duration-300 mb-8 group text-sm font-bold uppercase tracking-widest justify-center"
        >
          <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform duration-300" />
          Return to Base
        </NavLink>

        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <div className="h-10 w-10 rounded-xl bg-black border border-[var(--neon-blue)] text-[var(--neon-blue)] flex items-center justify-center shadow-[0_0_15px_rgba(0,243,255,0.3)]">
            <Zap size={20} strokeWidth={2.5} />
          </div>
          <span className="text-2xl font-extrabold text-white tracking-tight uppercase">
            Care<span className="text-[var(--neon-blue)]">Predict</span>
          </span>
        </div>

        {/* Gen-Z Morph Container */}
        <div>
          <AnimatePresence mode="wait" custom={isLogin}>
            <motion.div
              key={isLogin ? 'login' : 'register'}
              custom={isLogin}
              variants={genZMorphVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{
                type: 'spring',
                stiffness: 450,
                damping: 25,
                mass: 0.5
              }}
              className="glass-panel glowing-wrap p-8 md:p-10 w-full"
              style={{ willChange: 'transform, opacity, filter' }}
            >
              <h2 className="text-2xl font-extrabold text-white text-center mb-1 uppercase tracking-wider">
                {isLogin ? 'System Access' : 'Register Identity'}
              </h2>
              <p className="text-xs text-[var(--neon-blue)] text-center mb-8 uppercase tracking-[0.2em] font-bold">
                {isLogin ? 'Authenticate to proceed to neural dashboard.' : 'Initialize new operator credentials.'}
              </p>

              {error && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-red-900/30 border border-red-500 rounded-xl p-3 mb-6 text-center"
                >
                  <p className="text-sm text-red-400 font-bold uppercase tracking-wider">{error}</p>
                </motion.div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                {!isLogin && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest">Operator Name</label>
                    <div className="relative">
                      <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500"><UserIcon size={16} /></div>
                      <input
                        type="text" value={name} onChange={(e) => setName(e.target.value)}
                        onFocus={() => setFocusedField('name')} onBlur={() => setFocusedField('')}
                        placeholder="Dr. Jane Smith"
                        className={inputClasses('name')}
                      />
                    </div>
                  </motion.div>
                )}

                <div>
                  <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest">Neural ID (Email)</label>
                  <div className="relative">
                    <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500"><Mail size={16} /></div>
                    <input
                      type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                      onFocus={() => setFocusedField('email')} onBlur={() => setFocusedField('')}
                      placeholder="operator@hospital.org"
                      className={inputClasses('email')}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest">Passphrase</label>
                  <div className="relative">
                    <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500"><Lock size={16} /></div>
                    <input
                      type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                      onFocus={() => setFocusedField('password')} onBlur={() => setFocusedField('')}
                      placeholder="••••••••"
                      className={inputClasses('password')}
                    />
                  </div>
                </div>

                {!isLogin && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <label className="block text-xs font-bold text-gray-400 mb-2 uppercase tracking-widest">Clearance Level</label>
                    <div className="relative">
                      <select
                        value={role}
                        onChange={(e) => setRole(e.target.value as Role)}
                        onFocus={() => setFocusedField('role')} onBlur={() => setFocusedField('')}
                        className={`w-full px-4 py-3.5 glass-input rounded-xl text-sm font-medium appearance-none cursor-pointer transition-all duration-300 ${
                          focusedField === 'role' ? 'scale-[1.02] border-[var(--neon-blue)] shadow-[0_0_15px_rgba(0,243,255,0.3)]' : ''
                        }`}
                      >
                        <option value="doctor" className="bg-[#090a0f]">Doctor — Clinical Access</option>
                        <option value="patient" className="bg-[#090a0f]">Patient — Limited Access</option>
                        <option value="admin" className="bg-[#090a0f]">Admin — Full Control</option>
                      </select>
                      <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none">
                        <ChevronDown size={16} />
                      </div>
                    </div>
                  </motion.div>
                )}

                <button
                  type="submit"
                  className="w-full bg-[var(--neon-blue)] text-black font-extrabold py-3.5 rounded-xl shadow-[0_0_15px_rgba(0,243,255,0.4)] hover:shadow-[0_0_30px_rgba(0,243,255,0.6)] hover:bg-white hover:-translate-y-0.5 transition-all duration-300 uppercase tracking-widest text-sm"
                >
                  {isLogin ? 'Authenticate' : 'Initialize Account'}
                </button>
              </form>

              <p className="text-sm text-gray-500 text-center mt-8 cursor-pointer">
                {isLogin ? (
                  <>No credentials? <span onClick={toggleAuthMode} className="text-[var(--neon-purple)] font-bold hover:text-[var(--neon-blue)] transition-colors duration-300 uppercase">Register</span></>
                ) : (
                  <>Already registered? <span onClick={toggleAuthMode} className="text-[var(--neon-purple)] font-bold hover:text-[var(--neon-blue)] transition-colors duration-300 uppercase">Sign in</span></>
                )}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Security notice */}
        <p className="text-center text-[10px] text-gray-600 mt-6 uppercase tracking-widest">
          Encrypted Neural Handshake Protocol v3.0
        </p>


      </motion.div>
    </div>
  );
};

export default Auth;
