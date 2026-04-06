Hardware Connection:
ESP32 GPIO 13 --> LED Anode

YOUTUBE LINK: https://youtu.be/fHXTF8N93n8
GOOGLE DRIVE: https://drive.google.com/file/d/1BLE5qFYt84k83WVKORKm58mnNljl45IH/view?usp=sharing



1) espclient.py explained

	This file is the HTTP client. Its job is:
	--	connect to Wi-Fi
	--	read the ESP32 sensors
	--	every 30 seconds, send the data to ThingSpeak
	--	stop after 5 minutes
		
		
	network lets the ESP32 connect to Wi-Fi.
	socket lets the ESP32 create a network connection and send an HTTP request.
	time is used for delays and measuring elapsed time.
	esp32 gives access to ESP32-specific functions like temperature and hall sensor reading.
	Timer creates a hardware timer that fires repeatedly every 30 seconds.
	
	    request = (
        "GET /update?api_key={}&field1={}&field2={} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(THINGSPEAK_WRITE_API_KEY, temp_f, hall, host)
	
	----creates an HTTP GET request. Meaning:
		/update is the ThingSpeak endpoint
		api_key=... tells ThingSpeak which channel to write to
		field1=... carries the temperature
		field2=... carries the hall sensor value
		Host: is a normal HTTP header
		Connection: close says the server can close the connection after replying
		the blank line \r\n ends the HTTP headers
		
	s = socket.socket()
    try:
        s.connect(addr)
        s.send(request.encode())
	----Meaning: 
		socket.socket() creates a TCP socket.
		s.connect(addr) connects to ThingSpeak.
		s.send(request.encode()) sends the HTTP request as bytes.
		
	response = b""
    while True:
        data = s.recv(256)
        if not data:
            break
        response += data
	
		----This reads the response back from the server.

			response = b"" starts with empty bytes.
			s.recv(256) reads up to 256 bytes at a time.
			if no more data comes, the loop ends.
			otherwise it appends the data to response
			
    print("ThingSpeak response:")
    try:
        print(response.decode())
    except:
         print(response)
		 
		----This prints the server response.
			response.decode() converts bytes to text
			if decoding fails, it just prints the raw bytes
	finally:
        s.close()
		    finally:
        ----This closes the socket no matter what happened. That is good practice.
	
	def main():
	    timer = Timer(0)
		timer.init(period=30000, mode=Timer.PERIODIC, callback=timer_callback)
		
		---- This starts the hardware timer.
				Timer(0) creates timer number 0.
				period=30000 means 30,000 milliseconds = 30 seconds.
				mode=Timer.PERIODIC means it repeats over and over.
				callback=timer_callback says which function to run every time it fires.
				
		try:
			while time.time() - start_time < 300:
				if upload_flag:
					upload_flag = False
					temp_f, hall = read_sensors()
					print("Temperature (F):", temp_f)
					print("Hall Sensor:", hall)
					send_to_thingspeak(temp_f, hall)
				time.sleep_ms(100)
				
		---- This is the heart of the client.

			while time.time() - start_time < 300: means run until 300 seconds = 5 minutes have passed.
			if upload_flag: checks whether the timer requested an upload.
			upload_flag = False resets the flag so it won’t upload again immediately.
			temp_f, hall = read_sensors() gets the new measurements.
			the two print(...) lines show the current readings in the terminal.
			send_to_thingspeak(temp_f, hall) uploads them.
			time.sleep_ms(100) gives a short 100 ms pause so the loop does not spin too fast.
			
		if __name__ == "__main__":
			main()
			---- This means: if the file is run directly, start the program by calling main()