import requests
import time

def TurnPlugON(SHELLY_IP):
    BASE_URL = f"http://{SHELLY_IP}/relay/0" 
    try:
        response = requests.get(f"{BASE_URL}?turn=on", timeout=5)
        response.raise_for_status()  # Raises exception for HTTP errors
        return "Plug turned ON:"+response.text
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out. Shelly plug may be unreachable."
    except requests.exceptions.ConnectionError:
        return "ERROR: Connection error. Check the IP or network."
    except requests.exceptions.HTTPError as err:
        return f"ERROR: HTTP error: {err}"
    except Exception as e:
        return f"ERROR: Unexpected error: {e}"

def TurnPlugOFF(SHELLY_IP):
    BASE_URL = f"http://{SHELLY_IP}/relay/0"     
    try:
        response = requests.get(f"{BASE_URL}?turn=off", timeout=5)
        response.raise_for_status()
        return "Plug turned OFF:", response.text
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out. Shelly plug may be unreachable."
    except requests.exceptions.ConnectionError:
        return "ERROR: Connection error. Check the IP or network."
    except requests.exceptions.HTTPError as err:
        return f"ERROR: HTTP error: {err}"
    except Exception as e:
        return f"ERROR: Unexpected error: {e}"


# Example usage
print("waiting")
time.sleep(5)
response=TurnPlugON("10.163.42.152")
print(response)
time.sleep(5)
response=TurnPlugOFF("10.163.42.152")
print(response)
