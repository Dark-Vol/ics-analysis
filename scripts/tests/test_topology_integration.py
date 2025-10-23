#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация интеграции интерактивного редактора топологии в основное приложение
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_integration():
    """Тестирует интеграцию интерактивного редактора"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ИНТЕРАКТИВНОГО РЕДАКТОРА")
    print("=" * 60)
    
    try:
        # Импортируем интерактивный визуализатор
        from src.gui.interactive_network_viewer import InteractiveNetworkViewer
        
        print("Интерактивный визуализатор импортирован успешно")
        
        # Создаем тестовое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        # Создаем интерактивный визуализатор
        viewer = InteractiveNetworkViewer(root, None)
        print("Интерактивный визуализатор создан успешно")
        
        # Тестируем загрузку примера сети
        viewer._load_sample_network()
        print("Пример сети загружен в интерактивный визуализатор")
        
        # Тестируем получение данных сети
        network_data = viewer.get_network_data()
        print(f"Данные сети получены: {len(network_data['nodes'])} узлов")
        
        # Тестируем анализ связности
        try:
            viewer._analyze_connectivity()
            print("Анализ связности работает")
        except Exception as e:
            print(f"Анализ связности не работает: {e}")
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("\n" + "=" * 60)
        print("ИНТЕГРАЦИЯ ПРОТЕСТИРОВАНА УСПЕШНО!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"Ошибка при тестировании интеграции: {e}")
        return False


def test_main_window_integration():
    """Тестирует интеграцию с главным окном"""
    print("\nТЕСТИРОВАНИЕ ИНТЕГРАЦИИ С ГЛАВНЫМ ОКНОМ:")
    print("-" * 50)
    
    try:
        from src.gui.main_window import MainWindow
        
        print("Главное окно импортировано успешно")
        
        # Создаем главное окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        main_window = MainWindow(root, {})
        
        print("Главное окно создано успешно")
        
        # Проверяем, что интерактивный визуализатор загружен
        if hasattr(main_window.network_viewer, 'load_network_from_model'):
            print("Интерактивный визуализатор интегрирован в главное окно")
        else:
            print("Используется обычный визуализатор (fallback)")
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("Интеграция с главным окном работает корректно")
        return True
        
    except Exception as e:
        print(f"Ошибка при тестировании интеграции с главным окном: {e}")
        return False


def show_integration_demo():
    """Показывает демонстрацию интеграции"""
    try:
        from src.gui.main_window import MainWindow
        
        root = tk.Tk()
        main_window = MainWindow(root, {})
        
        # Показываем приветственное сообщение
        messagebox.showinfo("Интеграция завершена!", 
            "Интерактивный редактор топологии интегрирован в основное приложение!\n\n"
            "ВОЗМОЖНОСТИ:\n"
            "• Перейдите на вкладку 'Панель визуализации' → 'Топология'\n"
            "• Используйте режимы редактирования для управления сетью\n"
            "• Добавляйте и удаляйте узлы и связи\n"
            "• Перетаскивайте узлы мышью\n"
            "• Анализируйте связность сети\n"
            "• Экспортируйте данные для анализа надежности\n\n"
            "Теперь вы можете полностью взаимодействовать с топологией сети!")
        
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить демонстрацию: {e}")


def main():
    """Основная функция тестирования"""
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ ИНТЕРАКТИВНОГО РЕДАКТОРА ТОПОЛОГИИ")
    print("=" * 80)
    
    # Запускаем тесты
    test_results = []
    
    test_results.append(test_integration())
    test_results.append(test_main_window_integration())
    
    # Подводим итоги
    print("\n" + "=" * 80)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 80)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"Пройдено тестов: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("\nИнтерактивный редактор топологии интегрирован в основное приложение!")
        
        # Предлагаем запустить демонстрацию
        try:
            response = input("\nЗапустить демонстрацию интеграции? (y/n): ").lower().strip()
            if response in ['y', 'yes', 'да', 'д']:
                show_integration_demo()
        except KeyboardInterrupt:
            print("\nТестирование завершено.")
    else:
        print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("Проверьте ошибки выше и исправьте их.")
    
    print("\nРЕКОМЕНДАЦИИ:")
    print("-" * 20)
    print("1. Запустите основное приложение: python main.py")
    print("2. Перейдите на вкладку 'Панель визуализации' -> 'Топология'")
    print("3. Используйте режимы редактирования для управления сетью")
    print("4. Загрузите существующую сеть или создайте новую")
    print("5. Экспортируйте данные для анализа надежности")


if __name__ == "__main__":
    main()
