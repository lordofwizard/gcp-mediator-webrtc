from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import socket
import struct
import pickle
import cv2
import threading

# Create a Flask app instance
app = Flask(__name__, static_url_path='/static')

# Variables to store the latest frame
latest_frame = None

def receive_frames():
    global latest_frame
    
    # Server IP and port
    server_ip = '0.0.0.0'
    server_port = 12345
    
    # Create a socket connection
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    
    print("Server is listening...")
    
    while True:
        client_socket, addr = server_socket.accept()
        print('Connection from:', addr)
        
        data = b""
        payload_size = struct.calcsize("L")
        
        while True:
            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    break
                data += packet
            
            if len(data) < payload_size:
                break
            
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_msg_size)[0]
            
            while len(data) < msg_size:
                data += client_socket.recv(4096)
            
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            # Deserialize the frame
            frame = pickle.loads(frame_data)
            latest_frame = frame

# Start a thread to receive frames
threading.Thread(target=receive_frames, daemon=True).start()

# Route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')

# Function to generate video frames received from the source
def generate_frames():
    global latest_frame
    while True:
        if latest_frame is not None:
            ret, buffer = cv2.imencode('.jpg', latest_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route to stream video frames
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

