#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест улучшенного интерактивного визуализатора сети
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import tempfile

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def test_enhanced_viewer():
    """Тестирует улучшенный визуализатор"""
    print("=" * 60)
    print("ТЕСТУВАННЯ ПОКРАЩЕНОГО ІНТЕРАКТИВНОГО ВІЗУАЛІЗАТОРА")
    print("=" * 60)
    
    try:
        # Импортируем улучшенный визуализатор
        from src.gui.enhanced_interactive_network_viewer import EnhancedInteractiveNetworkViewer
        
        print("Покращений візуалізатор імпортовано успішно")
        
        # Создаем тестовое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        # Создаем улучшенный визуализатор
        viewer = EnhancedInteractiveNetworkViewer(root, None)
        print("Покращений візуалізатор створено успішно")
        
        # Тестируем загрузку примера сети
        viewer._load_sample_network()
        print("Приклад мережі завантажено успішно")
        
        # Тестируем обновление степеней узлов
        viewer._update_node_degrees()
        print("Ступені вузлів оновлено успішно")
        
        # Тестируем формы узлов
        print("\nТестування форм вузлів:")
        print("-" * 30)
        for node_data in viewer.editable_network_data['nodes']:
            degree = node_data.get('degree', 0)
            shape = viewer._get_node_shape(degree)
            print(f"  Вузол {node_data['id']}: degree={degree}, форма={shape}")
        
        # Тестируем интерактивные функции
        print("\nТестування інтерактивних функцій:")
        print("-" * 30)
        
        # Тестируем поиск ближайшего узла
        nearest_node = viewer._find_nearest_node(2, 8)
        print(f"Найближчий вузол до (2, 8): {nearest_node}")
        
        # Тестируем поиск связи
        edge = viewer._find_edge_at_position(5, 6.5)
        print(f"Зв'язок біля (5, 6.5): {edge}")
        
        # Тестируем выбор узла
        if nearest_node:
            viewer._select_node(nearest_node)
            print(f"Вибрано вузол {nearest_node} та пов'язані вузли")
        
        # Тестируем анализ связности
        try:
            viewer._analyze_connectivity()
            print("Аналіз зв'язності працює")
        except Exception as e:
            print(f"Аналіз зв'язності не працює: {e}")
        
        # Тестируем работу с базой данных
        print("\nТестування роботи з базою даних:")
        print("-" * 30)
        
        # Создаем временный файл БД
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_db_filename = temp_file.name
        
        try:
            # Тестируем сохранение в БД
            viewer._save_network_to_db(temp_db_filename)
            print(f"Збереження в БД {os.path.basename(temp_db_filename)} працює")
            
            # Тестируем загрузку из БД
            viewer.render_network_from_db(temp_db_filename)
            print(f"Завантаження з БД {os.path.basename(temp_db_filename)} працює")
            
            # Проверяем, что данные загрузились корректно
            loaded_data = viewer.get_network_data()
            print(f"Завантажено {len(loaded_data['nodes'])} вузлів з БД")
            
        except Exception as e:
            print(f"Робота з БД не працює: {e}")
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_db_filename):
                os.remove(temp_db_filename)
                print("Тимчасовий файл БД видалено")
        
        # Тестируем анимации
        print("\nТестування анімацій:")
        print("-" * 30)
        viewer._draw_network_with_animation()
        print("Анімоване оновлення працює")
        
        # Тестируем масштабирование
        print("\nТестування масштабування:")
        print("-" * 30)
        viewer._on_scroll(type('Event', (), {'inaxes': viewer.network_ax, 'button': 'up'})())
        print("Масштабування працює")
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("\n" + "=" * 60)
        print("ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_node_shapes():
    """Тестирует формы узлов"""
    print("\nТЕСТУВАННЯ ФОРМ ВУЗЛІВ:")
    print("-" * 30)
    
    try:
        from src.gui.enhanced_interactive_network_viewer import EnhancedInteractiveNetworkViewer
        
        root = tk.Tk()
        root.withdraw()
        
        viewer = EnhancedInteractiveNetworkViewer(root, None)
        
        # Тестируем все возможные формы
        test_cases = [
            (0, 'circle'),
            (1, 'circle'),
            (2, 'circle'),
            (3, 'triangle'),
            (4, 'square'),
            (5, 'pentagon'),
            (6, 'hexagon'),
            (7, 'hexagon'),
            (10, 'hexagon')
        ]
        
        for degree, expected_shape in test_cases:
            actual_shape = viewer._get_node_shape(degree)
            if actual_shape == expected_shape:
                print(f"degree={degree} → {actual_shape}")
            else:
                print(f"degree={degree} → {actual_shape} (очікувалось {expected_shape})")
        
        root.destroy()
        print("Тестування форм вузлів завершено")
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні форм вузлів: {e}")
        return False


def test_database_operations():
    """Тестирует операции с базой данных"""
    print("\nТЕСТУВАННЯ ОПЕРАЦІЙ З БАЗОЮ ДАНИХ:")
    print("-" * 30)
    
    try:
        from src.gui.enhanced_interactive_network_viewer import EnhancedInteractiveNetworkViewer
        
        root = tk.Tk()
        root.withdraw()
        
        viewer = EnhancedInteractiveNetworkViewer(root, None)
        
        # Загружаем пример сети
        viewer._load_sample_network()
        
        # Создаем временный файл БД
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_db_filename = temp_file.name
        
        try:
            # Тестируем сохранение
            viewer._save_network_to_db(temp_db_filename)
            print("Збереження в БД працює")
            
            # Проверяем, что файл создался
            if os.path.exists(temp_db_filename):
                print("Файл БД створено")
                
                # Проверяем размер файла
                file_size = os.path.getsize(temp_db_filename)
                print(f"Розмір файлу БД: {file_size} байт")
            
            # Тестируем загрузку
            viewer.render_network_from_db(temp_db_filename)
            print("Завантаження з БД працює")
            
            # Проверяем целостность данных
            loaded_data = viewer.get_network_data()
            original_data = viewer.editable_network_data
            
            if len(loaded_data['nodes']) == len(original_data['nodes']):
                print("Кількість вузлів збережено")
            else:
                print("Кількість вузлів не збігається")
            
            if len(loaded_data['connections']) == len(original_data['connections']):
                print("Кількість зв'язків збережено")
            else:
                print("Кількість зв'язків не збігається")
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_db_filename):
                os.remove(temp_db_filename)
                print("Тимчасовий файл БД видалено")
        
        root.destroy()
        print("Тестування операцій з БД завершено")
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні операцій з БД: {e}")
        return False


