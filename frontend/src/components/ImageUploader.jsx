function ImageUploader({ onImageSelected }) {
  function handleImageChange(event) {
    const file = event.target.files?.[0] || null;
    onImageSelected(file);
    event.target.value = "";
  }

  return (
    <label className="action-button upload-button">
      <input type="file" accept="image/*" onChange={handleImageChange} />
      <span>Choose File</span>
      <strong aria-hidden="true">{"\u2192"}</strong>
    </label>
  );
}

export default ImageUploader;
