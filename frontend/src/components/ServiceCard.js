export function ServiceCard({ title, description, icon }) {
  return (
    <div className="card serviceCard">
      <div className="serviceIcon" aria-hidden="true">
        {icon}
      </div>
      <div className="cardTitle">{title}</div>
      <div className="cardText">{description}</div>
    </div>
  );
}

