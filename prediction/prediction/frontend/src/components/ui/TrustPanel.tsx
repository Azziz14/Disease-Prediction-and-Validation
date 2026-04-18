import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, ShieldCheck } from 'lucide-react';
import { getModelInfoAPI, ModelInfo } from '../../services/api';

const TrustPanel: React.FC<{ disease: string }> = ({ disease }) => {
  const [info, setInfo] = useState<ModelInfo | null>(null);

  useEffect(() => {
    getModelInfoAPI(disease).then(setInfo);
  }, [disease]);

  if (!info?.available) return null;

  return (
    <div className="bg-white rounded-2xl border border-border-subtle shadow-card p-6">
      <div className="flex items-center gap-2 mb-5 pb-3 border-b border-border-muted">
        <Brain size={16} className="text-brand" />
        <h3 className="text-sm font-display font-semibold text-text-primary">Model Trust & Transparency</h3>
      </div>

      <div className="space-y-3">
        {info.models.map((m, i) => (
          <div key={m.id}>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-text-secondary font-medium flex items-center gap-1.5">
                {m.name}
                {m.is_best && (
                  <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-50 text-health-success border border-emerald-100">
                    <ShieldCheck size={9} /> Best
                  </span>
                )}
              </span>
              <span className="text-text-primary font-bold">{m.accuracy}%</span>
            </div>
            <div className="w-full h-1.5 bg-surface-alt rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${m.accuracy}%` }}
                transition={{ duration: 0.8, delay: 0.15 + i * 0.08 }}
                className={`h-full rounded-full ${m.is_best ? 'bg-health-success' : 'bg-brand/50'}`}
              />
            </div>
          </div>
        ))}
      </div>

      {info.best_model && (
        <div className="mt-4 pt-3 border-t border-border-muted">
          <p className="text-xs text-text-muted">
            Ensemble: <span className="font-medium text-text-secondary">{info.best_model} + ANN weighted average</span>
          </p>
        </div>
      )}

      <div className="mt-4 bg-surface-alt rounded-xl p-3">
        <p className="text-[10px] text-text-muted leading-relaxed">
          AI predictions are probabilistic. All results should be validated by qualified healthcare professionals.
        </p>
      </div>
    </div>
  );
};

export default TrustPanel;
