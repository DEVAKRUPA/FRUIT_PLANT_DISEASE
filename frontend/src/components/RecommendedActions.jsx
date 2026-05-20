function splitRecommendation(text) {
  if (!text) {
    return [];
  }

  return text
    .split(/(?<=\.)\s+/)
    .map((item) => item.replace(/\.$/, "").trim())
    .filter(Boolean)
    .slice(0, 4);
}

function RecommendedActions({ result }) {
  const recommendation = result?.recommendation || result?.treatment || result?.precautions;
  const actions = splitRecommendation(recommendation);

  return (
    <section className="dashboard-card actions-card" aria-label="Recommended actions">
      <div className="card-heading">
        <span className="section-kicker">Next Steps</span>
        <h2>Recommended Actions</h2>
      </div>

      {recommendation ? (
        <ol className="action-list">
          {actions.length ? (
            actions.map((action, index) => (
              <li key={action}>
                <span>{index + 1}</span>
                <p>{action}</p>
              </li>
            ))
          ) : (
            <li>
              <span>1</span>
              <p>{recommendation}</p>
            </li>
          )}
        </ol>
      ) : (
        <div className="empty-state compact-empty">
          <span>No actions yet</span>
          <p>Analyze a leaf image to receive care recommendations.</p>
        </div>
      )}
    </section>
  );
}

export default RecommendedActions;
