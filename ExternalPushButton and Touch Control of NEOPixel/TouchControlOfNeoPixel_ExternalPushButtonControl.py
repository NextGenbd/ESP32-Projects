import network
import ntptime
import machine
import esp32
import neopixel
import time

from machine import Pin, RTC, Timer, TouchPad

# -------------------------
# USER SETTINGS
# -------------------------
WIFI_SSID = "*****"
WIFI_PASSWORD = "*******"

UTC_OFFSET = -4   # UTC-4 for Daylight savings time.

RED_LED_PIN = 13
BUTTON_PIN = 27
TOUCH_PIN = 14

# Built-in NeoPixel data pin
NEOPIXEL_PIN = 0
# Built-in NeoPixel power enable pin
NEOPIXEL_POWER = 2 

"""
not touching the wire shows value> 600
light touching to holding the wire
shows value <590
"""
TOUCH_THRESHOLD = 580

# -------------------------
# HARDWARE SETUP
# -------------------------
red_led = Pin(RED_LED_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
# Turn on NeoPixel power
neo_power = Pin(NEOPIXEL_POWER, Pin.OUT)
neo_power.value(1)

np = neopixel.NeoPixel(Pin(NEOPIXEL_PIN, Pin.OUT), 1)
touch = TouchPad(Pin(TOUCH_PIN))
rtc = RTC()

time_timer  = Timer(0)
touch_timer = Timer(1)
sleep_timer = Timer(2)

# -------------------------
# HELPER FUNCTIONS
# -------------------------
def neopixel_off():
    np[0] = (0, 0, 0)
    np.write()

def neopixel_green():
    np[0] = (0, 20, 0)
    np.write()
    
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("Connected to", WIFI_SSID)
        print("IP Address:", wlan.ifconfig()[0])
    else:
        print("WiFi connection failed")

    return wlan

def sync_time():
    try:
        ntptime.host = "pool.ntp.org"
        ntptime.settime()

        year, month, day, weekday, hour, minute, second, subseconds = rtc.datetime()

        hour += UTC_OFFSET
        if hour < 0:
            hour += 24
            day -= 1
        elif hour >= 24:
            hour -= 24
            day += 1

        rtc.datetime((year, month, day, weekday, hour, minute, second, subseconds))
        print("RTC updated from NTP")
    except Exception as e:
        print("Time sync failed:", e)

def print_datetime(timer):
    year, month, day, weekday, hour, minute, second, subseconds = rtc.datetime()
    print("Date: {:02d}/{:02d}/{:04d}".format(month, day, year))
    print("Time: {:02d}:{:02d}:{:02d} HRS".format(hour, minute, second))

def check_touch(timer):
    value = touch.read()

    if value < TOUCH_THRESHOLD:
        neopixel_green()
    else:
        neopixel_off()

def go_to_sleep(timer):
    print("I am going to sleep for 1 minute.")
    
    # stop all timers before sleep
    time_timer.deinit()
    touch_timer.deinit()
    sleep_timer.deinit()
    
    neopixel_off()
    red_led.value(0)
    
    # sleep for 1 minute, with timer wake enabled
    machine.deepsleep(60000)

def check_wakeup_reason():
    
    print("Reset cause:", machine.reset_cause())
    reason = machine.wake_reason()

    if reason == machine.PIN_WAKE:
        print("Woke up due to EXT0 wakeup.")
    elif reason == machine.TIMER_WAKE:
        print("Woke up due to timer wakeup.")
    else:
        print("Normal power on / reset")

# -------------------------
# MAIN PROGRAM
# -------------------------
red_led.value(1)
neopixel_off()

check_wakeup_reason()

esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ANY_HIGH)

connect_wifi()
sync_time()

time_timer.init(period=15000, mode=Timer.PERIODIC, callback=print_datetime)
touch_timer.init(period=50, mode=Timer.PERIODIC, callback=check_touch)
sleep_timer.init(period=30000, mode=Timer.ONE_SHOT, callback=go_to_sleep)

# keep main program alive
while True:
    time.sleep(1)