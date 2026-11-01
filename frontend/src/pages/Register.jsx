import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api.js";

export default function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!email) return setError("Email is required");
    if (password.length < 8) return setError("Password must be at least 8 characters");
    try {
      await api.register(name, email, password);
      navigate("/login");
    } catch (err) {
      setError(err.status === 400 ? "Email already registered" : "Unable to create account");
    }
  };

  return (
    <form onSubmit={submit} style={{ maxWidth: 360, margin: "40px auto" }}>
      <h2>Create account</h2>
      <p><label>Name <input value={name} onChange={(e) => setName(e.target.value)} required /></label></p>
      <p><label>Email <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label></p>
      <p><label>Password <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></label></p>
      <button type="submit">Create Account</button>
      <p>Already have an account? <Link to="/login">Log in</Link></p>
      {error && <p role="alert" style={{ color: "crimson" }}>{error}</p>}
    </form>
  );
}
