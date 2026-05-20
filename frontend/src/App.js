import { useState } from "react";
import axios from "axios";
import ActionCard from "./components/ActionCard";
import CameraCapture from "./components/CameraCapture";
import Header from "./components/Header";
import ImageUploader from "./components/ImageUploader";
import LeafPreview from "./components/LeafPreview";
import PredictionResult from "./components/PredictionResult";
import RecommendedActions from "./components/RecommendedActions";
import TipCard from "./components/TipCard";
import Footer from "./components/Footer";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";
const API_URL = `${API_BASE_URL}/api/predict/`;
const MAX_IMAGE_SIZE = 10 * 1024 * 1024;
const NETWORK_ERROR_MESSAGE =
  "Cannot connect to backend. Make sure Django is running on your laptop IP and the API URL is correct.";

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [selectedAt, setSelectedAt] = useState("");
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  function handleImageSelected(imageFile) {
    setResult(null);
    setErrorMessage("");

    if (!imageFile) {
      clearImage();
      return;
    }

    if (imageFile.size > MAX_IMAGE_SIZE) {
      setSelectedImage(null);
      setPreviewUrl("");
      setSelectedAt("");
      setErrorMessage("Please choose an image smaller than 10MB.");
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedImage(imageFile);
    setPreviewUrl(URL.createObjectURL(imageFile));
    setSelectedAt(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
  }

  function clearImage() {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedImage(null);
    setPreviewUrl("");
    setSelectedAt("");
    setResult(null);
    setErrorMessage("");
  }

  function buildBackendErrorMessage(data) {
    const message = data?.error || data?.message || "Prediction failed.";
    const confidence = data?.confidence ?? data?.accuracy;

    if (confidence !== undefined) {
      return `${message} Confidence: ${confidence}%.`;
    }

    return message;
  }

  function getErrorMessage(error) {
    const data = error.response?.data;
    return data ? buildBackendErrorMessage(data) : NETWORK_ERROR_MESSAGE;
  }

  async function handlePredict() {
    if (!selectedImage) {
      setErrorMessage("Please choose or capture a leaf image first.");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedImage);

    setIsLoading(true);
    setResult(null);
    setErrorMessage("");

    try {
      const response = await axios.post(API_URL, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.data.success) {
        setResult(response.data);
      } else {
        setErrorMessage(buildBackendErrorMessage(response.data));
      }
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app">
      <main className="dashboard-main">
        <section className="workspace">
        <Header />

        <section className="welcome-panel">
          <h2>Welcome to Fruit Plant Disease Detector {"\uD83C\uDF43"}</h2>
          <p>
            Upload or capture a leaf image to detect disease and get smart
            recommendations.
          </p>
        </section>

        <div className="action-grid">
          <ActionCard
            accent="green"
            icon={"\u25A7"}
            title="Upload from Gallery"
            text="Choose an image from your device gallery"
          >
            <ImageUploader onImageSelected={handleImageSelected} />
          </ActionCard>

          <ActionCard
            accent="orange"
            icon={"\u25C9"}
            title="Open Camera"
            text="Take a photo of the affected leaf"
          >
            <CameraCapture onCapture={handleImageSelected} />
          </ActionCard>
        </div>

        <div className="dashboard-grid">
          <LeafPreview
            previewUrl={previewUrl}
            result={result}
            selectedAt={selectedAt}
            isLoading={isLoading}
            hasImage={Boolean(selectedImage)}
            onAnalyze={handlePredict}
            onClear={clearImage}
          />

          <PredictionResult result={result} />
          <RecommendedActions result={result} />
        </div>

        {isLoading && <p className="status-text">Analyzing the leaf image...</p>}
        {errorMessage && <p className="error-message global-error">{errorMessage}</p>}

        <TipCard />
        </section>
      </main>

      <Footer />
    </div>
  );
}

export default App;
