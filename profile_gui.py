from tkinter import *
from tkinter import filedialog
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

    def canvas_draw(self, canvas, x0=0, y0=0, scale=1, add_tags=False, **kwargs):
        self.calculate_profile()

        arc_kwargs = dict(kwargs)
        if 'outline' in kwargs:
            kwargs['fill'] = kwargs['outline']
            del kwargs['outline']

        # Scale profile parameters
        b = [x*scale for x in self.b]
        h, h1, h2, h3, w1, w2, w3, r1, r3 = (x*scale for x in (self.height, self.h1, self.h2, self.h3,
                                                               self.w1, self.w2, self.w3,
                                                               self.r1, self.r3))

        x = x0-self.width*scale/2
        y = y0-h
        
        # Left edge segment B0 (horizontal)
        if b[0] > 0:
            x1 = x + b[0]
            tag = 'b0' if add_tags else ''
            canvas.create_line([(x, y), (x1, y)], tag=tag, **kwargs)
            x = x1
        
        for j in range(self.waves):
            # Segment B1 (arc)
            if b[1] > 0:
                tag = 'b1' if add_tags else ''
                self.arc(canvas, center=(x, y+r1), radius=r1,
                         start=90, extent=-self.angle.deg, tag=tag, **arc_kwargs)
                x += w1
                y += h1

            # Segment B2 (inclined)
            if b[2] > 0:
                x1 = x + w2
                y1 = y + h2
                tag = 'b2' if add_tags else ''
                canvas.create_line([(x, y), (x1, y1)], tag=tag, **kwargs)
                x = x1
                y = y1

            # Segment B3 (arc)
            if b[3] > 0:
                x1 = x + w3
                y1 = y + h3
                tag = 'b3' if add_tags else ''
                self.arc(canvas, center=(x1, y1-r3), radius=r3,
                         start=270, extent=-self.angle.deg, tag=tag,  **arc_kwargs)
                x = x1
                y = y1

            # Segment B4 (horizontal)
            if b[4] > 0:
                x1 = x + b[4]
                tag = 'b4' if add_tags else ''
                canvas.create_line([(x, y), (x1, y)], tag=tag, **kwargs)
                x = x1

            # Symmetrically against B4 segment
            # Segment B3 (arc)
            if b[3] > 0:
                x1 = x + w3
                y1 = y - h3
                tag = 'b3' if add_tags else ''
                self.arc(canvas, center=(x, y-r3), radius=r3,
                         start=270, extent=self.angle.deg, tag=tag, **arc_kwargs)
                x = x1
                y = y1

            # Segment B2 (inclined)
            if b[2] > 0:
                x1 = x + w2
                y1 = y - h2
                tag = 'b2' if add_tags else ''
                canvas.create_line([(x, y), (x1, y1)], tag=tag, **kwargs)
                x = x1
                y = y1

            # Segment B1 (arc)
            if b[1] > 0:
                x1 = x + w1
                y1 = y - h1
                tag = 'b1' if add_tags else ''
                self.arc(canvas, center=(x1, y1+r1), radius=r1,
                         start=90, extent=self.angle.deg, tag=tag, **arc_kwargs)
                x = x1
                y = y1

            # Segment B5 (horizontal)
            if j < self.waves-1 and b[5] > 0:
                x1 = x + b[5]
                tag = 'b5' if add_tags else ''
                canvas.create_line([(x, y), (x1, y)], tag=tag, **kwargs)
                x = x1

        # Right edge segment B0
        if b[0] > 0:
            x1 = x + b[0]
            tag = 'b0' if add_tags else ''
            canvas.create_line([(x, y), (x1, y)], tag=tag, **kwargs)


class LocaleDoubleVar(StringVar):
    def __init__(self, master=None, value=None, name=None):
        StringVar.__init__(self, master, value, name)

    def get(self):
        return locale.atof(StringVar.get(self))


