import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

class IPCameraViewer:
    def __init__(self, parent, camera_ip, update_interval=1000):
        self.parent = parent
        self.camera_url = f"http://{camera_ip}/cam.jpg"
        self.update_interval = update_interval

        self.label = tk.Label(self.parent)
        self.label.pack()

        self.update_image()

    def fetch_image(self):
        try:
            response = requests.get(self.camera_url, timeout=2)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print("Error fetching image:", e)
            return None

    def update_image(self):
        img_tk = self.fetch_image()
        if img_tk:
            self.label.config(image=img_tk)
            self.label.image = img_tk
        self.parent.after(self.update_interval, self.update_image)


def open_camera_popup(event=None):
    popup = tk.Toplevel(root)
    popup.title("Camera Stream")
    viewer = IPCameraViewer(popup, "10.163.60.35")

#example usage
##root = tk.Tk()
##root.title("Main Window")
##
### Bind left mouse click to open the popup
##root.bind("<Button-1>", open_camera_popup)
##
##label = tk.Label(root, text="Click anywhere to open camera stream")
##label.pack(padx=20, pady=20)
##
##root.mainloop()
