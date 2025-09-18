import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
from io import BytesIO

class IPCameraViewer:
    def __init__(self, parent, camera_ip, update_interval=1000):
        self.parent = parent
        self.camera_url = f"http://{camera_ip}/cam.jpg"
        self.update_interval = update_interval

        self.label = tk.Label(self.parent)
        self.label.pack(expand=True, fill="both")

        self.update_image()

    def fetch_image(self):
        try:
            response = requests.get(self.camera_url, timeout=2)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print("Error fetching image:", e)
            # Create a gray image with text overlay
            img = Image.new("RGB", (320, 240), color="gray")
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()

            text = "Camera unreachable"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_position = ((img.width - text_width) // 2, (img.height - text_height) // 2)
            draw.text(text_position, text, fill="white", font=font)

            return ImageTk.PhotoImage(img)

    def update_image(self):
        img_tk = self.fetch_image()
        if img_tk:
            self.label.config(image=img_tk)
            self.label.image = img_tk
        self.parent.after(self.update_interval, self.update_image)



class CameraPopup:
    def __init__(self, camera_ip, title="Camera Stream"):
        self.popup = tk.Toplevel()
        self.popup.title(title)
        self.viewer = IPCameraViewer(self.popup, camera_ip)

root = tk.Tk()
root.withdraw()  # Hide root if you want only the popup
CameraPopup("10.163.60.35")
root.mainloop()
