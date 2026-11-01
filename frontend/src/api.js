const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const TOKEN_KEY = "access_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

async function request(method, path, body) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const res = await fetch(BASE + path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401 && !path.startsWith("/auth/")) {
    // Expired/invalid token: clear it and go to login (LLD section 5).
    clearToken();
    window.location.assign("/login");
    throw new Error("Unauthorized");
  }
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(typeof data?.detail === "string" ? data.detail : "Request failed");
    err.status = res.status;
    throw err;
  }
  return data;
}

export const api = {
  register: (name, email, password) => request("POST", "/auth/register", { name, email, password }),
  login: (email, password) =>
    request("POST", `/auth/login?${new URLSearchParams({ email, password })}`),
  me: () => request("GET", "/users/me"),
  companies: () => request("GET", "/companies"),
  applications: (status) =>
    request("GET", "/applications" + (status ? `?${new URLSearchParams({ status })}` : "")),
  application: (id) => request("GET", `/applications/${id}`),
  createApplication: (data) => request("POST", "/applications", data),
  updateApplication: (id, data) => request("PUT", `/applications/${id}`, data),
  deleteApplication: (id) => request("DELETE", `/applications/${id}`),
  rounds: (appId) => request("GET", `/applications/${appId}/rounds`),
  createRound: (appId, data) => request("POST", `/applications/${appId}/rounds`, data),
  updateRound: (appId, id, data) => request("PUT", `/applications/${appId}/rounds/${id}`, data),
  deleteRound: (appId, id) => request("DELETE", `/applications/${appId}/rounds/${id}`),
};

export const STATUSES = ["APPLIED", "INTERVIEWING", "OFFER", "REJECTED"];
export const ROUND_STATUSES = ["PENDING", "PASSED", "FAILED"];
