import { Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, clearToken, getToken } from "./api.js";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Applications from "./pages/Applications.jsx";
import ApplicationForm from "./pages/ApplicationForm.jsx";

function Shell() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const authed = !!getToken();

  useEffect(() => {
    if (authed) api.me().then((u) => setEmail(u.email)).catch(() => {});
  }, [authed]);

  if (!authed) return <Navigate to="/login" replace />;

  const logout = () => {
    clearToken();
    navigate("/login");
  };

  return (
    <div>
      <header style={{ display: "flex", justifyContent: "space-between", padding: 8, borderBottom: "1px solid #ccc" }}>
        <strong>Placement Tracker</strong>
        <span>
          {email && <>User: {email} </>}
          <button onClick={logout}>Logout</button>
        </span>
      </header>
      <main style={{ padding: 16 }}>
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<Shell />}>
        <Route path="/applications" element={<Applications />} />
        <Route path="/applications/new" element={<ApplicationForm />} />
        <Route path="/applications/:id/edit" element={<ApplicationForm />} />
      </Route>
      <Route path="*" element={<Navigate to="/applications" replace />} />
    </Routes>
  );
}
