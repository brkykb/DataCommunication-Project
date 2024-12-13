from flask import Flask, request, jsonify
import tensorflow as tf
from PIL import Image
import numpy as np

app = Flask(__name__)

# Modeli yükle
MODEL_PATH = "recycling_model"
model = tf.keras.models.load_model(MODEL_PATH)

# Sınıflandırma fonksiyonu
def classify_image(image_path):
    # Fotoğrafı aç ve modele uygun hale getir
    image = Image.open(image_path).resize((118, 118))
    image_array = np.array(image) / 255.0  # Normalize
    image_array = np.expand_dims(image_array, axis=0)  # Batch boyutu ekle

    # Model ile tahmin yap
    predictions = model.predict(image_array)
    classes = ["plastic", "glass", "metal"]  # Modelin sınıfları
    return classes[np.argmax(predictions)]

# API endpoint
@app.route('/classify', methods=['POST'])
def classify():
    if 'photo' not in request.files:
        return jsonify({"error": "Fotoğraf yüklenmedi"}), 400

    # Fotoğrafı kaydet
    photo = request.files['photo']
    photo_path = "uploaded_image.jpg"
    photo.save(photo_path)

    # Fotoğrafı sınıflandır
    result = classify_image(photo_path)
    return jsonify({"type": result})

# Sunucuyu çalıştır
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
