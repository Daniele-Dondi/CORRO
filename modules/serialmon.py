import tkinter as tk
from tkinter import messagebox
import serial
import threading

class SerialMon():
    def __init__(self, root,Port,BaudRate):
        #self.root = root
        self.root =tk.Toplevel(root)
        self.root.grab_set()
        self.root.title("Serial Communication")
        try:
            self.serial_port = serial.Serial(Port,BaudRate, timeout=1)
        except:
            messagebox.showerror("ERROR", "Could not connect")
            return
        self.receive_label = tk.Label(self.root, text="Received Data:")
        self.receive_label.pack()        
        self.receive_text = tk.Text(self.root, height=10, width=50)
        self.receive_text.pack()
        self.F=tk.Frame(self.root)
        self.F.pack()
        self.send_entry = tk.Entry(self.F)
        self.send_entry.pack(side="left")
        self.send_button = tk.Button(self.F, text="Send", command=self.send_data)
        self.send_button.pack()
        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.destroy)
        self.exit_button.pack()
        self.read_thread = threading.Thread(target=self.read_data)
        self.read_thread.daemon = True
        self.read_thread.start()

    def send_data(self):
        data = self.send_entry.get()
        if data:
            self.serial_port.write(data.encode())
            self.send_entry.delete(0, tk.END)

    def read_data(self):
        while True:
            if not self.root.winfo_exists():
                # window no longer exists; break out of loop
                break
            if self.serial_port.in_waiting > 0:
                data = self.serial_port.readline().decode().strip()
                self.receive_text.insert(tk.END, data + '\n')
                self.receive_text.see(tk.END)

##if __name__ == "__main__":
##    root = tk.Tk()
##    app = SerialMon(root,'COM1', 9600)
##    root.mainloop()
