import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  adminLogout,
  deleteAppointment,
  fetchAdminAppointments,
  fetchAdminStats,
  isAdminLoggedIn,
  updateAppointmentStatus,
} from "../services/adminService";

const DEPT_ICONS = {
  "Internal Medicine": "🩺",
  "Cardiology": "❤️",
  "Dermatology": "🧴",
  "Laboratory": "🧪",
};
const DEPT_TR = {
  "Internal Medicine": "Dahiliye",
  "Cardiology": "Kardiyoloji",
  "Dermatology": "Dermatoloji",
  "Laboratory": "Laboratuvar",
};
const STATUS_CONFIG = {
  pending:   { label: "Bekliyor",   cls: "statusPending" },
  confirmed: { label: "Onaylandı",  cls: "statusConfirmed" },
  cancelled: { label: "İptal",      cls: "statusCancelled" },
};

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  return <span className={`statusBadge ${cfg.cls}`}>{cfg.label}</span>;
}

function StatCard({ icon, value, label, sub }) {
  return (
    <div className="adminStatCard">
      <div className="adminStatIcon">{icon}</div>
      <div className="adminStatValue">{value}</div>
      <div className="adminStatLabel">{label}</div>
      {sub && <div className="adminStatSub">{sub}</div>}
    </div>
  );
}

