						ECE 56800: Embedded Systems
							Spring 2026

PROJECT# Lab 2 – LED control using ADC, PWM, Timers and Interrupts

Microcontroller board: ADAFRUIT ESP32
Power:3V
Default frequency: 10 Hz
Default Duty cycle: 512 (~50%)

PWM frequency range: 1 to 20 Hz
PWM Duty Cycle range: 0 to 1023.

Connections:
	ESP32 GPIO 36 --> Potentiometer OUTPUT
	ESP32 3V -->  Potentiometer VCC
	ESP32 GND --> Potentiometer GND
	ESP32 GPIO 38 --> SW38 on-board push Button
	ESP32 GPIO 12 --> 1k ohm resistor --> LED anode
 	LED Cathode --> ESP32 GND

DEMO VIDEO LINK: 
DEMO VIDEO LINK: 
YOUTUBE: https://youtu.be/bdQY1Nj-kdI?si=1sH-HrkyCtkdK87l

Google Drive: https://drive.google.com/file/d/1Ax3-ncE2lOYHhZ6qJfbcIpFDfXrfRUIk/view?usp=sharing


Overall block diagram:



                    ┌────────────────────┐
                    │   		START            │ 
                    │    						 │
                    └──────────┬─────────┘
				   ▼
                    ┌────────────────────┐
                    │   RTC_Init_User_Input		 │
                    │  rtc.datetime(...)   		 │
                    │  print_datetime()    		 │
                    └──────────┬─────────┘
                               	   │
                                   ▼
                 ┌───────────────────────────────┐
                 │      USER ENTERS DATE/TIME   			 |
                 │  Year, Month, Day, Weekday,  			 |
                 │  Hour, Minute, Second, etc.  			 |
                 └──────────────┬────────────────┘
                                     ▼
        ┌─────────────────────────────────────────────────┐
        │            INITIAL HARDWARE SETUP                					│
        │                                                  					│
        │  PWM  -> LED on GPIO12                           					│
        │  ADC  -> Potentiometer on GPIO36                 					│
        │  Button -> Pushbutton on GPIO38                  					│
        │  Timers -> RTC print / ADC read / debounce       					│
        └───────────────┬─────────────────────────────────┘
                              │
                              ▼
          ┌────────────────────────────┐
          │   START DEFAULT LED PWM OUTPUT      │
          │   Frequency = 10 Hz                 │
          │   Duty      = 512 (50%)             │
          │   mode = -1  (pot disabled)         │
          └──────────────┬─────────────┘
                               │
                         ▼
       ┌───────────────────────────────────┐
       │               TIMER STARTUP                   │
       │                                               │
       │ tim_rtc_print  -> every 30 s -> print time    │
       │ tim_adc_read   -> every 100 ms -> read pot    │
       │ button irq     -> on press -> change mode     │
       └───────────────┬───────────────────┘
                       │
                       ▼
              ┌──────────────────────┐
              │   MAIN LOOP FOREVER  		│
              │   sleep_ms(50)       		│
              │   all real work done 		│
              │   by timers/IRQ      		│
              └──────────────────────┘
