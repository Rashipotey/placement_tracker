import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, STATUSES } from "../api.js";

export default function Applications() {
  const [status, setStatus] = useState("");
  const [apps, setApps] = useState(null);
  const [companies, setCompanies] = useState({});
  const [error, setError] = useState(false);
  const [toDelete, setToDelete] = useState(null);

  const load = useCallback(() => {
    setApps(null);
    setError(false);
    Promise.all([api.applications(status), api.companies()])
      .then(([a, c]) => {
        setCompanies(Object.fromEntries(c.map((x) => [x.id, x])));
        setApps(a);
      })
      .catch(() => setError(true));
  }, [status]);

  useEffect(load, [load]);

  const confirmDelete = async () => {
    try {
      await api.deleteApplication(toDelete.id);
      setToDelete(null);
      load();
    } catch {
      setToDelete(null);
      setError(true);
    }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>Applications</h2>
        <Link to="/applications/new"><button>+ New</button></Link>
      </div>
      <p>
        <label>Filter by status:{" "}
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
      </p>
      {error && <p role="alert">Failed to load applications <button onClick={load}>Retry</button></p>}
      {!error && apps === null && <p>Loading applications...</p>}
      {!error && apps && apps.length === 0 && (
        <p>You have no applications yet. <Link to="/applications/new">Create your first application</Link></p>
      )}
      {!error && apps && apps.length > 0 && (
        <table>
          <thead><tr><th>Company</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {apps.map((a) => (
              <tr key={a.id}>
                <td>{companies[a.company_id]?.name}</td>
                <td>{companies[a.company_id]?.role}</td>
                <td>{a.status}</td>
                <td>
                  <Link to={`/applications/${a.id}/edit`}>Edit</Link>{" "}
                  <Link to={`/applications/${a.id}/rounds`}>Rounds</Link>{" "}
                  <button onClick={() => setToDelete(a)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {toDelete && (
        <div role="dialog" style={{ border: "1px solid #888", padding: 16, marginTop: 16, maxWidth: 320 }}>
          <strong>Confirm delete</strong>
          <p>Delete application "{companies[toDelete.company_id]?.name}"? This cannot be undone.</p>
          <button onClick={() => setToDelete(null)}>Cancel</button>{" "}
          <button onClick={confirmDelete}>Delete</button>
        </div>
      )}
    </div>
  );
}
