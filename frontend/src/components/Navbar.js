import { NavLink } from "react-router-dom";

export function Navbar() {
  return (
    <header className="navbar">
      <div className="container navbarInner">
        <NavLink to="/" className="brand" aria-label="Clinic home">
          <span className="brandMark" aria-hidden="true">
            +
          </span>
          <div className="brandText">
            <div className="brandTitle">Blue Clinic</div>
            <div className="brandSub">Your health is our priority</div>
          </div>
        </NavLink>

        <nav className="navLinks" aria-label="Primary">
          <NavLink
            to="/"
            className={({ isActive }) => (isActive ? "navLink active" : "navLink")}
            end
          >
            Home
          </NavLink>
          <NavLink
            to="/appointment"
            className={({ isActive }) => (isActive ? "navLink active" : "navLink")}
          >
            Book Appointment
          </NavLink>
          <NavLink
            to="/ai-assistant"
            className={({ isActive }) => (isActive ? "navLink active" : "navLink")}
          >
            AI Assistant
          </NavLink>
          <NavLink
            to="/appointments"
            className={({ isActive }) => (isActive ? "navLink active" : "navLink")}
          >
            Appointments
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

