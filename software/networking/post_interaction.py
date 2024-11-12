import network
import urequests
import time
from machine import Pin, SoftI2C
import ssd1306
i2c = SoftI2C(scl = Pin(7), sda = Pin(6))
screen = ssd1306.SSD1306_I2C(128,64,i2c)

# Wi-Fi credentials
SSID = 'Cronset43'
PASSWORD = 'Reibzwecken95'

# Server URL
SERVER_URL = 'https://eucalyptus--python-executer-endpoint.modal.run/'  # Replace with your server URL

# paths to send requests
EXECUTE_URL = SERVER_URL + "execute"
POSITION_URL = SERVER_URL + "position"

# Button pin
button_pin = 9  # GPIO pin connected to the button

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print('Connecting to WiFi...')
        time.sleep(1)
    print('Connected to WiFi:', wlan.ifconfig())

# Send HTTP POST request
def send_post_request(URL, payload=""):
    try:
        response = urequests.post(URL, json=payload)
        if response.status_code == 200:
            try:
                data = response.json()
                print("Response:", data)
                return data
            except ValueError:
                print("Error decoding JSON")
                return None
        else:
            print("HTTP Error:", response.status_code)
            return None
    except Exception as e:
        print("Exception during POST request:", e)
        return None
    finally:
        response.close()

# Main function
def main():
    connect_wifi()
    button = Pin(button_pin, Pin.IN, Pin.PULL_UP)

    last_position_time = 0
    position_interval = 0.1  # Send position data request every 0.1 seconds

    while True:
        current_time = time.time()
        
        data = ""
        
        # Check button press
        if button.value() == 0:  # Button pressed
            print('Button pressed, sending POST request...')
            data = send_post_request(EXECUTE_URL, {"run": True})
            time.sleep(0.2)  # Debounce delay

        # Send position data request every 0.1 seconds
        if current_time - last_position_time >= position_interval:
            print('Sending position data request...')
            data = send_post_request(POSITION_URL)
            last_position_time = current_time
            
            
            if data != "":
                # Extract x and y from the response data
                x_pos = data.get('position')[0]
                y_pos = data.get('position')[1]

                # Display positions on the OLED screen
                screen.fill(0)  # Clear the screen
                screen.text('X: {}'.format(x_pos), 0, 0, 1)
                screen.text('Y: {}'.format(y_pos), 0, 10, 1)
                screen.show()
        
        time.sleep(0.01)  # Short delay to prevent excessive CPU usage

try:
    main()
except Exception as e:
    print('Error:', e)
