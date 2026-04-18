import React from 'react';

type AlertSeverity = 'high' | 'moderate' | 'normal';

interface AlertBoxProps {
  message: string;
  severity?: AlertSeverity;
}

const AlertBox: React.FC<AlertBoxProps> = ({
  message,
  severity = 'normal'
}) => {
  const severityLabel: Record<AlertSeverity, string> = {
    high: 'High Risk',
    moderate: 'Moderate Risk',
    normal: 'Normal'
  };

  return (
    <div className={`hc-alert hc-alert-${severity}`} role="alert">
      <span className="hc-alert-badge">{severityLabel[severity]}</span>
      <p className="hc-alert-message">{message}</p>
    </div>
  );
};

export default AlertBox;
