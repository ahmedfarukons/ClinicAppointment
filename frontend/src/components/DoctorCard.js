export function DoctorCard({ name, specialty, availability, imageUrl }) {
  return (
    <div className="card doctorCard">
      <div className="doctorMedia">
        <img
          className="doctorImg"
          src={imageUrl}
          alt={`${name} profile`}
          loading="lazy"
        />
      </div>
      <div className="doctorInfo">
        <div className="cardTitle">{name}</div>
        <div className="chipRow">
          <span className="chip">{specialty}</span>
          <span className="chip chipSoft">{availability}</span>
        </div>
      </div>
    </div>
  );
}

