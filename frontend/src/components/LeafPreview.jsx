import LoadingButton from "./LoadingButton";

function getPlantName(result) {
  if (result?.leaf_category) {
    return result.leaf_category.replace(" Leaf", "");
  }

  if (result?.prediction) {
    return result.prediction.split(" ")[0];
  }

  return "Unknown";
}

function LeafPreview({
  previewUrl,
  result,
  selectedAt,
  isLoading,
  hasImage,
  onAnalyze,
  onClear,
}) {
  return (
    <section className="dashboard-card preview-card" aria-label="Leaf preview">
      <div className="card-heading row-heading">
        <div>
          <span className="section-kicker">Leaf Image</span>
          <h2>Leaf Preview</h2>
        </div>
        <button
          type="button"
          className="clear-button"
          onClick={onClear}
          disabled={!hasImage || isLoading}
        >
          Clear
        </button>
      </div>

      <div className="leaf-preview-frame">
        {previewUrl ? (
          <img src={previewUrl} alt="Selected leaf preview" />
        ) : (
          <div className="empty-state">
            <span>No image selected</span>
            <p>Upload or capture a leaf image to begin analysis.</p>
          </div>
        )}
      </div>

      <div className="preview-details">
        <div>
          <span>Plant</span>
          <strong>{getPlantName(result)}</strong>
        </div>
        <div>
          <span>Captured/Uploaded</span>
          <strong>{selectedAt || "Not selected"}</strong>
        </div>
      </div>

      <LoadingButton
        isLoading={isLoading}
        loadingText="Analyzing..."
        onClick={onAnalyze}
        disabled={isLoading || !hasImage}
      >
        Analyze Leaf
      </LoadingButton>
    </section>
  );
}

export default LeafPreview;
