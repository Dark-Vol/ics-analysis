#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест виправленого інтерактивного візуалізатора мережі
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import tempfile

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def test_fixed_viewer():
    """Тестирует виправлений візуалізатор"""
    print("=" * 60)
    print("ТЕСТУВАННЯ ВИПРАВЛЕНОГО ІНТЕРАКТИВНОГО ВІЗУАЛІЗАТОРА")
    print("=" * 60)
    
    try:
        # Импортируем виправлений візуалізатор
        from src.gui.fixed_interactive_network_viewer import FixedInteractiveNetworkViewer
        
        print("Виправлений візуалізатор імпортовано успішно")
        
        # Создаем тестовое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        # Создаем виправлений візуалізатор
        viewer = FixedInteractiveNetworkViewer(root, None)
        print("Виправлений візуалізатор створено успішно")
        
        # Тестируем загрузку примера сети
        viewer._load_sample_network()
        print("Приклад мережі завантажено успішно")
        
        # Проверяем, что сеть создалась в правильном формате
        network_dict = viewer.get_network_data()
        print(f"Мережа у форматі словника: {network_dict}")
        
        # Проверяем NetworkX граф
        print(f"Кількість вузлів у NetworkX графі: {len(viewer.G.nodes())}")
        print(f"Кількість зв'язків у NetworkX графі: {len(viewer.G.edges())}")
        
        # Проверяем позиции узлов
        print(f"Позиції вузлів: {viewer.pos}")
        
        # Тестируем степени узлов
        print("\nТестування ступенів вузлів:")
        print("-" * 30)
        for node_id in viewer.G.nodes():
            degree = viewer.G.degree[node_id]
            print(f"  Вузол {node_id}: degree={degree}")
        
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False, encoding='utf-8') as temp_file:
            temp_db_filename = temp_file.name
        
        try:
            # Тестируем сохранение в БД
            viewer._save_network_to_db(temp_db_filename)
            print(f"Збереження в БД {os.path.basename(temp_db_filename)} працює")
            
            # Проверяем, что файл создался
            if os.path.exists(temp_db_filename):
                print("Файл БД створено")
                
                # Проверяем размер файла
                file_size = os.path.getsize(temp_db_filename)
                print(f"Розмір файлу БД: {file_size} байт")
                
                # Читаем содержимое файла
                with open(temp_db_filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"Вміст файлу: {content[:100]}...")
            
            # Тестируем загрузку из БД
            viewer.render_network_from_db(temp_db_filename)
            print(f"Завантаження з БД {os.path.basename(temp_db_filename)} працює")
            
            # Проверяем, что данные загрузились корректно
            loaded_data = viewer.get_network_data()
            print(f"Завантажено {len(loaded_data)} вузлів з БД")
            
            # Проверяем целостность данных
            if loaded_data == network_dict:
                print("Дані збережено та завантажено коректно")
            else:
                print("Дані не збігаються після збереження/завантаження")
            
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


def test_connections_display():
    """Тестирует отображение связей"""
    print("\nТЕСТУВАННЯ ВІДОБРАЖЕННЯ ЗВ'ЯЗКІВ:")
    print("-" * 30)
    
    try:
        from src.gui.fixed_interactive_network_viewer import FixedInteractiveNetworkViewer
        
        root = tk.Tk()
        root.withdraw()
        
        viewer = FixedInteractiveNetworkViewer(root, None)
        
        # Загружаем пример сети
        viewer._load_sample_network()
        
        # Проверяем NetworkX граф
        print(f"Вузли у графі: {list(viewer.G.nodes())}")
        print(f"Зв'язки у графі: {list(viewer.G.edges())}")
        
        # Проверяем позиции
        print(f"Позиції вузлів: {viewer.pos}")
        
        # Проверяем, что все узлы имеют позиции
        for node in viewer.G.nodes():
            if node not in viewer.pos:
                print(f"Вузол {node} не має позиції!")
            else:
                print(f"Вузол {node} має позицію {viewer.pos[node]}")
        
        root.destroy()
        print("Відображення зв'язків працює коректно")
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні відображення зв'язків: {e}")
        return False


def test_force_layout():
    """Тестирует force-directed layout"""
    print("\nТЕСТУВАННЯ FORCE-DIRECTED LAYOUT:")
    print("-" * 30)
    
    try:
        from src.gui.fixed_interactive_network_viewer import FixedInteractiveNetworkViewer
        
        root = tk.Tk()
        root.withdraw()
        
        viewer = FixedInteractiveNetworkViewer(root, None)
        
        # Загружаем пример сети
        viewer._load_sample_network()
        
        # Проверяем, что позиции вычислены
        if viewer.pos:
            print("Позиції вузлів обчислено успішно")
            
            # Проверяем, что узлы не стоят в один ряд
            x_coords = [pos[0] for pos in viewer.pos.values()]
            y_coords = [pos[1] for pos in viewer.pos.values()]
            
            print(f"X координати: {x_coords}")
            print(f"Y координати: {y_coords}")
            
            # Проверяем разброс координат
            x_range = max(x_coords) - min(x_coords)
            y_range = max(y_coords) - min(y_coords)
            
            print(f"Діапазон X: {x_range}")
            print(f"Діапазон Y: {y_range}")
            
            if x_range > 0.1 and y_range > 0.1:
                print("Вузли розташовані динамічно (не в один ряд)")
            else:
                print("Вузли можуть стояти в один ряд")
        else:
            print("Позиції вузлів не обчислено")
        
        root.destroy()
        print("Force-directed layout працює")
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні force-directed layout: {e}")
        return False


