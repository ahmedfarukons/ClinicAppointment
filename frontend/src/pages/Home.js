import { Link } from "react-router-dom";
import { ServiceCard } from "../components/ServiceCard";
import { DoctorCard } from "../components/DoctorCard";

const services = [
  {
    title: "Internal Medicine",
    description: "General exams, follow-up care, and preventive health services.",
    icon: "🩺",
  },
  {
    title: "Cardiology",
    description: "ECG, blood pressure monitoring, and heart health assessment.",
    icon: "❤️",
  },
  {
    title: "Dermatology",
    description: "Skin exams, allergy evaluation, and treatment planning.",
    icon: "🧴",
  },
  {
    title: "Laboratory",
    description: "Fast basic tests and reliable reporting.",
    icon: "🧪",
  },
];

const doctors = [
  {
    name: "Dr. Elif Demir",
    specialty: "Internal Medicine",
    availability: "Weekdays",
    imageUrl: "https://placehold.co/128x128/png?text=Dr",
  },
  {
    name: "Dr. Mehmet Kaya",
    specialty: "Cardiology",
    availability: "Mon / Wed / Fri",
    imageUrl: "https://placehold.co/128x128/png?text=Dr",
  },
  {
    name: "Dr. Zeynep Aslan",
    specialty: "Dermatology",
    availability: "Tue / Thu",
    imageUrl: "https://placehold.co/128x128/png?text=Dr",
  },
];

const testimonials = [
  {
    name: "Seda K.",
    text: "Booking an appointment was very easy. The clinic was clean and the doctors were attentive.",
  },
  {
    name: "Ahmet Y.",
    text: "Fast examination and clear guidance. The waiting time was minimal.",
  },
  {
    name: "Melis A.",
    text: "Friendly staff and a modern environment. My check-up process was very comfortable.",
  },
];

export function Home() {
  return (
    <div className="page">
      <section className="hero">
        <div className="container heroInner">
          <div className="heroCopy">
            <div className="badge">Modern Clinic • Online Appointment</div>
            <h1 className="heroTitle">Blue Clinic</h1>
            <p className="heroText">
              We are here for your health with trusted physicians, a hygienic
              environment, and a fast appointment system.
            </p>
            <div className="heroActions">
              <Link className="btn btnPrimary btnLarge" to="/appointment">
                Book Appointment
              </Link>
              <Link className="btn btnGhost btnLarge" to="/ai-assistant">
                Ask the AI Assistant
              </Link>
              <a className="btn btnGhost btnLarge" href="#services">
                Services
              </a>
            </div>

            <div className="heroStats">
              <div className="stat">
                <div className="statValue">15+</div>
                <div className="statLabel">Years of experience</div>
              </div>
              <div className="stat">
                <div className="statValue">3</div>
                <div className="statLabel">Specialist doctors</div>
              </div>
              <div className="stat">
                <div className="statValue">24/7</div>
                <div className="statLabel">Information support</div>
              </div>
            </div>
          </div>

          <div className="heroPanel" aria-hidden="true">
            <div className="panelTop">
              <div className="pulseDot" />
              <div className="panelTitle">Quick Appointment</div>
            </div>
            <div className="panelBody">
              <div className="panelRow">
                <div className="panelLabel">Visit</div>
                <div className="panelValue">General Check-up</div>
              </div>
              <div className="panelRow">
                <div className="panelLabel">Duration</div>
                <div className="panelValue">~ 20 min</div>
              </div>
              <div className="panelRow">
                <div className="panelLabel">Location</div>
                <div className="panelValue">Main Branch</div>
              </div>
              <div className="panelHint">Book now and our team will call you.</div>
            </div>
          </div>
        </div>
      </section>

      <section className="section" id="services">
        <div className="container">
          <div className="sectionHead">
            <h2 className="sectionTitle">Services</h2>
            <p className="sectionText">
              Departments and planned examination flow designed for your needs.
            </p>
          </div>

          <div className="grid gridCards">
            {services.map((s) => (
              <ServiceCard
                key={s.title}
                title={s.title}
                description={s.description}
                icon={s.icon}
              />
            ))}
          </div>
        </div>
      </section>

      <section className="section sectionAlt">
        <div className="container">
          <div className="sectionHead">
            <h2 className="sectionTitle">Our Doctors</h2>
            <p className="sectionText">
              A safe and attentive examination experience with our specialist team.
            </p>
          </div>

          <div className="grid gridDoctors">
            {doctors.map((d) => (
              <DoctorCard
                key={d.name}
                name={d.name}
                specialty={d.specialty}
                availability={d.availability}
                imageUrl={d.imageUrl}
              />
            ))}
          </div>
        </div>
      </section>

      <section className="section" id="testimonials">
        <div className="container">
          <div className="sectionHead">
            <h2 className="sectionTitle">Patient Reviews</h2>
            <p className="sectionText">
              Short sample reviews that reflect the quality of our service.
            </p>
          </div>

          <div className="grid gridTestimonials">
            {testimonials.map((t) => (
              <div key={t.name} className="card testimonialCard">
                <div className="quoteMark" aria-hidden="true">
                  “
                </div>
                <div className="testimonialText">{t.text}</div>
                <div className="testimonialName">{t.name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section sectionAlt" id="contact">
        <div className="container">
          <div className="sectionHead">
            <h2 className="sectionTitle">Contact</h2>
            <p className="sectionText">
              Contact us for questions. You can use the form for appointment requests.
            </p>
          </div>

          <div className="grid gridContact">
            <div className="card contactCard">
              <div className="contactIcon" aria-hidden="true">
                📍
              </div>
              <div className="cardTitle">Address</div>
              <div className="cardText">12 Health Street, Central District, Istanbul</div>
            </div>
            <div className="card contactCard">
              <div className="contactIcon" aria-hidden="true">
                📞
              </div>
              <div className="cardTitle">Phone</div>
              <div className="cardText">+90 (555) 000 00 00</div>
            </div>
            <div className="card contactCard">
              <div className="contactIcon" aria-hidden="true">
                ✉️
              </div>
              <div className="cardTitle">Email</div>
              <div className="cardText">contact@blueclinic.com</div>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container ctaInner">
          <div>
            <div className="ctaTitle">Create your appointment today</div>
            <div className="ctaText">
              Fill out the form and our team will contact you shortly.
            </div>
          </div>
          <Link className="btn btnPrimary btnLarge" to="/appointment">
            Book Appointment
          </Link>
        </div>
      </section>
    </div>
  );
}

