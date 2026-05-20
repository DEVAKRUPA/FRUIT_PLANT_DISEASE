import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "ml_training" / "Dataset"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "predictor" / "ml_model" / "efficientnet_b0"

MODEL_PATH = OUTPUT_DIR / "efficientnet_b0_model.keras"
LABELS_PATH = OUTPUT_DIR / "labels.json"
HISTORY_PATH = OUTPUT_DIR / "training_history.png"
CONFUSION_MATRIX_PATH = OUTPUT_DIR / "confusion_matrix.png"
CLASSIFICATION_REPORT_PATH = OUTPUT_DIR / "classification_report.txt"

IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
INITIAL_EPOCHS = 20
FINE_TUNE_EPOCHS = 10
VALIDATION_SPLIT = 0.2
SEED = 42


def validate_dataset_path():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset folder not found: {DATASET_PATH}")

    class_folders = sorted(folder.name for folder in DATASET_PATH.iterdir() if folder.is_dir())
    if not class_folders:
        raise RuntimeError(f"No class folders found in dataset folder: {DATASET_PATH}")


def load_datasets():
    validate_dataset_path()

    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_PATH,
        validation_split=VALIDATION_SPLIT,
        subset="training",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        shuffle=True,
    )
    validation_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_PATH,
        validation_split=VALIDATION_SPLIT,
        subset="validation",
        seed=SEED,
        image_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="int",
        shuffle=False,
    )

    class_names = list(train_ds.class_names)

    print("Class names:")
    for index, class_name in enumerate(class_names):
        print(f"{index}: {class_name}")
    print(f"Number of classes: {len(class_names)}")
    print(f"Train batch count: {tf.data.experimental.cardinality(train_ds).numpy()}")
    print(f"Validation batch count: {tf.data.experimental.cardinality(validation_ds).numpy()}")

    labels = {str(index): class_name for index, class_name in enumerate(class_names)}
    with LABELS_PATH.open("w", encoding="utf-8") as file:
        json.dump(labels, file, indent=2)
        file.write("\n")

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000, seed=SEED).prefetch(autotune)
    validation_ds = validation_ds.cache().prefetch(autotune)

    return train_ds, validation_ds, class_names


def build_model(num_classes):
    data_augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.1),
            tf.keras.layers.RandomZoom(0.1),
            tf.keras.layers.RandomContrast(0.1),
        ],
        name="data_augmentation",
    )

    base_model = EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3),
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3))
    x = data_augmentation(inputs)
    x = preprocess_input(x)
    x = base_model(x, training=False)
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss="sparse_categorical_crossentropy",
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
        EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
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


def fine_tune_model(model, base_model):
    base_model.trainable = True
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )


def combine_histories(histories):
    combined = {
        "accuracy": [],
        "val_accuracy": [],
        "loss": [],
        "val_loss": [],
    }

    for history in histories:
        for metric in combined:
            combined[metric].extend(history.history.get(metric, []))

    return combined


def save_training_history(histories):
    history = combine_histories(histories)
    epochs = range(1, len(history["accuracy"]) + 1)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(epochs, history["accuracy"], label="Training Accuracy")
    plt.plot(epochs, history["val_accuracy"], label="Validation Accuracy")
    plt.title("EfficientNetB0 Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(epochs, history["loss"], label="Training Loss")
    plt.plot(epochs, history["val_loss"], label="Validation Loss")
    plt.title("EfficientNetB0 Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    plt.tight_layout()
    plt.savefig(HISTORY_PATH)
    plt.close()


def collect_predictions(model, validation_ds):
    y_true_batches = []
    y_pred_batches = []

    for images, labels in validation_ds:
        predictions = model.predict(images, verbose=0)
        y_true_batches.append(labels.numpy())
        y_pred_batches.append(np.argmax(predictions, axis=1))

    y_true = np.concatenate(y_true_batches)
    y_pred = np.concatenate(y_pred_batches)
    return y_true, y_pred


def save_evaluation_outputs(model, validation_ds, class_names):
    y_true, y_pred = collect_predictions(model, validation_ds)
    labels = list(range(len(class_names)))

    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=class_names,
        zero_division=0,
    )
    with CLASSIFICATION_REPORT_PATH.open("w", encoding="utf-8") as file:
        file.write(report)

    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=class_names,
    )
    fig, ax = plt.subplots(figsize=(13, 11))
    display.plot(ax=ax, xticks_rotation=90, cmap="Blues", colorbar=False)
    plt.title("EfficientNetB0 Confusion Matrix")
    plt.tight_layout()
    plt.savefig(CONFUSION_MATRIX_PATH)
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    train_ds, validation_ds, class_names = load_datasets()
    model, base_model = build_model(len(class_names))

    callbacks = build_callbacks()
    initial_history = model.fit(
        train_ds,
        validation_data=validation_ds,
        epochs=INITIAL_EPOCHS,
        callbacks=callbacks,
    )

    fine_tune_model(model, base_model)
    fine_tune_history = model.fit(
        train_ds,
        validation_data=validation_ds,
        epochs=INITIAL_EPOCHS + FINE_TUNE_EPOCHS,
        initial_epoch=INITIAL_EPOCHS,
        callbacks=callbacks,
    )

    model.save(MODEL_PATH)
    save_training_history([initial_history, fine_tune_history])
    save_evaluation_outputs(model, validation_ds, class_names)

    print(f"Saved model path: {MODEL_PATH}")
    print(f"Saved labels path: {LABELS_PATH}")
    print(f"Saved training history path: {HISTORY_PATH}")
    print(f"Saved confusion matrix path: {CONFUSION_MATRIX_PATH}")
    print(f"Saved classification report path: {CLASSIFICATION_REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"EfficientNetB0 training failed: {exc}")
        raise
