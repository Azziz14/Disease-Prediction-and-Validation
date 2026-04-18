import React, { ReactNode } from 'react';

interface InputFieldProps {
  label: string;
  name: string;
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  icon?: ReactNode;
  placeholder?: string;
  error?: string;
  required?: boolean;
  min?: number;
  max?: number;
  step?: number;
}

const InputField: React.FC<InputFieldProps> = ({
  label,
  name,
  value,
  onChange,
  type = 'text',
  icon,
  placeholder,
  error,
  required = true,
  min,
  max,
  step
}) => {
  return (
    <div className="mb-5">
      <label htmlFor={name} className="block text-sm font-medium text-text-secondary mb-1.5">
        {label} {required && <span className="text-health-danger">*</span>}
      </label>
      <div className="relative">
        {icon && (
          <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none">
            {icon}
          </div>
        )}
        <input
          id={name}
          name={name}
          type={type}
          value={value}
          onChange={onChange}
          className={`w-full rounded-xl border bg-white px-4 py-3 text-sm text-text-primary outline-none transition-all placeholder:text-text-muted ${
            icon ? 'pl-11' : ''
          } ${
            error
              ? 'border-health-danger focus:border-health-danger focus:ring-2 focus:ring-health-danger/10'
              : 'border-border-subtle focus:border-brand focus:ring-2 focus:ring-brand/10'
          }`}
          placeholder={placeholder || label}
          required={required}
          min={min}
          max={max}
          step={step}
          aria-invalid={!!error}
        />
      </div>
      {error && (
        <p className="mt-1 text-xs font-medium text-health-danger">{error}</p>
      )}
    </div>
  );
};

export default InputField;
