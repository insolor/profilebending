from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox as messagebox
from profile_bending import *
import locale
from locale import setlocale, LC_NUMERIC
setlocale(LC_NUMERIC, '')


class ProfileTk(Profile):
    def __init__(self, **kwargs):
        Profile.__init__(self, **kwargs)

    @staticmethod
    def arc(canvas, center, radius, start, extent, **kwargs):
        canvas.create_arc((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius),
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
                         start=90, extent=-self.angle.deg, tag='b1', **arc_kwargs)
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
                self.arc(canvas, center=(x1, y1-r3), radius=r3,
                         start=270, extent=-self.angle.deg, tag='b3',  **arc_kwargs)
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
                self.arc(canvas, center=(x, y-r3), radius=r3,
                         start=270, extent=self.angle.deg, tag='b3', **arc_kwargs)
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
                         start=90, extent=self.angle.deg, tag='b1', **arc_kwargs)
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


class LocaleDoubleVar(StringVar):
    def __init__(self, master=None, value=None, name=None):
        StringVar.__init__(self, master, value, name)

    def get(self):
        return locale.atof(StringVar.get(self))


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
        def init_canvas(parent):
            canvas = Canvas(parent, width=640, height=480, bg=canvas_background)
            canvas.pack(side='top', fill='both', expand=1)
            canvas.bind('<1>', self._on_click_on_canvas)
            canvas.bind('<Configure>', self._on_resize_canvas)
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
            self.vars = dict()
            row = 1

            label = Label(parent, text='Длины участков:')
            label.grid(row=row, column=1, columnspan=2)
            row += 1

            for i in range(6):
                label = Label(parent, text='B%d =' % i)
                label.grid(row=row, column=1)

                var = LocaleDoubleVar(value=self.params['b'][i])
                entry = Entry(parent, textvariable=var)
                self.vars[entry] = var
                entry.grid(row=row, column=2)
                entry.bind('<FocusIn>', self._on_focus_in_text_box)
                entry.bind('<FocusOut>', self._on_focus_out_text_box)
                entry.bind('<Return>', self._on_focus_out_text_box)
                self.entry_b.append(entry)
                row += 1

            row += 1

            label = Label(parent, text='Количество волн:')
            label.grid(row=row, column=1, columnspan=2)

            row += 1

            label = Label(parent, text='N =')
            label.grid(row=row, column=1)

            var = IntVar(value=self.params['waves'])
            self.entry_waves = Entry(parent, textvariable=var)
            self.vars[self.entry_waves] = var
            self.entry_waves.grid(row=row, column=2)
            self.entry_waves.bind('<FocusOut>', self._on_focus_out_text_box)
            self.entry_waves.bind('<Return>', self._on_focus_out_text_box)
            self.entry_waves.tag = 'waves'

            row += 1

            label = Label(parent, text='Количество клетей:')
            label.grid(row=row, column=1, columnspan=2)

            row += 1

            label = Label(parent, text='M =')
            label.grid(row=row, column=1)

            var = IntVar(value=self.params['m'])
            self.entry_m = Entry(parent, textvariable=var)
            self.vars[self.entry_m] = var
            self.entry_m.grid(row=row, column=2)
            self.entry_m.bind('<FocusOut>', self._on_focus_out_text_box)
            self.entry_m.bind('<Return>', self._on_focus_out_text_box)
            self.entry_m.tag = 'm'

            row += 1

            label = Label(parent, text='Начальный угол:')
            label.grid(row=row, column=1, columnspan=2)

            row += 1

            label = Label(parent, text='Amin =')
            label.grid(row=row, column=1)

            var = LocaleDoubleVar(value=self.params['amin'].deg)
            self.entry_amin = Entry(parent, textvariable=var)
            self.vars[self.entry_amin] = var
            self.entry_amin.grid(row=row, column=2)
            self.entry_amin.bind('<FocusOut>', self._on_focus_out_text_box)
            self.entry_amin.bind('<Return>', self._on_focus_out_text_box)
            self.entry_amin.tag = 'amin'

            row += 1

            label = Label(parent, text='Конечный угол:')
            label.grid(row=row, column=1, columnspan=2)

            row += 1

            label = Label(parent, text='Amax =')
            label.grid(row=row, column=1)

            var = LocaleDoubleVar(value=self.params['amax'].deg)
            self.entry_amax = Entry(parent, textvariable=var)
            self.vars[self.entry_amax] = var
            self.entry_amax.grid(row=row, column=2)
            self.entry_amax.bind('<FocusOut>', self._on_focus_out_text_box)
            self.entry_amax.bind('<Return>', self._on_focus_out_text_box)
            self.entry_amax.tag = 'amax'

            row += 1

            button = Button(parent, text='Рассчитать')
            button.bind('<1>', self._button_calculate)
            button.grid(row=row, column=1, columnspan=2)

        super().__init__()

        self.canvas_width = 640
        self.canvas_height = 480
        self.baseline = self.canvas_height / 2
        self.border = 40

        self.params = dict(
            b=[1.0 for _ in range(6)],
            waves=3,
            amin=Angle(deg=0),
            amax=Angle(deg=60),
            m=10
        )

        sidebar_frame = Frame(self, width=160)
        canvas_frame = Frame(self, width=self.canvas_width, height=self.canvas_height)
        sidebar_frame.pack(side='left', fill='y')
        canvas_frame.pack(side='right', fill='both', expand=1)
        
        init_main_menu()
        init_controls(sidebar_frame)
        self.canvas = init_canvas(canvas_frame)

        self.profile = ProfileTk(b=self.params['b'], waves=self.params['waves'], angle=self.params['amax'])
        self.redraw_profile()

    def redraw_profile(self):
        self.canvas.delete(ALL)
        scale = (self.canvas_width-self.border) / self.profile.width
        if self.profile.h * scale + self.border > self.canvas_height:
            scale = (self.canvas_height-self.border) / self.profile.h
        self.baseline = (self.canvas_height + self.profile.h * scale) / 2
        self.profile.canvas_draw(self.canvas, x0=self.canvas_width/2,
                                 y0=self.baseline,
                                 scale=scale, width=2,
                                 outline=line_color)

    def _on_resize_canvas(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.redraw_profile()
    
    def _on_focus_in_text_box(self, event):
        b_index = self.entry_b.index(event.widget)
        paint_by_tag(self.canvas, 'b%d' % b_index, color=line_highlight)

    def _on_focus_out_text_box(self, event):
        if event.widget in self.entry_b:
            b_index = self.entry_b.index(event.widget)
            paint_by_tag(self.canvas, 'b%d' % b_index, color=line_color)

        var = self.vars[event.widget]
        try:
            new_val = var.get()
        except ValueError:
            messagebox.showerror('Ошибка', 'Неправильный формат числа с плавающей запятой')
            event.widget.focus_set()
            return

        redraw_profile = False
        if event.widget in self.entry_b:
            b_index = self.entry_b.index(event.widget)
            if new_val != self.params['b'][b_index]:
                redraw_profile = True
                self.params['b'][b_index] = new_val
        elif hasattr(event.widget, 'tag'):
            if new_val != self.params[event.widget.tag]:
                redraw_profile = event.widget.tag in {'amax', 'waves'}
                if event.widget.tag in {'amin', 'amax'}:
                    self.params[event.widget.tag] = Angle(deg=new_val)
                else:
                    self.params[event.widget.tag] = new_val

        if redraw_profile:
            self.profile.b = self.params['b']
            self.profile.waves = self.params['waves']
            self.profile.angle = self.params['amax']
            self.redraw_profile()

        # Highlight a section after redraw
        if event.keycode == 13 and event.widget in self.entry_b:
            self._on_focus_in_text_box(event)
    
    def _button_calculate(self, event):
        pass

    def _on_click_on_canvas(self, event):
        overlap_range = 10
        overlap_items = self.canvas.find_overlapping(event.x-overlap_range, event.y-overlap_range,
                                                     event.x+overlap_range, event.y+overlap_range)
        if overlap_items:
            closest_item = self.canvas.find_closest(event.x, event.y)[0]
            tags = list(self.canvas.gettags(closest_item))
            if CURRENT in tags:
                tags.remove(CURRENT)
            index = int(tags[0][1])
            self.entry_b[index].focus_set()

app = App()
app.mainloop()
