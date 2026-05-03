import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { usePatientData } from '../hooks/usePatientData';
import { useAuth } from '../context/AuthContext';
import { Search, Filter, ShieldAlert, ShieldCheck, Activity, ChevronDown, ChevronUp, FileDown, X, Maximize2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { downloadReportPDF } from '../services/api';

const History: React.FC = () => {
  const { history, loadData } = usePatientData();
  const { isAdmin } = useAuth();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [highRiskOnly, setHighRiskOnly] = useState(false);
  const [expandedRecordId, setExpandedRecordId] = useState<string | null>(null);
  const [modalImage, setModalImage] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const pid = params.get('patientId');
    if (pid) {
      setSearchTerm(pid);
      loadData(pid);
    } else if (isAdmin) {
      // Force load all for Admin if no specific ID
      loadData();
    }
  }, [location, isAdmin]);

  const filteredHistory = history.filter(record => {
    const q = searchTerm.toLowerCase();
    const matchSearch = 
      (record.patientId?.toLowerCase() || "").includes(q) ||
      (record.patientName?.toLowerCase() || "").includes(q) ||
      (record.disease?.toLowerCase() || "").includes(q) ||
      (record.doctorId?.toLowerCase() || "").includes(q);
      
    const matchRisk = highRiskOnly ? (record.risk || "").toLowerCase().includes('high') : true;
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

  const riskScore = (risk?: string) => {
    if (risk === 'High') return 3;
    if (risk === 'Moderate') return 2;
    return 1;
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
                <th className="px-5 py-4">Details</th>
              </tr>
            </thead>
            <tbody>
              {filteredHistory.length > 0 ? (
                filteredHistory.map((record) => (
                  <React.Fragment key={record.id}>
                    <tr className="border-b border-border-muted hover:bg-surface-alt transition-colors group">
                      <td className="px-5 py-4 font-medium text-text-primary group-hover:text-brand transition-colors">{record.patientId}</td>
                      {isAdmin && <td className="px-5 py-4 font-mono text-xs text-text-muted">{record.doctorId}</td>}
                      <td className="px-5 py-4 text-text-secondary">{(() => {
                        const d = new Date(record.timestamp);
                        return isNaN(d.getTime()) ? 'N/A' : d.toLocaleDateString();
                      })()}</td>
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
                      <td className="px-5 py-4">
                        <button
                          type="button"
                          onClick={() => setExpandedRecordId(expandedRecordId === record.id ? null : record.id)}
                          className="inline-flex items-center gap-1 rounded-lg border border-border-subtle px-2 py-1 text-xs font-semibold text-text-secondary hover:bg-surface-alt"
                        >
                          {expandedRecordId === record.id ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
                          {expandedRecordId === record.id ? 'Hide' : 'Expand'}
                        </button>
                      </td>
                    </tr>

                    {expandedRecordId === record.id && (
                      <tr className="border-b border-border-muted bg-surface-alt/60">
                        <td colSpan={isAdmin ? 9 : 8} className="px-5 py-4">
                          <div className="grid gap-4 md:grid-cols-3">
                            <div className="rounded-xl border border-border-subtle bg-white p-3">
                              <p className="text-[10px] uppercase tracking-widest text-purple-500 mb-2 font-semibold">Recommended Medicines</p>
                              {(record.autoMedications || []).length > 0 ? (
                                <div className="space-y-2">
                                  {(record.autoMedications || []).map((med, idx) => (
                                    <div key={`med-${idx}`} className="rounded-lg border border-border-subtle p-2">
                                      <p className="text-sm font-semibold text-text-primary">
                                        {typeof med === 'object' ? String(med.name || med.purpose || 'Medication') : String(med)}
                                      </p>
                                      <p className="text-xs text-text-muted">
                                        {typeof med === 'object' ? `${String(med.dosage || 'Dose N/A')} ${med.frequency ? `- ${String(med.frequency)}` : ''}` : ''}
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              ) : (record.matchedDrugs || []).length > 0 ? (
                                <div className="space-y-1">
                                  {(record.matchedDrugs || []).map((drug, idx) => (
                                    <p key={`match-${idx}`} className="text-xs text-text-primary">
                                      - {typeof drug === 'object' ? String(drug.name || drug.purpose || 'Drug') : String(drug)}
                                    </p>
                                  ))}
                                </div>
                              ) : (
                                <p className="text-xs text-text-muted">No medicine recommendations saved for this log.</p>
                              )}
                            </div>

                            <div className="rounded-xl border border-red-200 bg-red-50 p-3">
                              <p className="text-[10px] uppercase tracking-widest text-red-600 mb-2 font-semibold">Wrong / Unsafe Medicines</p>
                              {((record.drugInteractions || []).length > 0 || (record.prescriptionEvaluation?.details || []).length > 0) ? (
                                <div className="space-y-1">
                                  {(record.drugInteractions || []).map((item, idx) => (
                                    <p key={`unsafe-${idx}`} className="text-xs text-red-700">- {item}</p>
                                  ))}
                                  {(record.prescriptionEvaluation?.details || []).map((item, idx) => (
                                    <p key={`rx-${idx}`} className="text-xs text-amber-700">- {item}</p>
                                  ))}
                                </div>
                              ) : (
                                <p className="text-xs text-red-600/80">No unsafe medicine warning recorded for this log.</p>
                              )}
                            </div>

                            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3">
                              <p className="text-[10px] uppercase tracking-widest text-emerald-700 mb-2 font-semibold">Health Measures To Take</p>
                              {([
                                ...(record.recommendations?.lifestyle || []),
                                ...(record.recommendations?.medical || []),
                                ...(record.recommendations?.precautions || [])
                              ]).length > 0 ? (
                                <div className="space-y-1">
                                  {[
                                    ...(record.recommendations?.lifestyle || []),
                                    ...(record.recommendations?.medical || []),
                                    ...(record.recommendations?.precautions || [])
                                  ].slice(0, 8).map((item, idx) => (
                                    <p key={`care-${idx}`} className="text-xs text-emerald-800">
                                      - {typeof item === 'object' ? String(item.name || item.purpose || 'Recommendation') : String(item)}
                                    </p>
                                  ))}
                                </div>
                              ) : (
                                <p className="text-xs text-emerald-700/80">No home-care recommendation saved for this log.</p>
                              )}
                            </div>

                             {/* 4. Visual Evidence (if available) */}
                             {record.prescription_image && (
                               <div className="rounded-xl border border-blue-200 bg-blue-50/30 p-3">
                                 <p className="text-[10px] uppercase tracking-widest text-blue-700 mb-2 font-semibold">Visual Scan Evidence</p>
                                 <div 
                                   className="relative group cursor-zoom-in"
                                   onClick={(e) => {
                                     e.stopPropagation();
                                     setModalImage(record.prescription_image);
                                   }}
                                 >
                                   <img 
                                     src={record.prescription_image.startsWith('data:') ? record.prescription_image : `data:image/jpeg;base64,${record.prescription_image}`} 
                                     alt="Prescription Evidence" 
                                     className="max-h-48 rounded-lg border border-blue-200 object-cover w-full transition-all group-hover:scale-[1.02]"
                                   />
                                   <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/10 rounded-lg">
                                      <Maximize2 size={24} className="text-blue-900 bg-white/90 p-1.5 rounded-full shadow-lg" />
                                   </div>
                                 </div>
                                 <p className="text-[9px] text-blue-600/70 mt-2 italic uppercase tracking-tighter text-center">Original prescription document captured via Clinical Vision Auditor</p>
                               </div>
                             )}

                             {/* 5. PDF Clinical Report Actions */}
                             <div className="mt-4 pt-4 border-t border-border-subtle flex justify-end gap-3">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    downloadReportPDF(record.mongoId || record.id); // Prefer mongoId for PDF generation
                                  }}
                                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-health-primary text-white text-[10px] font-bold uppercase tracking-widest hover:bg-emerald-700 transition-all shadow-sm"
                                >
                                  <FileDown size={14} /> Download Clinical PDF
                                </button>
                             </div>
                          </div>
                          {(() => {
                            const previousSameDisease = filteredHistory
                              .filter((entry) => entry.id !== record.id && entry.disease === record.disease)
                              .find((entry) => new Date(entry.timestamp).getTime() < new Date(record.timestamp).getTime());
                            if (!previousSameDisease) return null;
                            return (
                              <div className="mt-4 rounded-xl border border-border-subtle bg-white p-3">
                                <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Compared To Previous Test</p>
                                <p className="mt-1 text-xs text-text-secondary">
                                  {riskScore(record.risk) < riskScore(previousSameDisease.risk)
                                    ? 'Improved risk level'
                                    : riskScore(record.risk) > riskScore(previousSameDisease.risk)
                                      ? 'Condition worsened'
                                      : 'Risk level unchanged'}
                                  {' | '}
                                  Confidence change {((record.confidence - previousSameDisease.confidence) * 100).toFixed(1)}%
                                </p>
                              </div>
                            );
                          })()}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan={isAdmin ? 9 : 8} className="px-6 py-14 text-center">
                    <p className="text-text-secondary text-sm font-medium">No matching records found.</p>
                    <p className="text-text-muted text-xs mt-1">Adjust your filters or run a new diagnosis.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* LIGHTBOX MODAL */}
      <AnimatePresence>
        {modalImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setModalImage(null)}
            className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/95 backdrop-blur-xl"
          >
            <button className="absolute top-6 right-6 p-3 text-white/50 hover:text-white transition-colors">
              <X size={32} />
            </button>
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative max-w-5xl w-full h-full flex items-center justify-center"
              onClick={(e) => e.stopPropagation()}
            >
              <img
                src={modalImage.startsWith('data:') ? modalImage : `data:image/jpeg;base64,${modalImage}`}
                alt="High-Res Evidence"
                className="max-w-full max-h-full object-contain rounded shadow-2xl border border-white/10"
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default History;
