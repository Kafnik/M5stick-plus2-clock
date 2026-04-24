from m5stack import *
from m5ui import *
from uiflow import *
import machine
import time

# 1. Настройка экрана
setScreenColor(0x000000)
lcd.setRotation(1)

# Переменные (Дата по твоему формату)
mode = 0  
now_h, now_m, now_day, now_month, now_year = 12, 0, 22, 4, 2026
press_start = 0

# Интерфейс
lcd.rect(0, 0, 240, 22, 0x111111, 0x111111)
label_top = M5TextBox(5, 4, "M5STACK STUDIO OS v3.5", lcd.FONT_Default, 0x00CCFF, rotate=0)
label_time = M5TextBox(35, 35, "00:00:00", lcd.FONT_DejaVu40, 0x00FF00, rotate=0)
label_date = M5TextBox(50, 85, "00.00.0000", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)

# ПОЛНОСТЬЮ ВЫКЛЮЧАЕМ ДИОД (пин 19), чтобы не грелся как на фото
led = machine.Pin(19, machine.Pin.OUT)
led.value(1) 

# Пин кнопки питания (Power Button на боку)
pwr_key = machine.Pin(35, machine.Pin.IN) 

hw_rtc = machine.RTC()

def update_ui():
    global mode, now_h, now_m, now_day, now_month, now_year
    t = hw_rtc.datetime()
    if mode == 0:
        label_time.setText("{:02d}:{:02d}:{:02d}".format(t[4], t[5], t[6]))
        label_date.setText("{:02d}.{:02d}.{:04d}".format(t[2], t[1], t[0]))
        label_time.setColor(0x00FF00)
    else:
        label_time.setText("{:02d}:{:02d}".format(now_h, now_m))
        label_date.setText("{:02d}.{:02d}.{:04d}".format(now_day, now_month, now_year))
        # Цвета для режима настройки
        if mode == 1: label_time.setColor(0xFF0000) # Часы
        elif mode == 2: label_time.setColor(0xFFFF00) # Минуты
        elif mode >= 3: label_date.setColor(0x00CCFF) # Дата

def buttonA_wasPressed():
    global mode, now_h, now_m, now_day, now_month, now_year
    if mode == 1: now_h = (now_h + 1) % 24
    elif mode == 2: now_m = (now_m + 1) % 60
    elif mode == 3: now_day = (now_day % 31) + 1
    elif mode == 4: now_month = (now_month % 12) + 1
    elif mode == 5: now_year = (now_year + 1) if now_year < 2035 else 2026
    update_ui()

def buttonB_wasPressed():
    global mode, now_h, now_m, now_day, now_month, now_year
    if mode == 0:
        t = hw_rtc.datetime()
        now_year, now_month, now_day, _, now_h, now_m, _, _ = t
        mode = 1
    else:
        mode = mode + 1
        if mode > 5: mode = 1
    update_ui()

btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)

# ГЛАВНЫЙ ЦИКЛ
while True:
    update_ui()
    
    # ПРОВЕРКА ЗАЖАТИЯ БОКОВОЙ КНОПКИ (PWR)
    if pwr_key.value() == 0:
        if press_start == 0:
            press_start = time.ticks_ms()
        
        # Считаем время зажатия
        duration = time.ticks_diff(time.ticks_ms(), press_start) / 1000.0
        
        # Рисуем шкалу прогресса сохранения
        # Если дойдет до конца (3 сек) — стик вырубится железно
        bar_width = int((duration / 2.5) * 240) 
        if bar_width > 240: bar_width = 240
        lcd.rect(0, 125, bar_width, 10, 0x00FF00, 0x00FF00)
        
    elif press_start != 0:
        # Кнопку отпустили — проверяем, сколько держали
        duration = time.ticks_diff(time.ticks_ms(), press_start) / 1000.0
        
        # Если держал больше 0.2 сек, но меньше 2.5 сек — СОХРАНЯЕМ
        if 0.2 < duration < 2.5:
            hw_rtc.datetime((now_year, now_month, now_day, 0, now_h, now_m, 0, 0))
            mode = 0
            # Вспышка для подтверждения
            lcd.clear(0x00FF00)
            wait(0.2)
            lcd.clear(0x000000)
        
        # Убираем шкалу и сбрасываем таймер
        lcd.rect(0, 125, 240, 10, 0x000000, 0x000000)
        press_start = 0

    wait(0.1)