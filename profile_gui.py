from tkinter import *
from tkinter.ttk import *
from profile import *

class ProfileTk(Profile):
    def __init__(self, **kwargs):
        Profile.__init__(self, **kwargs)

    def canvas_draw(self, parent):
        def arc(parent, center, radius, startAngle, endAngle):
            parent.create_arc((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius),
                start=startAngle, extent=endAngle, style=ARC)
        
        self.calculate_profile()
        d = []
        x = 0
        # x = -self.width/2

        # Left edge segment B0 (horizontal)
        if self.b[0] > 0:
            x1 = x + self.b[0]
            parent.create_line([(x, self.h), (x1, self.h)])
            x = x1

        for j in range(self.waves):
            # Segment B1 (arc)
            if self.b[1] > 0:
                x1 = x + self.w1
                arc(parent, center=(x, self.h-self.r1), radius=self.r1,
                    startAngle=90-self.ag, endAngle=90)
                x = x1

            # Segment B2 (inclined)
            if self.b[2] > 0:
                x1 = x + self.w2
                # d.append(sdxf.Line(points=[(x, self.h1), (x1, self.h2)], **common))
                x = x1

            # Segment B3 (arc)
            if self.b[3] > 0:
                x1 = x + self.w3
                # d.append(sdxf.Arc(center=(x1, self.r3), radius=self.r3,
                                  # startAngle=270-self.ag, endAngle=270, **common))
                x = x1

            # Segment B4 (horizontal)
            if self.b[4] > 0:
                x1 = x + self.b[4]
                # d.append(sdxf.Line(points=[(x, 0), (x1, 0)], **common))
                x = x1

            # Symmetrically against B4 segment
            # Segment B3 (arc)
            if self.b[3] > 0:
                x1 = x + self.w3
                # d.append(sdxf.Arc(center=(x, self.r3), radius=self.r3,
                                  # startAngle=270, endAngle=270+self.ag, **common))
                x = x1

            # Segment B2 (inclined)
            if self.b[2] > 0:
                x1 = x + self.w2
                # d.append(sdxf.Line(points=[(x, self.h2), (x1, self.h1)], **common))
                x = x1

            # Segment B1 (arc)
            if self.b[1] > 0:
                x1 = x + self.w1
                # d.append(sdxf.Arc(center=(x1, self.h-self.r1), radius=self.r1,
                                  # startAngle=90, endAngle=90+self.ag, **common))
                x = x1

            # Segment B5 (horizontal)
            if j < self.waves-1 and self.b[5] > 0:
                # x1 = x + self.b[5]
                # d.append(sdxf.Line(points=[(x, self.h), (x1, self.h)], **common))
                x = x1

        # Right edge segment B0
        if self.b[0] > 0:
            x1 = x + self.b[0]
            parent.create_line([(x, self.h), (x1, self.h)])


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
        
        profile = ProfileTk(b=[100, 100, 100, 100, 100, 100], waves=1, angle=45)
        profile.canvas_draw(self.canvas)
    
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
