from m5stack import *
from m5ui import *
from uiflow import * 
import machine

# 1. Настройка экрана
setScreenColor(0x000000)
lcd.setRotation(1)

# Переменные
mode = 0  
now_h, now_m, now_day, now_month, now_year = 12, 0, 21, 4, 2026
last_sec = -1 

# Интерфейс (PrimeBot Style)
lcd.rect(0, 0, 240, 22, 0x111111, 0x111111)
label_top = M5TextBox(5, 4, "M5STACK STUDIO OS v3.4", lcd.FONT_Default, 0x00CCFF, rotate=0)
label_time = M5TextBox(35, 35, 000000, lcd.FONT_DejaVu40, 0x00FF00, rotate=0)
label_date = M5TextBox(50, 85, 00.00.0000, lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_info = M5TextBox(10, 115, B NEXT  M5 +1  PWR APPLY, lcd.FONT_Default, 0xAAAAAA, rotate=0)

# Светодиод ВЫКЛ (чтобы не грелся)
led = machine.Pin(19, machine.Pin.OUT)
led.value(1)

rtc_hw = machine.RTC()

def update_ui(force=False)
    global mode, now_h, now_m, now_day, now_month, now_year, last_sec
    t = rtc_hw.datetime()
    if not force and mode == 0 and t[6] == last_sec return
    last_sec = t[6]

    if mode == 0
        label_time.setText({02d}{02d}{02d}.format(t[4], t[5], t[6]))
        label_date.setText({02d}.{02d}.{04d}.format(t[2], t[1], t[0]))
        label_time.setColor(0x00FF00)
        label_date.setColor(0xFFFFFF)
    else
        label_time.setText({02d}{02d}.format(now_h, now_m))
        label_date.setText({02d}.{02d}.{04d}.format(now_day, now_month, now_year))
        # Подсветка активного поля
        if mode == 1 label_time.setColor(0xFF0000)
        elif mode == 2 label_time.setColor(0xFFFF00)
        elif mode = 3 label_date.setColor(0xFF0000 if mode == 3 else 0xFFFF00 if mode == 4 else 0x00CCFF)

def buttonA_wasPressed()
    global mode, now_h, now_m, now_day, now_month, now_year
    if mode == 1 now_h = (now_h + 1) % 24
    elif mode == 2 now_m = (now_m + 1) % 60
    elif mode == 3 now_day = (now_day % 31) + 1
    elif mode == 4 now_month = (now_month % 12) + 1
    elif mode == 5 now_year = (now_year + 1) if now_year  2030 else 2024
    update_ui(force=True)

def buttonB_wasPressed()
    global mode, now_h, now_m, now_day, now_month, now_year
    if mode == 0
        t = rtc_hw.datetime()
        now_year, now_month, now_day, _, now_h, now_m, _, _ = t
        mode = 1
    else
        mode = mode + 1
        if mode  5 mode = 1
    update_ui(force=True)

def force_save()
    global mode
    if mode != 0
        rtc_hw.datetime((now_year, now_month, now_day, 0, now_h, now_m, 0, 0))
        mode = 0
        lcd.fill_rect(0, 110, 240, 25, 0x00FF00) # Зеленая вспышка - успех
        wait(0.3)
        lcd.fill_rect(0, 110, 240, 25, 0x111111)
    update_ui(force=True)

# Регистрация кнопок
btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)

# Создаем объект для работы с чипом питания напрямую
try
    import i2c_bus
    # Адрес чипа питания обычно 0x34
    axp_i2c = i2c_bus.easyI2C(i2c_bus.PORTA, 0x34)
except
    axp_i2c = None

while True
    update_ui()
    
    # ПРОВЕРКА КНОПКИ ПИТАНИЯ ЧЕРЕЗ РЕГИСТРЫ (Самый надежный способ)
    pwr_pressed = False
    try
        # Пробуем стандартную библиотеку axp
        if axp.getBtnPress() == 1 pwr_pressed = True
    except
        try
            # Пробуем системный статус
            if power.get_button_status() == 1 pwr_pressed = True
        except
            pass
            
    if pwr_pressed
        force_save()
        wait(0.5)

    wait(0.1)