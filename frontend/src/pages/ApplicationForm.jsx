import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, STATUSES } from "../api.js";
import { Empty, ErrorBox, Loading } from "../ui.jsx";

export default function ApplicationForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [companies, setCompanies] = useState(null);
  const [companiesError, setCompaniesError] = useState("");
  const [companyId, setCompanyId] = useState("");
  const [status, setStatus] = useState("APPLIED");
  const [notes, setNotes] = useState("");
  const [rounds, setRounds] = useState([]);
  const [roundId, setRoundId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadCompanies = useCallback(() => {
    setCompanies(null);
    setCompaniesError("");
    api.listCompanies().then(setCompanies).catch((err) => setCompaniesError(err.message || "Unable to load companies"));
  }, []);

  useEffect(() => {
    loadCompanies();
    if (id) {
      api.application(id)
        .then((a) => {
          setCompanyId(a.company_id);
          setStatus(a.status);
          setNotes(a.notes || "");
          setRoundId(a.round_id || "");
        })
        .catch((err) => setError(err.message || "Unable to load application"));
      api.rounds(id).then(setRounds).catch((err) => setError(err.message || "Unable to load rounds"));
    }
  }, [id, loadCompanies]);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!companyId) return setError("Company is required");
    if (!status) return setError("Status is required");
    const data = { company_id: companyId, status, notes: notes || null };
    setBusy(true);
    try {
      if (id) await api.updateApplication(id, { ...data, round_id: roundId || null });
      else await api.createApplication(data);
      navigate("/dashboard", { state: { notice: id ? "Application updated" : "Application created" } });
    } catch (err) {
      setError(err.status === 0 ? "Unable to save application" : `Unable to save application: ${err.message}`);
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit} className="card" noValidate>
      <h2>{id ? "Edit Application" : "New Application"}</h2>
      {companies === null && !companiesError && <Loading text="Loading companies..." />}
      {companiesError && <ErrorBox onRetry={loadCompanies}>Unable to load companies: {companiesError}</ErrorBox>}
      {companies && companies.length === 0 && (
        <Empty>No companies available. Ask an administrator to add companies before creating applications.</Empty>
      )}
      <label className="field"><span>Company *</span>
        <select value={companyId} onChange={(e) => setCompanyId(e.target.value)}>
          <option value="">Select company</option>
          {(companies || []).map((c) => <option key={c.id} value={c.id}>{c.name} - {c.role}</option>)}
        </select>
      </label>
      <label className="field"><span>Status *</span>
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </label>
      {id && (
        <label className="field"><span>Current round</span>
          <select value={roundId} onChange={(e) => setRoundId(e.target.value)}>
            <option value="">None</option>
            {rounds.map((r) => <option key={r.id} value={r.id}>{r.round_name}</option>)}
          </select>
        </label>
      )}
      <label className="field"><span>Notes</span>
        <textarea rows={4} value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>
      <div className="actions">
        <button type="submit" className="btn btn-primary" disabled={busy}>Save</button>
        <button type="button" className="btn" onClick={() => navigate("/dashboard")}>Cancel</button>
        {id && <Link to={`/applications/${id}/rounds`} className="btn">Manage rounds</Link>}
      </div>
      {error && <p className="alert" role="alert">{error}</p>}
    </form>
  );
}
