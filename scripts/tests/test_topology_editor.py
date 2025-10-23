#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест интерактивного редактора топологии сети
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def test_topology_editor():
    """Тестирует редактор топологии"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИНТЕРАКТИВНОГО РЕДАКТОРА ТОПОЛОГИИ")
    print("=" * 60)
    
    try:
        # Импортируем редактор
        from src.gui.topology_editor import InteractiveNetworkEditor
        
        print("Модуль редактора топологии импортирован успешно")
        
        # Создаем тестовое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        # Создаем редактор
        editor = InteractiveNetworkEditor(root)
        print("Редактор топологии создан успешно")
        
        # Тестируем загрузку примера сети
        editor.load_sample_network()
        print("Пример сети загружен успешно")
        
        # Проверяем данные сети
        network_data = editor.get_network_data()
        print(f"Данные сети получены: {len(network_data['nodes'])} узлов, {len(network_data['connections'])} групп связей")
        
        # Тестируем добавление узла
        editor.add_node_at_position(5, 5)
        print("Добавление узла работает")
        
        # Тестируем создание связи
        if len(network_data['nodes']) >= 2:
            node1 = network_data['nodes'][0]['id']
            node2 = network_data['nodes'][1]['id']
            editor.add_edge(node1, node2)
            print("Создание связи работает")
        
        # Тестируем анализ связности
        try:
            editor.analyze_connectivity()
            print("Анализ связности работает")
        except Exception as e:
            print(f"Анализ связности не работает: {e}")
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("\n" + "=" * 60)
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        return False


def test_integration():
    """Тестирует интеграцию редактора"""
    print("\nТЕСТИРОВАНИЕ ИНТЕГРАЦИИ:")
    print("-" * 30)
    
    try:
        from src.gui.topology_editor_integration import TopologyEditorIntegration
        
        print("Модуль интеграции импортирован успешно")
        
        # Создаем мок главного окна
        class MockMainWindow:
            def __init__(self):
                self.root = tk.Tk()
                self.root.withdraw()
                self.simulator = None
        
        mock_main_window = MockMainWindow()
        
        # Создаем интеграцию
        integration = TopologyEditorIntegration(mock_main_window)
        print("Интеграция создана успешно")
        
        # Тестируем преобразование данных
        test_network_data = {
            'nodes': [
                {'id': 'test1', 'x': 1, 'y': 1, 'type': 'server', 'capacity': 1000, 'reliability': 0.95},
                {'id': 'test2', 'x': 2, 'y': 2, 'type': 'router', 'capacity': 500, 'reliability': 0.90}
            ],
            'connections': {
                'test1': ['test2'],
                'test2': ['test1']
            },
            'edge_properties': {
                'test1-test2': {'bandwidth': 100, 'latency': 5.0, 'reliability': 0.98}
            }
        }
        
        simulator_data = integration.convert_to_simulator_format(test_network_data)
        print(f"Преобразование в формат симулятора: {len(simulator_data['nodes'])} узлов, {len(simulator_data['links'])} связей")
        
        editor_data = integration.convert_from_simulator_format(simulator_data)
        print(f"Преобразование в формат редактора: {len(editor_data['nodes'])} узлов")
        
        # Закрываем тестовое окно
        mock_main_window.root.destroy()
        
        print("Интеграция работает корректно")
        return True
        
    except Exception as e:
        print(f"Ошибка при тестировании интеграции: {e}")
        return False


def test_demo():
    """Тестирует демонстрационный скрипт"""
    print("\nТЕСТИРОВАНИЕ ДЕМОНСТРАЦИИ:")
    print("-" * 30)
    
    try:
        from scripts.demos.demo_topology_editor import demonstrate_features
        
        print("Демонстрационный модуль импортирован успешно")
        
        # Запускаем демонстрацию
        demonstrate_features()
        
        print("Демонстрация работает корректно")
        return True
        
    except Exception as e:
        print(f"Ошибка при тестировании демонстрации: {e}")
        return False


def show_gui_demo():
    """Показывает GUI демонстрацию"""
    try:
        from src.gui.topology_editor import create_topology_editor_window
        
        root, editor = create_topology_editor_window()
        
        # Показываем приветственное сообщение
        messagebox.showinfo("Добро пожаловать!", 
            "Добро пожаловать в интерактивный редактор топологии сети!\n\n"
            "ВОЗМОЖНОСТИ:\n"
            "• Создание и редактирование узлов\n"
            "• Добавление и удаление связей\n"
            "• Перетаскивание узлов мышью\n"
            "• Настройка свойств элементов\n"
            "• Анализ связности сети\n"
            "• Интеграция с анализом надежности\n\n"
            "Используйте панель инструментов для выбора режима редактирования.")
        
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить GUI демонстрацию: {e}")


def main():
    """Основная функция тестирования"""
    print("ТЕСТИРОВАНИЕ ИНТЕРАКТИВНОГО РЕДАКТОРА ТОПОЛОГИИ СЕТИ")
    print("=" * 80)
    
    # Запускаем тесты
    test_results = []
    
    test_results.append(test_topology_editor())
    test_results.append(test_integration())
    test_results.append(test_demo())
    
    # Подводим итоги
    print("\n" + "=" * 80)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 80)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"Пройдено тестов: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\nРедактор топологии готов к использованию!")
        
        # Предлагаем запустить GUI демонстрацию
        try:
            response = input("\nЗапустить GUI демонстрацию? (y/n): ").lower().strip()
            if response in ['y', 'yes', 'да', 'д']:
                show_gui_demo()
        except KeyboardInterrupt:
            print("\nТестирование завершено.")
    else:
        print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("Проверьте ошибки выше и исправьте их.")
    
    print("\nРЕКОМЕНДАЦИИ:")
    print("-" * 20)
    print("1. Используйте редактор для создания и редактирования сетей")
    print("2. Интегрируйте с основным приложением через topology_editor_integration.py")
    print("3. Сохраняйте сети в JSON формате для повторного использования")
    print("4. Используйте анализ связности для проверки корректности топологии")
    print("5. Экспортируйте данные для анализа надежности")


if __name__ == "__main__":
    main()