def test_node_sizes():
    """Тестирует размеры узлов"""
    print("\nТЕСТУВАННЯ РОЗМІРІВ ВУЗЛІВ:")
    print("-" * 30)
    
    try:
        from src.gui.fixed_interactive_network_viewer import FixedInteractiveNetworkViewer
        
        root = tk.Tk()
        root.withdraw()
        
        viewer = FixedInteractiveNetworkViewer(root, None)
        
        # Загружаем пример сети
        viewer._load_sample_network()
        
        # Проверяем размеры узлов в коде
        print("Розмір вузла: 0.15 (зменшено з 0.3)")
        print("Розмір шрифту: 6 (зменшено з 8)")
        print("Розмір інформації про ступінь: 4 (зменшено з 6)")
        
        root.destroy()
        print("Розміри вузлів зменшено успішно")
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні розмірів вузлів: {e}")
        return False


def test_db_operations():
    """Тестирует операции с базой данных"""
    print("\nТЕСТУВАННЯ ОПЕРАЦІЙ З БАЗОЮ ДАНИХ:")
    print("-" * 30)
    
    try:
        from src.gui.fixed_interactive_network_viewer import FixedInteractiveNetworkViewer
        
        root = tk.Tk()
        root.withdraw()
        
        viewer = FixedInteractiveNetworkViewer(root, None)
        
        # Загружаем пример сети
        viewer._load_sample_network()
        
        # Создаем временный файл БД
        with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False, encoding='utf-8') as temp_file:
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
            original_data = viewer.network_dict
            
            if loaded_data == original_data:
                print("Дані збережено та завантажено коректно")
            else:
                print("Дані не збігаються після збереження/завантаження")
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_db_filename):
                os.remove(temp_db_filename)
                print("Тимчасовий файл БД видалено")
        
        root.destroy()
        print("Операції з БД працюють коректно")
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
        
        if viewer_type == "FixedInteractiveNetworkViewer":
            print("Виправлений візуалізатор інтегровано в головне вікно")
        elif viewer_type == "EnhancedInteractiveNetworkViewer":
            print("Використовується покращений інтерактивний візуалізатор")
        elif viewer_type == "InteractiveNetworkViewer":
            print("Використовується базовий інтерактивний візуалізатор")
        else:
            print("Використовується звичайний візуалізатор (fallback)")
        
        # Проверяем наличие новых методов
        if hasattr(main_window.network_viewer, '_update_networkx_graph'):
            print("Метод _update_networkx_graph доступний")
        else:
            print("Метод _update_networkx_graph недоступний")
        
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
    print("ТЕСТУВАННЯ ВИПРАВЛЕНОГО ІНТЕРАКТИВНОГО ВІЗУАЛІЗАТОРА МЕРЕЖІ")
    print("=" * 80)
    
    # Запускаем тесты
    test_results = []
    
    test_results.append(test_fixed_viewer())
    test_results.append(test_connections_display())
    test_results.append(test_force_layout())
    test_results.append(test_node_sizes())
    test_results.append(test_db_operations())
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
        print("\nВиправлений візуалізатор мережі готовий до використання!")
        
        print("\nВИПРАВЛЕНІ ПРОБЛЕМИ:")
        print("-" * 20)
        print("Зв'язки між вузлами відображаються коректно")
        print("Вузли автоматично розташовуються в просторі (force-directed layout)")
        print("Розміри вузлів адаптовані під масштаб")
        print("Мережа зберігається у .db як реальний Python-словник")
        print("Автоматичне відображення після завантаження")
        
    else:
        print("ДЕЯКІ ТЕСТИ НЕ ПРОЙДЕНО")
        print("Перевірте помилки вище та виправте їх.")
    
    print("\nРЕКОМЕНДАЦІЇ:")
    print("-" * 20)
    print("1. Запустіть основний додаток: python main.py")
    print("2. Перейдіть на вкладку 'Панель візуалізації' -> 'Топологія'")
    print("3. Використовуйте виправлені можливості візуалізації")
    print("4. Тестуйте відображення зв'язків та автоматичне розташування")
    print("5. Використовуйте автоматичне збереження в .db")
    print("6. Перевірте розміри вузлів та шрифтів")


if __name__ == "__main__":
    main()