canvas_background = 'gray'
line_color = 'black'
line_highlight = 'yellow'
line_grayed = 'dark gray'


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
            canvas = Canvas(parent, width=self.canvas_width, height=self.canvas_height, bg=canvas_background)
            canvas.pack(side='top', fill='both', expand=1)
            canvas.bind('<1>', self._on_click_on_canvas)
            canvas.bind('<Configure>', self._on_resize_canvas)
            return canvas

        def init_main_menu():
            main_menu = Menu(self)
            self.config(menu=main_menu)
            file_menu = Menu(main_menu, tearoff=False)
            file_menu.add_command(label="Выход", command=self.destroy)
            help_menu = Menu(main_menu, tearoff=False)
            help_menu.add_command(label="О программе",
                                  command=lambda: messagebox.showinfo('О программе...', 'Калибровки'))
            main_menu.add_cascade(label="Файл", menu=file_menu)
            main_menu.add_cascade(label="Справка", menu=help_menu)

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
                label.grid(row=row, column=1, pady=2, sticky=E)

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
            label.grid(row=row, column=1, sticky=E)

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
            label.grid(row=row, column=1, sticky=E)

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
            label.grid(row=row, column=1, sticky=E)

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
            label.grid(row=row, column=1, sticky=E)

            var = LocaleDoubleVar(value=self.params['amax'].deg)
            self.entry_amax = Entry(parent, textvariable=var)
            self.vars[self.entry_amax] = var
            self.entry_amax.grid(row=row, column=2)
            self.entry_amax.bind('<FocusOut>', self._on_focus_out_text_box)
            self.entry_amax.bind('<Return>', self._on_focus_out_text_box)
            self.entry_amax.tag = 'amax'

            row += 1

            button = Button(parent, text='Рассчитать')
            button.bind('<1>', self.calculate)
            button.grid(row=row, column=1, columnspan=2, pady=4)

            row += 1
            button = Button(parent, text='Экспорт в файл dxf', state=DISABLED)
            button.bind('<1>', self.export)
            button.grid(row=row, column=1, columnspan=2)
            self.button_export = button

        def init_console(parent, height):
            scrollbar = Scrollbar(parent)
            scrollbar.pack(side='right', fill='y')
            console = Text(parent, height=height, state=DISABLED)
            console.pack(side='left', fill='both', expand=1)
            scrollbar['command'] = console.yview
            console['yscrollcommand'] = scrollbar.set

            def copy_selection():
                try:
                    text = console.get('sel.first', 'sel.last')
                except TclError:
                    return

                self.clipboard_clear()
                self.clipboard_append(text)

            def show_context_menu(event):
                 pos_x = console.winfo_rootx() + event.x
                 pos_y = console.winfo_rooty() + event.y
                 context_menu.tk_popup(pos_x, pos_y)

            context_menu = Menu(self, tearoff=False)
            context_menu.add_command(label="Копировать", command=copy_selection)
            console.bind("<3>", show_context_menu)

            return console

        super().__init__()

        self.canvas_width = 640
        self.canvas_height = 360
        self.baseline = self.canvas_height / 2
        self.border = 20

        self.params = dict(
            b=[10.0, 1.5, 10.0, 1.5, 10.0, 10.0],
            waves=3,
            amin=Angle(deg=0),
            amax=Angle(deg=60),
            m=10
        )

        self.calculated_profiles = []

        sidebar_frame = Frame(self, width=160)
        canvas_frame = Frame(self, width=self.canvas_width, height=self.canvas_height)
        console_frame = Frame(self)

        sidebar_frame.pack(side='left', fill='y')
        console_frame.pack(side='bottom', fill='x')
        canvas_frame.pack(side='right', fill='both', expand=1)
        
        init_main_menu()
        init_controls(sidebar_frame)
        self.canvas = init_canvas(canvas_frame)
        self.console = init_console(console_frame, height=10)

        self.profile = ProfileTk(b=self.params['b'], waves=self.params['waves'], angle=self.params['amax'])
        self.redraw_profiles()

    def cls(self):
        self.console.configure(state=NORMAL)
        self.console.delete(0.0, END)
        self.console.configure(state=DISABLED)

    def print(self, text='', end='\n'):
        self.console.configure(state=NORMAL)
        self.console.insert(END, text+end)
        self.console.configure(state=DISABLED)

    def redraw_profiles(self):
        if self.calculated_profiles:
            width = self.calculated_profiles[0].width
        else:
            width = self.profile.width
        height = self.profile.height

        self.canvas.delete(ALL)
        scale = (self.canvas_width-self.border) / width
        if height * scale + self.border > self.canvas_height:
            scale = (self.canvas_height-self.border) / height

        self.baseline = (self.canvas_height + height * scale) / 2
        center = self.canvas_width/2

        for profile in self.calculated_profiles:
            profile.canvas_draw(self.canvas, x0=center, y0=self.baseline, scale=scale, width=1, outline=line_grayed)

        self.profile.canvas_draw(self.canvas, x0=center,
                                 y0=self.baseline,
                                 scale=scale, width=2,
                                 add_tags=True,
                                 outline=line_color)

        self.cls()
        self.print('Ширина профиля: %.2f' % self.profile.width)
        self.print('Высота по средней линии: %.2f' % self.profile.height)
        self.print('Ширина развертки: %.2f' % self.profile.flat_width)

        if self.calculated_profiles:
            profiles = list(self.calculated_profiles)
            profiles.append(self.profile)
            for i, profile in enumerate(profiles):
                self.print()
                self.print('Клеть №%d' % (i+1))
                self.print('Ag = %-6.2f' % profile.angle.deg)
                self.print('R1 = %-6.2f    R3 = %-6.2f' % (profile.r1, profile.r3))
                self.print('H  = %-6.2f    H1 = %-6.2f    H2 = %-6.2f    H3 = %-6.2f' %
                           (profile.height, profile.h1, profile.h2, profile.h3))
                self.print('W1 = %-6.2f    W2 = %-6.2f    W3 = %-6.2f' % (profile.w1, profile.w2, profile.w3))

    def _on_resize_canvas(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.redraw_profiles()
    
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
            event.widget.selection_range(0, END)
            return

        redraw_profile = False
        try:
            if event.widget in self.entry_b:
                b_index = self.entry_b.index(event.widget)
                if new_val < 0:
                    raise ValueError('Длина участка не может быть отрицательной.')

                if new_val != self.params['b'][b_index]:
                    redraw_profile = True
                    self.params['b'][b_index] = new_val
            elif hasattr(event.widget, 'tag'):
                tag = event.widget.tag
                if (new_val != self.params[tag] and
                        not(type(self.params[tag]) is Angle and new_val == self.params[tag].deg)):
                    redraw_profile = True
                    if type(self.params[tag]) is Angle:
                        if not (0 <= new_val <= 90):
                            raise ValueError('Значение угла должно быть в диапазоне от 0 до 90 градусов.')
                        elif (tag == 'amin' and new_val > self.params['amax'].deg or
                              tag == 'amax' and new_val < self.params['amin'].deg):
                            raise ValueError('Значение начального угла должно быть меньше значения конечного угла.')

                        self.params[tag] = Angle(deg=new_val)
                    else:
                        if tag == 'waves' and (type(new_val) is not int or new_val <= 0):
                            raise ValueError('Количество волн должно быть целым числом больше нуля.')
                        elif tag == 'm' and (type(new_val) is not int or new_val <= 1):
                            raise ValueError('Количество клетей должно быть целым числом больше единицы.')

                        self.params[tag] = new_val

        except ValueError as err:
            messagebox.showerror('Ошибка', err)
            event.widget.focus_set()
            event.widget.selection_range(0, END)
            return

        if redraw_profile:
            self.calculated_profiles = []
            self.profile.b = self.params['b']
            self.profile.waves = self.params['waves']
            self.profile.angle = self.params['amax']
            self.redraw_profiles()
            self.button_export.configure(state=DISABLED)

        # Highlight a section after redraw
        if event.keycode == 13 and event.widget in self.entry_b:
            self._on_focus_in_text_box(event)
    
    def calculate(self, _):
        m = self.params['m']
        amin = self.params['amin']
        amax = self.params['amax']
        b = self.params['b']
        waves = self.params['waves']
        eps = 1e-5

        angles = []

        if self.params['amin'].rad == 0:
            amin = Angle(rad=sys.float_info.epsilon)
            m += 1  # Не считаем полностью развернутый лист клетью
        else:
            angles.append(amin)

        # При минимальном угле альфа получается максимальная ширина и наоборот
        wmax = part_width(b, amin.rad)
        wmin = part_width(b, amax.rad)

        dw = (wmax-wmin)/(m-1)
        w = wmax - dw

        a = amin
        for i in range(m-2):
            a = Angle(rad=secant_method(lambda x: part_width(b, x)-w, a.rad, amax.rad, eps))
            w -= dw
            angles.append(a)

        self.calculated_profiles = [ProfileTk(b=b, waves=waves, angle=angle) for angle in angles]

        self.redraw_profiles()

        self.button_export.configure(state=NORMAL)

    def export(self, _):
        filename = filedialog.SaveAs(self, filetypes=[('Файлы DXF', '.dxf')]).show()
        if filename:
            d = sdxf.Drawing()

            for i, profile in enumerate(self.calculated_profiles):
                layer = str(i)
                d.layers.append(sdxf.Layer(layer))
                d.extend(profile.dxf_draw(layer=layer))

            if not filename.endswith('.dxf'):
                filename += '.dxf'

            d.saveas(filename)

    def _on_click_on_canvas(self, event):
        overlap_range = 40
        overlap_items = self.canvas.find_overlapping(event.x-overlap_range, event.y-overlap_range,
                                                     event.x+overlap_range, event.y+overlap_range)
        if overlap_items:
            closest_item = self.canvas.find_closest(event.x, event.y)[0]
            tags = list(self.canvas.gettags(closest_item))
            if CURRENT in tags:
                tags.remove(CURRENT)

            if tags:
                index = int(tags[0][1])
                self.entry_b[index].focus_set()
                self.entry_b[index].selection_range(0, END)

app = App()
app.mainloop()
