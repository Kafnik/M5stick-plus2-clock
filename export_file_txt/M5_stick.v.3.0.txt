from m5stack import *
from m5ui import *
from uiflow import *
import machine

# 1. Настройка экрана
setScreenColor(0x000000)
lcd.setRotation(1) # Горизонтальный режим

# Переменные для работы меню
mode = 0  # 0: Часы, 1: Настройка Часов, 2: Настройка Минут
set_h = 12
set_m = 0

# Графические элементы (под Plus 2)
label_time = M5TextBox(35, 30, "00:00:00", lcd.FONT_DejaVu40, 0x00FF00, rotate=0)
label_date = M5TextBox(65, 85, "B: MENU / A: +1", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_info = M5TextBox(60, 115, "MODE: RUNNING", lcd.FONT_Default, 0x555555, rotate=0)

# Функция получения времени с защитой от ошибок
def get_time_data():
    try:
        # Пробуем самый вероятный способ для Plus 2
        return rtc.get_time() # Возвращает (час, мин, сек)
    except:
        try:
            # Запасной вариант
            t = rtc.now()
            return t[3], t[4], t[5]
        except:
            # Если совсем всё плохо - берем системное время
            import time
            t = time.localtime()
            return t[3], t[4], t[5]

def update_display():
    global mode, set_h, set_m
    if mode == 0:
        h, m, s = get_time_data()
        label_time.setText("{:02d}:{:02d}:{:02d}".format(h, m, s))
        label_time.setColor(0x00FF00) # Зеленый
        label_info.setText("MODE: RUNNING")
    elif mode == 1:
        label_time.setText("{:02d} : --".format(set_h))
        label_time.setColor(0xFF0000) # Красный (редактируем часы)
        label_info.setText("SETTING: HOURS")
    elif mode == 2:
        label_time.setText("-- : {:02d}".format(set_m))
        label_time.setColor(0xFFFF00) # Желтый (редактируем минуты)
        label_info.setText("SETTING: MINUTES")

# Кнопка M5 (Центральная) - Прибавляет значение
def buttonA_wasPressed():
    global mode, set_h, set_m
    if mode == 1:
        set_h = (set_h + 1) % 24
    elif mode == 2:
        set_m = (set_m + 1) % 60
    update_display()

# Кнопка B (Боковая) - Переключает режимы
def buttonB_wasPressed():
    global mode, set_h, set_m
    if mode == 0:
        # Заходим в настройки
        h, m, s = get_time_data()
        set_h, set_m = h, m
        mode = 1
    elif mode == 1:
        mode = 2 # Переходим к минутам
    elif mode == 2:
        # СОХРАНЯЕМ В ЖЕЛЕЗО
        try:
            rtc.set_time(set_h, set_m, 0)
            # Также на всякий случай поставим дату, чтобы чип не сбоил
            rtc.set_date(2026, 4, 21) 
        except:
            # Запасной метод сохранения
            rtc.settime((2026, 4, 21, set_h, set_m, 0))
        mode = 0 # Выход в режим часов
    update_display()

# Регистрируем кнопки
btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)

# Лампочка для Plus 2 (G19)
led = machine.Pin(19, machine.Pin.OUT)

# Запуск
while True:
    update_display()
    if mode == 0:
        led.value(0) # Мигаем только в обычном режиме
        wait(0.5)
        led.value(1)
        wait(0.5)
    else:
        wait(0.1) # В меню обновляем быстрее для четкого нажатия