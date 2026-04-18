import React from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';

interface ChartComponentProps {
  label: string;
  value: number;
  unit: string;
  min: number;
  max: number;
  normalMin: number;
  normalMax: number;
}

const ChartComponent: React.FC<ChartComponentProps> = ({
  label,
  value,
  unit,
  min,
  max,
  normalMin,
  normalMax
}) => {
  const clampedValue = Number.isFinite(value) ? Math.max(min, Math.min(max, value)) : min;
  const chartData = [{ metric: label, value: clampedValue }];

  const status = clampedValue > normalMax ? 'high' : clampedValue < normalMin ? 'moderate' : 'normal';

  return (
    <article className="hc-chart-card">
      <header className="hc-chart-header">
        <h4>{label}</h4>
        <span className={`hc-pill hc-pill-${status}`}>
          {clampedValue.toFixed(1)} {unit}
        </span>
      </header>

      <div className="hc-chart-body">
        <ResponsiveContainer width="100%" height={170}>
          <BarChart data={chartData} margin={{ top: 16, right: 14, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dbeafe" />
            <XAxis dataKey="metric" tick={{ fill: '#365b85', fontSize: 12 }} />
            <YAxis domain={[min, max]} tick={{ fill: '#365b85', fontSize: 12 }} />
            <Tooltip
              formatter={(val) => {
                const numericValue = typeof val === 'number' ? val : Number(val || 0);
                return [`${numericValue.toFixed(1)} ${unit}`, label];
              }}
            />
            <ReferenceArea y1={normalMin} y2={normalMax} fill="#dcfce7" fillOpacity={0.65} />
            <ReferenceLine y={normalMin} stroke="#16a34a" strokeDasharray="5 5" />
            <ReferenceLine y={normalMax} stroke="#16a34a" strokeDasharray="5 5" />
            <Bar dataKey="value" fill="#1c7ed6" radius={[8, 8, 0, 0]} barSize={44} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="hc-range-label">
        Normal Range: {normalMin} - {normalMax} {unit}
      </p>
    </article>
  );
};

export default ChartComponent;
