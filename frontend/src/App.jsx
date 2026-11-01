import { Link, NavLink, Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { getToken } from "./api.js";
import { useAuth } from "./auth.jsx";
import { ErrorBox, Loading } from "./ui.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Applications from "./pages/Applications.jsx";
import ApplicationForm from "./pages/ApplicationForm.jsx";
import Rounds from "./pages/Rounds.jsx";
import Companies from "./pages/Companies.jsx";
import Admin from "./pages/Admin.jsx";

function Shell() {
  const navigate = useNavigate();
  const { user, loading, logout, refresh } = useAuth();

  if (!getToken()) return <Navigate to="/login" replace />;
  if (loading) return <div className="container"><Loading text="Loading..." /></div>;
  if (!user) {
    return (
      <div className="container">
        <ErrorBox onRetry={refresh}>Failed to load your profile</ErrorBox>
      </div>
    );
  }

  const isAdmin = user.role === "ADMIN";
  const onLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div>
      <header className="topbar">
        <strong className="brand">Placement Tracker</strong>
        <nav className="nav">
          {isAdmin ? (
            <NavLink to="/admin">Company management</NavLink>
          ) : (
            <>
              <NavLink to="/dashboard">Dashboard</NavLink>
              <NavLink to="/companies">Companies</NavLink>
            </>
          )}
          <span className="who">User: {user.email} ({user.role})</span>
          <button className="btn btn-sm" onClick={onLogout}>Logout</button>
        </nav>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </div>
  );
}

function AdminOnly({ children }) {
  const { user } = useAuth();
  if (user?.role === "ADMIN") return children;
  return (
    <div className="card">
      <p className="alert" role="alert">Access denied: this page is for administrators.</p>
      <Link to="/">Go to my dashboard</Link>
    </div>
  );
}

// "/" sends each role to its own dashboard.
function Home() {
  const { user } = useAuth();
  return <Navigate to={user?.role === "ADMIN" ? "/admin" : "/dashboard"} replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<Shell />}>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Applications />} />
        <Route path="/companies" element={<Companies />} />
        <Route path="/admin" element={<AdminOnly><Admin /></AdminOnly>} />
        <Route path="/applications/new" element={<ApplicationForm />} />
        <Route path="/applications/:id/edit" element={<ApplicationForm />} />
        <Route path="/applications/:id/rounds" element={<Rounds />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
