import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/common/Navbar';
import Home from './pages/Home';
import Diagnosis from './pages/Diagnosis';
import CyberParticleBackground from './components/ui/CyberParticleBackground';
import './index.css';

import { AuthProvider } from './context/AuthContext';
import Auth from './pages/Auth';
import ProtectedRoute from './components/common/ProtectedRoute';
import DashboardLayout from './pages/DashboardLayout';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import History from './pages/History';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col relative" style={{ fontFamily: "'Space Grotesk', 'Inter', sans-serif", color: 'white' }}>
          {/* Global particle background — visible on every page */}
          <CyberParticleBackground />

          {/* All content floats above the particle canvas */}
          <div className="relative flex-1 flex flex-col" style={{ zIndex: 1 }}>
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={
                <>
                  <Navbar />
                  <main className="flex-1 w-full flex flex-col"><Home /></main>
                </>
              } />
              <Route path="/diagnosis" element={
                <>
                  <Navbar />
                  <main className="flex-1 w-full flex flex-col pt-20"><Diagnosis /></main>
                </>
              } />

              <Route path="/login" element={<Auth />} />
              <Route path="/register" element={<Auth />} />

              {/* Protected Dashboard with Sidebar */}
              <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/history" element={<History />} />
              </Route>
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;

