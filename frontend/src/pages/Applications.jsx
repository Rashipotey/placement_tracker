import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, STATUSES } from "../api.js";
import { ConfirmDialog, Empty, ErrorBox, Loading, Notice } from "../ui.jsx";

export default function Applications() {
  const [status, setStatus] = useState("");
  const [apps, setApps] = useState(null);
  const [companies, setCompanies] = useState({});
  const [error, setError] = useState("");
  const [toDelete, setToDelete] = useState(null);
  const [notice, setNotice] = useState("");

  const load = useCallback(() => {
    setApps(null);
    setError("");
    Promise.all([api.applications(status), api.listCompanies()])
      .then(([a, c]) => {
        setCompanies(Object.fromEntries(c.map((x) => [x.id, x])));
        setApps(a);
      })
      .catch((err) => setError(err.message || "Failed to load applications"));
  }, [status]);

  useEffect(load, [load]);

  const confirmDelete = async () => {
    try {
      await api.deleteApplication(toDelete.id);
      setToDelete(null);
      setNotice("Application deleted");
      load();
    } catch (err) {
      setToDelete(null);
      setError(err.message || "Failed to delete application");
    }
  };

  return (
    <div>
      <div className="page-head">
        <h2>Applications</h2>
        <Link to="/applications/new" className="btn btn-primary">+ New</Link>
      </div>
      <Notice extra={notice} />
      <label className="field filter"><span>Filter by status</span>
        <select value={status} onChange={(e) => { setNotice(""); setStatus(e.target.value); }}>
          <option value="">All</option>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </label>
      {error && <ErrorBox onRetry={load}>Failed to load applications{error !== "Failed to load applications" ? `: ${error}` : ""}</ErrorBox>}
      {!error && apps === null && <Loading text="Loading applications..." />}
      {!error && apps && apps.length === 0 && (
        <Empty>You have no applications yet. <Link to="/applications/new">Create your first application</Link></Empty>
      )}
      {!error && apps && apps.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Company</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
            <tbody>
              {apps.map((a) => (
                <tr key={a.id}>
                  <td>{companies[a.company_id]?.name}</td>
                  <td>{companies[a.company_id]?.role}</td>
                  <td>{a.status}</td>
                  <td className="row-actions">
                    <div className="actions">
                      <Link to={`/applications/${a.id}/edit`} className="btn btn-sm">Edit</Link>
                      <Link to={`/applications/${a.id}/rounds`} className="btn btn-sm">Rounds</Link>
                      <button className="btn btn-sm btn-danger" onClick={() => setToDelete(a)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {toDelete && (
        <ConfirmDialog
          message={`Delete application "${companies[toDelete.company_id]?.name}"? This cannot be undone.`}
          onCancel={() => setToDelete(null)}
          onConfirm={confirmDelete}
        />
      )}
    </div>
  );
}
