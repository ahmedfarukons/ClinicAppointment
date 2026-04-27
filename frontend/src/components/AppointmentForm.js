import { useEffect, useMemo, useState } from "react";

function digitsOnly(value) {
  return (value || "").replace(/\D/g, "");
}

function formatPhoneNumber(value) {
  const d = digitsOnly(value);
  let x = d;
  if (x.startsWith("90")) x = x.slice(2);
  if (x.startsWith("0")) x = x.slice(1);
  x = x.slice(0, 10);
  const p1 = x.slice(0, 3);
  const p2 = x.slice(3, 6);
  const p3 = x.slice(6, 8);
  const p4 = x.slice(8, 10);
  if (!x) return "";
  if (x.length <= 3) return `0 (${p1}`;
  if (x.length <= 6) return `0 (${p1}) ${p2}`;
  if (x.length <= 8) return `0 (${p1}) ${p2} ${p3}`;
  return `0 (${p1}) ${p2} ${p3} ${p4}`;
}

function isValidPhone(value) {
  const d = digitsOnly(value);
  if (d.length === 10) return d.startsWith("5");
  if (d.length === 11) return d.startsWith("05");
  return false;
}

function todayISO() {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function buildTimeSlots() {
  const slots = [];
  for (let h = 9; h <= 17; h++) {
    const hh = String(h).padStart(2, "0");
    slots.push(`${hh}:00`);
    slots.push(`${hh}:30`);
  }
  return slots;
}

const TIME_SLOTS = buildTimeSlots();

const CLINIC_DATA = {
  "Internal Medicine": {
    icon: "🩺",
    label: "Internal Medicine",
    trLabel: "Dahiliye",
    doctors: ["Uzm. Dr. Ahmet Yılmaz", "Uzm. Dr. Ayşe Kaya"],
  },
  "Cardiology": {
    icon: "❤️",
    label: "Cardiology",
    trLabel: "Kardiyoloji",
    doctors: ["Doç. Dr. Mehmet Demir", "Prof. Dr. Elif Çelik"],
  },
  "Dermatology": {
    icon: "🧴",
    label: "Dermatology",
    trLabel: "Dermatoloji",
    doctors: ["Uzm. Dr. Can Arslan", "Uzm. Dr. Zeynep Şahin"],
  },
  "Laboratory": {
    icon: "🧪",
    label: "Laboratory",
    trLabel: "Laboratuvar",
    doctors: ["Uzm. Dr. Ali Can", "Uzm. Dr. Hale Mutlu"],
  },
};

export function AppointmentForm({ initialDepartment, onCreated }) {
  const [fullName, setFullName]     = useState("");
  const [phone, setPhone]           = useState("");
  const [date, setDate]             = useState("");
  const [time, setTime]             = useState("");
  const [department, setDepartment] = useState(initialDepartment || "");
  const [doctor, setDoctor]         = useState("");
  const [bookedTimes, setBookedTimes] = useState([]);

  const [touched, setTouched] = useState({
    fullName: false, phone: false, date: false, time: false,
    department: false, doctor: false,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError]   = useState("");
  const [confirmation, setConfirmation] = useState(null);

  /* When department changes, reset doctor & time */
  useEffect(() => {
    setDoctor("");
    setTime("");
  }, [department]);

  /* When doctor or date changes, fetch booked slots */
  useEffect(() => {
    if (!date || !doctor) { setBookedTimes([]); return; }
    fetch(`/api/appointments?date=${date}&doctor=${encodeURIComponent(doctor)}`)
      .then((r) => r.ok ? r.json() : [])
      .then((data) => setBookedTimes(data.map((a) => a.time)))
      .catch(() => setBookedTimes([]));
  }, [date, doctor]);

  const bookedSet = useMemo(() => new Set(bookedTimes), [bookedTimes]);

  const liveErrors = useMemo(() => {
    const e = {};
    if (!fullName.trim())     e.fullName   = "Full name is required.";
    if (!department)          e.department = "Department selection is required.";
    if (!doctor)              e.doctor     = "Doctor selection is required.";
    if (!phone.trim())        e.phone      = "Phone number is required.";
    else if (!isValidPhone(phone)) e.phone = "Invalid phone format. Example: 0 (5xx) xxx xx xx";
    if (!date)                e.date       = "Date selection is required.";
    if (!time)                e.time       = "Time selection is required.";
    return e;
  }, [fullName, phone, date, time, department, doctor]);

  const canSubmit = useMemo(() =>
    Object.keys(liveErrors).length === 0 && !isSubmitting,
    [liveErrors, isSubmitting]
  );

  async function onSubmit(e) {
    e.preventDefault();
    setSubmitError("");
    setTouched({ fullName: true, phone: true, date: true, time: true, department: true, doctor: true });
    if (Object.keys(liveErrors).length > 0) return;
    if (bookedSet.has(time)) {
      setSubmitError("This time slot is already full. Please choose another slot.");
      return;
    }

    setIsSubmitting(true);
    try {
      const rawDigits = digitsOnly(phone);
      const normalizedPhone = rawDigits.startsWith("0") ? rawDigits : `0${rawDigits}`;
      const payload = {
        patient_name: fullName.trim(),
        phone: normalizedPhone,
        date,
        time,
        department,
        doctor,
      };

      const res = await fetch("/api/appointments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        let msg = "Failed to create appointment.";
        try { msg = (await res.json()).detail || msg; } catch {}
        throw new Error(msg);
      }
      const data = await res.json();
      onCreated?.(data);

      setConfirmation({
        name: payload.patient_name,
        phoneDisplay: formatPhoneNumber(payload.phone),
        date: payload.date,
        time: payload.time,
        department: CLINIC_DATA[payload.department]?.label || payload.department,
        doctor: payload.doctor,
      });

      // reset form
      setFullName(""); setPhone(""); setDate(""); setTime(""); setDoctor("");
      setTouched({ fullName: false, phone: false, date: false, time: false, department: false, doctor: false });
      // refresh slots
      setBookedTimes([]);
    } catch (err) {
      setSubmitError(err?.message || "Failed to create appointment. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const clinicDepts = Object.entries(CLINIC_DATA);
  const availableDoctors = department ? (CLINIC_DATA[department]?.doctors || []) : [];

  return (
    <form className="form" onSubmit={onSubmit}>
      <div className="formGrid">

        {/* Full Name */}
        <label className="field">
          <span className="label">Full Name<br /><small>Ad Soyad</small></span>
          <div className="inputWrap">
            <span className="inputIcon" aria-hidden="true">👤</span>
            <input
              className={touched.fullName && liveErrors.fullName ? "input inputInvalid" : "input"}
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              onBlur={() => setTouched((t) => ({ ...t, fullName: true }))}
              placeholder="Example: Ahmet Yılmaz"
              autoComplete="name"
              required
            />
          </div>
          {touched.fullName && liveErrors.fullName && <span className="fieldError">{liveErrors.fullName}</span>}
        </label>

        {/* Phone */}
        <label className="field">
          <span className="label">Phone<br /><small>Telefon</small></span>
          <div className="inputWrap">
            <span className="inputIcon" aria-hidden="true">📞</span>
            <input
              className={touched.phone && liveErrors.phone ? "input inputInvalid" : "input"}
              value={phone}
              onChange={(e) => setPhone(formatPhoneNumber(e.target.value))}
              onBlur={() => setTouched((t) => ({ ...t, phone: true }))}
              placeholder="Example: 05xx xxx xx xx"
              inputMode="tel"
              autoComplete="tel"
              required
            />
          </div>
          {touched.phone && liveErrors.phone
            ? <span className="fieldError">{liveErrors.phone}</span>
            : <span className="hint">Enter at least 10 digits.<br /><small>En az 10 rakam girin.</small></span>}
        </label>

        {/* Department */}
        <div className="field fieldSpan2">
          <span className="label">Choose Department<br /><small>Bölüm Seçin</small></span>
          <div className="deptGrid">
            {clinicDepts.map(([key, info]) => (
              <button
                key={key}
                type="button"
                className={`deptCard${department === key ? " deptCardSelected" : ""}`}
                onClick={() => { setDepartment(key); setTouched((t) => ({ ...t, department: true })); }}
              >
                <span className="deptIcon">{info.icon}</span>
                <span className="deptLabel">{info.label}</span>
                <span className="deptSub">{info.trLabel}</span>
              </button>
            ))}
          </div>
          {touched.department && liveErrors.department && <span className="fieldError">{liveErrors.department}</span>}
        </div>

        {/* Doctor Selection */}
        {department && (
          <div className="field fieldSpan2">
            <span className="label">Choose Doctor<br /><small>Doktor Seçin</small></span>
            <div className="doctorGrid">
              {availableDoctors.map((doc) => (
                <button
                  key={doc}
                  type="button"
                  className={`doctorCard${doctor === doc ? " doctorCardSelected" : ""}`}
                  onClick={() => { setDoctor(doc); setTime(""); setTouched((t) => ({ ...t, doctor: true })); }}
                >
                  <span className="doctorAvatar">👨‍⚕️</span>
                  <span className="doctorName">{doc}</span>
                  <span className="doctorSpec">{CLINIC_DATA[department]?.label}</span>
                </button>
              ))}
            </div>
            {touched.doctor && liveErrors.doctor && <span className="fieldError">{liveErrors.doctor}</span>}
          </div>
        )}

        {/* Date */}
        <label className="field">
          <span className="label">Date<br /><small>Tarih</small></span>
          <div className="inputWrap">
            <span className="inputIcon" aria-hidden="true">📅</span>
            <input
              className={touched.date && liveErrors.date ? "input inputInvalid" : "input"}
              value={date}
              onChange={(e) => { setDate(e.target.value); setTime(""); }}
              onBlur={() => setTouched((t) => ({ ...t, date: true }))}
              type="date"
              min={todayISO()}
              required
            />
          </div>
          {touched.date && liveErrors.date && <span className="fieldError">{liveErrors.date}</span>}
        </label>

        {/* Time Slots */}
        <div className="field fieldSpan2">
          <div className="fieldHead">
            <span className="label">Choose Time<br /><small>Saat Seçin</small></span>
            <div className="legend" aria-label="Saat durumu">
              <span className="legendItem"><span className="legendDot legendAvail" />Available</span>
              <span className="legendItem"><span className="legendDot legendFull" />Full</span>
              <span className="legendItem"><span className="legendDot legendSel" />Selected</span>
            </div>
          </div>

          {!date || !doctor ? (
            <div className="hint">
              {!doctor ? "Please select a doctor first." : "Please select a date first."}
            </div>
          ) : (
            <div className="slotGrid" role="list" aria-label="Saat dilimleri">
              {TIME_SLOTS.map((slot) => {
                const isBooked   = bookedSet.has(slot);
                const isSelected = time === slot;
                return (
                  <button
                    key={slot}
                    type="button"
                    className={isBooked ? "slotBtn slotFull" : isSelected ? "slotBtn slotSelected" : "slotBtn slotAvailable"}
                    onClick={() => { if (!isBooked) { setTime(slot); setTouched((t) => ({ ...t, time: true })); setSubmitError(""); } }}
                    disabled={isBooked}
                    role="listitem"
                  >
                    <span className="slotTime">{slot}</span>
                    {isBooked && <span className="slotTag">Full</span>}
                  </button>
                );
              })}
            </div>
          )}
          {touched.time && liveErrors.time && <span className="fieldError">{liveErrors.time}</span>}
        </div>
      </div>

      {/* Confirmation card */}
      {confirmation && (
        <div className="confirmCard" role="status" aria-live="polite">
          <div className="confirmTitle">✅ Appointment Confirmed</div>
          <div className="confirmGrid">
            <div className="confirmItem"><div className="confirmLabel">Full Name</div><div className="confirmValue">{confirmation.name}</div></div>
            <div className="confirmItem"><div className="confirmLabel">Phone</div><div className="confirmValue">{confirmation.phoneDisplay}</div></div>
            <div className="confirmItem"><div className="confirmLabel">Department</div><div className="confirmValue">{confirmation.department}</div></div>
            <div className="confirmItem"><div className="confirmLabel">Doctor</div><div className="confirmValue">{confirmation.doctor}</div></div>
            <div className="confirmItem"><div className="confirmLabel">Date</div><div className="confirmValue">{confirmation.date}</div></div>
            <div className="confirmItem"><div className="confirmLabel">Time</div><div className="confirmValue">{confirmation.time}</div></div>
          </div>
        </div>
      )}

      {submitError && <div className="alert alertError">{submitError}</div>}

      <button className="btn btnPrimary btnLarge" disabled={!canSubmit} type="submit">
        {isSubmitting ? (
          <><span className="spinner" aria-hidden="true" />Submitting...</>
        ) : (
          "Book Appointment"
        )}
      </button>
    </form>
  );
}
