def get_recommendation(label):

    # Apple
    if label == "Apple Healthy":
        return "No disease detected. Keep plant healthy 🌿"

    elif label == "Apple Rust":
        return "Remove infected leaves and spray sulfur-based fungicide."

    elif label == "Apple Scab":
        return "Prune infected parts and apply copper fungicide spray."

    # Banana
    elif label == "Banana Cordana":
        return "Remove infected leaves and apply organic fungicide."

    elif label == "Banana Healthy":
        return "Plant is healthy. Maintain proper irrigation."

    elif label == "Banana Yellow Brown Sigatoka":
        return "Use resistant varieties and apply fungicide spray."

    # Guava
    elif label == "Guava Algal Leaf Spot":
        return "Prune affected branches and apply copper-based spray."

    elif label == "Guava Healthy":
        return "No disease detected. Maintain good soil nutrition."

    elif label == "Guava Red Rust":
        return "Remove infected leaves and spray neem oil or bio-fungicide."

    # Grape
    elif label == "Grape Black Rot":
        return "Remove infected leaves, avoid overhead watering, improve air circulation, and apply a suitable fungicide if infection spreads."

    elif label == "Grape Leaf Blight":
        return "Prune affected leaves, keep the area clean, avoid excess moisture, and use a recommended fungicide for leaf blight control."

    elif label == "Grape Healthy":
        return "No disease detected. Keep the grape plant healthy with proper watering, sunlight, and regular monitoring."

    # Mango
    elif label == "Mango Gall Midge":
        return "Remove infested shoots and use insecticide spray."

    elif label == "Mango Healthy":
        return "No disease detected. Maintain proper watering and nutrients."

    elif label == "Mango Sooty Mould":
        return "Control honeydew insects and clean leaves with water spray."

    # Papaya
    elif label == "Papaya Curl":
        return "Remove infected leaves and control whiteflies using neem oil."

    elif label == "Papaya Healthy":
        return "Plant is healthy. Keep monitoring regularly."

    elif label == "Papaya Ring Spot":
        return "Remove infected plants and use resistant varieties."

    else:
        return "No recommendation available."
