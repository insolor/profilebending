
import sys
from math import pi, sin, cos
from locale import setlocale, LC_NUMERIC, atof, format_string
setlocale(LC_NUMERIC, '')

sys.path.append('../../SDXF')
import sdxf


def input_float(prompt='', cond=None, msg_on_false_cond=''):
    while True:
        try:
            inp = input(prompt)
            ret = atof(inp)
        except ValueError:
            print('Неверный ввод: \'%s\'' % inp)
        else:
            if cond and not cond(ret):
                print(msg_on_false_cond)
            else:
                break
    return ret


def width(b, alpha):
    return (b[1]+b[3])/alpha*sin(alpha)+b[2]*cos(alpha)


def secant_method(func, a1, a2, eps, stop=1000):
    n = 0
    while True:
        if abs(a1-a2)<eps or stop and n > stop:
            assert abs(func(a2))<eps, 'Failed to reach a null of the function'
            return a2
        
        try:
            a1 = a2 - (a2-a1)*func(a2)/(func(a2)-func(a1))
            a2 = a1 - (a1-a2)*func(a1)/(func(a1)-func(a2))
        except ZeroDivisionError:
            assert abs(func(a2))<eps, 'Failed to reach a null of the function'
            return a2
        
        n += 1

print('Введите длины участков b0-b5:')
b = [0 for i in range(6)]
for i in range(6):
    b[i] = input_float('b%d = ' % i,
                       cond=lambda x: x>=0,
                       msg_on_false_cond='Длина участка не может быть отрицательной.')

N = int(input_float('Введите количество волн N = ',
                    cond=lambda x: x>0 and x<1000 and int(x)==x,
                    msg_on_false_cond='Количество волн должно быть целым числом больше нуля.'))

M = int(input_float('Введите количество клетей M = ',
                    cond=lambda x: x>1 and x<1000 and int(x)==x,
                    msg_on_false_cond='Количество клетей должно быть целым числом больше единицы.'))

ag = input_float('Введите начальный угол Amin = ',
                 cond=lambda x: x>=0 and x<180,
                 msg_on_false_cond='Начальный угол должен быть больше или равен нулю и меньше 180 градусов.')

amin = ag/180*pi

ag = input_float('Введите конечный угол Amax = ',
                 cond=lambda x: x>amin and x<180,
                 msg_on_false_cond='Конечный угол должен быть больше начального, но меньше 180 градусов.')

amax = ag/180*pi

eps = 1e-5

angles = []

# При минимальном угле альфа получается максимальная ширина и наоборот
if amin == 0:
    amin = sys.float_info.epsilon
    M += 1  # Не считаем полностью развернутый лист клетью
else:
    angles.append(amin)

Wmax = width(b, amin)
Wmin = width(b, amax)

DW = (Wmax-Wmin)/(M-1)
W = Wmax - DW

a = amin
for i in range(M-2):
    a = secant_method(lambda x: width(b, x)-W, a, amax, eps)
    W -= DW
    angles.append(a)
angles.append(amax)

calc = []
for i, angle in enumerate(angles):
    ag = angle/pi*180
    
    sinA = sin(angle)
    cosA = cos(angle)
    
    R1 = b[1] / angle
    R3 = b[3] / angle
    
    H2 = R3 * (1 - cosA)
    H1 = H2 + b[2] * sinA
    
    H = b[2] * sinA + (R1 + R3) * (1 - cosA)
    
    W1 = R1 * sinA
    W2 = b[2] * cosA
    W3 = R3 * sinA
    
    print('Клеть №%d' % (i+1))
    print(format_string('Ag = %-6.2f', ag))
    print(format_string('R1 = %-6.2f    R3 = %-6.2f', (R1, R3)))
    print(format_string('H  = %-6.2f    H1 = %-6.2f    H2 = %-6.2f', (H, H1, H2)))
    print(format_string('W1 = %-6.2f    W2 = %-6.2f    W3 = %-6.2f', (W1, W2, W3)))
    print()

    calc.append(dict(ag=ag, R1=R1, R3=R3, H=H, H1=H1, H2=H2, W1=W1, W2=W2, W3=W3))

# Write to dxf file
d = sdxf.Drawing()

# Reserve two layers
d.layers.append(sdxf.Layer('0'))
d.append(sdxf.Line(points=[(0, 0), (0, 0)], layer='0'))
d.layers.append(sdxf.Layer('1'))
d.append(sdxf.Line(points=[(0, 0), (0, 0)], layer='1'))

for i, item in enumerate(calc):
    W = 2*b[0]+(2*item['W1']+2*item['W2']+2*item['W3']+b[4])*N
    if N>1:
        W += b[5]*(N-1)
    
    x = -W/2
    
    layer = str(i+1)
    d.layers.append(sdxf.Layer(layer))
    
    # Left edge segment B0 (horizontal)
    if b[0] > 0:
        x1 = x + b[0]
        d.append(sdxf.Line(points=[(x, item['H']),(x1, item['H'])], layer=layer))
        x = x1
    
    for j in range(N):
        # Segment B1 (arc)
        if b[1] > 0:
            x1 = x + item['W1']
            d.append(sdxf.Arc(center=(x, item['H']-item['R1']), radius=item['R1'],
                              startAngle=90-item['ag'], endAngle=90, layer=layer))
            x = x1
        
        # Segment B2 (inclined)
        if b[2] > 0:
            x1 = x + item['W2']
            d.append(sdxf.Line(points=[(x, item['H1']), (x1, item['H2'])], layer=layer))
            x = x1
        
        # Segment B3 (arc)
        if b[3] > 0:
            x1 = x + item['W3']
            d.append(sdxf.Arc(center=(x1, item['R3']), radius=item['R3'],
                              startAngle=270-item['ag'], endAngle=270, layer=layer))
            x = x1
        
        # Segment B4 (horizontal)
        if b[4] > 0:
            x1 = x + b[4]
            d.append(sdxf.Line(points=[(x, 0),(x1, 0)], layer=layer))
            x = x1
        
        # Symmetrically against B4 segment
        # Segment B3 (arc)
        if b[3] > 0:
            x1 = x + item['W3']
            d.append(sdxf.Arc(center=(x, item['R3']), radius=item['R3'],
                              startAngle=270, endAngle=270+item['ag'], layer=layer))
            x = x1
        
        # Segment B2 (inclined)
        if b[2] > 0:
            x1 = x + item['W2']
            d.append(sdxf.Line(points=[(x, item['H2']), (x1, item['H1'])], layer=layer))
            x = x1
        
        # Segment B1 (arc)
        if b[1] > 0:
            x1 = x + item['W1']
            d.append(sdxf.Arc(center=(x1, item['H']-item['R1']), radius=item['R1'],
                              startAngle=90, endAngle=90+item['ag'], layer=layer))
            x = x1
        
        # Segment B5 (horizontal)
        if j < N-1 and b[5] > 0:
            x1 = x + b[5]
            d.append(sdxf.Line(points=[(x, item['H']),(x1, item['H'])], layer=layer))
            x = x1
    
    # Right edge segment B0
    if b[0] > 0:
        x1 = x + b[0]
        d.append(sdxf.Line(points=[(x, item['H']),(x1, item['H'])], layer=layer))
        x = x1


fname = input('Введите имя файла dxf: ')
if not fname:
    fname = 'profile'
fname += '.dxf'

d.saveas(fname)

print('Файл сохранён.')

input()
