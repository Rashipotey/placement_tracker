import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";
import { ConfirmDialog, Empty, ErrorBox, Loading, Notice } from "../ui.jsx";

const EMPTY = { name: "", role: "", location: "", package_lpa: "", application_link: "" };

// ADMIN dashboard: company management (list / create / edit / delete).
export default function Admin() {
  const [companies, setCompanies] = useState(null);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null); // company id being edited, or "new"
  const [form, setForm] = useState(EMPTY);
  const [formError, setFormError] = useState("");
  const [toDelete, setToDelete] = useState(null);
  const [notice, setNotice] = useState("");
  const [deleteError, setDeleteError] = useState("");

  const load = useCallback(() => {
    setCompanies(null);
    setError("");
    api.listCompanies().then(setCompanies).catch((err) => setError(err.message || "Failed to load companies"));
  }, []);

  useEffect(load, [load]);

  const startNew = () => {
    setEditing("new");
    setForm(EMPTY);
    setFormError("");
    setNotice("");
    setDeleteError("");
  };

  const startEdit = (c) => {
    setEditing(c.id);
    setForm({
      name: c.name,
      role: c.role,
      location: c.location || "",
      package_lpa: c.package_lpa ?? "",
      application_link: c.application_link || "",
    });
    setFormError("");
    setNotice("");
    setDeleteError("");
  };

  const save = async (e) => {
    e.preventDefault();
    setFormError("");
    if (!form.name.trim()) return setFormError("Company name is required");
    if (!form.role.trim()) return setFormError("Role is required");
    const lpa = form.package_lpa === "" ? null : Number(form.package_lpa);
    if (lpa !== null && (Number.isNaN(lpa) || lpa < 0)) return setFormError("Package (LPA) must be a number of 0 or more");
    const data = {
      name: form.name,
      role: form.role,
      location: form.location || null,
      package_lpa: lpa,
      application_link: form.application_link || null,
    };
    try {
      if (editing === "new") await api.createCompany(data);
      else await api.updateCompany(editing, data);
      setNotice(editing === "new" ? "Company created" : "Company updated");
      setEditing(null);
      load();
    } catch (err) {
      setFormError(`Unable to save company: ${err.message}`);
    }
  };

  const confirmDelete = async () => {
    const target = toDelete;
    setToDelete(null);
    setNotice("");
    setDeleteError("");
    try {
      await api.deleteCompany(target.id);
      setNotice("Company deleted");
      load();
    } catch (err) {
      setDeleteError(
        err.status === 409
          ? `Cannot delete "${target.name}": it is referenced by one or more applications.`
          : `Failed to delete company: ${err.message}`
      );
    }
  };

  return (
    <div>
      <div className="page-head">
        <h2>Company management</h2>
        <button className="btn btn-primary" onClick={startNew}>+ New company</button>
      </div>
      <Notice extra={notice} />
      {deleteError && <p className="alert" role="alert">{deleteError}</p>}
      {error && <ErrorBox onRetry={load}>Failed to load companies: {error}</ErrorBox>}
      {!error && companies === null && <Loading text="Loading companies..." />}
      {!error && companies && companies.length === 0 && <Empty>No companies yet. Add the first one.</Empty>}
      {!error && companies && companies.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Company</th><th>Role</th><th>Location</th><th>Package (LPA)</th><th>Actions</th></tr></thead>
            <tbody>
              {companies.map((c) => (
                <tr key={c.id}>
                  <td>{c.name}</td>
                  <td>{c.role}</td>
                  <td>{c.location}</td>
                  <td>{c.package_lpa}</td>
                  <td className="row-actions">
                    <div className="actions">
                      <button className="btn btn-sm" onClick={() => startEdit(c)}>Edit</button>
                      <button className="btn btn-sm btn-danger" onClick={() => setToDelete(c)}>Delete</button>
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
          <h3>{editing === "new" ? "New Company" : "Edit Company"}</h3>
          <label className="field"><span>Company name *</span>
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label className="field"><span>Role *</span>
            <input value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
          </label>
          <label className="field"><span>Location</span>
            <input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          </label>
          <label className="field"><span>Package (LPA)</span>
            <input type="number" min="0" step="any" value={form.package_lpa}
              onChange={(e) => setForm({ ...form, package_lpa: e.target.value })} />
          </label>
          <label className="field"><span>Application link</span>
            <input value={form.application_link} onChange={(e) => setForm({ ...form, application_link: e.target.value })} />
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
          message={`Delete company "${toDelete.name}"? This cannot be undone.`}
          onCancel={() => setToDelete(null)}
          onConfirm={confirmDelete}
        />
      )}
    </div>
  );
}
