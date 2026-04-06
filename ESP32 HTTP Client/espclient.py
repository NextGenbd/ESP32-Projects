"""
espclient.py
ESP32 HTTP Client for ThingSpeak
MicroPython v1.20 recommended for hall sensor support
MAJHARUL HOQUE
m.harulhoq@gmail.com
"""

# Required Libraries
import network
import socket
import time
import esp32
from machine import Timer

# =========================
# USER SETTINGS
# =========================

# WiFi SETTINGS
WIFI_SSID = "xxxxxxx"
WIFI_PASSWORD = "xxxxxxx"
# THINGSPEAK API keys
THINGSPEAK_WRITE_API_KEY = "xxxxxxxxxx"

# =========================
# GLOBAL FLAG FOR TIMER
# =========================
upload_flag = False


def timer_callback(timer):
    global upload_flag
    upload_flag = True

# WiFi connection module
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout_s = 20
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout_s:
                raise RuntimeError("Wi-Fi connection timed out")
            time.sleep(1)

    print("Connected to", WIFI_SSID)
    print("IP Address:", wlan.ifconfig()[0])
    time.sleep(3) # Give a moment to settle the connection.
    return wlan


def read_sensors():
    # raw_temperature() returns Fahrenheit on ESP32 in MicroPython
    temp_f = esp32.raw_temperature()
    hall = esp32.hall_sensor()
    return temp_f, hall

# Module to send data to the ThingSpeak Server
def send_to_thingspeak(temp_f, hall):
    host = "api.thingspeak.com"
    
    addr = None
    ### The program will make 3 attempts to connect to the server.
    for attempt in range(3):
        try:
            addr = socket.getaddrinfo(host, 80)[0][-1]
            break
        except OSError as e:
            print("DNS lookup failed on attempt", attempt+1, "error", e)
            time.sleep(2)

    if addr is None:
        print("Skipping this upload because DNS failed.")
        return

    request = (
        "GET /update?api_key={}&field1={}&field2={} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(THINGSPEAK_WRITE_API_KEY, temp_f, hall, host)

    s = socket.socket()
    try:
        s.connect(addr)
        s.send(request.encode())

        response = b""
        while True:
            data = s.recv(256)
            if not data:
                break
            response += data

        #### Debug purpose:  to print the response and
        #### make sure the device is connected to the server 
        #print("ThingSpeak response:")
        #try:
            #print(response.decode())
        #except:
            #print(response)

    except OSError as e:
        print("Socket error during upload:", e)

    finally:
        s.close()


def main():
    global upload_flag

    connect_wifi()

    timer = Timer(0)
    timer.init(period=30000, mode=Timer.PERIODIC, callback=timer_callback)

    print("Running for 5 minutes. Upload interval = 30 seconds.")
    upload_count = 0

    try:
        while upload_count < 10:
            if upload_flag:
                upload_flag = False
                temp_f, hall = read_sensors()
                print("Temperature (F):", temp_f)
                print("Hall Sensor:", hall)
                send_to_thingspeak(temp_f, hall)
                upload_count += 1

            time.sleep_ms(100)

    finally:
        timer.deinit()
        print("Done. 5-minute client run complete.")


if __name__ == "__main__":
    main()
