from tkinter import *
from tkinter.ttk import *
from profile import *

class ProfileTk(Profile):
    def __init__(self, **kwargs):
        Profile.__init__(self, **kwargs)

    def canvas_draw(self, parent, x0=0, y0=100, scale=10, **common):
        def arc(parent, center, radius, start, extent, **common):
            parent.create_arc((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius),
                start=start, extent=extent, style=ARC, **common)
        
        self.calculate_profile()
        d = []
        x = x0-self.width/2
        y = y0
        
        # Scale profile parameters
        b = [x*scale for x in self.b]
        h1, h2, h3, w1, w2, w3, r1, r3 = (x*scale for x in (self.h1, self.h2, self.h3,
                                                            self.w1, self.w2, self.w3,
                                                            self.r1, self.r3))
        
        # Left edge segment B0 (horizontal)
        if b[0] > 0:
            x1 = x + b[0]
            parent.create_line([(x, y), (x1, y)], tag='b0', **common)
            x = x1
        
        for j in range(self.waves):
            # Segment B1 (arc)
            if b[1] > 0:
                arc(parent, center=(x, y+r1), radius=r1,
                    start=90, extent=-self.angle_deg, tag='b1', **common)
                x += w1
                y += h1

            # Segment B2 (inclined)
            if b[2] > 0:
                x1 = x + w2
                y1 = y + h2
                parent.create_line([(x, y), (x1, y1)], tag='b2', **common)
                x = x1
                y = y1

            # Segment B3 (arc)
            if b[3] > 0:
                x1 = x + w3
                y1 = y + h3
                arc(parent, center=(x1, y1-r1), radius=r1,
                    start=270, extent=-self.angle_deg, tag='b3', **common)
                x = x1
                y = y1

            # Segment B4 (horizontal)
            if b[4] > 0:
                x1 = x + b[4]
                parent.create_line([(x, y), (x1, y)], tag='b4', **common)
                x = x1

            # Symmetrically against B4 segment
            # Segment B3 (arc)
            if b[3] > 0:
                x1 = x + w3
                y1 = y - h3
                arc(parent, center=(x, y-r1), radius=r1,
                    start=270, extent=self.angle_deg, tag='b3', **common)
                x = x1
                y = y1

            # Segment B2 (inclined)
            if b[2] > 0:
                x1 = x + w2
                y1 = y - h2
                parent.create_line([(x, y), (x1, y1)], tag='b2', **common)
                x = x1
                y = y1

            # Segment B1 (arc)
            if b[1] > 0:
                x1 = x + w1
                y1 = y - h1
                arc(parent, center=(x1, y1+r1), radius=r1,
                    start=90, extent=self.angle_deg, tag='b1', **common)
                x = x1
                y = y1

            # Segment B5 (horizontal)
            if j < self.waves-1 and b[5] > 0:
                x1 = x + b[5]
                parent.create_line([(x, y), (x1, y)], tag='b5', **common)
                x = x1

        # Right edge segment B0
        if b[0] > 0:
            x1 = x + b[0]
            parent.create_line([(x, y), (x1, y)], tag='b0', **common)


class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        sidebarFrame = Frame(self, width=160)
        canvasFrame = Frame(self, width=640, height=480)
        sidebarFrame.pack(side='left', fill='y')
        canvasFrame.pack(side='right', fill='both', expand=1)
        
        self._init_canvas(canvasFrame)
        self._init_main_menu()
        self._init_labels_and_text_boxes(sidebarFrame)
        
        profile = ProfileTk(b=[20, 20, 20, 20, 20, 20], waves=4, angle_deg=60)
        profile.canvas_draw(self.canvas, width=2)
        self.canvas.itemconfig('b4', fill='yellow')
    
    def _init_canvas(self, parent):
        self.canvas = Canvas(parent, width=640, height=480, bg="white")
        # self.imgobj = self.canvas.create_image(0, 0)
        self.canvas.pack(side='top', fill='both', expand=1)
    
    def _init_main_menu(self):
        main_menu = Menu(self)
        self.config(menu=main_menu)
        file_menu = Menu(main_menu)
        main_menu.add_cascade(label="File", menu=file_menu)
        # file_menu.add_command(label="Open", command=self.show_img)
        # file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        
    def _init_labels_and_text_boxes(self, parent):
        # Create labels and text boxes for b-parameters
        self.entry_b = []
        row = 1
        
        label = Label(parent, text='Длины участков:')
        label.grid(row=row, column=1, columnspan=2)
        row += 1
        
        for i in range(6):
            label = Label(parent, text='B%d =' % i)
            label.grid(row=row, column=1)
            self.entry_b.append(Entry(parent))
            self.entry_b[-1].grid(row=row, column=2)
            row += 1
        
        row += 1
        
        label = Label(parent, text='Количество волн:')
        label.grid(row=row, column=1, columnspan=2)
        row += 1
        label = Label(parent, text='N =')
        label.grid(row=row, column=1)
        self.entry_waves = Entry(parent)
        self.entry_waves.grid(row=row, column=2)
        
        row += 1
        
        label = Label(parent, text='Количество клетей:')
        label.grid(row=row, column=1, columnspan=2)
        row += 1
        label = Label(parent, text='M =')
        label.grid(row=row, column=1)
        self.entry_m = Entry(parent)
        self.entry_m.grid(row=row, column=2)
        
        row += 1
        
        label = Label(parent, text='Начальный угол:')
        label.grid(row=row, column=1, columnspan=2)
        row += 1
        label = Label(parent, text='Amin =')
        label.grid(row=row, column=1)
        self.entry_amin = Entry(parent)
        self.entry_amin.grid(row=row, column=2)
        
        row += 1
        
        label = Label(parent, text='Конечный угол:')
        label.grid(row=row, column=1, columnspan=2)
        row += 1
        label = Label(parent, text='Amax =')
        label.grid(row=row, column=1)
        self.entry_amax = Entry(parent)
        self.entry_amax.grid(row=row, column=2)

app = App()
app.mainloop()
