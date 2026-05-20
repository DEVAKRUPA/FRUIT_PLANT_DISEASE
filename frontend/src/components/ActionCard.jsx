function ActionCard({ accent = "green", icon, title, text, children }) {
  return (
    <section className={`action-card ${accent}`} aria-label={title}>
      <div className="action-card-copy">
        <div className="action-icon" aria-hidden="true">
          {icon}
        </div>
        <div>
          <h2>{title}</h2>
          <p>{text}</p>
        </div>
      </div>
      <div className="action-card-control">{children}</div>
    </section>
  );
}

export default ActionCard;
