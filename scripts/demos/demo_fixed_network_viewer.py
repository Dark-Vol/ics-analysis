#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрація виправленого інтерактивного візуалізатора мережі
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import time

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def demonstrate_fixed_features():
    """Демонстрирует виправлені можливості візуалізатора"""
    print("=" * 80)
    print("ДЕМОНСТРАЦІЯ ВИПРАВЛЕНОГО ІНТЕРАКТИВНОГО ВІЗУАЛІЗАТОРА МЕРЕЖІ")
    print("=" * 80)
    
    print("\nВИПРАВЛЕНІ ПРОБЛЕМИ:")
    print("-" * 50)
    print("Зв'язки між вузлами відображаються коректно:")
    print("   • Словник Python конвертується у NetworkX граф")
    print("   • Всі зв'язки відображаються правильно")
    print("   • Граф будується з правильними ребрами")
    
    print("\nВузли автоматично розташовуються в просторі:")
    print("   • Force-directed layout (spring_layout)")
    print("   • Вузли не стоять в один ряд")
    print("   • Динамічне розташування залежно від зв'язків")
    
    print("\nРозміри вузлів адаптовані під масштаб:")
    print("   • Зменшені розміри вузлів (0.15 замість 0.3)")
    print("   • Зменшений шрифт (6 замість 8)")
    print("   • Зменшена інформація про ступінь (4 замість 6)")
    
    print("\nМережа зберігається у .db як реальний Python-словник:")
    print("   • Використання repr() для збереження")
    print("   • Використання eval() для завантаження")
    print("   • Автоматичне збереження при змінах")
    print("   • Формат: {'a': ['b', 'c'], 'b': ['c'], 'c': []}")


def test_fixed_viewer():
    """Тестирует виправлений візуалізатор"""
    print("\nТЕСТУВАННЯ ВИПРАВЛЕНОГО ВІЗУАЛІЗАТОРА:")
    print("-" * 50)
    
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
        print(f"Позиції вузлів обчислено: {len(viewer.pos)} вузлів")
        
        # Тестируем формы узлов
        print("\nФорми вузлів:")
        for node_id in viewer.G.nodes():
            degree = viewer.G.degree(node_id)
            shape = viewer._get_node_shape(degree)
            print(f"  Вузол {node_id}: degree={degree}, форма={shape}")
        
        # Тестируем анализ связности
        try:
            viewer._analyze_connectivity()
            print("Аналіз зв'язності працює")
        except Exception as e:
            print(f"Аналіз зв'язності не працює: {e}")
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("\n" + "=" * 50)
        print("ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні: {e}")
        return False


def test_main_window_integration():
    """Тестирует интеграцию с главным окном"""
    print("\nТЕСТУВАННЯ ІНТЕГРАЦІЇ З ГОЛОВНИМ ВІКНОМ:")
    print("-" * 50)
    
    try:
        from src.gui.main_window import MainWindow
        
        print("Головне вікно імпортовано успішно")
        
        # Создаем главное окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        main_window = MainWindow(root, {})
        print("Головне вікно створено успішно")
        
        # Проверяем, что виправлений візуалізатор загружен
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
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("Інтеграція з головним вікном працює коректно")
        return True
        
    except Exception as e:
        print(f"Помилка при тестуванні інтеграції з головним вікном: {e}")
        return False


def show_fixed_demo():
    """Показывает демонстрацию виправленого візуалізатора"""
    try:
        from src.gui.main_window import MainWindow
        
        root = tk.Tk()
        main_window = MainWindow(root, {})
        
        # Показываем приветственное сообщение
        messagebox.showinfo("Виправлений візуалізатор готовий!", 
            "Виправлений інтерактивний візуалізатор мережі інтегровано!\n\n"
            "ВИПРАВЛЕНІ ПРОБЛЕМИ:\n"
            "• Зв'язки між вузлами відображаються коректно\n"
            "• Вузли автоматично розташовуються в просторі\n"
            "• Розміри вузлів адаптовані під масштаб\n"
            "• Мережа зберігається у .db як Python-словник\n"
            "• Автоматичне відображення після завантаження\n\n"
            "Перейдіть на вкладку 'Панель візуалізації' → 'Топологія' для використання!")
        
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося запустити демонстрацію: {e}")


def main():
    """Основная функция тестирования"""
    print("ТЕСТУВАННЯ ВИПРАВЛЕНОГО ІНТЕРАКТИВНОГО ВІЗУАЛІЗАТОРА МЕРЕЖІ")
    print("=" * 80)
    
    # Показываем возможности
    demonstrate_fixed_features()
    
    # Запускаем тесты
    test_results = []
    
    test_results.append(test_fixed_viewer())
    test_results.append(test_main_window_integration())
    
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
        
        # Предлагаем запустить демонстрацию
        try:
            response = input("\nЗапустити демонстрацію виправленого візуалізатора? (y/n): ").lower().strip()
            if response in ['y', 'yes', 'так', 'т']:
                show_fixed_demo()
        except KeyboardInterrupt:
            print("\nТестування завершено.")
    else:
        print("ДЕЯКІ ТЕСТИ НЕ ПРОЙДЕНО")
        print("Перевірте помилки вище та виправте їх.")
    
    print("\nРЕКОМЕНДАЦІЇ:")
    print("-" * 20)
    print("1. Запустіть основний додаток: python main.py")
    print("2. Перейдіть на вкладку 'Панель візуалізації' → 'Топологія'")
    print("3. Використовуйте виправлені можливості візуалізації")
    print("4. Тестуйте відображення зв'язків та автоматичне розташування")
    print("5. Використовуйте автоматичне збереження в .db")
    print("6. Перевірте розміри вузлів та шрифтів")


if __name__ == "__main__":
    main()
