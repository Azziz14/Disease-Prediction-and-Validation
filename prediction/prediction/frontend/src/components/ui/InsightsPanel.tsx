import React, { useEffect, useState } from 'react';
import { Lightbulb, Pill, Activity, CheckCircle, Info, BrainCircuit, ShieldAlert, Clock } from 'lucide-react';

const InsightsPanel: React.FC<{ predictionResult: any; disease?: string }> = ({ predictionResult, disease }) => {
  const [wikiExplanation, setWikiExplanation] = useState<string>('');
  const [loadingWiki, setLoadingWiki] = useState<boolean>(false);

  useEffect(() => {
    if (disease) {
      setLoadingWiki(true);
      // Fetch Wikipedia summary
      const title = disease === 'diabetes' ? 'Diabetes' : disease === 'heart' ? 'Cardiovascular_disease' : 'Mental_disorder';
      fetch(`https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&titles=${title}&format=json&origin=*`)
        .then(res => res.json())
        .then(data => {
          const pages = data.query?.pages;
          if (pages) {
            const pageId = Object.keys(pages)[0];
            const extract = pages[pageId]?.extract;
            // Strip HTML tags
            if (extract) {
              const stripped = extract.replace(/<\/?[^>]+(>|$)/g, "");
              setWikiExplanation(stripped.substring(0, 300) + '...');
            }
          }
          setLoadingWiki(false);
        })
        .catch(err => {
          console.error('Wikipedia API Error:', err);
          setLoadingWiki(false);
        });
    }
  }, [disease]);

  if (!predictionResult) return null;

  const { consensus_intelligence } = predictionResult;
  const consensus = consensus_intelligence || {};
  const { prediction, auto_medications, recommendations } = predictionResult;

  // Use consensus data if available, fallback to individual prediction
  const displayDiagnosis = consensus.diagnosis || prediction?.disease || disease;
  const displayRisk = consensus.risk || prediction?.risk || 'Calculating';
  const displayConfidence = consensus.confidence || prediction?.confidence;
  const displayNarrative = consensus.narrative || prediction?.explanation;
  const displayMeds = consensus.medication_data || auto_medications || [];
  const displayDirectives = consensus.directives || recommendations || {};
  
  // Structured Daily Routine Extraction
  const dailyRoutine = displayDirectives.daily_routine || [];
  const lifestyle = displayDirectives.lifestyle || [];
  const precautions = displayDirectives.precautions || [];

  return (
    <div className="bg-[#0b1222] rounded-[32px] border border-cyan-500/20 shadow-[0_0_50px_rgba(0,243,255,0.05)] p-6 md:p-8 space-y-8 mt-6 animate-in fade-in zoom-in duration-500 overflow-hidden relative">
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 blur-3xl -mr-32 -mt-32 rounded-full" />
      
      {/* Header & Neural Chain */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-white/5">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 shadow-[0_0_15px_rgba(0,243,255,0.15)]">
            <BrainCircuit size={28} className="text-cyan-400" />
          </div>
          <div>
            <h3 className="text-2xl font-bold text-white tracking-tight">Neural Consensus Intelligence</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse" />
              <p className="text-xs font-bold uppercase tracking-widest text-cyan-300/70">Multi-Model Fusion Active</p>
            </div>
          </div>
        </div>

        {/* Neural Chain Visual */}
        <div className="flex items-center gap-2 bg-black/40 px-4 py-3 rounded-2xl border border-white/5">
          {['Core', 'NLP', 'AI', 'Sync'].map((step, i) => (
            <React.Fragment key={step}>
              <div className="flex flex-col items-center">
                <div className={`w-2 h-2 rounded-full ${i <= 3 ? 'bg-cyan-400' : 'bg-white/20 shadow-[0_0_8px_rgba(0,243,255,0.5)]'}`} />
                <span className="text-[8px] uppercase tracking-tighter text-white/40 mt-1">{step}</span>
              </div>
              {i < 3 && <div className="w-4 h-px bg-white/10" />}
            </React.Fragment>
          ))}
          <div className="ml-2 pl-3 border-l border-white/10">
            <p className="text-[10px] text-white/40 uppercase">Handshake</p>
            <p className="text-xs font-bold text-green-400">Verified</p>
          </div>
        </div>
      </div>
      
      {/* Risk and Merged Narrative */}
      <div className="relative z-10 grid gap-6 lg:grid-cols-[1fr_0.8fr]">
        <div className="space-y-4">
          <div className={`p-6 rounded-[24px] border ${
            displayRisk === 'High' ? 'bg-red-500/10 border-red-500/30 shadow-[0_0_20px_rgba(239,68,68,0.05)]' :
            displayRisk === 'Moderate' ? 'bg-amber-500/10 border-amber-500/30' :
            'bg-emerald-500/10 border-emerald-500/30'
          }`}>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-xl font-bold text-white capitalize">
                {displayDiagnosis} Detection
              </h4>
              <div className={`px-4 py-1 rounded-full text-xs font-bold uppercase tracking-widest ${
                displayRisk === 'High' ? 'bg-red-500/20 text-red-300' :
                displayRisk === 'Moderate' ? 'bg-amber-500/20 text-amber-200' :
                'bg-emerald-500/20 text-emerald-300'
              }`}>
                {displayRisk} Risk
              </div>
            </div>
            <p className="text-base text-white/80 leading-relaxed font-medium">{displayNarrative}</p>
            
            {displayConfidence && (
              <div className="mt-5 pt-4 border-t border-white/5 flex items-center justify-between">
                <span className="text-xs text-white/40 uppercase tracking-widest font-bold">Consensus Accuracy</span>
                <span className="text-lg font-black text-cyan-400">{(displayConfidence * 100).toFixed(2)}%</span>
              </div>
            )}
          </div>
          
          {/* Wiki layer (simplified in consensus mode) */}
          {displayDiagnosis && !consensus_intelligence && (
            <div className="bg-white/[0.02] p-4 rounded-xl border border-white/5">
              <div className="flex items-center gap-2 mb-2">
                <Info size={16} className="text-cyan-400"/>
                <h5 className="font-medium text-white/90">Clinical Context</h5>
              </div>
              <p className="text-sm text-white/60 italic leading-snug">{wikiExplanation}</p>
            </div>
          )}
        </div>

        <div className="space-y-6">
          {/* Daily Clinical Routine - NEW */}
          {dailyRoutine.length > 0 && (
            <div className="bg-cyan-500/5 p-6 rounded-[24px] border border-cyan-500/20 space-y-4">
              <h4 className="text-md font-bold text-cyan-400 flex items-center gap-2 uppercase tracking-widest text-[10px]">
                <Clock size={18} className="text-cyan-400"/> Structured Daily Routine
              </h4>
              <div className="space-y-3">
                {dailyRoutine.map((item: string, idx: number) => {
                  const parts = item.split(': ');
                  const time = parts[0];
                  const task = parts[1] || '';
                  return (
                    <div key={idx} className="relative pl-6 border-l border-white/10 group">
                      <div className="absolute -left-[5px] top-1 w-2 h-2 rounded-full bg-cyan-500/50 group-hover:bg-cyan-400 transition-colors" />
                      <p className="text-[10px] font-black text-cyan-300 uppercase leading-none mb-1">{String(time)}</p>
                      <p className="text-xs text-white/80">
                        {typeof task === 'object' ? String(task.name || task.purpose || 'Directive') : String(task)}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Unified Clinical Directives */}
          <div className="bg-black/20 p-6 rounded-[24px] border border-white/5 space-y-4">
            <h4 className="text-md font-bold text-white flex items-center gap-2 uppercase tracking-widest text-[10px]">
              <Activity size={18} className="text-emerald-400"/> Lifestyle Directives
            </h4>
            
            <div className="space-y-3">
              {precautions?.slice(0, 3).map((pre: string, idx: number) => (
                <div key={`pre-${idx}`} className="flex items-start gap-3 bg-red-500/10 p-3 rounded-xl border border-red-500/20 text-sm text-red-200">
                  <ShieldAlert size={16} className="text-red-400 mt-0.5 shrink-0"/>
                  <span className="font-medium">{typeof pre === 'object' ? JSON.stringify(pre) : String(pre)}</span>
                </div>
              ))}
              
              {lifestyle?.slice(0, 2).map((rec: string, idx: number) => (
                <div key={`life-${idx}`} className="flex items-start gap-3 bg-white/[0.03] p-3 rounded-xl border border-white/5 text-sm text-white/80">
                  <CheckCircle size={16} className="text-emerald-400 mt-0.5 shrink-0"/>
                  <span>{typeof rec === 'object' ? JSON.stringify(rec) : String(rec)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Medication Education Bridge */}
      {displayMeds.length > 0 && (
        <div className="relative z-10 pt-4">
          <h4 className="text-md font-bold text-white flex items-center gap-2 mb-4 uppercase tracking-[0.2em] text-[10px]">
            <Pill size={18} className="text-purple-400"/> Pharmacological Insight
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {displayMeds.map((med: any, idx: number) => (
              <div key={idx} className="bg-[linear-gradient(135deg,rgba(176,91,255,0.08),rgba(0,243,255,0.05))] p-5 rounded-[24px] border border-white/10 shadow-lg group hover:border-purple-500/40 transition-all duration-300">
                <div className="flex items-center justify-between mb-3">
                  <div className="font-extrabold text-purple-200 text-lg group-hover:text-white transition-colors">{typeof med === 'object' ? String(med.name || 'Medication') : String(med)}</div>
                  <div className="bg-purple-500/20 p-1.5 rounded-lg">
                    <Pill size={14} className="text-purple-300" />
                  </div>
                </div>
                
                {(med.purpose || med.note) && (
                  <div className="space-y-1 mb-3">
                    <p className="text-[9px] uppercase tracking-widest text-cyan-300/60 font-black">Mechanism / Note</p>
                    <p className="text-[13px] text-white/90 leading-tight font-medium uppercase">{String(med.note || med.purpose || '')}</p>
                  </div>
                )}
                
                {med.target_condition && (
                  <div className="space-y-1">
                    <p className="text-[9px] uppercase tracking-widest text-purple-300/60 font-black">Target Indication</p>
                    <p className="text-[13px] text-white/80 leading-tight">{String(med.target_condition)}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default InsightsPanel;

