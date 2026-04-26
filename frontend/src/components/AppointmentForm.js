import { useMemo, useState } from "react";

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

function buildErrors({ fullName, phone, date, time }) {
  const errors = {};
  if (!fullName.trim()) errors.fullName = "Full name is required.";
  if (!phone.trim()) errors.phone = "Phone number is required.";
  else if (!isValidPhone(phone)) errors.phone = "Invalid phone format. Example: 0 (5xx) xxx xx xx";
  if (!date) errors.date = "Date is required.";
  if (!time) errors.time = "Time is required.";
  return errors;
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
  for (let h = 9; h <= 18; h++) {
    const hh = String(h).padStart(2, "0");
    slots.push(`${hh}:00`);
    if (h !== 18) slots.push(`${hh}:30`);
  }
  return slots;
}

const TIME_SLOTS = buildTimeSlots();

function buildBookedSet(appointments, date) {
  const set = new Set();
  if (!date) return set;
  (appointments || []).forEach((a) => {
    if (a?.date === date && a?.time) set.add(a.time);
  });
  return set;
}

export function AppointmentForm({ appointments, onCreated }) {
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");

  const [touched, setTouched] = useState({
    fullName: false,
    phone: false,
    date: false,
    time: false,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const [confirmation, setConfirmation] = useState(null);

  const bookedSet = useMemo(() => {
    return buildBookedSet(appointments, date);
  }, [appointments, date]);

  const liveErrors = useMemo(() => {
    return buildErrors({ fullName, phone, date, time });
  }, [fullName, phone, date, time]);

  const canSubmit = useMemo(() => {
    return Object.keys(liveErrors).length === 0 && !isSubmitting;
  }, [liveErrors, isSubmitting]);

  async function onSubmit(e) {
    e.preventDefault();
    setSubmitError("");
    setSubmitSuccess(false);
    setConfirmation(null);

    const nextTouched = { fullName: true, phone: true, date: true, time: true };
    setTouched(nextTouched);
    const errors = buildErrors({ fullName, phone, date, time });
    if (Object.keys(errors).length > 0) {
      return;
    }

    if (bookedSet.has(time)) {
      setSubmitError("The selected time slot is full. Please choose another time.");
      return;
    }

    setIsSubmitting(true);
    try {
      const rawDigits = digitsOnly(phone);
      const normalizedPhone = rawDigits.startsWith("0") ? rawDigits : `0${rawDigits}`;
      const payload = {
        name: fullName.trim(),
        phone: normalizedPhone,
        date,
        time,
      };

      // Fake (local) booking: update parent state instantly
      onCreated?.(payload);

      setSubmitSuccess(true);
      setConfirmation({
        name: payload.name,
        phoneDisplay: formatPhoneNumber(payload.phone),
        date: payload.date,
        time: payload.time,
      });
      setTouched({ fullName: false, phone: false, date: false, time: false });
      setFullName("");
      setPhone("");
      setDate("");
      setTime("");
    } catch (err) {
      setSubmitError(err?.message || "Appointment could not be created. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="form" onSubmit={onSubmit}>
      <div className="formGrid">
        <label className="field">
          <span className="label">Full Name</span>
          <div className="inputWrap">
            <span className="inputIcon" aria-hidden="true">
              👤
            </span>
            <input
              className={touched.fullName && liveErrors.fullName ? "input inputInvalid" : "input"}
              value={fullName}
              onChange={(e) => {
                setFullName(e.target.value);
              }}
              onBlur={() => setTouched((t) => ({ ...t, fullName: true }))}
              placeholder="Example: Alex Johnson"
              autoComplete="name"
              required
            />
          </div>
          {touched.fullName && liveErrors.fullName ? (
            <span className="fieldError">{liveErrors.fullName}</span>
          ) : null}
        </label>

        <label className="field">
          <span className="label">Phone</span>
          <div className="inputWrap">
            <span className="inputIcon" aria-hidden="true">
              📞
            </span>
            <input
              className={touched.phone && liveErrors.phone ? "input inputInvalid" : "input"}
              value={phone}
              onChange={(e) => {
                setPhone(formatPhoneNumber(e.target.value));
              }}
              onBlur={() => setTouched((t) => ({ ...t, phone: true }))}
              placeholder="Example: 05xx xxx xx xx"
              inputMode="tel"
              autoComplete="tel"
              required
            />
          </div>
          {touched.phone && liveErrors.phone ? (
            <span className="fieldError">{liveErrors.phone}</span>
          ) : (
            <span className="hint">Enter at least 10 digits.</span>
          )}
        </label>

        <label className="field">
          <span className="label">Date</span>
          <div className="inputWrap">
            <span className="inputIcon" aria-hidden="true">
              📅
            </span>
            <input
              className={touched.date && liveErrors.date ? "input inputInvalid" : "input"}
              value={date}
              onChange={(e) => {
                setDate(e.target.value);
                setTime("");
              }}
              onBlur={() => setTouched((t) => ({ ...t, date: true }))}
              type="date"
              min={todayISO()}
              required
            />
          </div>
          {touched.date && liveErrors.date ? (
            <span className="fieldError">{liveErrors.date}</span>
          ) : null}
        </label>

        <div className="field fieldSpan2">
          <div className="fieldHead">
            <span className="label">Time Selection</span>
            <div className="legend" aria-label="Time availability legend">
              <span className="legendItem">
                <span className="legendDot legendAvail" aria-hidden="true" />
                Available
              </span>
              <span className="legendItem">
                <span className="legendDot legendFull" aria-hidden="true" />
                Full
              </span>
              <span className="legendItem">
                <span className="legendDot legendSel" aria-hidden="true" />
                Selected
              </span>
            </div>
          </div>

          {!date ? (
            <div className="hint">Please select a date first.</div>
          ) : (
            <div className="slotGrid" role="list" aria-label="Time slots">
              {TIME_SLOTS.map((slot) => {
                const isBooked = bookedSet.has(slot);
                const isSelected = time === slot;
                return (
                  <button
                    key={slot}
                    type="button"
                    className={
                      isBooked
                        ? "slotBtn slotFull"
                        : isSelected
                          ? "slotBtn slotSelected"
                          : "slotBtn slotAvailable"
                    }
                    onClick={() => {
                      if (!isBooked) {
                        setTime(slot);
                        setTouched((t) => ({ ...t, time: true }));
                        setSubmitError("");
                      }
                    }}
                    disabled={isBooked}
                    role="listitem"
                  >
                    <span className="slotTime">{slot}</span>
                    {isBooked ? <span className="slotTag">Full</span> : null}
                  </button>
                );
              })}
            </div>
          )}

          {touched.time && liveErrors.time ? (
            <span className="fieldError">{liveErrors.time}</span>
          ) : null}
        </div>
      </div>

      {confirmation ? (
        <div className="confirmCard" role="status" aria-live="polite">
          <div className="confirmTitle">Confirmation Details</div>
          <div className="confirmGrid">
            <div className="confirmItem">
              <div className="confirmLabel">Full Name</div>
              <div className="confirmValue">{confirmation.name}</div>
            </div>
            <div className="confirmItem">
              <div className="confirmLabel">Phone</div>
              <div className="confirmValue">{confirmation.phoneDisplay}</div>
            </div>
            <div className="confirmItem">
              <div className="confirmLabel">Date</div>
              <div className="confirmValue">{confirmation.date}</div>
            </div>
            <div className="confirmItem">
              <div className="confirmLabel">Time</div>
              <div className="confirmValue">{confirmation.time}</div>
            </div>
          </div>
        </div>
      ) : null}

      {submitError ? <div className="alert alertError">{submitError}</div> : null}
      {submitSuccess ? (
        <div className="successCard" role="status" aria-live="polite">
          <div className="successIcon" aria-hidden="true">
            <span className="check" />
          </div>
          <div>
            <div className="successTitle">Your appointment request has been received</div>
            <div className="successText">
              Your request was created successfully. Our team will call you shortly to confirm it.
            </div>
          </div>
        </div>
      ) : null}

      <button className="btn btnPrimary btnLarge" disabled={!canSubmit} type="submit">
        {isSubmitting ? (
          <>
            <span className="spinner" aria-hidden="true" />
            Sending...
          </>
        ) : (
          "Create Appointment"
        )}
      </button>
    </form>
  );
}

