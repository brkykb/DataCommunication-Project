import socket
import threading
import tensorflow as tf
import numpy as np
import cv2
import sqlite3
from datetime import datetime

# Load model
model = tf.keras.models.load_model("recycle.h5")
labels = ['Can', 'Glass', 'Paper', 'Plastic']  # Güncel etiketler

# Database setup
def init_db():
    conn = sqlite3.connect("classifications.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_ip TEXT,
            image_size INTEGER,
            result TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(client_ip, image_size, result):
    conn = sqlite3.connect("classifications.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO classifications (client_ip, image_size, result, timestamp)
        VALUES (?, ?, ?, ?)
    """, (client_ip, image_size, result, timestamp))
    conn.commit()
    conn.close()

# Image classification
def classify_image(image_data):
    try:
        # Preprocess image
        image = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.resize(image, (128, 128))
        image = image / 255.0  # Normalize
        image = np.expand_dims(image, axis=0)

        # Predict
        predictions = model.predict(image)
        label = labels[np.argmax(predictions)]
        return label
    except Exception as e:
        print(f"Error in classify_image: {e}")
        return "Error in classification"

# Client handler
def handle_client(client_socket, addr):
    """Handle communication with a single client."""
    print(f"New connection from {addr}")
    try:
        data = b""
        while True:
            packet = client_socket.recv(4096)
            if not packet:  # End of data
                break
            data += packet
        print(f"Received {len(data)} bytes of image data from {addr}")

        # Classify image
        result = classify_image(data)

        # Save result to database
        save_to_db(client_ip=addr[0], image_size=len(data), result=result)

        # Send result
        client_socket.send(result.encode())
    except Exception as e:
        print(f"Error with client {addr}: {e}")
        client_socket.send(b"Error processing image")
    finally:
        input() 
        client_socket.close()
        print(f"Connection with {addr} closed.")

# TCP Server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 8080))
server_socket.listen(2)  # Allow up to 5 pending connections
print("Server listening on port 8080...")

# Initialize database
init_db()

try:
    while True:
        client_socket, addr = server_socket.accept()
        # Create a new thread for each client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()
except KeyboardInterrupt:
    print("Server manually stopped.")
finally:
    server_socket.close()
    print("Server shut down.")
