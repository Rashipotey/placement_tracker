import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { Empty, ErrorBox, Loading } from "../ui.jsx";

// Read-only list of companies for regular users (CPT-45): no create/edit/delete actions.
export default function Companies() {
  const [companies, setCompanies] = useState(null);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    setCompanies(null);
    setError("");
    api.listCompanies().then(setCompanies).catch((err) => setError(err.message || "Failed to load companies"));
  }, []);

  useEffect(load, [load]);

  return (
    <div>
      <div className="page-head"><h2>Companies</h2></div>
      {error && <ErrorBox onRetry={load}>Failed to load companies: {error}</ErrorBox>}
      {!error && companies === null && <Loading text="Loading companies..." />}
      {!error && companies && companies.length === 0 && (
        <Empty>No companies available yet. An administrator can add them.</Empty>
      )}
      {!error && companies && companies.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Company</th><th>Role</th><th>Location</th></tr></thead>
            <tbody>
              {companies.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.role}</td>
                  <td>{c.location}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
