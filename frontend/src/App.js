import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { Navbar } from "./components/Navbar";
import { Footer } from "./components/Footer";
import { Home } from "./pages/Home";
import { Appointment } from "./pages/Appointment";
import { AppointmentList } from "./pages/AppointmentList";
import { AIAssistant } from "./pages/AIAssistant";
import { AdminLogin } from "./pages/AdminLogin";
import { AdminDashboard } from "./pages/AdminDashboard";
import { isAdminLoggedIn } from "./services/adminService";

const STORAGE_KEY = "clinic_appointments_v1";

function addDaysISO(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

const SEEDED_APPOINTMENTS = [
  { name: "Seda Kaya", phone: "05550000001", date: addDaysISO(0), time: "10:00" },
  { name: "Ahmet Yilmaz", phone: "05550000002", date: addDaysISO(0), time: "10:30" },
  { name: "Melis Arslan", phone: "05550000003", date: addDaysISO(1), time: "13:00" },
  { name: "Emre Demir", phone: "05550000004", date: addDaysISO(1), time: "15:30" },
];

function AdminProtectedRoute({ children }) {
  if (!isAdminLoggedIn()) return <Navigate to="/admin/login" replace />;
  return children;
}

function App() {
  const location = useLocation();
  const isAdminPage = location.pathname.startsWith("/admin");

  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setAppointments(JSON.parse(raw));
      else setAppointments(SEEDED_APPOINTMENTS);
    } catch {
      setAppointments(SEEDED_APPOINTMENTS);
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(appointments));
    } catch {}
  }, [appointments]);

  const actions = useMemo(() => {
    return {
      addAppointment: (appt) => {
        setAppointments((prev) => [
          { ...appt, id: crypto.randomUUID?.() || String(Date.now()) },
          ...prev,
        ]);
      },
      clearAppointments: () => setAppointments([]),
    };
  }, []);

  return (
    <div className={isAdminPage ? "adminShell" : "appShell"}>
      {!isAdminPage && <Navbar />}
      <main className={isAdminPage ? "" : "appMain"}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/ai-assistant" element={<AIAssistant />} />
          <Route
            path="/appointment"
            element={
              <Appointment
                appointments={appointments}
                onAppointmentCreated={actions.addAppointment}
              />
            }
          />
          <Route
            path="/appointments"
            element={
              <AppointmentList
                appointments={appointments}
                onClear={actions.clearAppointments}
              />
            }
          />
          {/* Admin routes */}
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route
            path="/admin"
            element={
              <AdminProtectedRoute>
                <AdminDashboard />
              </AdminProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      {!isAdminPage && <Footer />}
    </div>
  );
}

export default App;
