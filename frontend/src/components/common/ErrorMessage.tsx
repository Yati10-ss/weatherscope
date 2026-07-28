interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="error-message" role="alert">
      <span aria-hidden="true">⚠️</span>
      <div>
        <strong>Unable to complete the request</strong>
        <p>{message}</p>
      </div>
      {onRetry ? (
        <button className="button button--secondary button--small" onClick={onRetry} type="button">
          Retry
        </button>
      ) : null}
    </div>
  );
}
