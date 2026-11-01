import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ROUND_STATUSES } from "../api.js";
import { ConfirmDialog, Empty, ErrorBox, Loading, Notice } from "../ui.jsx";

const EMPTY = { round_name: "", status: "PENDING", feedback: "" };

export default function Rounds() {
  const { id } = useParams();
  const [rounds, setRounds] = useState(null);
  const [currentId, setCurrentId] = useState(null);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null); // round id being edited, or "new"
  const [form, setForm] = useState(EMPTY);
  const [formError, setFormError] = useState("");
  const [toDelete, setToDelete] = useState(null);
  const [notice, setNotice] = useState("");

  const load = useCallback(() => {
    setRounds(null);
    setError("");
    Promise.all([api.rounds(id), api.application(id)])
      .then(([r, a]) => {
        setRounds(r);
        setCurrentId(a.round_id);
      })
      .catch((err) => setError(err.message || "Failed to load rounds"));
  }, [id]);

  useEffect(load, [load]);

  const startNew = () => {
    setEditing("new");
    setForm(EMPTY);
    setFormError("");
    setNotice("");
  };

  const startEdit = (r) => {
    setEditing(r.id);
    setForm({ round_name: r.round_name, status: r.status, feedback: r.feedback || "" });
    setFormError("");
    setNotice("");
  };

  const save = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!form.round_name.trim()) return setFormError("Round name is required");
    const data = { round_name: form.round_name, status: form.status, feedback: form.feedback || null };
    try {
      if (editing === "new") await api.createRound(id, data);
      else await api.updateRound(id, editing, data);
      setNotice(editing === "new" ? "Round created" : "Round updated");
      setEditing(null);
      load();
    } catch (err) {
      setFormError(`Unable to save round: ${err.message}`);
    }
  };

  const confirmDelete = async () => {
    try {
      await api.deleteRound(id, toDelete.id);
      setToDelete(null);
      setNotice("Round deleted");
      load();
    } catch (err) {
      setToDelete(null);
      setError(err.message || "Failed to delete round");
    }
  };

  return (
    <div>
      <div className="page-head">
        <h2>Rounds</h2>
        <div className="actions">
          <Link to="/dashboard" className="btn">Back to applications</Link>
          <button className="btn btn-primary" onClick={startNew}>+ New round</button>
        </div>
      </div>
      <Notice extra={notice} />
      {error && <ErrorBox onRetry={load}>Failed to load rounds{error !== "Failed to load rounds" ? `: ${error}` : ""}</ErrorBox>}
      {!error && rounds === null && <Loading text="Loading rounds..." />}
      {!error && rounds && rounds.length === 0 && <Empty>This application has no rounds yet.</Empty>}
      {!error && rounds && rounds.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Round</th><th>Status</th><th>Feedback</th><th>Actions</th></tr></thead>
            <tbody>
              {rounds.map((r) => (
                <tr key={r.id}>
                  <td>{r.round_name}{r.id === currentId && " (current)"}</td>
                  <td>{r.status}</td>
                  <td>{r.feedback}</td>
                  <td className="row-actions">
                    <div className="actions">
                      <button className="btn btn-sm" onClick={() => startEdit(r)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => setToDelete(r)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {editing && (
        <form onSubmit={save} className="card" style={{ marginTop: 16 }} noValidate>
          <h3>{editing === "new" ? "New Round" : "Edit Round"}</h3>
          <label className="field"><span>Round name *</span>
            <input value={form.round_name} onChange={(e) => setForm({ ...form, round_name: e.target.value })} />
          </label>
          <label className="field"><span>Status</span>
            <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              {ROUND_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </label>
          <label className="field"><span>Feedback</span>
            <textarea rows={3} value={form.feedback} onChange={(e) => setForm({ ...form, feedback: e.target.value })} />
          </label>
          <div className="actions">
            <button type="submit" className="btn btn-primary">Save</button>
            <button type="button" className="btn" onClick={() => setEditing(null)}>Cancel</button>
          </div>
          {formError && <p className="alert" role="alert">{formError}</p>}
        </form>
      )}
      {toDelete && (
        <ConfirmDialog
          message={`Delete round "${toDelete.round_name}"? This cannot be undone.`}
          onCancel={() => setToDelete(null)}
          onConfirm={confirmDelete}
        />
      )}
    </div>
  );
}
