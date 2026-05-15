import React, { createContext, useContext, useState, ReactNode } from 'react';
import { loginAPI, registerAPI } from '../services/api';

export type Role = 'doctor' | 'admin' | 'patient';

export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
  clinical_rank?: number;
}

interface AuthContextType {
  user: User | null;
  register: (email: string, password: string, role: Role, name: string) => Promise<{ success: boolean; error?: string }>;
  loginWithPassword: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const stored = localStorage.getItem('carepredict_user');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });

  const setActiveUser = (newUser: User) => {
    setUser(newUser);
    localStorage.setItem('carepredict_user', JSON.stringify(newUser));
  };

  const register = async (email: string, password: string, role: Role, name: string): Promise<{ success: boolean; error?: string }> => {
    const emailLower = email.toLowerCase().trim();

    if (!emailLower || !password || !name) {
      return { success: false, error: 'All fields are required.' };
    }
    if (password.length < 6) {
      return { success: false, error: 'Password must be at least 6 characters.' };
    }

    const result = await registerAPI({
      email: emailLower,
      password,
      role,
      name
    });

    if (!result.success || !result.user) {
      return { success: false, error: result.error || 'Registration failed. Please try again.' };
    }

    setActiveUser(result.user);
    return { success: true };
  };

  const loginWithPassword = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    const emailLower = email.toLowerCase().trim();

    if (!emailLower || !password) {
      return { success: false, error: 'Email and password are required.' };
    }
    if (password.length < 6) {
      return { success: false, error: 'Password must be at least 6 characters.' };
    }

    const result = await loginAPI({
      email: emailLower,
      password
    });

    if (!result.success || !result.user) {
      return { success: false, error: result.error || 'Login failed. Please try again.' };
    }

    setActiveUser(result.user);
    return { success: true };
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('carepredict_user');
  };

  return (
    <AuthContext.Provider value={{
      user,
      register,
      loginWithPassword,
      logout,
      isAuthenticated: !!user,
      isAdmin: user?.role?.toLowerCase() === 'admin'
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
