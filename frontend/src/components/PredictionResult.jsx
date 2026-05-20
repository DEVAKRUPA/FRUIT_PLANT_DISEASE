function getConfidenceLabel(confidence) {
  if (confidence >= 80) {
    return "High Confidence";
  }

  if (confidence >= 50) {
    return "Medium Confidence";
  }

  return "Low Confidence";
}

function getDescription(result) {
  if (!result) {
    return "";
  }

  return (
    result.precautions ||
    result.recommendation ||
    result.treatment ||
    "Prediction details will appear after analysis."
  );
}

function PredictionResult({ result }) {
  if (!result) {
    return (
      <section className="dashboard-card result-card" aria-label="Prediction result">
        <div className="card-heading">
          <span className="section-kicker">Diagnosis</span>
          <h2>Prediction Result</h2>
        </div>
        <div className="empty-state result-empty">
          <span>No prediction yet</span>
          <p>Analyze a leaf image to see disease result and recommendation.</p>
        </div>
      </section>
    );
  }

  const confidence = Number(result.confidence ?? result.accuracy ?? 0);
  const confidenceLabel = getConfidenceLabel(confidence);
  const isHealthy = result.prediction?.toLowerCase().includes("healthy");

  return (
    <section className="dashboard-card result-card" aria-label="Prediction result">
      <div className="card-heading">
        <span className="section-kicker">Diagnosis</span>
        <h2>Prediction Result</h2>
      </div>

      <div className={isHealthy ? "disease-banner healthy" : "disease-banner"}>
        <div>
          <span>Disease Name</span>
          <strong>{result.prediction}</strong>
        </div>
        <em>{isHealthy ? "Healthy" : result.disease || "Detected"}</em>
      </div>

      <div className="confidence-panel">
        <div
          className="confidence-ring"
          style={{ "--score": `${Math.min(confidence, 100)}%` }}
          aria-label={`Confidence ${confidence.toFixed(2)} percent`}
        >
          <span>{confidence.toFixed(2)}%</span>
        </div>
        <div>
          <h3>Confidence Score</h3>
          <strong>{confidenceLabel}</strong>
        </div>
      </div>

      <div className="info-block">
        <h3>Short Description</h3>
        <p>{getDescription(result)}</p>
      </div>
    </section>
  );
}

export default PredictionResult;
