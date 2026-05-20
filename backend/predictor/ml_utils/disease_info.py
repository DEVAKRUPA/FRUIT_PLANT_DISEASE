DISEASE_INFO = {
    "Apple Healthy": {
        "leaf_category": "Apple Leaf",
        "disease": "Healthy",
        "precautions": "Keep regular watering, pruning, and field hygiene. Continue checking leaves for early spots or rust.",
        "treatment": "No treatment is needed. Maintain good nutrition and remove fallen infected plant waste from nearby plants.",
    },
    "Apple Rust": {
        "leaf_category": "Apple Leaf",
        "disease": "Rust",
        "precautions": "Avoid overhead watering and improve air circulation around the plant. Remove heavily infected leaves early.",
        "treatment": "Use a recommended fungicide for rust disease and repeat as advised by a local agriculture expert.",
    },
    "Apple Scab": {
        "leaf_category": "Apple Leaf",
        "disease": "Scab",
        "precautions": "Keep the area clean, remove fallen leaves, and avoid wet leaves for long periods.",
        "treatment": "Apply a suitable scab-control fungicide and prune crowded branches to improve airflow.",
    },
    "Banana Cordana": {
        "leaf_category": "Banana Leaf",
        "disease": "Cordana Leaf Spot",
        "precautions": "Remove infected leaf parts and keep enough spacing between plants for airflow.",
        "treatment": "Use a recommended fungicide and avoid excess irrigation that keeps leaves wet.",
    },
    "Banana Healthy": {
        "leaf_category": "Banana Leaf",
        "disease": "Healthy",
        "precautions": "Maintain proper watering, balanced fertilizer, and clean surroundings.",
        "treatment": "No disease treatment is needed. Continue routine care and regular inspection.",
    },
    "Banana Yellow Brown Sigatoka": {
        "leaf_category": "Banana Leaf",
        "disease": "Yellow Brown Sigatoka",
        "precautions": "Remove old infected leaves and avoid dense planting. Keep the plantation well ventilated.",
        "treatment": "Apply a suitable fungicide for Sigatoka and follow local spray schedule guidance.",
    },
    "Guava Algal Leaf Spot": {
        "leaf_category": "Guava Leaf",
        "disease": "Algal Leaf Spot",
        "precautions": "Reduce leaf wetness, prune crowded branches, and remove infected leaves.",
        "treatment": "Use copper-based treatment if recommended locally and improve drainage around the plant.",
    },
    "Guava Healthy": {
        "leaf_category": "Guava Leaf",
        "disease": "Healthy",
        "precautions": "Keep the plant clean, watered, and well pruned. Monitor leaves after humid weather.",
        "treatment": "No treatment is needed. Continue normal care and balanced nutrition.",
    },
    "Guava Red Rust": {
        "leaf_category": "Guava Leaf",
        "disease": "Red Rust",
        "precautions": "Remove affected leaves and reduce conditions that keep foliage damp for long periods.",
        "treatment": "Apply suitable copper-based or recommended fungicidal treatment after expert advice.",
    },
    "Grape Black Rot": {
        "leaf_category": "Grape Leaf",
        "disease": "Black Rot",
        "precautions": "Remove infected leaves, avoid overhead watering, and improve air circulation.",
        "treatment": "Apply a suitable fungicide if infection spreads.",
        "recommendation": "Remove infected leaves, avoid overhead watering, improve air circulation, and apply a suitable fungicide if infection spreads.",
    },
    "Grape Leaf Blight": {
        "leaf_category": "Grape Leaf",
        "disease": "Leaf Blight",
        "precautions": "Prune affected leaves, keep the area clean, and avoid excess moisture.",
        "treatment": "Use a recommended fungicide for leaf blight control.",
        "recommendation": "Prune affected leaves, keep the area clean, avoid excess moisture, and use a recommended fungicide for leaf blight control.",
    },
    "Grape Healthy": {
        "leaf_category": "Grape Leaf",
        "disease": "Healthy",
        "precautions": "Keep the grape plant healthy with proper watering, sunlight, and regular monitoring.",
        "treatment": "No disease treatment is needed.",
        "recommendation": "No disease detected. Keep the grape plant healthy with proper watering, sunlight, and regular monitoring.",
    },
    "Mango Gall Midge": {
        "leaf_category": "Mango Leaf",
        "disease": "Gall Midge Damage",
        "precautions": "Remove affected leaves and monitor new flushes where pest damage often starts.",
        "treatment": "Use locally recommended pest management methods and consult an agriculture expert for severe cases.",
    },
    "Mango Healthy": {
        "leaf_category": "Mango Leaf",
        "disease": "Healthy",
        "precautions": "Keep the tree clean, avoid water stress, and inspect leaves during new growth.",
        "treatment": "No treatment is needed. Maintain routine watering, pruning, and nutrition.",
    },
    "Mango Sooty Mould": {
        "leaf_category": "Mango Leaf",
        "disease": "Sooty Mould",
        "precautions": "Control sap-sucking insects such as scales, aphids, and mealybugs because they encourage sooty mould.",
        "treatment": "Wash affected leaves gently and use recommended insect control to stop honeydew production.",
    },
    "Papaya Curl": {
        "leaf_category": "Papaya Leaf",
        "disease": "Leaf Curl",
        "precautions": "Control whiteflies and remove severely affected plants to reduce spread.",
        "treatment": "Use recommended pest control methods and keep the field free from weed hosts.",
    },
    "Papaya Healthy": {
        "leaf_category": "Papaya Leaf",
        "disease": "Healthy",
        "precautions": "Maintain good drainage, balanced fertilizer, and regular pest monitoring.",
        "treatment": "No treatment is needed. Continue normal plant care and field sanitation.",
    },
    "Papaya Ring Spot": {
        "leaf_category": "Papaya Leaf",
        "disease": "Ring Spot",
        "precautions": "Control aphids, remove infected plants early, and avoid planting near infected papaya crops.",
        "treatment": "There is no simple cure for viral ring spot. Remove infected plants and use resistant varieties when possible.",
    },
}


def get_disease_info(prediction):
    disease_info = DISEASE_INFO.get(
        prediction,
        {
            "leaf_category": "Unknown Leaf",
            "disease": "Unknown",
            "precautions": "Please upload a clear fruit leaf image and try again.",
            "treatment": "No treatment suggestion is available for this prediction yet.",
        },
    ).copy()
    if "recommendation" not in disease_info:
        disease_info["recommendation"] = (
            f"{disease_info['precautions']} {disease_info['treatment']}"
        )
    return disease_info
