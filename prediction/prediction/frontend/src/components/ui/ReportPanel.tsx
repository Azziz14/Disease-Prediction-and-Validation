import React, { useState } from 'react';
import { FileText, ChevronDown, ChevronRight, Printer } from 'lucide-react';

const ReportPanel: React.FC<{ report: any }> = ({ report }) => {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  if (!report) return null;

  const toggle = (key: string) => setExpanded(prev => ({ ...prev, [key]: !prev[key] }));

  const Section: React.FC<{ title: string; sectionKey: string; children: React.ReactNode }> = ({ title, sectionKey, children }) => (
    <div className="border border-border-subtle rounded-xl overflow-hidden">
      <button onClick={() => toggle(sectionKey)} className="w-full flex items-center justify-between px-4 py-3 bg-surface-alt hover:bg-surface-hover transition-colors">
        <span className="text-sm font-semibold text-text-primary">{title}</span>
        {expanded[sectionKey] ? <ChevronDown size={15} className="text-text-muted" /> : <ChevronRight size={15} className="text-text-muted" />}
      </button>
      {expanded[sectionKey] && <div className="px-4 py-3 border-t border-border-muted">{children}</div>}
    </div>
  );

  return (
    <div className="bg-white rounded-2xl border border-border-subtle shadow-card p-6">
      <div className="flex items-center justify-between mb-5 pb-3 border-b border-border-muted">
        <div className="flex items-center gap-2">
          <FileText size={16} className="text-brand" />
          <h3 className="text-sm font-display font-semibold text-text-primary">Health Report</h3>
        </div>
        <button onClick={() => window.print()} className="flex items-center gap-1.5 text-xs font-medium text-text-muted hover:text-brand transition-colors">
          <Printer size={13} /> Print
        </button>
      </div>

      <div className="space-y-3">
        {report.summary && (
          <Section title="Summary" sectionKey="summary">
            <p className="text-sm text-text-secondary leading-relaxed">{report.summary}</p>
          </Section>
        )}

        {report.feature_analysis && (
          <Section title="Feature Analysis" sectionKey="features">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[10px] text-text-muted uppercase tracking-wider">
                    <th className="text-left py-2">Feature</th>
                    <th className="text-left py-2">Value</th>
                    <th className="text-left py-2">Normal</th>
                    <th className="text-left py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {report.feature_analysis.map((f: any, i: number) => (
                    <tr key={i} className="border-t border-border-muted">
                      <td className="py-2 font-medium text-text-primary">{f.name}</td>
                      <td className="py-2 text-text-secondary">{f.value}</td>
                      <td className="py-2 text-text-muted">{f.normal_range}</td>
                      <td className="py-2">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                          f.status === 'High' ? 'bg-red-50 text-health-danger' :
                          f.status === 'Low' ? 'bg-amber-50 text-amber-600' :
                          'bg-emerald-50 text-health-success'
                        }`}>
                          {f.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        )}

        {report.recommendations && (
          <Section title="Recommendations" sectionKey="recs">
            <ul className="space-y-1.5">
              {report.recommendations.map((r: any, i: number) => (
                <li key={i} className="flex items-start gap-2 text-sm text-text-secondary">
                  <span className="text-brand mt-1">•</span> {typeof r === 'object' ? String(r.name || r.purpose || 'Directive') : String(r)}
                </li>
              ))}
            </ul>
          </Section>
        )}

        {report.disclaimer && (
          <div className="bg-amber-50 border border-amber-100 rounded-xl p-3 mt-3">
            <p className="text-xs text-amber-700">{report.disclaimer}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportPanel;