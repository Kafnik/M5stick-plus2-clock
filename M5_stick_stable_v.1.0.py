from m5stack import *
from m5ui import *
from uiflow import *
import machine

# 1. Настройка экрана
setScreenColor(0x000000)
lcd.setRotation(1)

# Переменные
mode = 0  
set_h = 12
set_m = 0

# Интерфейс
label_time = M5TextBox(35, 30, "00:00:00", lcd.FONT_DejaVu40, 0x00FF00, rotate=0)
label_date = M5TextBox(20, 85, "B: MODE | M5: +1", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_info = M5TextBox(30, 115, "POWER: SAVE", lcd.FONT_Default, 0xFF0000, rotate=0)

# ВЫКЛЮЧАЕМ ДИОД (пин 19 в 1), чтобы не жарил
led = machine.Pin(19, machine.Pin.OUT)
led.value(1)

# Работа с временем напрямую
hw_rtc = machine.RTC()

def get_real_time():
    t = hw_rtc.datetime() 
    return t[4], t[5], t[6]

def update_ui():
    global mode, set_h, set_m
    if mode == 0:
        h, m, s = get_real_time()
        label_time.setText("{:02d}:{:02d}:{:02d}".format(h, m, s))
        label_time.setColor(0x00FF00)
        label_info.setText("STATUS: RUNNING")
    elif mode == 1:
        label_time.setText("{:02d} : --".format(set_h))
        label_time.setColor(0xFF0000)
        label_info.setText("SETTING HOURS")
    elif mode == 2:
        label_time.setText("-- : {:02d}".format(set_m))
        label_time.setColor(0xFFFF00)
        label_info.setText("SETTING MINUTES")

# --- КНОПКИ ---

def buttonA_wasPressed():
    # Кнопка M5 (Центральная) - ПРИБАВЛЯЕТ
    global mode, set_h, set_m
    if mode == 1: set_h = (set_h + 1) % 24
    elif mode == 2: set_m = (set_m + 1) % 60
    update_ui()

def buttonB_wasPressed():
    # Кнопка B (Передняя боковая) - ЛИСТАЕТ
    global mode, set_h, set_m
    if mode == 0:
        h, m, s = get_real_time()
        set_h, set_m = h, m
        mode = 1
    elif mode == 1: mode = 2
    elif mode == 2: mode = 1
    update_ui()

def save_and_apply():
    # СОХРАНЕНИЕ
    global mode, set_h, set_m
    if mode != 0:
        # Пишем в железный RTC (Год, Мес, День, День_нед, Час, Мин, Сек, Мс)
        hw_rtc.datetime((2026, 4, 21, 2, set_h, set_m, 0, 0))
        mode = 0
        # Вспышка экрана для подтверждения
        lcd.clear(0xFFFFFF)
        wait(0.1)
        lcd.clear(0x000000)
    update_ui()

# Регистрация кнопок M5 и B
btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)

# РАБОТА С КНОПКОЙ ПИТАНИЯ (Power) БЕЗ 'axp'
# В Plus 2 она часто висит на btnPWR
try:
    btnPWR.wasPressed(save_and_apply)
except NameError:
    # Если btnPWR не найден, используем прямую проверку пина питания
    pwr_key = machine.Pin(35, machine.Pin.IN) # Пин кнопки питания на Plus 2

while True:
    update_ui()
    
    # Если btnPWR не сработал выше, проверяем пин вручную
    try:
        if 'pwr_key' in locals() and pwr_key.value() == 0:
            save_and_apply()
            wait(0.5)
    except:
        pass
        
    wait(0.5 if mode == 0 else 0.1)