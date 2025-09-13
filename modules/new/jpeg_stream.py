from PIL import Image, ImageTk
import urllib.request
import io

class JPEGPreviewer:
    def __init__(self, root, container):
        self.root = root
        self.container = container
        self.image_label = None
        self.running = False
        self.url = ""
        self.refresh_interval = 1000  # milliseconds

    def start(self, url):
        if not url.startswith("http"):
            messagebox.showerror("ERROR", "Invalid image URL")
            return

        self.url = url
        self.running = True

        # Clear previous content
        for widget in self.container.winfo_children():
            widget.destroy()

        self.image_label = ttk.Label(self.container)
        self.image_label.pack()

        self._update_image()

    def stop(self):
        self.running = False

    def _update_image(self):
        if not self.running:
            return

        try:
            with urllib.request.urlopen(self.url) as u:
                raw_data = u.read()
            im = Image.open(io.BytesIO(raw_data))
            im = im.resize((640, 360))
            photo = ImageTk.PhotoImage(im)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception as e:
            print("Error loading image:", e)

        self.root.after(self.refresh_interval, self._update_image)

# Inside your CameraConfigurator class
def setup_preview_controls(self):
    self.jpeg_frame = ttk.Frame(self.tabCamera)
    self.jpeg_frame.pack(pady=10)

    self.preview = JPEGPreviewer(self.root, self.jpeg_frame)

    ttk.Button(self.jpeg_frame, text="Start Preview", command=lambda: self.preview.start(self.CameraStreamURL.get())).pack(side="left")
    ttk.Button(self.jpeg_frame, text="Stop Preview", command=self.preview.stop).pack(side="left")
