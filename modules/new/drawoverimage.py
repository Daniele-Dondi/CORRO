import tkinter as tk
from PIL import Image, ImageTk

class DrawApp:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Draw & Manage 7-segments reading zones")
        
        # Carica sfondo
        pil_img = Image.open(image_path)
        self.bg_width, self.bg_height = pil_img.size
        self.bg_image = ImageTk.PhotoImage(pil_img)
        
        # Canvas
        self.canvas = tk.Canvas(root, 
                                width=self.bg_width, 
                                height=self.bg_height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.bg_image, anchor='nw')
        
        # Stato disegno
        self.start_x = None
        self.start_y = None
        self.current_shape = None
        
        # Elenco di tutti i rettangoli
        self.rectangles = []
        # Rettangolo attualmente selezionato
        self.selected_rect = None

        
        # Toolbar
        toolbar = tk.Frame(root)
        tk.Button(toolbar, text="Elimina selezionato", command=self.delete_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="X+ SKEW", command=self.skew_plus_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="X- SKEW", command=self.skew_minus_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="X+ SIZE", command=self.x_plus_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="X- SIZE", command=self.x_minus_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="Y+ SIZE", command=self.y_plus_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="Y- SIZE", command=self.y_minus_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="X+ POS", command=self.x_plus_pos_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="X- POS", command=self.x_minus_pos_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="Y+ POS", command=self.y_plus_pos_selected).pack(side='left', padx=5)
        tk.Button(toolbar, text="Y- POS", command=self.y_minus_pos_selected).pack(side='left', padx=5)
        
        self.Displacement = tk.Spinbox(toolbar, from_=1, to=10, width=10, relief="sunken", repeatdelay=500, repeatinterval=100)
        self.Displacement.pack()       
        toolbar.pack(anchor='nw', pady=5)
        
        # Bind eventi mouse
        self.canvas.bind("<ButtonPress-1>",    self.on_button_press)
        self.canvas.bind("<B1-Motion>",        self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>",  self.on_button_release)
        # Click per selezione
        self.canvas.tag_bind("rectangle", "<Button-1>", self.on_select)

    def on_button_press(self, event):
        # Inizia un nuovo rettangolo
        self.start_x, self.start_y = event.x, event.y
        self.current_shape =self.canvas.create_polygon(self.start_x, self.start_y,self.start_x, self.start_y,self.start_x, self.start_y,self.start_x, self.start_y,outline='red', width=4, tags="rectangle", fill="")
        # Aggiungo alla lista
        self.rectangles.append(self.current_shape)

    def on_move_press(self, event):
        # Aggiorna coordinate del rettangolo in corso
        if not self.current_shape: 
            return
        self.canvas.coords(self.current_shape,self.start_x, self.start_y, event.x, self.start_y, event.x, event.y,self.start_x,event.y)

    def on_button_release(self, event):
        # Fine disegno
        self.current_shape = None
        self.start_x = None
        self.start_y = None

    def on_select(self, event):
        # Seleziono il rettangolo cliccato
        # 'current' restituisce l’ID dell’oggetto sotto il cursore
        clicked = self.canvas.find_withtag("current")[0]
        
        # Deseleziono precedente (se presente)
        if self.selected_rect:
            self.canvas.itemconfig(self.selected_rect, dash=())
        
        # Seleziono il nuovo e ne cambio lo stile
        self.selected_rect = clicked
        self.canvas.itemconfig(self.selected_rect, dash=(4,2))

    def skew_plus_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if num==0 or num==2:
                points[num]+=int(self.Displacement.get())
            if num==4 or num==6:
                points[num]-=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def skew_minus_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if num==0 or num==2:
                points[num]-=int(self.Displacement.get())
            if num==4 or num==6:
                points[num]+=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)        

    def x_plus_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if num==2 or num==4:
                points[num]+=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def x_minus_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if num==2 or num==4:
                points[num]-=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def y_plus_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if num==5 or num==7:
                points[num]+=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def y_minus_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if num==5 or num==7:
                points[num]-=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def x_plus_pos_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if num % 2==0:
                points[num]+=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def x_minus_pos_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if num % 2==0:
                points[num]-=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def y_plus_pos_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if not(num % 2==0):
                points[num]+=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def y_minus_pos_selected(self):
        if not self.selected_rect:
            return
        points=self.canvas.coords(self.selected_rect)
        for num in range(len(points)):
            if not(num % 2==0):
                points[num]-=int(self.Displacement.get())
        self.canvas.coords(self.selected_rect,points)

    def delete_selected(self):
        if not self.selected_rect:
            return
        # Rimuovo dal Canvas
        self.canvas.delete(self.selected_rect)
        # Rimuovo dalla lista
        self.rectangles.remove(self.selected_rect)
        # Reset selezione
        self.selected_rect = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawApp(root, "display.jpg")  # Sostituisci con il tuo file
    root.mainloop()
