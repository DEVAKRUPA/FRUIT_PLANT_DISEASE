import json
import os
from pathlib import Path

from django.conf import settings


MODEL_NAME = os.environ.get("FRUIT_DISEASE_MODEL_NAME", "mobilenet_v2")
MODEL_ROOT = Path(settings.BASE_DIR) / "predictor" / "ml_model"
MODEL_DIR = MODEL_ROOT / MODEL_NAME
MODEL_PATHS = [
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

        _model = load_model(model_path, compile=False)

    return _model


def get_class_names():
    global _class_names

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
            _class_names = [
                name
                for name, _index in sorted(
                    class_metadata.items(),
                    key=lambda item: int(item[1]),
                )
            ]
        else:
            _class_names = class_metadata

    return _class_names
