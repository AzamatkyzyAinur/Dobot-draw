import os
import time
import cv2
import numpy as np
from pydobot import Dobot

# === Dobot & Drawing Configuration ===
port = '/dev/ttyUSB0'  # Обновите порт при необходимости
scale = 0.5  # Масштаб: пиксель -> мм
x_offset = 150  # Смещение по X (мм)
y_offset = -50  # Смещение по Y (мм)
pen_down_z = -59  # Высота ручки при рисовании
pen_up_z = -55  # Высота ручки при перемещении

def pixel_to_robot(px, py):
    x = px * scale + x_offset
    y = py * scale + y_offset
    return x, y

def get_first_image(folder):
    for file in os.listdir(folder):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            return os.path.join(folder, file)
    raise FileNotFoundError("Нет изображений в папке.")

def process_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (200, 200))
    _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    return binary

def is_in_workspace(rx, ry):
    return 100 <= rx <= 250 and -100 <= ry <= 100

def draw_contours_only(device, binary_image):
    # Инвертируем изображение, чтобы найти контуры вокруг черных областей
    inverted = cv2.bitwise_not(binary_image)
    
    # Находим контуры (обрамляющие линии черных областей)
    contours, _ = cv2.findContours(inverted, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours_drawn = 0
    
    print(f"Найдено {len(contours)} контуров")
    
    # Рисуем каждый контур
    for i, contour in enumerate(contours):
        # Пропускаем очень маленькие контуры (возможно, шум)
        if cv2.contourArea(contour) < 3:
            continue
            
        # Преобразуем контур в список точек
        points = [point[0] for point in contour]
        if len(points) < 3:  # Пропускаем слишком короткие контуры
            continue
            
        # Получаем первую точку
        first_point = points[0]
        rx, ry = pixel_to_robot(first_point[0], first_point[1])
        
        if not is_in_workspace(rx, ry):
            continue
            
        # Перемещаемся к началу с поднятой ручкой
        device.move_to(rx, ry, pen_up_z, 0)
        time.sleep(0.1)
        
        # Опускаем ручку
        device.move_to(rx, ry, pen_down_z, 0)
        time.sleep(0.05)
        
        # Рисуем контур
        for point in points[1:]:
            rx, ry = pixel_to_robot(point[0], point[1])
            if is_in_workspace(rx, ry):
                device.move_to(rx, ry, pen_down_z, 0)
                time.sleep(0.01)
        
        # Замыкаем контур, возвращаясь к первой точке
        rx, ry = pixel_to_robot(first_point[0], first_point[1])
        device.move_to(rx, ry, pen_down_z, 0)
        time.sleep(0.01)
        
        # Поднимаем ручку
        device.move_to(rx, ry, pen_up_z, 0)
        time.sleep(0.05)
        
        contours_drawn += 1
        if i % 5 == 0:  # Выводим статус каждые 5 контуров
            print(f"Нарисовано {contours_drawn} контуров из {len(contours)}")
    
    return contours_drawn

# === Основная программа ===
if __name__ == '__main__':
    try:
        image_folder = 'image'
        image_path = get_first_image(image_folder)
        print(f"📷 Используем изображение: {image_path}")
        
        # Обработка изображения
        binary_image = process_image(image_path)
        
        # Подключение к Dobot
        print("Подключение к Dobot...")
        device = Dobot(port=port)
        time.sleep(1)
        
        # Перемещение в стартовую позицию
        print("Перемещение в стартовую позицию...")
        device.move_to(200, 0, pen_up_z, 0)
        time.sleep(1)
        
        # Рисование изображения (только контуры)
        print(" Рисование изображения...")
        total_contours = draw_contours_only(device, binary_image)
        
        # Возвращение домой
        print(" Возвращение в исходную позицию...")
        device.move_to(200, 0, pen_up_z, 0)
        print(f"Рисование завершено! Нарисовано {total_contours} контуров")
        
    except Exception as e:
        print("Ошибка:", e)
        import traceback
        traceback.print_exc()
    finally:
        if 'device' in locals():
            device.close()
            print("Dobot отключён.")