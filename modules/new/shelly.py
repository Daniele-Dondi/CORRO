import requests
import time

# Replace with your Shelly device's local IP
SHELLY_IP = "10.163.42.152"  # example IP
BASE_URL = f"http://{SHELLY_IP}/relay/0"

##def turn_on():
##    response = requests.get(f"{BASE_URL}?turn=on")
##    print("Turned ON:", response.status_code, response.text)
##
##def turn_off():
##    response = requests.get(f"{BASE_URL}?turn=off")
##    print("Turned OFF:", response.status_code, response.text)

def turn_on():
    try:
        response = requests.get(f"{BASE_URL}?turn=on", timeout=5)
        response.raise_for_status()  # Raises exception for HTTP errors
        print("Plug turned ON:", response.text)
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out. Shelly plug may be unreachable.")
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection error. Check the IP or network.")
    except requests.exceptions.HTTPError as err:
        print(f"ERROR: HTTP error: {err}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")

def turn_off():
    try:
        response = requests.get(f"{BASE_URL}?turn=off", timeout=5)
        response.raise_for_status()
        print("Plug turned OFF:", response.text)
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out. Shelly plug may be unreachable.")
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection error. Check the IP or network.")
    except requests.exceptions.HTTPError as err:
        print(f"ERROR: HTTP error: {err}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")


# Example usage
print("waiting")
time.sleep(5)
turn_on()
time.sleep(5)
turn_off()
