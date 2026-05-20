import { useEffect, useRef, useState } from "react";

const CAMERA_SECURE_CONTEXT_MESSAGE =
  "Camera access requires HTTPS or localhost. On another device, use HTTPS or upload from gallery.";

function CameraCapture({ onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [isCameraOpen, setIsCameraOpen] = useState(false);
  const [cameraReady, setCameraReady] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  function hasVideoDimensions(video) {
    return video.videoWidth > 0 && video.videoHeight > 0;
  }

  function isInsecureNetworkHost() {
    const hostname = window.location.hostname;
    return (
      !window.isSecureContext &&
      hostname !== "localhost" &&
      hostname !== "127.0.0.1"
    );
  }

  function markCameraReady() {
    const video = videoRef.current;

    if (video && hasVideoDimensions(video)) {
      setCameraReady(true);
    }
  }

  function waitForVideoReady(video) {
    if (hasVideoDimensions(video)) {
      return Promise.resolve();
    }

    return new Promise((resolve, reject) => {
      const timeoutId = window.setTimeout(() => {
        cleanup();
        reject(new Error("Camera stream did not become ready."));
      }, 5000);

      function cleanup() {
        window.clearTimeout(timeoutId);
        video.removeEventListener("loadedmetadata", handleReady);
        video.removeEventListener("canplay", handleReady);
      }

      function handleReady() {
        if (!hasVideoDimensions(video)) {
          return;
        }

        cleanup();
        resolve();
      }

      video.addEventListener("loadedmetadata", handleReady);
      video.addEventListener("canplay", handleReady);
    });
  }

  function stopCamera() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }

    setCameraReady(false);
    setIsCameraOpen(false);
  }

  async function startCamera() {
    setErrorMessage("");

    if (isInsecureNetworkHost()) {
      setErrorMessage(CAMERA_SECURE_CONTEXT_MESSAGE);
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      setErrorMessage(CAMERA_SECURE_CONTEXT_MESSAGE);
      return;
    }

    try {
      stopCamera();
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      });
      streamRef.current = stream;
      setIsCameraOpen(true);

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
        await waitForVideoReady(videoRef.current);
        setCameraReady(true);
      }
    } catch {
      if (streamRef.current) {
        setCameraReady(false);
        setErrorMessage("Camera is not ready yet. Please wait a second and try again.");
      } else {
        stopCamera();
        setErrorMessage(
          "Camera permission was blocked or no camera was found. Please allow camera access and try again."
        );
      }
    }
  }

  function capturePhoto() {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) {
      return;
    }

    if (!cameraReady || !hasVideoDimensions(video)) {
      setErrorMessage("Camera is not ready yet. Please wait a second and try again.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setErrorMessage("Could not capture a photo. Please try again.");
          return;
        }

        const file = new File([blob], "captured-leaf.jpg", {
          type: "image/jpeg",
        });
        onCapture(file);
        stopCamera();
      },
      "image/jpeg",
      0.95
    );
  }

  useEffect(() => stopCamera, []);

  return (
    <div className="camera-capture">
      <div className={isCameraOpen ? "camera-frame open" : "camera-frame"}>
        <video
          ref={videoRef}
          className={isCameraOpen ? "camera-video active" : "camera-video"}
          autoPlay
          playsInline
          muted
          onLoadedMetadata={markCameraReady}
          onCanPlay={markCameraReady}
        />
        {!isCameraOpen && <p>Camera is closed</p>}
      </div>

      <div className="button-row">
        <button type="button" className="action-button camera-button" onClick={startCamera}>
          <span>Open Camera</span>
          <strong aria-hidden="true">{"\u2192"}</strong>
        </button>
        <button
          type="button"
          className="secondary-button"
          onClick={capturePhoto}
          disabled={!isCameraOpen || !cameraReady}
        >
          {cameraReady ? "Capture" : "Wait"}
        </button>
        <button
          type="button"
          className="ghost-button"
          onClick={stopCamera}
          disabled={!isCameraOpen}
        >
          Stop
        </button>
      </div>

      {errorMessage && <p className="error-message camera-error">{errorMessage}</p>}
      <canvas ref={canvasRef} hidden />
    </div>
  );
}

export default CameraCapture;
