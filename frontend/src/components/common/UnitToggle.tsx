import type { UnitSystem } from '../../types/weather';

interface UnitToggleProps {
  value: UnitSystem;
  onChange: (value: UnitSystem) => void;
  disabled?: boolean;
}

export function UnitToggle({ value, onChange, disabled = false }: UnitToggleProps) {
  return (
    <div className="unit-toggle" aria-label="Weather unit system">
      <button
        type="button"
        aria-pressed={value === 'metric'}
        disabled={disabled}
        onClick={() => onChange('metric')}
      >
        °C Metric
      </button>
      <button
        type="button"
        aria-pressed={value === 'imperial'}
        disabled={disabled}
        onClick={() => onChange('imperial')}
      >
        °F Imperial
      </button>
    </div>
  );
}