export function AdminDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Filters
  const [filterDate, setFilterDate] = useState("");
  const [filterDept, setFilterDept] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [filterSearch, setFilterSearch] = useState("");

  useEffect(() => {
    if (!isAdminLoggedIn()) navigate("/admin/login");
  }, [navigate]);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [s, a] = await Promise.all([
        fetchAdminStats(),
        fetchAdminAppointments({
          date: filterDate,
          department: filterDept,
          status: filterStatus,
          search: filterSearch,
        }),
      ]);
      setStats(s);
      setAppointments(a);
    } catch (err) {
      setError(err.message || "Veriler yüklenemedi");
    } finally {
      setLoading(false);
    }
  }, [filterDate, filterDept, filterStatus, filterSearch]);

  useEffect(() => { loadData(); }, [loadData]);

  function handleLogout() {
    adminLogout();
    navigate("/admin/login");
  }

  async function handleStatus(id, newStatus) {
    try {
      await updateAppointmentStatus(id, newStatus);
      setAppointments((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: newStatus } : a))
      );
      loadData();  // refresh stats
    } catch (err) {
      alert(err.message);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteAppointment(id);
      setAppointments((prev) => prev.filter((a) => a.id !== id));
      setDeleteConfirm(null);
      loadData();
    } catch (err) {
      alert(err.message);
    }
  }

  function exportCSV() {
    const headers = ["ID", "Hasta", "Telefon", "Bölüm", "Doktor", "Tarih", "Saat", "Durum", "Oluşturuldu"];
    const rows = appointments.map((a) => [
      a.id,
      a.patient_name,
      a.phone,
      DEPT_TR[a.department] || a.department || "",
      a.doctor || "",
      a.date,
      a.time,
      STATUS_CONFIG[a.status]?.label || a.status,
      new Date(a.created_at).toLocaleString("tr-TR"),
    ]);
    const csv = [headers, ...rows].map((r) => r.map((c) => `"${c}"`).join(",")).join("\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `randevular_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function clearFilters() {
    setFilterDate("");
    setFilterDept("");
    setFilterStatus("");
    setFilterSearch("");
  }

  return (
    <div className="adminDash">
      {/* ── Header ─────────────────────────────────────────── */}
      <header className="adminHeader">
        <div className="adminHeaderLeft">
          <span className="adminHeaderLogo">🏥</span>
          <div>
            <div className="adminHeaderTitle">Klinik Yönetim Paneli</div>
            <div className="adminHeaderSub">İşletme Randevu Sistemi</div>
          </div>
        </div>
        <div className="adminHeaderRight">
          <button className="btn adminRefreshBtn" onClick={loadData}>
            🔄 Yenile
          </button>
          <button className="btn adminLogoutBtn" onClick={handleLogout}>
            Çıkış Yap
          </button>
        </div>
      </header>

      <div className="adminContent">
        {/* ── Stats ──────────────────────────────────────────── */}
        {stats && (
          <div className="adminStatsRow">
            <StatCard icon="📋" value={stats.total} label="Toplam Randevu" />
            <StatCard icon="📅" value={stats.today} label="Bugün" sub="randevu" />
            <StatCard icon="📆" value={stats.this_week} label="Bu Hafta" sub="randevu" />
            <StatCard
              icon="🟡"
              value={stats.by_status?.pending || 0}
              label="Bekleyen"
            />
            <StatCard
              icon="🟢"
              value={stats.by_status?.confirmed || 0}
              label="Onaylanan"
            />
            <StatCard
              icon="🔴"
              value={stats.by_status?.cancelled || 0}
              label="İptal"
            />
          </div>
        )}

        {/* ── Department mini bars ────────────────────────────── */}
        {stats && Object.keys(stats.by_department).length > 0 && (
          <div className="adminDeptBars">
            {Object.entries(stats.by_department).map(([dept, count]) => (
              <div key={dept} className="adminDeptBar">
                <span className="adminDeptBarIcon">{DEPT_ICONS[dept] || "🏥"}</span>
                <span className="adminDeptBarName">{DEPT_TR[dept] || dept}</span>
                <div className="adminDeptBarTrack">
                  <div
                    className="adminDeptBarFill"
                    style={{ width: `${Math.min(100, (count / stats.total) * 100)}%` }}
                  />
                </div>
                <span className="adminDeptBarCount">{count}</span>
              </div>
            ))}
          </div>
        )}

        {/* ── Filters ────────────────────────────────────────── */}
        <div className="adminFilters">
          <div className="adminFiltersRow">
            <div className="field" style={{ flex: "1 1 160px" }}>
              <label className="label">📅 Tarih</label>
              <input
                className="input"
                type="date"
                value={filterDate}
                onChange={(e) => setFilterDate(e.target.value)}
              />
            </div>
            <div className="field" style={{ flex: "1 1 160px" }}>
              <label className="label">🏥 Bölüm</label>
              <select
                className="input"
                value={filterDept}
                onChange={(e) => setFilterDept(e.target.value)}
              >
                <option value="">Tümü</option>
                <option value="Internal Medicine">🩺 Dahiliye</option>
                <option value="Cardiology">❤️ Kardiyoloji</option>
                <option value="Dermatology">🧴 Dermatoloji</option>
                <option value="Laboratory">🧪 Laboratuvar</option>
              </select>
            </div>
            <div className="field" style={{ flex: "1 1 160px" }}>
              <label className="label">🔖 Durum</label>
              <select
                className="input"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <option value="">Tümü</option>
                <option value="pending">🟡 Bekliyor</option>
                <option value="confirmed">🟢 Onaylandı</option>
                <option value="cancelled">🔴 İptal</option>
              </select>
            </div>
            <div className="field" style={{ flex: "2 1 220px" }}>
              <label className="label">🔍 Hasta / Telefon Ara</label>
              <input
                className="input"
                type="text"
                value={filterSearch}
                onChange={(e) => setFilterSearch(e.target.value)}
                placeholder="İsim veya telefon..."
              />
            </div>
          </div>

          <div className="adminFiltersActions">
            <button className="btn" onClick={clearFilters}>
              Filtreleri Temizle
            </button>
            <button className="btn btnPrimary" onClick={exportCSV} disabled={appointments.length === 0}>
              📥 CSV İndir ({appointments.length})
            </button>
          </div>
        </div>

        {/* ── Error ──────────────────────────────────────────── */}
        {error && <div className="alert alertError">{error}</div>}

        {/* ── Table ──────────────────────────────────────────── */}
        <div className="tableCard">
          <div className="tableHead">
            <div className="tableTitle">Randevular</div>
            <div className="tableMeta">{appointments.length} kayıt</div>
          </div>

          {loading ? (
            <div className="adminLoadingRow">
              <span className="spinner" style={{ borderTopColor: "var(--primary-600)", borderColor: "rgba(29,116,245,0.2)", width: 24, height: 24 }} />
              Yükleniyor...
            </div>
          ) : appointments.length === 0 ? (
            <div className="emptyState">
              <div className="emptyTitle">Randevu bulunamadı</div>
              <div className="emptyText">Filtreleri değiştirerek tekrar deneyin.</div>
            </div>
          ) : (
            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Hasta</th>
                    <th>Telefon</th>
                    <th>Bölüm</th>
                    <th>Doktor</th>
                    <th>Tarih</th>
                    <th>Saat</th>
                    <th>Durum</th>
                    <th>İşlemler</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((appt) => (
                    <tr key={appt.id}>
                      <td className="tdStrong">{appt.patient_name}</td>
                      <td>{appt.phone}</td>
                      <td>
                        {DEPT_ICONS[appt.department]} {DEPT_TR[appt.department] || appt.department}
                      </td>
                      <td>{appt.doctor || "—"}</td>
                      <td>
                        {new Date(appt.date + "T00:00:00").toLocaleDateString("tr-TR", {
                          day: "2-digit", month: "short", year: "numeric",
                        })}
                      </td>
                      <td>{appt.time}</td>
                      <td><StatusBadge status={appt.status} /></td>
                      <td>
                        <div className="adminActions">
                          {appt.status !== "confirmed" && (
                            <button
                              className="adminActionBtn adminActionConfirm"
                              onClick={() => handleStatus(appt.id, "confirmed")}
                              title="Onayla"
                            >
                              ✓
                            </button>
                          )}
                          {appt.status !== "cancelled" && (
                            <button
                              className="adminActionBtn adminActionCancel"
                              onClick={() => handleStatus(appt.id, "cancelled")}
                              title="İptal Et"
                            >
                              ✕
                            </button>
                          )}
                          {appt.status === "pending" && (
                            <button
                              className="adminActionBtn adminActionPending"
                              onClick={() => handleStatus(appt.id, "pending")}
                              title="Bekleyene Al"
                            >
                              ↺
                            </button>
                          )}
                          <button
                            className="adminActionBtn adminActionDelete"
                            onClick={() => setDeleteConfirm(appt.id)}
                            title="Sil"
                          >
                            🗑
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* ── Delete Confirm Modal ────────────────────────────── */}
      {deleteConfirm && (
        <div className="adminModal">
          <div className="adminModalCard">
            <div className="adminModalIcon">⚠️</div>
            <div className="adminModalTitle">Randevuyu Sil</div>
            <div className="adminModalText">
              Bu randevu kalıcı olarak silinecek. Bu işlem geri alınamaz.
            </div>
            <div className="adminModalActions">
              <button className="btn" onClick={() => setDeleteConfirm(null)}>
                Vazgeç
              </button>
              <button
                className="btn btnDanger"
                onClick={() => handleDelete(deleteConfirm)}
              >
                Evet, Sil
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
