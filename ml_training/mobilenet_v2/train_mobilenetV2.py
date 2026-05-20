import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml_training" / "Dataset"
INVALID_IMAGES_DIR = PROJECT_ROOT / "invalid_images_backup"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "predictor" / "ml_model" / "mobilenet_v2"

MODEL_PATH = OUTPUT_DIR / "mobilenet_v2_model.keras"
LABELS_PATH = OUTPUT_DIR / "labels.json"
HISTORY_PATH = OUTPUT_DIR / "training_history.png"
CONFUSION_MATRIX_PATH = OUTPUT_DIR / "confusion_matrix.png"
CLASSIFICATION_REPORT_PATH = OUTPUT_DIR / "classification_report.txt"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
INITIAL_EPOCHS = 20
FINE_TUNE_EPOCHS = 10
VALIDATION_SPLIT = 0.2
EXPECTED_CLASS_COUNT = 18

JACKFRUIT_FOLDERS = {
    "jackfruit_algal",
    "jackfruit_black_spot",
    "jackfruit_healthy",
}
NESTED_FRUIT_FOLDERS = {"apple", "grapes", "guava", "mango", "papaya", "banana"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
NON_TRAINING_EXTENSIONS = {".txt", ".csv", ".json", ".xml", ".ini", ".db"}
NON_TRAINING_FILENAMES = {".ds_store", "thumbs.db"}


def label_from_folder(folder_name):
    words = folder_name.split("_")
    labels = []
    index = 0
    while index < len(words):
        if index + 2 < len(words) and words[index : index + 3] == ["y", "b", "sigatoka"]:
            labels.extend(["Yellow", "Brown", "Sigatoka"])
            index += 3
            continue
        if words[index] == "ringspot":
            labels.extend(["Ring", "Spot"])
        elif words[index] == "healthly":
            labels.append("Healthy")
        else:
            labels.append(words[index].capitalize())
        index += 1
    return " ".join(labels)


def get_class_folders():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset folder not found: {DATASET_PATH}")

    class_folders = sorted(folder.name for folder in DATASET_PATH.iterdir() if folder.is_dir())

    detected_jackfruit = sorted(
        str(folder.relative_to(DATASET_PATH))
        for folder in DATASET_PATH.rglob("*")
        if folder.is_dir() and folder.name.lower() in JACKFRUIT_FOLDERS
    )
    if detected_jackfruit:
        raise RuntimeError(
            "Jackfruit folders detected. Remove or replace these before training: "
            + ", ".join(detected_jackfruit)
        )

    nested_fruit_folders = [
        folder_name for folder_name in class_folders if folder_name.lower() in NESTED_FRUIT_FOLDERS
    ]
    if nested_fruit_folders:
        raise RuntimeError(
            "Unexpected nested fruit folders detected as top-level classes: "
            + ", ".join(nested_fruit_folders)
        )

    if len(class_folders) != EXPECTED_CLASS_COUNT:
        raise RuntimeError(
            f"Class count must be exactly {EXPECTED_CLASS_COUNT}. "
            f"Detected {len(class_folders)}: {', '.join(class_folders)}"
        )

    print("Detected class names:")
    for folder_name in class_folders:
        print(f"- {label_from_folder(folder_name)} ({folder_name})")

    return class_folders


def count_images(folder_path):
    return sum(
        1
        for file_path in folder_path.rglob("*")
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS
    )


def move_invalid_file(file_path, class_folder_name):
    destination_dir = INVALID_IMAGES_DIR / class_folder_name
    destination_dir.mkdir(parents=True, exist_ok=True)

    destination_path = destination_dir / file_path.name
    index = 1
    while destination_path.exists():
        destination_path = destination_dir / f"{file_path.stem}_{index}{file_path.suffix}"
        index += 1

    shutil.move(str(file_path), str(destination_path))
    return destination_path


def is_non_training_file(file_path):
    return (
        file_path.name.lower() in NON_TRAINING_FILENAMES
        or not file_path.suffix
        or file_path.suffix.lower() in NON_TRAINING_EXTENSIONS
        or file_path.suffix.lower() not in IMAGE_EXTENSIONS
    )


def clean_invalid_images(class_folders):
    total_files_scanned = 0
    invalid_files = []

    for class_folder_name in class_folders:
        class_folder = DATASET_PATH / class_folder_name

        for file_path in class_folder.rglob("*"):
            if not file_path.is_file():
                continue

            total_files_scanned += 1

            if is_non_training_file(file_path):
                destination_path = move_invalid_file(file_path, class_folder_name)
                invalid_files.append((class_folder_name, file_path.name, destination_path))
                continue

            try:
                with Image.open(file_path) as image:
                    image.verify()
            except (UnidentifiedImageError, OSError, ValueError):
                destination_path = move_invalid_file(file_path, class_folder_name)
                invalid_files.append((class_folder_name, file_path.name, destination_path))

    print("Dataset image validation report:")
    print(f"- Total files scanned: {total_files_scanned}")
    print(f"- Total invalid files moved: {len(invalid_files)}")
    print(f"- Invalid backup folder: {INVALID_IMAGES_DIR}")

    if invalid_files:
        print("- Invalid files moved:")
        for class_folder_name, file_name, _destination_path in invalid_files:
            print(f"  {class_folder_name}: {file_name}")
    else:
        print("- Invalid files moved: none")

    for class_folder_name in class_folders:
        image_count = count_images(DATASET_PATH / class_folder_name)
        if image_count == 0:
            raise RuntimeError(
                f"No valid images remain in class folder after cleaning: {class_folder_name}"
            )


def build_generators(class_folders):
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        validation_split=VALIDATION_SPLIT,
        rotation_range=25,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.1,
        zoom_range=0.2,
        brightness_range=[0.7, 1.3],
        horizontal_flip=True,
        fill_mode="nearest",
    )
    validation_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        validation_split=VALIDATION_SPLIT,
    )

    train_generator = train_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        classes=class_folders,
        class_mode="categorical",
        subset="training",
        shuffle=True,
    )
    validation_generator = validation_datagen.flow_from_directory(
        DATASET_PATH,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        classes=class_folders,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
    )

    labels_in_generator_order = [
        label_from_folder(folder_name)
        for folder_name, _index in sorted(
            train_generator.class_indices.items(),
            key=lambda item: item[1],
        )
    ]

    print("Generator class order:")
    for index, label in enumerate(labels_in_generator_order):
        print(f"{index}: {label}")

    with LABELS_PATH.open("w", encoding="utf-8") as file:
        json.dump(labels_in_generator_order, file, indent=2)
        file.write("\n")

    print(f"Train image count: {train_generator.samples}")
    print(f"Validation image count: {validation_generator.samples}")

    return train_generator, validation_generator, labels_in_generator_order


