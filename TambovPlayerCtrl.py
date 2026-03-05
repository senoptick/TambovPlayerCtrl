#!/usr/bin/env python3
import gpiod
import time
import subprocess
import threading
import sys
from gpiod.line import Direction, Bias

# ==================== НАСТРОЙКИ =====================
CHIP_NAME = '/dev/gpiochip0'               # основной чип на Orange Pi Zero 3

BUTTON_LINES = [9, 6, 5, 8]           # кнопка 1,2,3,4

SOUNDS = [
    "1.wav",  
    "2.wav",   
    "3.wav",  
    "4.wav"   
]

DEBOUNCE_TIME = 0.25          # секунды — антидребезг
LOCK_TIMEOUT = 1.5            # секунды — минимальная пауза между запусками любой мелодии

# ==================== КОД =====================

print(f"Запуск плеера кнопок на {CHIP_NAME}")
print(f"Линии кнопок: {BUTTON_LINES}")
print(f"Звуки:\n" + "\n".join(f"  Кнопка {i+1}: {s}" for i,s in enumerate(SOUNDS)))
print("Нажмите Ctrl+C для выхода")

# Глобальный лок + таймер последнего проигрывания
audio_lock = threading.Lock()
last_play_time = 0.0

def play_sound(sound_file):
    global last_play_time
    now = time.time()
    
    with audio_lock:
        if now - last_play_time < LOCK_TIMEOUT:
            print(f"   Игнор — слишком быстро ({now - last_play_time:.2f} сек)")
            return
        last_play_time = now
    
    print(f"   → Запускаю: {sound_file}")
    # Запуск в фоне, тихо (-q)
    subprocess.Popen(["aplay", "-q", sound_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_multiple_line_values(chip_path, line_offsets):


def main():
    try:
        prev_values = [1] * len(BUTTON_LINES)
        
        with gpiod.request_lines(
            CHIP_NAME,
            consumer="get-multiple-line-values",
            config={tuple(BUTTON_LINES): gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP)},
        ) as request:
            vals = request.get_values()
            for i, val in enumerate(vals):
                now = time.time()
                    
                # Сработало нажатие (переход 1 → 0) и debounce прошёл
                if val == 0 and prev_values[i] == 1 and (now - last_change_times[i] > DEBOUNCE_TIME):
                    last_change_times[i] = now
                    sound = SOUNDS[i]
                    # Запуск в отдельном потоке
                    threading.Thread(target=play_sound, args=(sound,), daemon=True).start()    
            prev_values = vals.copy()
            time.sleep(0.020)  # ~50 Гц — достаточно, CPU почти не грузит

    except PermissionError:
        print("Ошибка: нет доступа к /dev/gpiochip*. Запусти от root или добавь пользователя в группу gpio:")
        print("   sudo usermod -aG gpio $USER   # потом перелогинься")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Ошибка: {CHIP_NAME} не найден. Проверь: ls /dev/gpiochip*")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nВыход по Ctrl+C")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
    finally:
        print("Очистка GPIO...")
        # lines не нужно явно release — with сам закроет

if __name__ == "__main__":
    main()
