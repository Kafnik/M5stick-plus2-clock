from m5stack import *
from m5ui import *
from uiflow import *
import time
import machine

# Настройка экрана под разрешение Plus2 (240x135)
setScreenColor(0x000000)
lcd.setRotation(1) 

# Создаем красивые надписи
# Сдвигаем координаты, чтобы всё было по центру
label_time = M5TextBox(35, 25, "00:00:00", lcd.FONT_DejaVu40, 0x00FF00, rotate=0)
label_date = M5TextBox(65, 80, "20.04.2026", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_author = M5TextBox(60, 110, "M5STACK STUDIO", lcd.FONT_Default, 0x444444, rotate=0)

# В PLUS2 светодиод на G19
led = machine.Pin(19, machine.Pin.OUT)

def update_clock():
    # Используем стандартный модуль time вместо rtc
    t = time.localtime()
    # t[0]-год, t[1]-мес, t[2]-день, t[3]-час, t[4]-мин, t[5]-сек
    
    time_str = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
    date_str = "{:02d}.{:02d}.{:04d}".format(t[2], t[1], t[0])
    
    label_time.setText(time_str)
    label_date.setText(date_str)

# --- УСТАНОВКА ВРЕМЕНИ (сделай это ОДИН РАЗ) ---
# Если у тебя на часах 2000 год, раскомментируй строку ниже, 
# впиши время и запусти один раз. Потом можно снова закомментировать.
# rtc.settime((2026, 4, 20, 20, 15, 0)) 

while True:
    try:
        update_clock()
        
        # Мигаем диодом
        led.value(0)
        wait(0.1)
        led.value(1)
        wait(0.9)
    except Exception as e:
        lcd.clear()
        lcd.print("Error: " + str(e), 0, 0, 0xFF0000)
        break