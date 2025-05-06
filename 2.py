from pydobot import Dobot
import time

port = '/dev/ttyUSB0'  # Обнови порт при необходимости

# Подключение к Dobot
device = Dobot(port=port)
time.sleep(1)

# Начальная позиция
x = 200
y = 0
z = 0  # Начинаем с безопасной высоты
r = 0

# Перемещаемся в начальную точку
device.move_to(x, y, z, r)
time.sleep(1)

print("\n=== Калибровка высоты Z ===")
print("Добро пожаловать в режим калибровки!")
print("Нажимай:\n  [w] для опускания Z\n  [s] для поднятия Z\n  [q] чтобы завершить\n")

try:
    while True:
        print(f"Текущий уровень Z: {z:.2f}")
        key = input("Команда (w/s/q): ").lower().strip()

        if key == 'w':
            z -= 1
        elif key == 's':
            z += 1
        elif key == 'q':
            print(f" Финальное значение Z: {z:.2f}")
            break
        else:
            print("Неверная команда. Используй только w/s/q.")
            continue

        # Движение к новой позиции
        device.move_to(x, y, z, r)
        time.sleep(0.5)

except KeyboardInterrupt:
    print(" Остановлено вручную.")

finally:
    device.close()
    print(" Dobot отключён.")
