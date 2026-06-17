import json
import os
from pathlib import Path

from django.conf import settings


MODEL_NAME = os.environ.get("FRUIT_DISEASE_MODEL_NAME", "efficientnet_b0")
MODEL_ROOT = Path(settings.BASE_DIR) / "predictor" / "ml_model"
MODEL_DIR = MODEL_ROOT / MODEL_NAME
MODEL_PATHS = [
    MODEL_DIR / f"{MODEL_NAME}_model.keras",
    MODEL_DIR / f"{MODEL_NAME}_model.h5",
    MODEL_DIR / "mobilenet_v2_model.keras",
    MODEL_DIR / "mobilenet_v2_model.h5",
    MODEL_DIR / "model.keras",
    MODEL_DIR / "model.h5",
    MODEL_DIR / "fruit_disease_model.keras",
    MODEL_DIR / "fruit_disease_model.h5",
]
CLASS_NAMES_PATHS = [
    MODEL_DIR / "labels.json",
    MODEL_DIR / "mobilenet_v2_labels.json",
    MODEL_DIR / "class_names.json",
    MODEL_DIR / "class_indices.json",
    MODEL_ROOT / "class_names.json",
]

_model = None
_class_names = None
_label_source = None


DISPLAY_NAME_OVERRIDES = {
    "apple_healthy": "Apple Healthy",
    "apple_rust": "Apple Rust",
    "apple_scab": "Apple Scab",
    "banana_cordana": "Banana Cordana",
    "banana_healthy": "Banana Healthy",
    "banana_y_b_sigatoka": "Banana Yellow Brown Sigatoka",
    "grape_black_rot": "Grape Black Rot",
    "grape_healthy": "Grape Healthy",
    "grape_leaf_blight": "Grape Leaf Blight",
    "guava_algal_leaves_spot": "Guava Algal Leaf Spot",
    "guava_healthy": "Guava Healthy",
    "guava_red_rust": "Guava Red Rust",
    "mango_gall_midge": "Mango Gall Midge",
    "mango_healthy": "Mango Healthy",
    "mango_sooty_mould": "Mango Sooty Mould",
    "papaya_curl": "Papaya Curl",
    "papaya_healthy": "Papaya Healthy",
    "papaya_ringspot": "Papaya Ring Spot",
}


def get_model_path():
    return next((path for path in MODEL_PATHS if path.exists()), MODEL_PATHS[0])


def get_model():
    global _model

    if _model is None:
        model_path = get_model_path()

        if not model_path.exists():
            searched_paths = ", ".join(str(path) for path in MODEL_PATHS)
            raise FileNotFoundError(f"Model file not found. Searched: {searched_paths}")

        from tensorflow.keras.models import load_model

        print(f"Loading model from: {model_path}")
        _model = load_model(model_path, compile=False)

    return _model


def format_class_name(class_name):
    return DISPLAY_NAME_OVERRIDES.get(
        class_name,
        class_name.replace("_", " ").title(),
    )


def get_class_names():
    global _class_names, _label_source

    if _class_names is None:
        class_names_path = next(
            (path for path in CLASS_NAMES_PATHS if path.exists()),
            None,
        )

        if class_names_path is None:
            searched_paths = ", ".join(str(path) for path in CLASS_NAMES_PATHS)
            raise FileNotFoundError(f"Class names file not found. Searched: {searched_paths}")

        with class_names_path.open("r", encoding="utf-8") as file:
            class_metadata = json.load(file)

        if isinstance(class_metadata, dict):
            first_key = next(iter(class_metadata))
            if str(first_key).isdigit():
                ordered_labels = [
                    class_metadata[str(index)]
                    for index in range(len(class_metadata))
                ]
            else:
                ordered_labels = [
                    name
                    for name, _index in sorted(
                        class_metadata.items(),
                        key=lambda item: int(item[1]),
                    )
                ]
        else:
            ordered_labels = class_metadata

        _class_names = [format_class_name(class_name) for class_name in ordered_labels]
        _label_source = class_names_path
        print(f"Loaded labels from: {_label_source}")
        print(f"Number of labels: {len(_class_names)}")

    return _class_names


def get_label_source():
    if _label_source is None:
        get_class_names()
    return _label_source
