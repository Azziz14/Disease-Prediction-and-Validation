import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar } from 'recharts';

interface ChartPanelProps {
  features: any;
  confidence?: number;
}

const ChartPanel: React.FC<ChartPanelProps> = ({ features, confidence }) => {
  const barData = [
    { name: 'Glucose', value: Number(features.glucose) || 0, fill: '#2563eb' },
    { name: 'BP', value: Number(features.bloodPressure) || 0, fill: '#06b6d4' },
    { name: 'BMI', value: Number(features.bmi) || 0, fill: '#6366f1' },
    { name: 'Age', value: Number(features.age) || 0, fill: '#8b5cf6' },
  ];

  const confData = [{ name: 'Confidence', value: confidence ? Math.round(confidence * 100) : 0, fill: '#2563eb' }];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white rounded-2xl border border-border-subtle shadow-card p-6">
        <h3 className="text-sm font-display font-semibold text-text-primary mb-5 pb-3 border-b border-border-muted">
          Feature Distribution
        </h3>
        <div className="h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e5e7eb', fontSize: 12 }} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={28} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {confidence !== undefined && (
        <div className="bg-white rounded-2xl border border-border-subtle shadow-card p-6 flex flex-col items-center">
          <h3 className="text-sm font-display font-semibold text-text-primary mb-4 pb-3 border-b border-border-muted w-full">
            Model Confidence
          </h3>
          <div className="h-[200px] w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart cx="50%" cy="50%" innerRadius="60%" outerRadius="90%" data={confData} startAngle={180} endAngle={0}>
                <RadialBar dataKey="value" cornerRadius={6} background={{ fill: '#f3f4f6' }} />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute text-center">
              <p className="text-2xl font-display font-bold text-text-primary">{confData[0].value}%</p>
              <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Confidence</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChartPanel;
