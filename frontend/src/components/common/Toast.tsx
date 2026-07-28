import { useEffect } from 'react';

interface ToastProps {
  message: string;
  onClose: () => void;
  durationMs?: number;
}

export function Toast({ message, onClose, durationMs = 4500 }: ToastProps) {
  useEffect(() => {
    const timerId = window.setTimeout(onClose, durationMs);
    return () => window.clearTimeout(timerId);
  }, [durationMs, message, onClose]);

  return (
    <div className="toast toast--success" role="status" aria-live="polite" aria-atomic="true">
      <span className="toast__icon" aria-hidden="true">✓</span>
      <p>{message}</p>
      <button
        className="toast__close"
        type="button"
        aria-label="Dismiss notification"
        onClick={onClose}
      >
        ×
      </button>
    </div>
  );
}
