const BASE = "";

function adminHeaders() {
  const token = localStorage.getItem("adminToken");
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  };
}

export async function adminLogin(username, password) {
  const res = await fetch(`${BASE}/admin/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Giriş başarısız");
  }
  const data = await res.json();
  localStorage.setItem("adminToken", data.access_token);
  return data;
}

export function adminLogout() {
  localStorage.removeItem("adminToken");
}

export function isAdminLoggedIn() {
  return !!localStorage.getItem("adminToken");
}

export async function fetchAdminStats() {
  const res = await fetch(`${BASE}/admin/stats`, { headers: adminHeaders() });
  if (!res.ok) throw new Error("İstatistikler alınamadı");
  return res.json();
}

export async function fetchAdminAppointments(filters = {}) {
  const params = new URLSearchParams();
  if (filters.date) params.set("date", filters.date);
  if (filters.department) params.set("department", filters.department);
  if (filters.doctor) params.set("doctor", filters.doctor);
  if (filters.search) params.set("search", filters.search);
  if (filters.status) params.set("appt_status", filters.status);
  const res = await fetch(`${BASE}/admin/appointments?${params}`, {
    headers: adminHeaders(),
  });
  if (!res.ok) throw new Error("Randevular alınamadı");
  return res.json();
}

export async function updateAppointmentStatus(id, status) {
  const res = await fetch(`${BASE}/admin/appointments/${id}/status`, {
    method: "PATCH",
    headers: adminHeaders(),
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error("Durum güncellenemedi");
  return res.json();
}

export async function deleteAppointment(id) {
  const res = await fetch(`${BASE}/admin/appointments/${id}`, {
    method: "DELETE",
    headers: adminHeaders(),
  });
  if (!res.ok) throw new Error("Randevu silinemedi");
  return res.json();
}
