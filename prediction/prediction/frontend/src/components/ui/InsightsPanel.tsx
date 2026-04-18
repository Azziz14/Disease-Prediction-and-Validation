import React from 'react';
import { Lightbulb } from 'lucide-react';

const InsightsPanel: React.FC<{ predictionResult: any }> = ({ predictionResult }) => {
  if (!predictionResult?.explanation) return null;

  const entries = Object.entries(predictionResult.explanation);
  if (entries.length === 0) return null;

  return (
    <div className="bg-white rounded-2xl border border-border-subtle shadow-card p-6">
      <div className="flex items-center gap-2 mb-4 pb-3 border-b border-border-muted">
        <Lightbulb size={16} className="text-brand" />
        <h3 className="text-sm font-display font-semibold text-text-primary">Clinical Insights</h3>
      </div>
      <div className="space-y-3">
        {entries.map(([key, value]) => (
          <div key={key} className="flex items-start gap-3 p-3 bg-surface-alt rounded-xl">
            <div className="w-1.5 h-1.5 rounded-full bg-brand mt-2 shrink-0" />
            <div>
              <p className="text-sm font-medium text-text-primary">{key}</p>
              <p className="text-xs text-text-secondary mt-0.5">{value as string}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InsightsPanel;
