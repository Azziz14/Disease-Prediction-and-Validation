export type AlertSeverity = 'high' | 'moderate' | 'normal';

export interface ClinicalMetrics {
  glucose: number;
  bloodPressure: number;
  bmi: number;
  age: number;
}

export interface RangeAlert {
  key: keyof ClinicalMetrics;
  message: string;
  severity: AlertSeverity;
}

export const CLINICAL_RANGES = {
  glucose: { min: 0, max: 260, normalMin: 70, normalMax: 140, label: 'Glucose', unit: 'mg/dL' },
  bloodPressure: { min: 40, max: 220, normalMin: 80, normalMax: 120, label: 'Blood Pressure', unit: 'mmHg' },
  bmi: { min: 10, max: 55, normalMin: 18, normalMax: 25, label: 'BMI', unit: 'kg/m2' }
} as const;

export const evaluateRangeAlerts = (metrics: ClinicalMetrics): RangeAlert[] => {
  const alerts: RangeAlert[] = [];

  if (metrics.glucose > CLINICAL_RANGES.glucose.normalMax) {
    alerts.push({
      key: 'glucose',
      message: 'High Glucose Level Detected',
      severity: 'high'
    });
  }

  if (metrics.bloodPressure > CLINICAL_RANGES.bloodPressure.normalMax) {
    alerts.push({
      key: 'bloodPressure',
      message: 'Blood Pressure is Above Normal',
      severity: 'high'
    });
  }

  if (metrics.bmi > CLINICAL_RANGES.bmi.normalMax) {
    alerts.push({
      key: 'bmi',
      message: 'BMI is Above Healthy Range',
      severity: 'moderate'
    });
  }

  return alerts;
};

export const buildHealthSummary = (
  metrics: ClinicalMetrics,
  risk: string | undefined
): string[] => {
  const summary: string[] = [];

  if (metrics.glucose > CLINICAL_RANGES.glucose.normalMax) {
    summary.push('Elevated glucose is a major driver of diabetes risk classification.');
  }

  if (metrics.bmi > CLINICAL_RANGES.bmi.normalMax) {
    summary.push('Higher BMI can increase insulin resistance and metabolic stress.');
  }

  if (metrics.age >= 45) {
    summary.push('Age above 45 is associated with higher baseline risk in diabetes models.');
  }

  if (metrics.bloodPressure > CLINICAL_RANGES.bloodPressure.normalMax) {
    summary.push('Blood pressure above normal can indicate cardiometabolic strain.');
  }

  if (summary.length === 0) {
    summary.push('Core markers are mostly within expected ranges, supporting a lower risk profile.');
  }

  if (risk && risk.toLowerCase() === 'high') {
    summary.push('Model classified the patient as high risk based on the combined pattern of these features.');
  }

  if (risk && risk.toLowerCase() === 'low') {
    summary.push('Model classified the patient as low risk, but continued monitoring is still recommended.');
  }

  return summary;
};
