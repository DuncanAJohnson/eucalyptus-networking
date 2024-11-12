import socket
import time
import select

class ESPNOWBridge:
    def __init__(self, host, port=8888):
        self.host = host
        self.port = port
        self.sock = None
        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.setblocking(False)  # Set socket to non-blocking mode

    def send_message(self, mac, message):
        command = f"COMPUTER:{mac}:{message}\n"
        print(f"Sending: {command.strip()}")  # Debug print
        self.sock.sendall(command.encode())

    def receive_message(self):
        ready = select.select([self.sock], [], [], 0.1)  # Wait up to 0.1 seconds for data
        if ready[0]:
            print("Data available to read")  # Debug print
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("Connection closed by ESP32")
                    self.connect()
                    return None, None
                message = data.decode().strip()
                print(f"Received raw: {message}")  # Debug print
                if message.startswith("ESPNOW:"):
                    _, mac, payload = message.split(':', 2)
                    return bytes.fromhex(mac), payload
                else:
                    print(f"Received message doesn't start with ESPNOW: {message}")  # Debug print
            except socket.error as e:
                print(f"Socket error: {e}")
                self.connect()
        else:
            print("No data available to read")  # Debug print
        return None, None

    def close(self):
        if self.sock:
            self.sock.close()

# Usage
ESP32_IP = "192.168.0.68"  # Replace with your ESP32's IP address
bridge = ESPNOWBridge(ESP32_IP)

# Send and receive messages
try:
    # send
    out_message = input("What to put on ESP32 screen: ")
    bridge.send_message("ffffffffffff", out_message)

    # receive
    while True:
        mac, message = bridge.receive_message()
        if mac:
            print(f"Received from {mac.hex()}: {message}")
        time.sleep(0.01)
except KeyboardInterrupt:
    print("Closing connection")
    bridge.close()