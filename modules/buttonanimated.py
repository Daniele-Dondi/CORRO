import tkinter as tk
from PIL import Image, ImageTk

class AnimatedButton:
    def __init__(self, master, gif_path, delay=100, **kwargs):
        self.master = master
        self.gif_path = gif_path
        self.delay = delay
        self.frames = []
        self.index = 0

        self._load_frames()
        self.button = tk.Button(master, image=self.frames[0], **kwargs)
        self.button.pack()

        self._animate()

    def _load_frames(self):
        gif = Image.open(self.gif_path)
        try:
            while True:
                frame = ImageTk.PhotoImage(gif.copy())
                self.frames.append(frame)
                gif.seek(len(self.frames))  # Next frame
        except EOFError:
            pass  # All frames loaded

    def _animate(self):
        self.button.config(image=self.frames[self.index])
        self.index = (self.index + 1) % len(self.frames)
        self.master.after(self.delay, self._animate)

##    def pack(self, **kwargs):
##        self.button.pack(**kwargs)
##
##    def grid(self, **kwargs):
##        self.button.grid(**kwargs)
##
##    def place(self, **kwargs):
##        self.button.place(**kwargs)
##
##root = tk.Tk()
##animated_btn = AnimatedButton(root, "run.gif", delay=100)
##root.mainloop()
