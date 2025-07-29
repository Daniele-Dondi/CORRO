import requests
import time

# Replace with your Shelly device's local IP
SHELLY_IP = "10.163.42.152"  # example IP
BASE_URL = f"http://{SHELLY_IP}/relay/0"

def turn_on():
    response = requests.get(f"{BASE_URL}?turn=on")
    print("Turned ON:", response.status_code, response.text)

def turn_off():
    response = requests.get(f"{BASE_URL}?turn=off")
    print("Turned OFF:", response.status_code, response.text)

# Example usage
print("waiting")
time.sleep(5)
turn_on()
time.sleep(5)
turn_off()
