from machine import Pin, PWM, ADC, RTC, Timer
import utime

# =======================
# USER CONFIG
# =======================
# Assign ESP32 resources to the components.
POT_GPIO_PIN = 36
LED_GPIO_PIN = 12
BUTTON_GPIO_PIN = 38


# =======================
# GLOBALS / STATE
# =======================
rtc = RTC()

"""
Control mode:
-1 	= default mode
0 	= pot controls frequency
1 	= pot controls duty
"""
mode = -1

# Switch Debounce state
debouncing = False

# Latest ADC reading from the POT
pot_raw = 0

"""
PWM settings
"""
#Initialize PWM
PWM_MIN_freq = 1
PWM_MAX_freq = 20
PWM_MIN_DUTY = 0
PWM_MAX_DUTY = 1023

# Default PWM state
pwm_freq = 10 # in Hz
pwm_duty = 512

# Timers
tim_rtc_print = Timer(0)
tim_adc_read  = Timer(1)
tim_debounce  = Timer(2)

# =======================
# INITIALIZE HARDWARE
# =======================

pwm = PWM(Pin(LED_GPIO_PIN), freq=pwm_freq, duty=pwm_duty)

# ADC to get input from Potentiometer.
adc = ADC(Pin(POT_GPIO_PIN, Pin.IN))

# ADC default difinition.
adc.atten(ADC.ATTN_11DB) # use 0-3.3V
adc.width(ADC.WIDTH_12BIT) # 0 to 4095

# Button control input.
button = Pin(BUTTON_GPIO_PIN, Pin.IN, Pin.PULL_UP)


# =======================
# HELPER FUNCTIONS
# =======================
def clamp(x, lo, hi):
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x

"""
Do integer division and linear scaling to convert
the POT values to frequency or duty cycle.
"""
def map_range(x, in_min, in_max, out_min, out_max):
    # avoid division by zero
    if in_max == in_min:
        return out_min
    return out_min + (x - in_min) * (out_max - out_min) // (in_max - in_min)

def print_datetime(temp=None):
    # rtc.datetime() => (year, month, day, weekday, hours, minutes, seconds, subseconds)
    dt = rtc.datetime()
    year, month, day, weekday, hour, minute, second, subsec = dt

    # Print date and time in Integer form.
    print("DATE: {:04d}-{:02d}-{:02d}  (weekday={})".format(year, month, day, weekday))
    print("TIME: {:02d}:{:02d}:{:02d}".format(hour, minute, second))


"""
Set PWM frequency and duty cycle. 
"""
def set_pwm_freq(new_Freq):
    global pwm_freq
    new_Freq = int(clamp(new_Freq, PWM_MIN_freq, PWM_MAX_freq))
    if new_Freq != pwm_freq:
        pwm_freq = new_Freq
        pwm.freq(pwm_freq)

def set_pwm_duty(new_duty):
    global pwm_duty
    new_duty = int(clamp(new_duty, PWM_MIN_DUTY, PWM_MAX_DUTY))
    if new_duty != pwm_duty:
        pwm_duty = new_duty
        pwm.duty(pwm_duty)


# =======================
# TIMER CALLBACKS
# =======================
def adc_timer_cb(temp):
    """
    Runs every 100 ms.
    Reads potentiometer and updates either frequency or duty depending on mode.
    """
    global pot_raw, mode

    pot_raw = adc.read()  # 0..4095

    if mode == 0:
        # pot controls frequency: map 0..4095 -> PWM_MIN_HZ..PWM_MAX_HZ
        freq = map_range(pot_raw, 0, 4095, PWM_MIN_freq, PWM_MAX_freq)
        set_pwm_freq(freq)
        # intensity unchanged in this mode
    elif mode == 1:
        # pot controls duty: map 0..4095 -> 0..1023
        duty = map_range(pot_raw, 0, 4095, PWM_MIN_DUTY, PWM_MAX_DUTY)
        set_pwm_duty(duty)
        # frequency unchanged in this mode

"""
Called once after debounce delay, re-enables button handling.
"""
def debounce_done_cb(temp):
    global debouncing
    debouncing = False

# =======================
# BUTTON IRQ
# =======================
def button_irq(pin):
    """
    We do a timer-based debounce and flip mode.
    """
    global mode, debouncing

    if debouncing:
        return

    # Start debouncing
    debouncing = True
    # Toggle mode

    if mode == -1:
        mode = 0
        print("MODE: Pot controls PWM FREQUENCY (Hz). Duty fixed at {}".format(pwm_duty))
    elif mode == 0:
        mode = 1
        print("MODE: Pot controls PWM DUTY. Frequency fixed at {} Hz".format(pwm_freq))
    else:
        mode = 0
        print("MODE: Pot controls PWM FREQUENCY (Hz). Duty fixed at {}".format(pwm_duty))
        
    # debounce delay ~200ms using one-shot timer
    tim_debounce.init(period=200, mode=Timer.ONE_SHOT, callback=debounce_done_cb)

# Attach interrupt (falling edge typical for pull-up buttons)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_irq)


# =======================
# USER INPUT and initialization
# =======================
def RTC_Init_User_Input():
    print("Enter current date/time in EDT (weekdays: 0=Mon, 1 = Tue, 2 = Wed,.... 6=Sun)")
    year = int(input("Year? "))
    month = int(input("Month? "))
    day = int(input("Day? "))
    weekday = int(input("Weekday? "))
    hour = int(input("Hour? "))
    minute = int(input("Minute? "))
    second = int(input("Second? "))
    microsecond = int(input("Microsecond? "))

    # tuple : Set RTC.datetime(year, month, day, weekday, hour, minute, second, subseconds)
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0))

    print("RTC initialized.")
    print_datetime()

# =======================
# MAIN Function
# =======================

### Initialize Date time.
RTC_Init_User_Input()


print("Starting PWM @ {} Hz, duty {} (about 50%).".format(pwm_freq , pwm_duty))
print("Printing date/time every 30 seconds. Reading pot every 100 ms.")
print("Press the button to toggle control between frequency control or  dutycycle control.\n")

# Start periodic timers
tim_rtc_print.init(period=30000, mode=Timer.PERIODIC, callback=print_datetime)
tim_adc_read.init(period=100, mode=Timer.PERIODIC, callback=adc_timer_cb)

while True:
    utime.sleep_ms(50)