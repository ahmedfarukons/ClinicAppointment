export function Footer() {
  return (
    <footer className="footer">
      <div className="container footerInner">
        <div>
          <div className="footerTitle">Blue Clinic</div>
          <div className="footerText">
            We are here for you with a modern medical approach and a friendly team.
          </div>
          <div className="socialRow" aria-label="Social media">
            <a className="socialBtn" href="#!" aria-label="Instagram">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5Z"
                  stroke="currentColor"
                  strokeWidth="1.7"
                />
                <path
                  d="M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"
                  stroke="currentColor"
                  strokeWidth="1.7"
                />
                <path
                  d="M17.5 6.8h.01"
                  stroke="currentColor"
                  strokeWidth="3.2"
                  strokeLinecap="round"
                />
              </svg>
            </a>
            <a className="socialBtn" href="#!" aria-label="X">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M6 6l12 12M18 6L6 18"
                  stroke="currentColor"
                  strokeWidth="1.9"
                  strokeLinecap="round"
                />
              </svg>
            </a>
            <a className="socialBtn" href="#!" aria-label="LinkedIn">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path
                  d="M6.5 10.5V18M6.5 6.6v.1"
                  stroke="currentColor"
                  strokeWidth="1.9"
                  strokeLinecap="round"
                />
                <path
                  d="M10.5 18v-4.1c0-1.9 1.1-3.3 3.1-3.3 2.1 0 2.9 1.5 2.9 3.3V18"
                  stroke="currentColor"
                  strokeWidth="1.9"
                  strokeLinecap="round"
                />
                <path
                  d="M10.5 11.5V18"
                  stroke="currentColor"
                  strokeWidth="1.9"
                  strokeLinecap="round"
                />
                <path
                  d="M3.5 4.5h17a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2h-17a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2Z"
                  stroke="currentColor"
                  strokeWidth="1.7"
                />
              </svg>
            </a>
          </div>
        </div>

        <div className="footerCols">
          <div className="footerCol">
            <div className="footerColTitle">Contact</div>
            <div className="footerText">Phone: +90 (555) 000 00 00</div>
            <div className="footerText">Address: Istanbul, Turkey</div>
            <div className="footerText">Email: contact@blueclinic.com</div>
          </div>
          <div className="footerCol">
            <div className="footerColTitle">Working Hours</div>
            <div className="footerText">Mon - Sat: 09:00 - 18:00</div>
            <div className="footerText">Sunday: Closed</div>
          </div>
        </div>
      </div>

      <div className="footerBottom">
        <div className="container footerBottomInner">
          <span>© {new Date().getFullYear()} Blue Clinic</span>
          <span className="footerSmall">Sample site for appointments and patient information</span>
        </div>
      </div>
    </footer>
  );
}

