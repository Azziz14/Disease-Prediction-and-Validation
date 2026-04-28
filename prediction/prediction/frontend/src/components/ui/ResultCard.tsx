import { ShieldAlert, ShieldCheck, Activity, Pill, AlertTriangle, Fingerprint, Crosshair, HeartPulse, BatteryCharging, CheckCircle2, FileDown } from 'lucide-react';
import { motion } from 'framer-motion';
import { downloadReportPDF } from '../../services/api';

const ResultCard: React.FC<{ result: any }> = ({ result }) => {
  if (!result) return null;

  const isHigh = result.risk === 'High';
  const isMod = result.risk === 'Moderate';
  const conf = Math.round(result.confidence * 100);

  const neonColor = isHigh ? 'var(--neon-purple)' : isMod ? '#ffaa00' : 'var(--neon-green)';
  const shadowClass = isHigh ? 'neon-text-purple' : isMod ? 'text-[#ffaa00]' : 'neon-text-green';

  const rx = result.prescription_evaluation;
  const ls = result.recommendations?.lifestyle || [];
  const med = result.recommendations?.medical || [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="glass-panel p-6 space-y-6 glowing-wrap"
    >
      {/* Risk Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl border" style={{ borderColor: neonColor, color: neonColor, boxShadow: `0 0 10px ${neonColor}40` }}>
            {isHigh ? <ShieldAlert size={28} /> : isMod ? <Activity size={28} /> : <ShieldCheck size={28} />}
          </div>
          <div>
            <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Risk Level</p>
            <p className={`text-2xl font-extrabold uppercase ${shadowClass}`}>
              {result.risk}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Confidence Index</p>
          <p className="text-2xl font-bold text-white uppercase">{conf}%</p>
        </div>
      </div>

      {/* Confidence Bar */}
      <div>
        <div className="w-full h-2 bg-black/50 rounded-full overflow-hidden border border-white/10">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${conf}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className={`h-full rounded-full`}
            style={{ backgroundColor: neonColor, boxShadow: `0 0 10px ${neonColor}` }}
          />
        </div>
      </div>

      {/* 1. Biomarker Abnormalities */}
      {result.abnormalities && result.abnormalities.length > 0 && (
        <div className="bg-red-900/10 border border-red-500/30 rounded-xl p-4 shadow-[0_0_15px_rgba(255,0,0,0.1)]">
          <h4 className="text-xs font-bold text-red-500 uppercase tracking-widest mb-3 flex items-center gap-2">
            <Fingerprint size={14} className="text-red-500" /> BIOMARKER ANOMALIES DETECTED
          </h4>
          <div className="space-y-2">
            {result.abnormalities.map((anomaly: string, i: number) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <AlertTriangle size={14} className="text-red-400 shrink-0 mt-0.5" />
                <span className="text-red-200/90 leading-tight">{anomaly}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 2. Prescription Validation (Only shown if prescription input was provided) */}
      {rx && rx.provided && (
        <div className={`border rounded-xl p-4 transition-all duration-300 ${
          rx.status === 'VALID' ? 'bg-green-900/10 border-[var(--neon-green)] shadow-[0_0_15px_rgba(57,255,20,0.15)]' :
          rx.status === 'INVALID' ? 'bg-red-900/20 border-red-500 shadow-[0_0_15px_rgba(255,0,0,0.2)]' :
          'bg-yellow-900/10 border-[#ffaa00] shadow-[0_0_15px_rgba(255,170,0,0.1)]'
        }`}>
          <h4 className={`text-xs font-bold uppercase tracking-widest mb-1 flex items-center gap-2 ${
            rx.status === 'VALID' ? 'text-[var(--neon-green)]' : rx.status === 'INVALID' ? 'text-red-500' : 'text-[#ffaa00]'
          }`}>
            <Pill size={14} /> PRESCRIPTION VALIDATION
          </h4>
          <p className="text-lg font-bold text-white mb-3">{rx.message}</p>
          
          {rx.details && rx.details.length > 0 && (
            <div className="space-y-1.5 border-t border-white/10 pt-3 mt-1">
              {rx.details.map((detail: string, i: number) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  {rx.status === 'VALID' ? (
                    <CheckCircle2 size={14} className="text-[var(--neon-green)] shrink-0 mt-0.5" />
                  ) : (
                    <span className="text-[#ffaa00] font-bold shrink-0 mt-0.5">{'>'}</span>
                  )}
                  <span className="text-gray-300">{detail}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* 3. Action Protocols / Recommendations */}
      {(ls.length > 0 || med.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Lifestyle */}
          {ls.length > 0 && (
            <div className="bg-black/30 border border-white/10 rounded-xl p-4 hover:border-[var(--neon-blue)] transition-colors">
               <h4 className="text-xs font-bold text-[var(--neon-blue)] uppercase tracking-widest mb-3 flex items-center gap-2">
                 <BatteryCharging size={14} /> DAILY PROTOCOL
               </h4>
               <ul className="space-y-2">
                 {ls.map((rec: string, i: number) => (
                   <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                     <span className="text-[var(--neon-blue)] mt-0.5">•</span>
                     {rec}
                   </li>
                 ))}
               </ul>
            </div>
          )}

          {/* Medical */}
          {med.length > 0 && (
            <div className="bg-black/30 border border-white/10 rounded-xl p-4 hover:border-[var(--neon-purple)] transition-colors">
               <h4 className="text-xs font-bold text-[var(--neon-purple)] uppercase tracking-widest mb-3 flex items-center gap-2">
                 <HeartPulse size={14} /> MEDICAL PROTOCOL
               </h4>
               <ul className="space-y-2">
                 {med.map((rec: string, i: number) => (
                   <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                     <span className="text-[var(--neon-purple)] mt-0.5">⚕</span>
                     {rec}
                   </li>
                 ))}
               </ul>
            </div>
          )}
        </div>
      )}

      {/* 3b. Handwriting Audit (Visual Scans only) */}
      {result.consensus_intelligence?.handwriting_audit && (
        <div className="bg-blue-900/10 border border-blue-500/30 rounded-xl p-4">
          <h4 className="text-xs font-bold text-blue-400 uppercase tracking-widest mb-3 flex items-center gap-2">
            <Activity size={14} className="text-blue-400" /> SCAN QUALITY AUDIT
          </h4>
          <div className="flex items-center justify-between mb-2">
             <span className="text-xs text-gray-400">Handwriting Clarity</span>
             <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
               result.consensus_intelligence.handwriting_audit.is_legible ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
             }`}>
               {result.consensus_intelligence.handwriting_audit.verdict}
             </span>
          </div>
          <p className="text-blue-200/80 text-sm italic">"{result.consensus_intelligence.handwriting_audit.audit_note}"</p>
        </div>
      )}

      {/* 4. Auto-Suggested Medications */}
      {result.auto_medications && result.auto_medications.length > 0 && (
        <div className="bg-purple-900/10 border border-purple-500/30 rounded-xl p-4 shadow-[0_0_15px_rgba(168,85,247,0.1)]">
          <h4 className="text-xs font-bold text-purple-400 uppercase tracking-widest mb-3 flex items-center gap-2">
            <Pill size={14} /> RECOMMENDED MEDICATIONS
          </h4>
          <div className="space-y-3">
            {result.auto_medications.map((med: any, i: number) => {
              // Check if we have detailed role info for this drug from the multimodal consensus
              const detailedInfo = (result.consensus_intelligence?.medication_details || []).find(
                (d: any) => d.name.toLowerCase().includes(med.name.toLowerCase()) || med.name.toLowerCase().includes(d.name.toLowerCase())
              );

              return (
                <div key={i} className="bg-white/5 rounded-lg p-3 border border-white/5">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="text-white font-bold text-sm">{med.name}</p>
                      <p className="text-cyan-400 text-xs font-mono">{med.dosage} — {med.frequency}</p>
                    </div>
                  </div>
                  <p className="text-gray-400 text-[11px] mt-1">{med.note}</p>
                  
                  {detailedInfo?.role && (
                    <div className="mt-2 pt-2 border-t border-white/5">
                      <p className="text-[10px] text-purple-300/80 uppercase tracking-widest mb-1">Drug Role & Purpose</p>
                      <p className="text-xs text-purple-100/90 leading-relaxed font-serif italic">{detailedInfo.role}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          <p className="text-[9px] text-gray-600 mt-3 italic">
            Auto-suggested based on risk assessment. Always consult a healthcare professional.
          </p>
        </div>
      )}

      {/* Original Core Drivers (Explanation) */}
      {result.explanation && Object.keys(result.explanation).length > 0 && (
        <div className="bg-black/20 border border-[var(--cyber-border)] rounded-xl p-4 border-dashed">
          <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-2">
            <Crosshair size={12} /> ALGORITHM WEIGHTS (XAI)
          </h4>
          <div className="space-y-1">
            {Object.entries(result.explanation).slice(0, 3).map(([key, val]) => (
              <div key={key} className="flex items-start justify-between text-xs">
                <span className="text-gray-400 capitalize">{key}</span>
                <span className="text-white opacity-60 font-mono">{val as string}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. PDF Clinical Report Download */}
      {result.record_id && (
        <motion.button
          whileHover={{ scale: 1.02, backgroundColor: 'rgba(34, 211, 238, 0.15)' }}
          whileTap={{ scale: 0.98 }}
          onClick={() => downloadReportPDF(result.record_id)}
          className="w-full mt-2 py-4 flex items-center justify-center gap-3 bg-cyan-500/10 border border-cyan-500/40 text-cyan-400 rounded-xl font-bold text-xs uppercase tracking-[0.2em] shadow-[0_0_20px_rgba(34,211,238,0.1)] hover:border-cyan-400 transition-all"
        >
          <FileDown size={16} /> DOWNLOAD CLINICAL PDF REPORT
        </motion.button>
      )}
    </motion.div>
  );
};

export default ResultCard;
