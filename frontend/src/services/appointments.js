import { apiFetch } from "./api";

const BASE_URL = "http://localhost:5000";

export function createAppointment(payload, { signal } = {}) {
  return apiFetch(`${BASE_URL}/appointments`, {
    method: "POST",
    body: payload,
    signal,
  });
}

// Prepared for real backend integration:
export function listAppointments({ signal } = {}) {
  return apiFetch(`${BASE_URL}/appointments`, { method: "GET", signal });
}

