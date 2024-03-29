
import sys
from math import pi, sin, cos
from locale import setlocale, LC_NUMERIC, atof
setlocale(LC_NUMERIC, '')

#sys.path.append('../../SDXF')
import sdxf


def input_float(prompt='', cond=None, msg_on_false_cond=''):
    while True:
        inp = input(prompt)
        try:
            ret = atof(inp)
        except ValueError:
            print('Неверный ввод: \'%s\'' % inp)
        else:
            if cond and not cond(ret):
                print(msg_on_false_cond)
            else:
                return ret


def partial_width(b, alpha):
    return (b[1]+b[3])/alpha*sin(alpha)+b[2]*cos(alpha)


def secant_method(func, a1, a2, eps, stop=1000):
    n = 0
    while True:
        if abs(a1-a2) < eps or stop and n > stop:
            assert abs(func(a2)) < eps, 'Failed to reach a null of the function'
            return a2
        
        try:
            a1 = a2 - (a2-a1)*func(a2)/(func(a2)-func(a1))
            a2 = a1 - (a1-a2)*func(a1)/(func(a1)-func(a2))
        except ZeroDivisionError:
            assert abs(func(a2)) < eps, 'Failed to reach a null of the function'
            return a2
        
        n += 1


class Angle(object):
    def __init__(self, deg=None, rad=None):
        if deg is not None:
            self.__deg = deg
            self.__rad = deg/180*pi
        elif rad is not None:
            self.__rad = rad
            self.__deg = rad*180/pi
        else:
            self.__rad = 0
            self.__deg = 0

    @property
    def rad(self):
        return self.__rad

    @property
    def deg(self):
        return self.__deg

    def __float__(self):
        return self.__rad


class Profile(object):
    def __init__(self, b, waves, angle):
        self.b = b
        self.waves = waves
        
        assert(type(angle) is Angle)
        self.angle = angle
        
        self.calculate_profile()

    def calculate_profile(self):
        sina = sin(self.angle)
        cosa = cos(self.angle)

        self.r1 = self.b[1] / self.angle.rad
        self.r3 = self.b[3] / self.angle.rad

        self.h1 = self.r1 * (1 - cosa)
        self.h2 = self.b[2] * sina
        self.h3 = self.r3 * (1 - cosa)

        self.height = self.h1 + self.h2 + self.h3

        self.w1 = self.r1 * sina
        self.w2 = self.b[2] * cosa
        self.w3 = self.r3 * sina

    @property
    def width(self):
        self.calculate_profile()
        return 2*self.b[0]+(2*self.w1+2*self.w2+2*self.w3+self.b[4])*self.waves + self.b[5]*(self.waves-1)

    @property
    def flat_width(self):
        self.calculate_profile()
        return 2*self.b[0]+(2*self.b[1]+2*self.b[2]+2*self.b[3]+self.b[4])*self.waves + self.b[5]*(self.waves-1)

    def dxf_draw(self, **common):
        d = []
        x = -self.width/2

        # Left edge segment B0 (horizontal)
        if self.b[0] > 0:
            x1 = x + self.b[0]
            d.append(sdxf.Line(points=[(x, self.height), (x1, self.height)], **common))
            x = x1

        for j in range(self.waves):
            # Segment B1 (arc)
            if self.b[1] > 0:
                x1 = x + self.w1
                d.append(sdxf.Arc(center=(x, self.height-self.r1), radius=self.r1,
                                  startAngle=90-self.angle.deg, endAngle=90, **common))
                x = x1

            # Segment B2 (inclined)
            if self.b[2] > 0:
                x1 = x + self.w2
                d.append(sdxf.Line(points=[(x, self.h2 + self.h3), (x1, self.h3)], **common))
                x = x1

            # Segment B3 (arc)
            if self.b[3] > 0:
                x1 = x + self.w3
                d.append(sdxf.Arc(center=(x1, self.r3), radius=self.r3,
                                  startAngle=270-self.angle.deg, endAngle=270, **common))
                x = x1

            # Segment B4 (horizontal)
            if self.b[4] > 0:
                x1 = x + self.b[4]
                d.append(sdxf.Line(points=[(x, 0), (x1, 0)], **common))
                x = x1

            # Symmetrically against B4 segment
            # Segment B3 (arc)
            if self.b[3] > 0:
                x1 = x + self.w3
                d.append(sdxf.Arc(center=(x, self.r3), radius=self.r3,
                                  startAngle=270, endAngle=270+self.angle.deg, **common))
                x = x1

            # Segment B2 (inclined)
            if self.b[2] > 0:
                x1 = x + self.w2
                d.append(sdxf.Line(points=[(x, self.h3), (x1, self.h2 + self.h3)], **common))
                x = x1

            # Segment B1 (arc)
            if self.b[1] > 0:
                x1 = x + self.w1
                d.append(sdxf.Arc(center=(x1, self.height-self.r1), radius=self.r1,
                                  startAngle=90, endAngle=90+self.angle.deg, **common))
                x = x1

            # Segment B5 (horizontal)
            if j < self.waves-1 and self.b[5] > 0:
                x1 = x + self.b[5]
                d.append(sdxf.Line(points=[(x, self.height), (x1, self.height)], **common))
                x = x1

        # Right edge segment B0
        if self.b[0] > 0:
            x1 = x + self.b[0]
            d.append(sdxf.Line(points=[(x, self.height), (x1, self.height)], **common))

        return d

    def print(self):
        print('Ag = %-6.2f' % self.angle.deg)
        print('R1 = %-6.2f    R3 = %-6.2f' % (self.r1, self.r3))
        print('H  = %-6.2f    H1 = %-6.2f    H2 = %-6.2f    H3 = %-6.2f' %
              (self.height, self.h1, self.h2, self.h3))
        print('W1 = %-6.2f    W2 = %-6.2f    W3 = %-6.2f' % (self.w1, self.w2, self.w3))


