const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "sudorank_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = "GET", body, auth = false, form = false } = {}) {
  const headers = {};
  if (body && !form) headers["Content-Type"] = "application/json";
  if (form) headers["Content-Type"] = "application/x-www-form-urlencoded";
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: form ? body : body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const message = (data && data.detail) || `Request failed (${res.status})`;
    throw new ApiError(typeof message === "string" ? message : JSON.stringify(message), res.status);
  }

  return data;
}

export const api = {
  register: (username, password) =>
    request("/api/auth/register", { method: "POST", body: { username, password } }),

  login: (username, password) =>
    request("/api/auth/login", {
      method: "POST",
      form: true,
      body: new URLSearchParams({ username, password }).toString(),
    }),

  me: () => request("/api/auth/me", { auth: true }),

  getDailyPuzzle: () => request("/api/puzzle/daily", { auth: true }),
  startDailyPuzzle: () => request("/api/puzzle/daily/start", { method: "POST", auth: true }),
  submitDailyPuzzle: (grid) =>
    request("/api/puzzle/daily/submit", { method: "POST", auth: true, body: { grid } }),

  dailyLeaderboard: () => request("/api/leaderboard/daily"),
  alltimeLeaderboard: () => request("/api/leaderboard/alltime"),

  newPractice: (difficulty) => request(`/api/practice/new?difficulty=${difficulty}`, { method: "POST" }),
  checkPractice: (id, grid) =>
    request(`/api/practice/${id}/check`, { method: "POST", body: { grid } }),
};

export { ApiError };
