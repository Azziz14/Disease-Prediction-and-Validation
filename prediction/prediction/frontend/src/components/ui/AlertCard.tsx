import React from 'react';
import { AlertTriangle, CheckCircle2 } from 'lucide-react';

const AlertCard: React.FC<{ features: any }> = ({ features }) => {
  const glucose = Number(features.glucose) || 0;
  const bmi = Number(features.bmi) || 0;
  const bp = Number(features.bloodPressure) || 0;

  const alerts: { msg: string; type: 'warn' | 'ok' }[] = [];

  if (glucose > 140) alerts.push({ msg: `Glucose elevated at ${glucose} mg/dL`, type: 'warn' });
  else if (glucose > 0) alerts.push({ msg: `Glucose within range (${glucose} mg/dL)`, type: 'ok' });

  if (bmi > 30) alerts.push({ msg: `BMI ${bmi} — Obese classification`, type: 'warn' });
  else if (bmi > 0 && bmi < 18.5) alerts.push({ msg: `BMI ${bmi} — Underweight`, type: 'warn' });
  else if (bmi > 0) alerts.push({ msg: `BMI within normal range (${bmi})`, type: 'ok' });

  if (bp > 140) alerts.push({ msg: `Blood Pressure ${bp} — Hypertensive`, type: 'warn' });
  else if (bp > 0) alerts.push({ msg: `Blood Pressure normal (${bp})`, type: 'ok' });

  if (alerts.length === 0) return null;

  return (
    <div className="space-y-2">
      {alerts.map((a, i) => (
        <div key={i} className={`flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-sm font-medium ${
          a.type === 'warn' ? 'bg-amber-50 text-amber-700 border border-amber-100' : 'bg-emerald-50 text-emerald-700 border border-emerald-100'
        }`}>
          {a.type === 'warn' ? <AlertTriangle size={15} /> : <CheckCircle2 size={15} />}
          {a.msg}
        </div>
      ))}
    </div>
  );
};

export default AlertCard;
