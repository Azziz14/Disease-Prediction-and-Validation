import React, { useState } from 'react';
import { usePatientData } from '../hooks/usePatientData';
import { useAuth } from '../context/AuthContext';
import { Search, Filter, ShieldAlert, ShieldCheck, Activity } from 'lucide-react';

const History: React.FC = () => {
  const { history } = usePatientData();
  const { isAdmin } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [highRiskOnly, setHighRiskOnly] = useState(false);

  const filteredHistory = history.filter(record => {
    const matchSearch = record.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.doctorId.toLowerCase().includes(searchTerm.toLowerCase());
    const matchRisk = highRiskOnly ? record.risk === 'High' : true;
    return matchSearch && matchRisk;
  });

  const riskBadge = (risk: string) => {
    if (risk === 'High') return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider bg-red-50 text-health-danger border border-red-100">
        <ShieldAlert size={11} /> High
      </span>
    );
    if (risk === 'Moderate') return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider bg-amber-50 text-health-warning border border-amber-100">
        <Activity size={11} /> Moderate
      </span>
    );
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider bg-emerald-50 text-health-success border border-emerald-100">
        <ShieldCheck size={11} /> Low
      </span>
    );
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-in fade-in">
      
      <div>
        <h1 className="text-2xl font-display font-bold text-text-primary tracking-tight">
          {isAdmin ? 'Global Records' : 'Patient History'}
        </h1>
        <p className="text-sm text-text-muted mt-0.5">Review archival AI prediction data.</p>
      </div>

      {/* Controls */}
      <div className="bg-white p-4 rounded-2xl border border-border-subtle shadow-card flex flex-col sm:flex-row gap-3 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-text-muted">
            <Search size={16} />
          </div>
          <input
            type="text"
            className="w-full pl-10 pr-4 py-2.5 bg-surface-alt border border-border-subtle rounded-xl outline-none focus:ring-2 focus:ring-brand/10 focus:border-brand text-sm text-text-primary placeholder-text-muted transition-all"
            placeholder="Search Patient ID..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />
        </div>
        <button 
          onClick={() => setHighRiskOnly(!highRiskOnly)}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            highRiskOnly
              ? 'bg-red-50 text-health-danger border border-red-200'
              : 'bg-white text-text-secondary border border-border-subtle hover:bg-surface-hover'
          }`}
        >
          <Filter size={15} /> High Risk Only
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl border border-border-subtle shadow-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[10px] text-text-muted uppercase tracking-widest bg-surface-alt border-b border-border-subtle font-bold">
              <tr>
                <th className="px-5 py-4">Patient ID</th>
                {isAdmin && <th className="px-5 py-4">Doctor ID</th>}
                <th className="px-5 py-4">Date</th>
                <th className="px-5 py-4">Disease</th>
                <th className="px-5 py-4">Glucose</th>
                <th className="px-5 py-4">BP</th>
                <th className="px-5 py-4">Confidence</th>
                <th className="px-5 py-4">Risk</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.length > 0 ? (
                filteredHistory.map((record) => (
                  <tr key={record.id} className="border-b border-border-muted hover:bg-surface-alt transition-colors group">
                    <td className="px-5 py-4 font-medium text-text-primary group-hover:text-brand transition-colors">{record.id}</td>
                    {isAdmin && <td className="px-5 py-4 font-mono text-xs text-text-muted">{record.doctorId}</td>}
                    <td className="px-5 py-4 text-text-secondary">{new Date(record.timestamp).toLocaleDateString()}</td>
                    <td className="px-5 py-4">
                      <span className="inline-block text-xs bg-surface-alt border border-border-subtle rounded-full px-2.5 py-0.5 font-medium capitalize text-text-secondary">
                        {record.disease || 'diabetes'}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-text-primary">{record.glucose}</td>
                    <td className="px-5 py-4 text-text-primary">{record.bloodPressure}</td>
                    <td className="px-5 py-4">
                      <span className="font-semibold text-text-primary">{(record.confidence * 100).toFixed(1)}%</span>
                    </td>
                    <td className="px-5 py-4">{riskBadge(record.risk)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={isAdmin ? 8 : 7} className="px-6 py-14 text-center">
                    <p className="text-text-secondary text-sm font-medium">No matching records found.</p>
                    <p className="text-text-muted text-xs mt-1">Adjust your filters or run a new diagnosis.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default History;
