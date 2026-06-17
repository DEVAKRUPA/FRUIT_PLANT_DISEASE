from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status

from .ml_utils.disease_info import get_disease_info
from .ml_utils.model_loader import (
    get_class_names,
    get_label_source,
    get_model,
    get_model_path,
)


CONFIDENCE_THRESHOLD = 60.0
IMAGE_SIZE = (224, 224)


def preprocess_image(uploaded_image):
    try:
        import numpy as np
        from PIL import Image, UnidentifiedImageError
        from tensorflow.keras.applications.efficientnet import preprocess_input
    except ImportError as exc:
        raise RuntimeError("Image processing dependencies are not installed.") from exc

    try:
        image = Image.open(uploaded_image)
        image = image.convert("RGB")
        image = image.resize(IMAGE_SIZE)
    except UnidentifiedImageError as exc:
        raise ValueError("Invalid image file.") from exc
    except OSError as exc:
        raise ValueError("Invalid image file.") from exc

    image_array = np.array(image, dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)
    return preprocess_input(image_array)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def predict_disease(request):
    uploaded_image = request.FILES.get("image")

    if uploaded_image is None:
        return Response(
            {
                "success": False,
                "error": "No image uploaded. Please upload an image using the form-data key 'image'.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        image_array = preprocess_image(uploaded_image)
    except ValueError:
        return Response(
            {
                "success": False,
                "error": "Invalid image. Please upload a valid image file.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    except RuntimeError as exc:
        return Response(
            {
                "success": False,
                "error": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        model = get_model()
        class_names = get_class_names()
    except Exception as exc:
        return Response(
            {
                "success": False,
                "error": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        import numpy as np

        predictions = model.predict(image_array)
        predicted_index = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_index] * 100)
        prediction = class_names[predicted_index]
        print(
            "Prediction debug: "
            f"model_path={get_model_path()}, "
            f"label_source={get_label_source()}, "
            f"number_of_labels={len(class_names)}, "
            f"predicted_index={predicted_index}, "
            f"predicted_label={prediction}, "
            f"confidence={confidence:.2f}%"
        )
    except Exception as exc:
        return Response(
            {
                "success": False,
                "error": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if confidence < CONFIDENCE_THRESHOLD:
        return Response(
            {
                "success": False,
                "error": "Leaf not detected or image is unclear. Please upload a clear fruit leaf image.",
                "confidence": round(confidence, 2),
            }
        )

    disease_info = get_disease_info(prediction)

    return Response(
        {
            "success": True,
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "recommendation": disease_info["recommendation"],
            "leaf_category": disease_info["leaf_category"],
            "disease": disease_info["disease"],
            "accuracy": round(confidence, 2),
            "precautions": disease_info["precautions"],
            "treatment": disease_info["treatment"],
        }
    )
