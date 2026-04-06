"""
espserver.py
ESP32 HTTP Web Server
MicroPython v1.20 recommended for hall sensor support
MAJHARUL HOQUE
m.harulhoq@gmail.com
"""

# Required Libraries
import network
import socket
import esp32
from machine import Pin


# =========================
# USER SETTINGS
# =========================
# -------------------------
# WiFi SETTINGS
# -------------------------
WIFI_SSID = "xxxxxxxxxx"
WIFI_PASSWORD = "xxxxxxxx"

# Change this if your onboard red LED is on a different GPIO
LED_PIN = 13

# =========================
# GLOBAL VARIABLES
# =========================
temp = 0
hall = 0
red_led_state = "OFF"

red_led = Pin(LED_PIN, Pin.OUT)
red_led.value(0)


def web_page():
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.

    Global variables:
    temp, hall, red_led_state
    """

    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <title>ESP32 Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h1 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none;
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h1>ESP32 WEB Server</h1>
    <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i>
    <span class="sensor-labels">Temperature</span>
    <span>""" + str(temp) + """</span>
    <sup class="units">&deg;F</sup>
    </p>
    <p>
    <i class="fas fa-bolt" style="color:#00add6;"></i>
    <span class="sensor-labels">Hall</span>
    <span>""" + str(hall) + """</span>
    <sup class="units">V</sup>
    </p>
    <p>
    RED LED Current State: <strong>""" + red_led_state + """</strong>
    </p>
    <p>
    <a href="/?red_led=on"><button class="button">RED ON</button></a>
    </p>
    <p>
    <a href="/?red_led=off"><button class="button button2">RED OFF</button></a>
    </p>
    </body>
    </html>"""
    return html_webpage

# WiFi connection module
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        import time
        timeout_s = 20
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout_s:
                raise RuntimeError("Wi-Fi connection timed out")
            time.sleep(1)

    print("Connected to", WIFI_SSID)
    print("IP Address:", wlan.ifconfig()[0])
    return wlan

# Read and update Sensor values
def update_sensor_values():
    global temp, hall, red_led_state
    temp = esp32.raw_temperature()
    hall = esp32.hall_sensor()
    red_led_state = "ON" if red_led.value() else "OFF"


def main():
    connect_wifi()
    update_sensor_values()

    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    server = socket.socket()
    server.bind(addr)
    server.listen(5)

    print("HTTP server running on port 80")

    while True:
        client, client_addr = server.accept()
        print("Client connected from", client_addr)

        try:
            request = client.recv(1024)
            request_str = request.decode()
            print("Request:")
            print(request_str)

            if "/?red_led=on" in request_str:
                red_led.value(1)
            elif "/?red_led=off" in request_str:
                red_led.value(0)

            update_sensor_values()
            response = web_page()

            client.send("HTTP/1.1 200 OK\r\n")
            client.send("Content-Type: text/html\r\n")
            client.send("Connection: close\r\n")
            client.send("\r\n")
            client.send(response)

        except Exception as e:
            print("Error:", e)

        finally:
            client.close()


if __name__ == "__main__":
    main()
