Hardware Connection:
• ESP32 Feather V2 USB-C -> USB connection to computer for power and Thonny programming
• ESP32 GPIO 13 -> onboard red LED (used as awake indicator)
• ESP32 GPIO 0 -> onboard NeoPixel data pin
• ESP32 GPIO 2 -> onboard NeoPixel power enable pin
• ESP32 GPIO 14 -> touch input jumper wire (TouchPad input used for touch sensing)
• ESP32 GPIO 27 -> external pushbutton input
• Pushbutton other terminal -> 3.3V
• Internal pull-down resistor is enabled in software for GPIO 27
• Common board ground is provided by the ESP32 board itself
• Wi-Fi connection used: 


Video Link:
YOUTUBE: https://youtu.be/2Bq30xneQ78?si=yc0Qzbk2YgSRNAME
Google drive: https://drive.google.com/file/d/1LErepaffAWInGU7xkoeD3o1NiY-GYu6o/view?usp=sharing


Program Behavior Flow:

START
  |
  v
Board powers on / wakes from deep sleep
  |
  v
Check wake-up reason
  |----> If EXT0 wake --> print "Woke up due to EXT0 wakeup."
  |----> If timer wake -> print "Woke up due to timer wakeup."
  |----> Else ---------> normal first boot
  |
  v
Turn RED LED ON
Turn NeoPixel OFF
Enable EXT0 wake on external switch
  |
  v
Connect to Wi-Fi
  |
  v
Print connected SSID and IP address
  |
  v
Get current time from pool.ntp.org
Set RTC and adjust to West Lafayette local time
  |
  v
Start Timer 1: every 15 s -> print Date and Time
Start Timer 2: every 50 ms -> read touch pin
                                |
                                |----> if touched -> NeoPixel GREEN
                                |----> if not touched -> NeoPixel OFF
  |
  v
Remain awake for 30 seconds
  |
  v
Print "I am going to sleep for 1 minute."
Turn RED LED OFF
Turn NeoPixel OFF
Timers off
Enter deep sleep for 60 seconds
  |
  v
During sleep:
  |----> If switch pressed -> EXT0 wake-up
  |----> If 1 minute expires -> timer wake-up
  |
  v
Board resets from deep sleep and starts program again
  |
  v
REPEAT
