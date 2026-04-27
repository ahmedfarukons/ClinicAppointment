import { apiFetch } from "./api";

const TOKEN_KEY = "clinic_ai_token";
const USERNAME_KEY = "clinic_ai_username";

export function getStoredAuth() {
  return {
    token: localStorage.getItem(TOKEN_KEY) || "",
    username: localStorage.getItem(USERNAME_KEY) || "",
  };
}

export function saveStoredAuth({ token, username }) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USERNAME_KEY, username);
}

export function clearStoredAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

export async function login(username, password) {
  const { data } = await apiFetch("/auth/login", {
    method: "POST",
    body: { username, password },
  });
  return data;
}

export async function register(username, password) {
  const { data } = await apiFetch("/auth/register", {
    method: "POST",
    body: { username, password },
  });
  return data;
}

export async function listSessions(token) {
  const { data } = await apiFetch("/sessions", { token });
  return data || [];
}

export async function listMessages(token, sessionId) {
  const { data } = await apiFetch(`/sessions/${sessionId}/messages`, { token });
  return data || [];
}

export async function deleteSession(token, sessionId) {
  const { data } = await apiFetch(`/sessions/${sessionId}`, {
    method: "DELETE",
    token,
  });
  return data;
}

export async function sendChatMessage(token, { message, sessionId }) {
  const { data } = await apiFetch("/chat", {
    method: "POST",
    token,
    timeoutMs: 45000,
    body: {
      message,
      ...(sessionId ? { session_id: sessionId } : null),
    },
  });
  return data;
}
