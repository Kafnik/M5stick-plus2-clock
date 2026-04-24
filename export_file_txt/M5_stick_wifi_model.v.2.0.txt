from m5stack import *
from m5ui import *
from uiflow import *
import time
import machine

# 1. Настройка экрана
setScreenColor(0x000000)
lcd.setRotation(1) # Горизонтально

# Создаем надписи (центровка под Plus 2)
label_time = M5TextBox(35, 30, "Sync...", lcd.FONT_DejaVu40, 0x00FF00, rotate=0)
label_date = M5TextBox(65, 85, "Connecting...", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)
label_status = M5TextBox(60, 115, "M5stack STUDIO", lcd.FONT_Default, 0x444444, rotate=0)

# 2. Подключение к Wi-Fi (Впиши свои данные!)
import wifiCfg
wifiCfg.doConnect('ИМЯ_ТВОЕГО_WIFI', 'ПАРОЛЬ_ОТ_WIFI')

# 3. Синхронизация времени по интернету
# timezone=3 это Москва. Если у тебя другой пояс, поменяй цифру.
from m5stack import rtc
try:
    rtc.ntp_sync(server='pool.ntp.org', tz=3)
    print("Time Synced!")
except:
    print("NTP Sync Failed")

# Светодиод на Plus 2 (G19)
led = machine.Pin(19, machine.Pin.OUT)

def update_display():
    # Получаем текущее время из системы
    t = time.localtime()
    # t[0]-год, t[1]-мес, t[2]-день, t[3]-час, t[4]-мин, t[5]-сек
    
    t_str = "{:02d}:{:02d}:{:02d}".format(t[3], t[4], t[5])
    d_str = "{:02d}.{:02d}.{:04d}".format(t[2], t[1], t[0])
    
    label_time.setText(t_str)
    label_date.setText(d_str)

# ОСНОВНОЙ ЦИКЛ (Тиканье)
while True:
    try:
        update_display()
        
        # Мигаем лампочкой каждую секунду
        led.value(0)
        wait(0.5)
        led.value(1)
        wait(0.5)
    except Exception as e:
        print("Loop error:", e)
        wait(1)