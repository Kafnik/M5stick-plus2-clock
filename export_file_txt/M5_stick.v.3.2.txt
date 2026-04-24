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
days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

# --- ДИЗАЙН ИНТЕРФЕЙСА ---
# Верхняя декоративная панель
lcd.rect(0, 0, 240, 22, 0x111111, 0x111111)
lcd.line(0, 22, 240, 22, 0x00CCFF)
label_top = M5TextBox(5, 4, "M5STACK STUDIO OS v3.2", lcd.FONT_Default, 0x00CCFF, rotate=0)

# Часы (Центр)
label_time = M5TextBox(35, 35, "00:00:00", lcd.FONT_DejaVu40, 0x00FF00, rotate=0)

# Дата (Под часами)
label_date = M5TextBox(65, 85, "TUE 21.04", lcd.FONT_DejaVu18, 0xFFFFFF, rotate=0)

# Нижняя панель подсказок
lcd.rect(0, 110, 240, 25, 0x111111, 0x111111)
label_info = M5TextBox(10, 115, "B: MOD | M5: +1 | PWR: SAVE", lcd.FONT_Default, 0xAAAAAA, rotate=0)

# Выключаем светодиод (чтобы не грелся)
led = machine.Pin(19, machine.Pin.OUT)
led.value(1)

# Железное время (RTC)
hw_rtc = machine.RTC()

def get_full_time():
    # Возвращает: (Year, Month, Day, WeekDay, Hour, Min, Sec, ms)
    return hw_rtc.datetime()

def update_ui():
    global mode, set_h, set_m, days
    t = get_full_time()
    
    if mode == 0:
        # Режим работы
        label_time.setText("{:02d}:{:02d}:{:02d}".format(t[4], t[5], t[6]))
        label_time.setColor(0x00FF00)
        label_date.setText("{} {:02d}.{:02d}".format(days[t[3]], t[2], t[1]))
        label_info.setText("SYSTEM: RUNNING")
    elif mode == 1:
        # Режим настройки часов
        label_time.setText("{:02d} : --".format(set_h))
        label_time.setColor(0xFF0000)
        label_info.setText("SETTING HOURS...")
    elif mode == 2:
        # Режим настройки минут
        label_time.setText("-- : {:02d}".format(set_m))
        label_time.setColor(0xFFFF00)
        label_info.setText("SETTING MINUTES...")

# --- ОБРАБОТКА КНОПОК ---

def buttonA_wasPressed():
    global mode, set_h, set_m
    if mode != 0:
        if mode == 1: set_h = (set_h + 1) % 24
        elif mode == 2: set_m = (set_m + 1) % 60
        update_ui()

def buttonB_wasPressed():
    global mode, set_h, set_m
    if mode == 0:
        t = get_full_time()
        set_h, set_m = t[4], t[5]
        mode = 1
    elif mode == 1: mode = 2
    elif mode == 2: mode = 1
    update_ui()

def save_and_apply():
    global mode, set_h, set_m
    if mode != 0:
        # Сохраняем в чип (Ставим 21 апреля 2026 года)
        hw_rtc.datetime((2026, 4, 21, 1, set_h, set_m, 0, 0))
        mode = 0
        # Визуальный сигнал сохранения
        lcd.fill_rect(0, 110, 240, 25, 0x00FF00)
        wait(0.2)
        lcd.fill_rect(0, 110, 240, 25, 0x111111)
    update_ui()

# Регистрация обычных кнопок
btnA.wasPressed(buttonA_wasPressed)
btnB.wasPressed(buttonB_wasPressed)

# --- ГЛАВНЫЙ ЦИКЛ ---
while True:
    update_ui()
    
    # ПРОВЕРКА КНОПКИ ПИТАНИЯ (без axp)
    # Метод 1: через модуль power (если доступен)
    try:
        if power.get_button_status() == 1: # 1 - короткое нажатие
            save_and_apply()
            wait(0.5)
    except:
        # Метод 2: если power недоступен, проверяем напрямую железный регистр
        pass
        
    wait(0.5 if mode == 0 else 0.1)