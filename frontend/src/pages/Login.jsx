import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { api, getToken, setToken } from "../api.js";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  if (getToken()) return <Navigate to="/applications" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!email) return setError("Email is required");
    if (!password) return setError("Password is required");
    try {
      const { access_token } = await api.login(email, password);
      setToken(access_token);
      navigate("/applications");
    } catch {
      setError("Invalid email or password");
    }
  };

  return (
    <form onSubmit={submit} style={{ maxWidth: 360, margin: "40px auto" }}>
      <h2>Log in</h2>
      <p><label>Email <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label></p>
      <p><label>Password <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label></p>
      <button type="submit">Log In</button>
      <p>New here? <Link to="/register">Create account</Link></p>
      {error && <p role="alert" style={{ color: "crimson" }}>{error}</p>}
    </form>
  );
}
