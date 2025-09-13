##import http.client
##from urllib.parse import urlparse
##from html.parser import HTMLParser
##
##def fetch_ip_camera_image(camera_url):
##    class ImageParser(HTMLParser):
##        def __init__(self):
##            super().__init__()
##            self.image_src = None
##
##        def handle_starttag(self, tag, attrs):
##            if tag == "img":
##                for attr, value in attrs:
##                    if attr == "src":
##                        self.image_src = value
##
##    try:
##        # Parse the camera URL
##        parsed = urlparse(camera_url)
##        host = parsed.hostname
##        snapshot_path = parsed.path
##
##        # Fetch the HTML page
##        conn = http.client.HTTPConnection(host,timeout=5)
##        conn.request("GET", snapshot_path)
##        response = conn.getresponse()
##        if response.status != 200:
##            return f"Error: Failed to fetch HTML ({response.status} {response.reason})"
##        html = response.read().decode()
##        conn.close()
##
##        # Parse HTML to find image path
##        parser = ImageParser()
##        parser.feed(html)
##        if not parser.image_src:
##            return "Error: No image tag found in HTML."
##
##        image_path = parser.image_src
##        if not image_path.startswith("/"):
##            image_path = "/" + image_path
##
##        # Fetch the image
##        conn = http.client.HTTPConnection(host)
##        conn.request("GET", image_path)
##        response = conn.getresponse()
##        if response.status != 200:
##            return f"Error: Failed to fetch image ({response.status} {response.reason})"
##        image_data = response.read()
##        conn.close()
##
##        return image_data  # Return raw image bytes
##
##    except Exception as e:
##        return f"Error: {str(e)}"
##
###EXAMPLE USAGE
##camera_url = "http://192.168.1.100/snapshot.html"
##result = fetch_ip_camera_image(camera_url)
##
##if isinstance(result, bytes):
##    with open("snapshot.jpg", "wb") as f:
##        f.write(result)
##    print("Image saved successfully.")
##else:
##    print(result)  # This is an error message

#############
##import requests
##from urllib.parse import urlparse, urljoin
##from html.parser import HTMLParser
##
##def fetch_ip_camera_image(camera_url):
##    class ImageParser(HTMLParser):
##        def __init__(self):
##            super().__init__()
##            self.image_src = None
##
##        def handle_starttag(self, tag, attrs):
##            if tag == "img":
##                for attr, value in attrs:
##                    if attr == "src":
##                        self.image_src = value
##
##    try:
##        # Fetch the HTML page
##        headers = {"User-Agent": "Mozilla/5.0"}
##        response = requests.get(camera_url, headers=headers, timeout=5)
##        response.raise_for_status()
##        html = response.text
##
##        # Parse HTML to find image path
##        parser = ImageParser()
##        parser.feed(html)
##        if not parser.image_src:
##            return "Error: No image tag found in HTML."
##
##        # Resolve full image URL
##        image_url = urljoin(camera_url, parser.image_src)
##
##        # Fetch the image
##        image_response = requests.get(image_url, headers=headers, timeout=5)
##        image_response.raise_for_status()
##
##        return image_response.content  # Return raw image bytes
##
##    except requests.exceptions.RequestException as e:
##        return f"Error: {str(e)}"
##
##camera_url = "http://192.168.1.100/snapshot.html"
##result = fetch_ip_camera_image(camera_url)
##
##if isinstance(result, bytes):
##    with open("snapshot.jpg", "wb") as f:
##        f.write(result)
##    print("Image saved successfully.")
##else:
##    print(result)  # Error message


import requests
from datetime import datetime

def GeneratePictureFileName():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def fetch_ip_camera_image(camera_ip, save_path=""):
    """
    Fetches a JPEG image from the ESP32-CAM and saves it to disk.

    Parameters:
        camera_ip (str): IP to the camera image endpoint (e.g., 192.168.1.45)
        save_path (str): Path to save the image file. If empty, a timestamped filename is generated.

    Returns:
        str: The path where the image was saved, or None if failed.
    """
    if not save_path:
        timestamp = GeneratePictureFileName()
        save_path = f"snapshot_{timestamp}.jpg"
        
    camera_url=f"http://{camera_ip}/cam.jpg"

    try:
        response = requests.get(camera_url, timeout=5)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            print(f"Image saved to {save_path}")
            return save_path
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to camera: {e}")
        return None
