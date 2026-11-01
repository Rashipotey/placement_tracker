import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api, STATUSES } from "../api.js";

export default function ApplicationForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [companies, setCompanies] = useState([]);
  const [companyId, setCompanyId] = useState("");
  const [status, setStatus] = useState("APPLIED");
  const [notes, setNotes] = useState("");
  const [rounds, setRounds] = useState([]);
  const [roundId, setRoundId] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.companies().then(setCompanies).catch(() => setError("Unable to load companies"));
    if (id) {
      api.application(id)
        .then((a) => {
          setCompanyId(a.company_id);
          setStatus(a.status);
          setNotes(a.notes || "");
          setRoundId(a.round_id || "");
        })
        .catch(() => setError("Unable to load application"));
      api.rounds(id).then(setRounds).catch(() => setError("Unable to load rounds"));
    }
  }, [id]);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!companyId) return setError("Company is required");
    if (!status) return setError("Status is required");
    const data = { company_id: companyId, status, notes: notes || null };
    try {
      if (id) await api.updateApplication(id, { ...data, round_id: roundId || null });
      else await api.createApplication(data);
      navigate("/applications");
    } catch {
      setError("Unable to save application");
    }
  };

  return (
    <form onSubmit={submit} style={{ maxWidth: 480 }}>
      <h2>{id ? "Edit Application" : "New Application"}</h2>
      <p>
        <label>Company *{" "}
          <select value={companyId} onChange={(e) => setCompanyId(e.target.value)}>
            <option value="">Select company</option>
            {companies.map((c) => <option key={c.id} value={c.id}>{c.name} - {c.role}</option>)}
          </select>
        </label>
      </p>
      <p>
        <label>Status *{" "}
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
      </p>
      {id && (
        <p>
          <label>Current round{" "}
            <select value={roundId} onChange={(e) => setRoundId(e.target.value)}>
              <option value="">None</option>
              {rounds.map((r) => <option key={r.id} value={r.id}>{r.round_name}</option>)}
            </select>
          </label>
        </p>
      )}
      <p><label>Notes<br /><textarea rows={4} cols={50} value={notes} onChange={(e) => setNotes(e.target.value)} /></label></p>
      <button type="submit">Save</button>{" "}
      <button type="button" onClick={() => navigate("/applications")}>Cancel</button>
      {error && <p role="alert" style={{ color: "crimson" }}>{error}</p>}
    </form>
  );
}
