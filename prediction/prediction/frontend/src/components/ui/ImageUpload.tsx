import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Image as ImageIcon, X, AlertTriangle, ScanLine } from 'lucide-react';
import { imagePredictAPI } from '../../services/api';

const ImageUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith('image/')) { setError('INVALID DATA TYPE: IMAGE REQUIRED.'); return; }
    if (f.size > 10 * 1024 * 1024) { setError('PAYLOAD TOO LARGE: 10MB LIMIT.'); return; }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setError('');
    setResult(null);
  }, []);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const res = await imagePredictAPI(file);
      if (res?.error) setError(res.error);
      else setResult(res);
    } catch {
      setError('UPLINK FAILURE: VISUAL CORTEX UNREACHABLE.');
    } finally {
      setLoading(false);
    }
  };

  const clear = () => { setFile(null); setPreview(null); setResult(null); setError(''); };

  const severityColor = (s: string) => {
    if (s === 'Critical') return 'border-[var(--neon-purple)] text-[var(--neon-purple)] shadow-[0_0_10px_var(--neon-purple)]';
    if (s === 'Moderate') return 'border-[#ffaa00] text-[#ffaa00] shadow-[0_0_10px_#ffaa00]';
    return 'border-[var(--neon-green)] text-[var(--neon-green)] shadow-[0_0_10px_rgba(57,255,20,0.5)]';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="glass-panel glowing-wrap p-6 md:p-10 w-full max-w-2xl mx-auto"
    >
      <div className="mb-8 pb-4 border-b border-white/10 text-center">
        <h2 className="text-2xl font-extrabold text-white uppercase tracking-widest flex justify-center items-center gap-3">
          <ScanLine className="text-[var(--neon-blue)]" /> Visual Scanner
        </h2>
        <p className="text-xs text-[var(--neon-blue)] mt-2 uppercase tracking-widest font-bold">Awaiting dermatoscopic input...</p>
      </div>

      {error && (
        <div className="bg-red-900/30 border border-red-500 rounded-xl p-4 mb-6 flex items-center gap-3">
          <AlertTriangle size={20} className="text-red-500" />
          <p className="text-sm text-red-500 font-bold uppercase tracking-wider">{error}</p>
        </div>
      )}

      {!preview ? (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-2xl p-16 flex flex-col items-center justify-center text-center cursor-pointer transition-all overflow-hidden ${
            dragOver ? 'border-[var(--neon-blue)] bg-[var(--neon-blue)]/10 shadow-[inset_0_0_50px_rgba(0,243,255,0.2)]' : 'border-white/20 hover:border-[var(--neon-blue)] hover:bg-white/5'
          }`}
          onClick={() => document.getElementById('image-input')?.click()}
        >
          <Upload size={48} className={`mb-4 transition-colors ${dragOver ? 'text-[var(--neon-blue)] neon-text-blue' : 'text-gray-500'}`} />
          <p className="text-lg font-bold text-white uppercase tracking-wider">Drag & drop optical data</p>
          <p className="text-sm text-gray-500 mt-2 uppercase">or click to interface</p>
          <input id="image-input" type="file" accept="image/*" className="hidden" onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])} />
        </div>
      ) : (
        <div className="space-y-6">
          <div className="relative rounded-xl overflow-hidden border border-[var(--neon-blue)] shadow-[0_0_20px_rgba(0,243,255,0.2)]">
            <img src={preview} alt="Preview" className="w-full h-64 object-cover opacity-80 mix-blend-screen" />
            
            <AnimatePresence>
              {loading && (
                <motion.div
                  initial={{ top: "-10%" }}
                  animate={{ top: "110%" }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="absolute left-0 w-full h-4 bg-[var(--neon-green)] opacity-70 blur-[4px]"
                  style={{ boxShadow: '0 0 20px var(--neon-green), 0 0 40px var(--neon-green)' }}
                />
              )}
            </AnimatePresence>

            <button onClick={clear} className="absolute top-3 right-3 p-2 rounded-lg bg-black/50 border border-white/20 hover:bg-black/80 hover:border-[var(--neon-purple)] text-white transition-colors z-10">
              <X size={18} />
            </button>

            {loading && (
              <div className="absolute inset-0 bg-black/40 flex items-center justify-center z-0">
                <span className="text-[var(--neon-green)] font-mono text-xl font-bold tracking-widest neon-text-green bg-black/50 px-4 py-2 rounded">SCANNING STRATA...</span>
              </div>
            )}
          </div>

          {!result && !loading && (
            <button
              onClick={handleSubmit}
              className="w-full flex items-center justify-center gap-3 bg-[var(--neon-blue)] text-black font-extrabold text-lg tracking-widest py-4 rounded-xl shadow-[0_0_20px_var(--neon-blue)] hover:bg-white hover:shadow-[0_0_30px_white] transition-all"
            >
              <ImageIcon size={20} /> INITIATE ANALYSIS
            </button>
          )}

          {result && !loading && (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="space-y-6 glass-input p-6 rounded-xl border border-[var(--neon-purple)] shadow-[inset_0_0_20px_rgba(176,91,255,0.1)]">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-[var(--neon-purple)] uppercase tracking-widest font-bold">Identified Anomaly</p>
                  <p className="text-2xl font-bold text-white uppercase mt-1">{result.classification}</p>
                </div>
                <span className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest bg-black ${severityColor(result.severity)}`}>
                  {result.severity}
                </span>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-400 font-bold uppercase tracking-widest">Confidence Index</span>
                  <span className="text-white font-bold">{result.confidence}%</span>
                </div>
                <div className="w-full h-3 bg-black border border-white/20 rounded-full overflow-hidden">
                  <motion.div initial={{ width: 0 }} animate={{ width: `${result.confidence}%` }} transition={{ duration: 1 }} className="h-full rounded-full bg-[var(--neon-purple)] shadow-[0_0_10px_var(--neon-purple)]" />
                </div>
              </div>

              {result.description && (
                <p className="text-sm text-gray-300 bg-black/40 border border-white/10 rounded-xl p-4 font-mono leading-relaxed">
                  <span className="text-[var(--neon-blue)] mr-2">{'>'}</span>{result.description}
                </p>
              )}
            </motion.div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default ImageUpload;
