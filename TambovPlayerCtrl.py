#!/usr/bin/env python3
import time
import subprocess
import threading
import sys
import wiringpi
import os
import signal

# ==================== НАСТРОЙКИ =====================

BUTTON_LINES = [2, 5, 7, 8]  # wiringPi номера пинов

SOUNDS = [
    "1.wav",
    "2.wav",
    "3.wav",
    "4.wav"
]

DEBOUNCE_TIME = 0.25
LOCK_TIMEOUT = 1.5

# ==================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ =====================

audio_lock = threading.Lock()
last_play_time = 0.0
current_player = None

# ==================== ФУНКЦИИ =====================

def play_sound(sound_file):
    global last_play_time, current_player
    now = time.time()

    with audio_lock:
        if now - last_play_time < LOCK_TIMEOUT:
            print(f"   Игнор — слишком быстро ({now - last_play_time:.2f} сек)")
            return
        last_play_time = now

    print(f"   → Запускаю: {sound_file}")
    if current_player is not None:
        print("cheto igraet")
        os.killpg(current_player.pid, signal.SIGTERM)
        current_player.wait(timeout=0.5)
            # или более жёстко: os.kill(current_player.pid, signal.SIGKILL)
    
    current_player = subprocess.Popen(
        ["aplay", "q", sound_file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid          # ← важно: новая process group
    )
    
# ==================== ОСНОВНОЙ КОД =====================

def main():

    print("Запуск плеера кнопок (WiringPi)")
    print(f"Линии кнопок: {BUTTON_LINES}")

    for i, s in enumerate(SOUNDS):
        print(f"  Кнопка {i+1}: {s}")

    print("Нажмите Ctrl+C для выхода")

    # инициализация wiringPi
    wiringpi.wiringPiSetup()

    # настройка пинов
    for pin in BUTTON_LINES:
        wiringpi.pinMode(pin, wiringpi.INPUT)
        wiringpi.pullUpDnControl(pin, wiringpi.PUD_UP)

    prev_values = [1] * len(BUTTON_LINES)
    last_change_times = [0.0] * len(BUTTON_LINES)

    try:
        while True:

            for i, pin in enumerate(BUTTON_LINES):

                val = wiringpi.digitalRead(pin)
                now = time.time()
                # нажатие (1 -> 0)
                if val == 0 and prev_values[i] == 1 and (now - last_change_times[i] > DEBOUNCE_TIME):

                    last_change_times[i] = now
                    sound = SOUNDS[i]

                    threading.Thread(
                        target=play_sound,
                        args=(sound,),
                        daemon=True
                    ).start()

                prev_values[i] = val

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nВыход")


if __name__ == "__main__":
    main()
