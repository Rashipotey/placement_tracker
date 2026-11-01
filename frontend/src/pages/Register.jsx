import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";

export default function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!name.trim()) return setError("Name is required");
    if (!email) return setError("Email is required");
    if (password.length < 8) return setError("Password must be at least 8 characters");
    setBusy(true);
    try {
      await api.register(name, email, password);
      navigate("/login", { state: { notice: "Account created. Please log in." } });
    } catch (err) {
      setError(err.status === 400 ? "Email already registered" : err.message);
      setBusy(false);
    }
  };

  return (
    <div className="container">
      <h1 className="brand">Placement Tracker</h1>
      <form onSubmit={submit} className="card auth-card" noValidate>
        <h2>Create account</h2>
        <label className="field"><span>Name</span>
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label className="field"><span>Email</span>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="field"><span>Password</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button type="submit" className="btn btn-primary" disabled={busy}>Create Account</button>
        <p>Already have an account? <Link to="/login">Log in</Link></p>
        {error && <p className="alert" role="alert">{error}</p>}
      </form>
    </div>
  );
}
