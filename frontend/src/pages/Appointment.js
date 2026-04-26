import { AppointmentForm } from "../components/AppointmentForm";
import { Link } from "react-router-dom";

export function Appointment({ appointments, onAppointmentCreated }) {
  return (
    <div className="page">
      <section className="pageHead">
        <div className="container">
          <div className="breadcrumbs">
            <Link to="/" className="crumb">
              Home
            </Link>
            <span className="crumbSep">/</span>
            <span className="crumbCurrent">Appointment</span>
          </div>
          <h1 className="pageTitle">Book an Appointment</h1>
          <p className="pageText">
            Enter your information. Our team will call you to confirm the selected time.
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="formCard">
            <div className="formCardHead">
              <div className="formCardTitle">Appointment Form</div>
              <div className="formCardHint">
                All fields are required.
              </div>
            </div>
            <AppointmentForm appointments={appointments} onCreated={onAppointmentCreated} />
          </div>
        </div>
      </section>
    </div>
  );
}

