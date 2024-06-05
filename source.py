import cv2
import socket
import struct
import pickle

# Server IP and port
server_ip = '192.168.0.239'
server_port = 12345

# Create a socket connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))

# Create a VideoCapture object
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Serialize the frame
    data = pickle.dumps(frame)

    # Send message length first
    message_size = struct.pack("L", len(data))
    
    # Then data
    client_socket.sendall(message_size + data)

# Release the capture and close the socket
cap.release()
client_socket.close()

