import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type Role = 'doctor' | 'admin' | 'patient';

// ═══ DEMO ACCOUNTS ═══
// Pre-seeded accounts for easy access
const DEMO_ACCOUNTS: Record<string, { password: string; name: string; role: Role }> = {
  'admin@admin.com':   { password: 'admin123',   name: 'System Admin',    role: 'admin' },
  'doctor@doctor.com': { password: 'doctor123',  name: 'Dr. Smith',       role: 'doctor' },
  'patient@patient.com': { password: 'patient123', name: 'John Doe',      role: 'patient' },
};

export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, role: Role, name: string) => void;
  loginWithPassword: (email: string, password: string) => { success: boolean; error?: string };
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check local storage on initial mount
    const storedUser = localStorage.getItem('carepredict_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error("Failed to parse user from local storage", e);
      }
    }
  }, []);

  const login = (email: string, role: Role, name: string) => {
    // Mock user login by generating deterministic ID from email for session
    const newUser: User = { 
      id: `usr_${btoa(email).substring(0, 10)}`, 
      email, 
      name, 
      role 
    };
    setUser(newUser);
    localStorage.setItem('carepredict_user', JSON.stringify(newUser));
  };

  const loginWithPassword = (email: string, password: string): { success: boolean; error?: string } => {
    const emailLower = email.toLowerCase().trim();
    const demo = DEMO_ACCOUNTS[emailLower];
    if (demo) {
      if (demo.password === password) {
        login(emailLower, demo.role, demo.name);
        return { success: true };
      }
      return { success: false, error: 'Invalid password for demo account.' };
    }
    // For non-demo accounts, accept any password >= 6 chars (mock auth)
    if (password.length >= 6) {
      login(emailLower, 'doctor', emailLower.split('@')[0]);
      return { success: true };
    }
    return { success: false, error: 'Password must be at least 6 characters.' };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('carepredict_user');
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      loginWithPassword,
      logout,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin'
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
