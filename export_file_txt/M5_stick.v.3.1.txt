from m5stack import *
from m5ui import *
from uiflow import *
import machine

# 1. Настройка экрана
setScreenColor(0x000000)
lcd.setRotation(1) 

# Переменные настроек
mode = 0  # 0: Часы, 1: Настройка Часов, 2: Настройка Минут
set_h = 12
set_m = 0

# Интерфейс
label_time = M5TextBox(35, 30, "00:00:00", lcd.FONT_DejaVu40, 0x00FF00, rotate=0)
label_date = M5TextBox(40, 85, "B: NEXT | A: +1", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_info = M5TextBox(30, 115, "PWR BTN TO SAVE", lcd.FONT_Default, 0xFFCC00, rotate=0)

# Выключаем красный диод сразу (пин 19, состояние 1 = ВЫКЛ)
led = machine.Pin(19, machine.Pin.OUT)
led.value(1)

def get_time_now():
    try:
        # Пробуем получить время (зависит от прошивки)
        t = rtc.now()
        return t[3], t[4], t[5]
    except:
        import time
        t = time.localtime()
        return t[3], t[4], t[5]

def update_ui():
    global mode, set_h, set_m
    if mode == 0:
        h, m, s = get_time_now()
        label_time.setText("{:02d}:{:02d}:{:02d}".format(h, m, s))
        label_time.setColor(0x00FF00)
        label_info.setText("MODE: RUNNING")
    elif mode == 1:
        label_time.setText("{:02d} : --".format(set_h))
        label_time.setColor(0xFF0000) # Красный - часы
        label_info.setText("SETTING HOURS...")
    elif mode == 2:
        label_time.setText("-- : {:02d}".format(set_m))
        label_time.setColor(0xFFFF00) # Желтый - минуты
        label_info.setText("SETTING MINUTES...")

# Кнопка M5 (Центральная) - ПРИБАВЛЯЕТ (+1)
def buttonA_wasPressed():
    global mode, set_h, set_m
    if mode == 1:
        set_h = (set_h + 1) % 24
    elif mode == 2:
        set_m = (set_m + 1) % 60
    update_ui()

# Кнопка B (Боковая) - ЛИСТАЕТ (Часы -> Минуты)
def buttonB_wasPressed():
    global mode, set_h, set_m
    if mode == 0:
        h, m, s = get_time_now()
        set_h, set_m = h, m
        mode = 1
    elif mode == 1:
        mode = 2
    elif mode == 2:
        mode = 0 # Просто выход без сохранения при листании
    update_ui()

# Кнопка ПИТАНИЯ (Power) - ПРИМЕНЯЕТ (Save)
def buttonPWR_wasPressed():
    global mode, set_h, set_m
    if mode != 0:
        # Пытаемся сохранить время всеми доступными способами
        try:
            rtc.set_time(set_h, set_m, 0)
            rtc.set_date(2026, 4, 21)
        except:
            try:
                rtc.datetime((2026, 4, 21, 2, set_h, set_m, 0))
            except:
                pass
        
        # Мигнем диодом, что сохранение прошло
        led.value(0)
        wait(0.2)
        led.value(1)
        
        mode = 0 # Возврат в режим часов
    update_ui()

# Регистрация кнопок
btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)
if hasattr(btn, 'PWR'): # Проверка наличия кнопки питания в библиотеке
    btnPWR.wasPressed(buttonPWR_wasPressed)
else:
    # Если кнопка питания не подхватывается, 
    # используем длинное нажатие B как альтернативу
    btnB.pressFor(1.0, buttonPWR_wasPressed)

while True:
    update_ui()
    wait(0.5 if mode == 0 else 0.1)