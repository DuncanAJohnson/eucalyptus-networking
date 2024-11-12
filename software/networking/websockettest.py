import network
import time
import machine
from machine import Pin
from websocket import connect

# WiFi credentials
SSID = 'Cronset43'
PASSWORD = 'Reibzwecken95'

# WebSocket server details
SERVER = 'wss://eucalyptus--python-executer-endpoint.modal.run/ws'  # e.g., 'ws://192.168.1.100/ws'

# Button pin
button_pin = 9  # GPIO pin connected to the button

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print('Connecting to WiFi...')
        time.sleep(1)
    print('Connected to WiFi:', wlan.ifconfig())

# WebSocket communication
def connect_websocket():
    ws = WebSocket(SERVER)
    ws.connect()
    return ws

# Main function
def main():
    connect_wifi()
    ws = connect(SERVER)
    
    button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

    while True:
        if button.value() == 0:  # Button pressed
            print('Button pressed, sending message...')
            ws.send('{"run": true, "code": "move_up()"}')
            time.sleep(1)  # Debounce delay

try:
    main()
except Exception as e:
    print('Error:', e)