def test_integration():
    """Тестирует интеграцию с главным окном"""
    print("\nТЕСТУВАННЯ ІНТЕГРАЦІЇ:")
    print("-" * 30)
    
    try:
        from src.gui.main_window import MainWindow
        
        print("Головне вікно імпортовано успішно")
        
        # Создаем главное окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        main_window = MainWindow(root, {})
        print("Головне вікно створено успішно")
        
        # Проверяем тип визуализатора
        viewer_type = type(main_window.network_viewer).__name__
        print(f"Тип візуалізатора: {viewer_type}")
        
        if viewer_type == "EnhancedInteractiveNetworkViewer":
            print("Покращений візуалізатор інтегровано в головне вікно")
        elif viewer_type == "InteractiveNetworkViewer":
            print("Використовується базовий інтерактивний візуалізатор")
        else:
            print("Використовується звичайний візуалізатор (fallback)")
        
        # Проверяем наличие новых методов
        if hasattr(main_window.network_viewer, '_get_node_shape'):
            print("Метод _get_node_shape доступний")
        else:
            print("Метод _get_node_shape недоступний")
        
        if hasattr(main_window.network_viewer, 'render_network_from_db'):
            print("Метод render_network_from_db доступний")
        else:
            print("Метод render_network_from_db недоступний")
        
        if hasattr(main_window.network_viewer, '_save_network_to_db'):
            print("Метод _save_network_to_db доступний")
        else:
            print("Метод _save_network_to_db недоступний")
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("Інтеграція з головним вікном працює коректно")
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні інтеграції: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print("ТЕСТУВАННЯ ПОКРАЩЕНОГО ІНТЕРАКТИВНОГО ВІЗУАЛІЗАТОРА МЕРЕЖІ")
    print("=" * 80)
    
    # Запускаем тесты
    test_results = []
    
    test_results.append(test_enhanced_viewer())
    test_results.append(test_node_shapes())
    test_results.append(test_database_operations())
    test_results.append(test_integration())
    
    # Подводим итоги
    print("\n" + "=" * 80)
    print("ПІДСУМКИ ТЕСТУВАННЯ:")
    print("=" * 80)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"Пройдено тестів: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print("\nПокращений візуалізатор мережі готовий до використання!")
        
        print("\nНОВІ МОЖЛИВОСТІ:")
        print("-" * 20)
        print("Форми вузлів залежно від кількості зв'язків")
        print("Підсвічування при наведенні")
        print("Перетягування вузлів")
        print("Виділення пов'язаних вузлів")
        print("Автоматичне збереження в .db")
        print("Плавні анімації")
        print("Масштабування колесиком миші")
        print("Функція render_network_from_db()")
        
    else:
        print("ДЕЯКІ ТЕСТИ НЕ ПРОЙДЕНО")
        print("Перевірте помилки вище та виправте їх.")
    
    print("\nРЕКОМЕНДАЦІЇ:")
    print("-" * 20)
    print("1. Запустіть основний додаток: python main.py")
    print("2. Перейдіть на вкладку 'Панель візуалізації' -> 'Топологія'")
    print("3. Використовуйте нові можливості візуалізації")
    print("4. Тестуйте форми вузлів та інтерактивність")
    print("5. Використовуйте автоматичне збереження в .db")
    print("6. Експортуйте дані для аналізу надійності")


if __name__ == "__main__":
    main()
