import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { api, getToken, setToken } from "../api.js";
import { useAuth } from "../auth.jsx";
import { Notice } from "../ui.jsx";

export default function Login() {
  const navigate = useNavigate();
  const { user, refresh } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user && getToken()) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!email) return setError("Email is required");
    if (!password) return setError("Password is required");
    setBusy(true);
    try {
      const { access_token } = await api.login(email, password);
      setToken(access_token);
      await refresh();
      navigate("/");
    } catch (err) {
      setError(err.status === 401 ? "Invalid email or password" : err.message);
      setBusy(false);
    }
  };

  return (
    <div className="container">
      <h1 className="brand">Placement Tracker</h1>
      <form onSubmit={submit} className="card auth-card" noValidate>
        <h2>Log in</h2>
        <Notice />
        <label className="field"><span>Email</span>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="field"><span>Password</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button type="submit" className="btn btn-primary" disabled={busy}>Log In</button>
        <p>New here? <Link to="/register">Create account</Link></p>
        {error && <p className="alert" role="alert">{error}</p>}
      </form>
    </div>
  );
}
