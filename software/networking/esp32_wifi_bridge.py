import network
import socket
from networking import Networking
import urequests
import time
from io import IO

import sensors
sens=sensors.SENSORS()

# Wi-Fi credentials
SSID = "Cronset43"
PASSWORD = "Reibzwecken95"

# TCP Server settings
TCP_PORT = 8888

# Initialize Wi-Fi
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, PASSWORD)

# Wait for Wi-Fi connection
while not sta_if.isconnected():
    time.sleep(0.1)

print('Connected to Wi-Fi')
print('IP Address:', sta_if.ifconfig()[0])

# Initialize Networking
networking = Networking(True, False)
networking.sta.connect(SSID, PASSWORD)
broadcast_mac = b'\xff\xff\xff\xff\xff\xff'
networking.aen.add_peer(broadcast_mac, "All")
networking.name = "Gateway"

# Set up TCP server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', TCP_PORT))
s.listen(1)
print(f'TCP Server listening on port {TCP_PORT}')

def forward_to_computer(mac, message, receive_time):
    global conn
    print(f"forward_to_computer called with mac: {mac.hex()}, message: {message}")  # Debug print
    try:
        data_to_send = f"ESPNOW:{mac.hex()}:{message}\n".encode()
        print(f"Sending to computer: {data_to_send}")  # Debug print
        conn.send(data_to_send)
        print("Sent successfully")  # Debug print
    except Exception as e:
        print(f"Error sending to computer: {e}")

networking.aen.irq(forward_to_computer)

print("ESP-NOW callback set up")

# initialize IO
io = IO()

conn = None
while True:
    if conn is None:
        conn, addr = s.accept()
        print(f'Connected by {addr}')
        # Send a test message
        test_message = "ESPNOW:ffffffffffff:Test message from ESP32\n"
        conn.send(test_message.encode())
        print(f"Sent test message: {test_message.strip()}")
        
    try:
        data = conn.recv(1024)
        if not data:
            print("No data received, closing connection")  # Debug print
            conn.close()
            conn = None
            continue
        
        print(f"Received from computer: {data}")  # Debug print
        parts = data.decode().strip().split(':')
        if len(parts) == 3 and parts[0] == "COMPUTER":
            mac = bytes.fromhex(parts[1])
            message = "Hello from ESP32".encode()
            print(f"Sending to ESP-NOW: {mac.hex()}, {message}")  # Debug print
            networking.aen.send(mac, message)
            
            io.write_to_screen(parts[2])
            
            # send messages back with roll data
            while True:
                roll, pitch = sens.readroll()
                message = ("ESPNOW:ffffffffffff:Roll: " + str(roll) + " and pitch: " + str(pitch) + "\n").encode()
                conn.send(message)
                
                time.sleep(0.5)
        else:
            print(f"Invalid message format: {parts}")  # Debug print
    except Exception as e:
        print(f"Error receiving from computer: {e}")
        conn.close()
        conn = None

    time.sleep(0.01)
    