def main():
    print('Введите длины участков b0-b5:')
    b = [0 for _ in range(6)]
    for i in range(6):
        b[i] = input_float('b%d = ' % i,
                           cond=lambda x: x >= 0,
                           msg_on_false_cond='Длина участка не может быть отрицательной.')

    N = int(input_float('Введите количество волн N = ',
                        cond=lambda x: 0 < x < 1000 and int(x) == x,
                        msg_on_false_cond='Количество волн должно быть целым числом больше нуля.'))

    M = int(input_float('Введите количество клетей M = ',
                        cond=lambda x: 1 < x < 1000 and int(x) == x,
                        msg_on_false_cond='Количество клетей должно быть целым числом больше единицы.'))

    amin = Angle(
        deg=input_float('Введите начальный угол Amin = ',
                        cond=lambda x: 0 <= x < 180,
                        msg_on_false_cond='Начальный угол должен быть больше или равен нулю и меньше 180 градусов.'))

    amax = Angle(
        deg=input_float('Введите конечный угол Amax = ',
                        cond=lambda x: amin.deg < x < 180,
                        msg_on_false_cond='Конечный угол должен быть больше начального, но меньше 180 градусов.'))

    eps = 1e-5

    angles = []

    if amin.rad == 0:
        amin = Angle(rad=sys.float_info.epsilon)
        M += 1  # Не считаем полностью развернутый лист клетью
    else:
        angles.append(amin)
    
    # При минимальном угле альфа получается максимальная ширина и наоборот
    Wmax = partial_width(b, amin.rad)
    Wmin = partial_width(b, amax.rad)

    DW = (Wmax-Wmin)/(M-1)
    W = Wmax - DW

    a = amin
    for i in range(M-2):
        a = Angle(rad=secant_method(lambda x: partial_width(b, x)-W, a.rad, amax.rad, eps))
        W -= DW
        angles.append(a)
    angles.append(amax)

    calc = []
    for i, angle in enumerate(angles):
        profile = Profile(b=b, waves=N, angle=angle)
        print('Клеть №%d' % (i+1))
        profile.print()
        print()
        calc.append(profile)
    
    # Write to dxf file
    d = sdxf.Drawing()

    # Reserve two layers
    # d.layers.append(sdxf.Layer('0'))
    # d.append(sdxf.Line(points=[(0, 0), (0, 0)], layer='0'))
    # d.layers.append(sdxf.Layer('1'))
    # d.append(sdxf.Line(points=[(0, 0), (0, 0)], layer='1'))

    for i, profile in enumerate(calc):
        layer = str(i)
        d.layers.append(sdxf.Layer(layer))
        d.extend(profile.dxf_draw(layer=layer))

    fname = input('Введите имя файла dxf: ')
    if not fname:
        fname = 'profile'
    fname += '.dxf'

    d.saveas(fname)

    print('Файл сохранён.')

    input()


if __name__ == '__main__':
    main()
