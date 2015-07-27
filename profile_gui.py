from tkinter import *
from tkinter.ttk import *
from profile_bending import *


class ProfileTk(Profile):
    def __init__(self, **kwargs):
        Profile.__init__(self, **kwargs)

    @staticmethod
    def arc(parent, center, radius, start, extent, **kwargs):
        parent.create_arc((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius),
                          start=start, extent=extent, style=ARC, **kwargs)

    def canvas_draw(self, canvas, x0=0, y0=0, scale=1, **kwargs):
        self.calculate_profile()

        arc_kwargs = dict(kwargs)
        if 'outline' in kwargs:
            kwargs['fill'] = kwargs['outline']
            del kwargs['outline']

        # Scale profile parameters
        b = [x*scale for x in self.b]
        h, h1, h2, h3, w1, w2, w3, r1, r3 = (x*scale for x in (self.h, self.h1, self.h2, self.h3,
                                                               self.w1, self.w2, self.w3,
                                                               self.r1, self.r3))
        
        x = x0-self.width*scale/2
        y = y0-h
        
        # Left edge segment B0 (horizontal)
        if b[0] > 0:
            x1 = x + b[0]
            canvas.create_line([(x, y), (x1, y)], tag='b0', **kwargs)
            x = x1
        
        for j in range(self.waves):
            # Segment B1 (arc)
            if b[1] > 0:
                self.arc(canvas, center=(x, y+r1), radius=r1,
                         start=90, extent=-self.angle_deg, tag='b1', **arc_kwargs)
                x += w1
                y += h1

            # Segment B2 (inclined)
            if b[2] > 0:
                x1 = x + w2
                y1 = y + h2
                canvas.create_line([(x, y), (x1, y1)], tag='b2', **kwargs)
                x = x1
                y = y1

            # Segment B3 (arc)
            if b[3] > 0:
                x1 = x + w3
                y1 = y + h3
                self.arc(canvas, center=(x1, y1-r1), radius=r1,
                         start=270, extent=-self.angle_deg, tag='b3',  **arc_kwargs)
                x = x1
                y = y1

            # Segment B4 (horizontal)
            if b[4] > 0:
                x1 = x + b[4]
                canvas.create_line([(x, y), (x1, y)], tag='b4', **kwargs)
                x = x1

            # Symmetrically against B4 segment
            # Segment B3 (arc)
            if b[3] > 0:
                x1 = x + w3
                y1 = y - h3
                self.arc(canvas, center=(x, y-r1), radius=r1,
                         start=270, extent=self.angle_deg, tag='b3', **arc_kwargs)
                x = x1
                y = y1

            # Segment B2 (inclined)
            if b[2] > 0:
                x1 = x + w2
                y1 = y - h2
                canvas.create_line([(x, y), (x1, y1)], tag='b2', **kwargs)
                x = x1
                y = y1

            # Segment B1 (arc)
            if b[1] > 0:
                x1 = x + w1
                y1 = y - h1
                self.arc(canvas, center=(x1, y1+r1), radius=r1,
                         start=90, extent=self.angle_deg, tag='b1', **arc_kwargs)
                x = x1
                y = y1

            # Segment B5 (horizontal)
            if j < self.waves-1 and b[5] > 0:
                x1 = x + b[5]
                canvas.create_line([(x, y), (x1, y)], tag='b5', **kwargs)
                x = x1

        # Right edge segment B0
        if b[0] > 0:
            x1 = x + b[0]
            canvas.create_line([(x, y), (x1, y)], tag='b0', **kwargs)


canvas_background = 'gray'
line_color = 'black'
line_highlight = 'yellow'


def paint_by_tag(canvas, tag, color):
    items = canvas.find_withtag(tag)
    for item in items:
        if canvas.type(item) == 'line':
            canvas.itemconfig(item, fill=color)
        else:
            canvas.itemconfig(item, outline=color)


class App(Tk):
    def __init__(self):
        self.canvas_width = 640
        self.canvas_height = 480

        def init_canvas(parent):
            canvas = Canvas(parent, width=640, height=480, bg=canvas_background)
            canvas.pack(side='top', fill='both', expand=1)
            return canvas

        def init_main_menu():
            main_menu = Menu(self)
            self.config(menu=main_menu)
            file_menu = Menu(main_menu)
            main_menu.add_cascade(label="File", menu=file_menu)
            # file_menu.add_command(label="Open", command=self.show_img)
            # file_menu.add_separator()
            file_menu.add_command(label="Exit", command=self.destroy)

        def init_controls(parent):
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
                self.entry_b[-1].bind('<FocusIn>', self._on_focus_in_text_box)
                self.entry_b[-1].bind('<FocusOut>', self._on_focus_out_text_box)
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

            row += 1

            button = Button(parent, text='Рассчитать')
            button.bind('<1>', self._button_action)
            button.grid(row=row, column=1, columnspan=2)

        Tk.__init__(self)
        sidebar_frame = Frame(self, width=160)
        canvas_frame = Frame(self, width=self.canvas_width, height=self.canvas_height)
        sidebar_frame.pack(side='left', fill='y')
        canvas_frame.pack(side='right', fill='both', expand=1)
        
        init_main_menu()
        init_controls(sidebar_frame)
        self.canvas = init_canvas(canvas_frame)

        self.profile = ProfileTk(b=[1 for _ in range(6)], waves=3, angle_deg=60)
        self.profile.canvas_draw(self.canvas, x0=self.canvas_width/2, y0=self.canvas_height/2, scale=20, width=2,
                                 outline=line_color)
        self.canvas.bind('<1>', self._on_click_on_canvas)

    def _on_focus_in_text_box(self, event):
        b_index = self.entry_b.index(event.widget)
        paint_by_tag(self.canvas, 'b%d' % b_index, color=line_highlight)
    
    def _on_focus_out_text_box(self, event):
        b_index = self.entry_b.index(event.widget)
        paint_by_tag(self.canvas, 'b%d' % b_index, color=line_color)
    
    def _button_action(self, event):
        pass

    def _on_click_on_canvas(self, event):
        overlap_range = 10
        overlap_items = self.canvas.find_overlapping(event.x-overlap_range, event.y-overlap_range,
                                                     event.x+overlap_range, event.y+overlap_range)
        if len(overlap_items) >= 1:
            closest_item = self.canvas.find_closest(event.x, event.y)[0]
            tags = list(self.canvas.gettags(closest_item))
            if CURRENT in tags:
                tags.remove(CURRENT)
            index = int(tags[0][1])
            self.entry_b[index].focus_set()

app = App()
app.mainloop()