def build_model(class_count):
    base_model = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3),
    )
    base_model.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.3)(x)
    output = Dense(class_count, activation="softmax")(x)

    model = Model(inputs=base_model.input, outputs=output)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base_model


def build_callbacks():
    return [
        ModelCheckpoint(
            MODEL_PATH,
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.2,
            patience=2,
            min_lr=1e-6,
            verbose=1,
        ),
    ]


def plot_training_history(histories):
    accuracy = []
    val_accuracy = []
    loss = []
    val_loss = []

    for history in histories:
        accuracy.extend(history.history.get("accuracy", []))
        val_accuracy.extend(history.history.get("val_accuracy", []))
        loss.extend(history.history.get("loss", []))
        val_loss.extend(history.history.get("val_loss", []))

    epochs = range(1, len(accuracy) + 1)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epochs, accuracy, label="Training Accuracy")
    plt.plot(epochs, val_accuracy, label="Validation Accuracy")
    plt.title("MobileNetV2 Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(epochs, loss, label="Training Loss")
    plt.plot(epochs, val_loss, label="Validation Loss")
    plt.title("MobileNetV2 Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    plt.tight_layout()
    plt.savefig(HISTORY_PATH)
    plt.close()


def save_evaluation_outputs(model, validation_generator, class_labels):
    validation_generator.reset()
    predictions = model.predict(validation_generator)
    predicted_classes = np.argmax(predictions, axis=1)
    true_classes = validation_generator.classes
    labels = list(range(len(class_labels)))

    report = classification_report(
        true_classes,
        predicted_classes,
        labels=labels,
        target_names=class_labels,
        zero_division=0,
    )
    with CLASSIFICATION_REPORT_PATH.open("w", encoding="utf-8") as file:
        file.write(report)

    matrix = confusion_matrix(true_classes, predicted_classes, labels=labels)
    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=class_labels,
    )
    fig, ax = plt.subplots(figsize=(13, 11))
    display.plot(ax=ax, xticks_rotation=90, cmap="Blues", colorbar=False)
    plt.title("MobileNetV2 Confusion Matrix")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH)
    plt.close(fig)


def fine_tune_model(model, base_model):
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    class_folders = get_class_folders()
    clean_invalid_images(class_folders)
    train_generator, validation_generator, class_labels = build_generators(class_folders)

    model, base_model = build_model(len(class_labels))
    initial_history = model.fit(
        train_generator,
        epochs=INITIAL_EPOCHS,
        validation_data=validation_generator,
        callbacks=build_callbacks(),
    )

    fine_tune_model(model, base_model)
    fine_tune_history = model.fit(
        train_generator,
        epochs=INITIAL_EPOCHS + FINE_TUNE_EPOCHS,
        initial_epoch=INITIAL_EPOCHS,
        validation_data=validation_generator,
        callbacks=build_callbacks(),
    )

    model.save(MODEL_PATH)
    plot_training_history([initial_history, fine_tune_history])
    save_evaluation_outputs(model, validation_generator, class_labels)

    print(f"Final model saved to: {MODEL_PATH}")
    print(f"Labels saved to: {LABELS_PATH}")
    print(f"Training history saved to: {HISTORY_PATH}")
    print(f"Confusion matrix saved to: {CONFUSION_MATRIX_PATH}")
    print(f"Classification report saved to: {CLASSIFICATION_REPORT_PATH}")


if __name__ == "__main__":
    main()
