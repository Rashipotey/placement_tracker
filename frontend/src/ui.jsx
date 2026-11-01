// Shared presentational pieces so every page uses the same states and controls.
import { useLocation } from "react-router-dom";

export function Loading({ text }) {
  return (
    <p className="loading" role="status">
      <span className="spinner" aria-hidden="true" />
      {text}
    </p>
  );
}

export function ErrorBox({ children, onRetry }) {
  return (
    <p className="alert" role="alert">
      {children}{" "}
      {onRetry && <button type="button" className="btn btn-sm" onClick={onRetry}>Retry</button>}
    </p>
  );
}

export function Empty({ children }) {
  return <p className="empty">{children}</p>;
}

// Success message passed through router state after a create/update/delete.
export function Notice({ extra }) {
  const { state } = useLocation();
  const text = extra || state?.notice;
  return text ? <p className="notice" role="status">{text}</p> : null;
}

export function ConfirmDialog({ message, onCancel, onConfirm }) {
  return (
    <div className="dialog-backdrop">
      <div className="card dialog" role="dialog" aria-modal="true">
        <strong>Confirm delete</strong>
        <p>{message}</p>
        <div className="actions">
          <button type="button" className="btn" onClick={onCancel}>Cancel</button>
          <button type="button" className="btn btn-danger" onClick={onConfirm}>Delete</button>
        </div>
      </div>
    </div>
  );
}
