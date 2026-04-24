from m5stack import *
from m5ui import *
from uiflow import *
import machine
import time

# 1. СРАЗУ ГАСИМ ДИОД (Пин 19)
led = machine.Pin(19, machine.Pin.OUT)
led.value(0) 

# 2. Настройка экрана
setScreenColor(0x000000)
lcd.setRotation(1)

# Переменные
mode = 0  
now_h, now_m, now_day, now_month, now_year = 12, 0, 22, 4, 2026
press_start = 0
last_activity = time.ticks_ms()
TIMEOUT = 60000 # 60 секунд

# Интерфейс
label_time = M5TextBox(35, 35, "00:00:00", lcd.FONT_DejaVu40, 0x00FF00, rotate=0)
label_date = M5TextBox(50, 85, "00.00.0000", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)

edit_labels = ["SYSTEM READY", "EDIT: HOURS", "EDIT: MINUTES", "EDIT: DAY", "EDIT: MONTH", "EDIT: YEAR"]

def draw_ui_design(status_idx=0):
    # Верхняя панель
    lcd.rect(0, 0, 240, 22, 0x111111, 0x111111)
    lcd.font(lcd.FONT_Default)
    lcd.print("M5STACK STUDIO v4.3", 5, 4, 0x00CCFF)
    lcd.line(0, 22, 240, 22, 0x00CCFF)
    # Нижняя панель
    lcd.rect(0, 112, 240, 20, 0x000000, 0x000000)
    lcd.print(edit_labels[status_idx], 10, 115, 0x888888)

def reset_timer():
    global last_activity
    last_activity = time.ticks_ms()

# Кнопка питания (пин 35)
pwr_key = machine.Pin(35, machine.Pin.IN) 
hw_rtc = machine.RTC()

def update_display():
    global mode, now_h, now_m, now_day, now_month, now_year
    t = hw_rtc.datetime()
    if mode == 0:
        label_time.setText("{:02d}:{:02d}:{:02d}".format(t[4], t[5], t[6]))
        label_date.setText("{:02d}.{:02d}.{:04d}".format(t[2], t[1], t[0]))
        label_time.setColor(0x00FF00)
        label_date.setColor(0xFFFFFF)
    else:
        label_time.setText("{:02d}:{:02d}".format(now_h, now_m))
        label_date.setText("{:02d}.{:02d}.{:04d}".format(now_day, now_month, now_year))
        # Цвета
        if mode == 1: label_time.setColor(0xFF0000)
        elif mode == 2: label_time.setColor(0xFFFF00)
        elif mode == 3: label_date.setColor(0x00FF00)
        elif mode == 4: label_date.setColor(0xFF00FF)
        elif mode == 5: label_date.setColor(0x00CCFF)

def buttonA_wasPressed():
    reset_timer()
    global mode, now_h, now_m, now_day, now_month, now_year
    if mode != 0:
        if mode == 1: now_h = (now_h + 1) % 24
        elif mode == 2: now_m = (now_m + 1) % 60
        elif mode == 3: now_day = (now_day % 31) + 1
        elif mode == 4: now_month = (now_month % 12) + 1
        elif mode == 5: now_year = (now_year + 1) if now_year < 2030 else 2000
        update_display()

def buttonB_wasPressed():
    reset_timer()
    global mode, now_h, now_m, now_day, now_month, now_year
    if mode == 0:
        t = hw_rtc.datetime()
        now_year, now_month, now_day, _, now_h, now_m, _, _ = t
        mode = 1
    else:
        mode = (mode + 1) if mode < 6 else 1
    draw_ui_design(mode)
    update_display()

btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)

draw_ui_design(0)

while True:
    update_display()
    
    # ПРОВЕРКА ТАЙМЕРА
    if time.ticks_diff(time.ticks_ms(), last_activity) > TIMEOUT:
        lcd.clear(0x000000)
        lcd.print("SHUTDOWN...", 70, 60, 0xFF0000)
        wait(1)
        # ИСПОЛЬЗУЕМ БОЛЕЕ СОВМЕСТИМУЮ КОМАНДУ ВЫКЛЮЧЕНИЯ
        try:
            from m5stack import power
            power.powerOff()
        except:
            # Если не сработало, просто гасим экран и уходим в вечный цикл (софт-сон)
            lcd.setBrightness(0)
            while True: pass

    # КНОПКА ПИТАНИЯ
    if pwr_key.value() == 0:
        reset_timer()
        if press_start == 0:
            press_start = time.ticks_ms()
        
        duration = time.ticks_diff(time.ticks_ms(), press_start) / 1000.0
        bar_w = int((duration / 2.0) * 240)
        if bar_w > 240: bar_w = 240
        lcd.rect(0, 130, bar_w, 5, 0x00FF00, 0x00FF00)
        
    elif press_start != 0:
        duration = time.ticks_diff(time.ticks_ms(), press_start) / 1000.0
        if 0.1 < duration < 1.8:
            hw_rtc.datetime((now_year, now_month, now_day, 0, now_h, now_m, 0, 0))
            mode = 0
            lcd.rect(0, 0, 240, 135, 0x00FF00, 0x00FF00)
            wait(0.1)
            lcd.rect(0, 0, 240, 135, 0x000000, 0x000000)
            draw_ui_design(0)
        
        lcd.rect(0, 130, 240, 5, 0x000000, 0x000000)
        press_start = 0

    wait(0.1)