import { Link } from "react-router-dom";

function formatDate(dateStr) {
  // expects YYYY-MM-DD
  if (!dateStr) return "-";
  const [y, m, d] = dateStr.split("-");
  return `${d}.${m}.${y}`;
}

export function AppointmentList({ appointments, onClear }) {
  return (
    <div className="page">
      <section className="pageHead">
        <div className="container">
          <div className="breadcrumbs">
            <Link to="/" className="crumb">
              Home
            </Link>
            <span className="crumbSep">/</span>
            <span className="crumbCurrent">Appointments</span>
          </div>
          <div className="pageHeadRow">
            <div>
              <h1 className="pageTitle">Appointments</h1>
              <p className="pageText">
                Admin-style list view. Records are stored locally in app state and localStorage for now.
              </p>
            </div>
            <div className="pageHeadActions">
              <Link className="btn btnGhost" to="/appointment">
                New Appointment
              </Link>
              <button className="btn btnDanger" onClick={onClear} type="button" disabled={!appointments?.length}>
                Clear List
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="tableCard">
            <div className="tableHead">
              <div className="tableTitle">Records</div>
              <div className="tableMeta">{appointments?.length || 0} appointments</div>
            </div>

            {!appointments?.length ? (
              <div className="emptyState">
                <div className="emptyTitle">No appointments yet</div>
                <div className="emptyText">
                  When you create a record from the appointment page, it will appear here.
                </div>
                <Link className="btn btnPrimary btnLarge" to="/appointment">
                  Create Appointment
                </Link>
              </div>
            ) : (
              <div className="tableWrap" role="region" aria-label="Appointments list">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Full Name</th>
                      <th>Phone</th>
                      <th>Date</th>
                      <th>Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {appointments.map((a) => (
                      <tr key={a.id || `${a.name}-${a.date}-${a.time}`}>
                        <td className="tdStrong">{a.name}</td>
                        <td>{a.phone}</td>
                        <td>{formatDate(a.date)}</td>
                        <td>{a.time}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

