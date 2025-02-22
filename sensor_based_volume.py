import subprocess
import time
import RPi.GPIO as GPIO

# GPIO setup for HC-SR04 sensor
TRIG = 17
ECHO = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Default zoom factor and limits
zoom_factor = 1.0  # Starting zoom factor
MAX_ZOOM_IN = 1.5  # Maximum zoom level
MAX_ZOOM_OUT = 1.0  # Minimum zoom level
ZOOM_STEP = 0.05  # The amount by which we zoom in or out each time

# Function to measure distance
def measure_distance():
    """Measure the distance using the HC-SR04 ultrasonic sensor."""
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    pulse_start = pulse_end = 0

    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()
    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound is 343 m/s, so multiply by 17150 to get cm
    return round(distance, 2)

# Function to increase volume
def volume_up():
    """Increase volume by executing the 'volumeup' action."""
    subprocess.run([ 
        "curl", "-s", "--data-binary", 
        '{ "jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action": "volumeup"}, "id": 1 }', 
        "-H", "Content-Type: application/json", 
        "-u", "kodi:Teamheureka17!", 
        "http://192.168.32.14:8080/jsonrpc" 
    ])

# Function to decrease volume
def volume_down():
    """Decrease volume by executing the 'volumedown' action."""
    subprocess.run([ 
        "curl", "-s", "--data-binary", 
        '{ "jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action": "volumedown"}, "id": 1 }', 
        "-H", "Content-Type: application/json", 
        "-u", "kodi:Teamheureka17!", 
        "http://192.168.32.14:8080/jsonrpc" 
    ])

# Function to zoom in
def zoom_in():
    """Zoom in by executing the 'zoomin' action."""
    subprocess.run([ 
        "curl", "-s", "--data-binary", 
        '{ "jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action": "zoomin"}, "id": 1 }', 
        "-H", "Content-Type: application/json", 
        "-u", "kodi:Teamheureka17!", 
        "http://192.168.32.14:8080/jsonrpc" 
    ])

# Function to zoom out
def zoom_out():
    """Zoom out by executing the 'zoomout' action."""
    subprocess.run([ 
        "curl", "-s", "--data-binary", 
        '{ "jsonrpc": "2.0", "method": "Input.ExecuteAction", "params": {"action": "zoomout"}, "id": 1 }', 
        "-H", "Content-Type: application/json", 
        "-u", "kodi:Teamheureka17!", 
        "http://192.168.32.14:8080/jsonrpc" 
    ])

# Function to reset zoom to default (1.0)
def reset_zoom():
    """Reset the zoom to 1.0."""
    subprocess.run([ 
        "curl", "-s", "--data-binary", 
        '{ "jsonrpc": "2.0", "method": "Player.SetZoom", "params": {"playerid": 1, "zoom": 1.0}, "id": 1 }', 
        "-H", "Content-Type: application/json", 
        "-u", "kodi:Teamheureka17!", 
        "http://192.168.32.14:8080/jsonrpc" 
    ])

# Function to set volume level based on distance
def set_volume_level(distance):
    """Set the volume based on the distance."""
    if distance < 50:
        print(f"Distance {distance} cm: Volume set to MAX")
        # Set volume to max by increasing it 10 times
        for _ in range(10):
            volume_up()
        time.sleep(0.5)  # Sleep to prevent rapid volume changes
    elif 50 <= distance <= 150:
        print(f"Distance {distance} cm: Volume set to MEDIUM")
        # Set volume to medium
        for _ in range(5):
            volume_up()  # Increase volume to a medium level
        time.sleep(0.5)
    else:
        print(f"Distance {distance} cm: Volume set to MIN")
        # Set volume to low by decreasing it 10 times
        for _ in range(10):
            volume_down()
        time.sleep(0.5)

# Function to set zoom level based on distance
def set_zoom_level(distance):
    global zoom_factor

    if distance < 50:
        print(f"Distance {distance} cm: Zooming in")
        # Zoom in, but do not exceed the max zoom factor
        if zoom_factor < MAX_ZOOM_IN:
            zoom_factor += ZOOM_STEP
            zoom_in()  # Apply zoom in action
        time.sleep(0.5)

    elif 50 <= distance <= 150:
        print(f"Distance {distance} cm: Zoom level remains the same")
        # No zoom change needed
        time.sleep(0.5)

    else:
        print(f"Distance {distance} cm: Zooming out")
        # Zoom out, but do not go below the min zoom factor
        if zoom_factor > MAX_ZOOM_OUT:
            zoom_factor -= ZOOM_STEP
            zoom_out()  # Apply zoom out action
        time.sleep(0.5)

# Main function
def main():
    """Continuously measure distance and adjust volume or zoom based on distance."""
    try:
        # Reset zoom to the starting value of 1.0
        reset_zoom()
        
        while True:
            distance = measure_distance()
            print(f"Measured Distance: {distance} cm")

            # Adjust volume based on the measured distance
            set_volume_level(distance)

            # Adjust zoom based on the measured distance
            set_zoom_level(distance)

            time.sleep(1)  # Wait before measuring distance again
    except KeyboardInterrupt:
        print("Exiting program.")
        GPIO.cleanup()  # Reset GPIO settings on exit

if __name__ == "__main__":
    main()
