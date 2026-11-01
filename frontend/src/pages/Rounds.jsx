import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ROUND_STATUSES } from "../api.js";

const EMPTY = { round_name: "", status: "PENDING", feedback: "" };

export default function Rounds() {
  const { id } = useParams();
  const [rounds, setRounds] = useState(null);
  const [currentId, setCurrentId] = useState(null);
  const [error, setError] = useState(false);
  const [editing, setEditing] = useState(null); // round id being edited, or "new"
  const [form, setForm] = useState(EMPTY);
  const [formError, setFormError] = useState("");
  const [toDelete, setToDelete] = useState(null);

  const load = useCallback(() => {
    setRounds(null);
    setError(false);
    Promise.all([api.rounds(id), api.application(id)])
      .then(([r, a]) => {
        setRounds(r);
        setCurrentId(a.round_id);
      })
      .catch(() => setError(true));
  }, [id]);

  useEffect(load, [load]);

  const startNew = () => {
    setEditing("new");
    setForm(EMPTY);
    setFormError("");
  };

  const startEdit = (r) => {
    setEditing(r.id);
    setForm({ round_name: r.round_name, status: r.status, feedback: r.feedback || "" });
    setFormError("");
  };

  const save = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!form.round_name.trim()) return setFormError("Round name is required");
    const data = { round_name: form.round_name, status: form.status, feedback: form.feedback || null };
    try {
      if (editing === "new") await api.createRound(id, data);
      else await api.updateRound(id, editing, data);
      setEditing(null);
      load();
    } catch {
      setFormError("Unable to save round");
    }
  };

  const confirmDelete = async () => {
    try {
      await api.deleteRound(id, toDelete.id);
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
        <h2>Rounds</h2>
        <span>
          <Link to="/applications">Back to applications</Link>{" "}
          <button onClick={startNew}>+ New round</button>
        </span>
      </div>
      {error && <p role="alert">Failed to load rounds <button onClick={load}>Retry</button></p>}
      {!error && rounds === null && <p>Loading rounds...</p>}
      {!error && rounds && rounds.length === 0 && <p>This application has no rounds yet.</p>}
      {!error && rounds && rounds.length > 0 && (
        <table>
          <thead><tr><th>Round</th><th>Status</th><th>Feedback</th><th>Actions</th></tr></thead>
          <tbody>
            {rounds.map((r) => (
              <tr key={r.id}>
                <td>{r.round_name}{r.id === currentId && " (current)"}</td>
                <td>{r.status}</td>
                <td>{r.feedback}</td>
                <td>
                  <button onClick={() => startEdit(r)}>Edit</button>{" "}
                  <button onClick={() => setToDelete(r)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {editing && (
        <form onSubmit={save} style={{ marginTop: 16, maxWidth: 480 }}>
          <h3>{editing === "new" ? "New Round" : "Edit Round"}</h3>
          <p><label>Round name *{" "}
            <input value={form.round_name} onChange={(e) => setForm({ ...form, round_name: e.target.value })} />
          </label></p>
          <p><label>Status{" "}
            <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              {ROUND_STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </label></p>
          <p><label>Feedback<br />
            <textarea rows={3} cols={50} value={form.feedback} onChange={(e) => setForm({ ...form, feedback: e.target.value })} />
          </label></p>
          <button type="submit">Save</button>{" "}
          <button type="button" onClick={() => setEditing(null)}>Cancel</button>
          {formError && <p role="alert" style={{ color: "crimson" }}>{formError}</p>}
        </form>
      )}
      {toDelete && (
        <div role="dialog" style={{ border: "1px solid #888", padding: 16, marginTop: 16, maxWidth: 320 }}>
          <strong>Confirm delete</strong>
          <p>Delete round "{toDelete.round_name}"? This cannot be undone.</p>
          <button onClick={() => setToDelete(null)}>Cancel</button>{" "}
          <button onClick={confirmDelete}>Delete</button>
        </div>
      )}
    </div>
  );
}
