/**
 * Single API client.
 *
 * The whole point: it attaches the SAME Bearer token to both backends —
 * Django (issuer/CRUD) and FastAPI (PDF/email + AI agent). The frontend logs in
 * once against Django and reuses that token everywhere.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";
const AI_URL = process.env.NEXT_PUBLIC_AI_URL ?? "http://localhost:8001";

const TOKEN_KEY = "access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const token = getToken();
  return token ? { ...extra, Authorization: `Bearer ${token}` } : extra;
}

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(`${res.status}: ${detail}`);
  }
  const text = await res.text();
  return (text ? JSON.parse(text) : null) as T;
}

/** Calls against the Django backend. */
export const django = {
  get: <T>(path: string) =>
    fetch(`${API_URL}${path}`, { headers: authHeaders() }).then(handle<T>),
  post: <T>(path: string, body: unknown) =>
    fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    }).then(handle<T>),
  put: <T>(path: string, body: unknown) =>
    fetch(`${API_URL}${path}`, {
      method: "PUT",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    }).then(handle<T>),
  del: (path: string) =>
    fetch(`${API_URL}${path}`, { method: "DELETE", headers: authHeaders() }).then(
      handle<null>,
    ),
};

/** Calls against the FastAPI services — SAME token. */
export const ai = {
  get: <T>(path: string) =>
    fetch(`${AI_URL}${path}`, { headers: authHeaders() }).then(handle<T>),
  post: <T>(path: string, body: unknown) =>
    fetch(`${AI_URL}${path}`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    }).then(handle<T>),
  /** Multipart upload (e.g. verify a PDF). Do NOT set Content-Type — the
   *  browser adds the multipart boundary automatically. */
  postForm: <T>(path: string, form: FormData) =>
    fetch(`${AI_URL}${path}`, {
      method: "POST",
      headers: authHeaders(),
      body: form,
    }).then(handle<T>),
  /** Downloads a binary (the inventory PDF) with the same Bearer. */
  postBlob: async (path: string, body: unknown): Promise<Blob> => {
    const res = await fetch(`${AI_URL}${path}`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`);
    return res.blob();
  },
};

export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${API_URL}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await handle<{ access: string }>(res);
  setToken(data.access);
}
