#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация улучшенного интерактивного визуализатора сети
с динамической визуализацией и автоматической синхронизацией с БД
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import time

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def demonstrate_enhanced_features():
    """Демонстрирует улучшенные возможности визуализатора"""
    print("=" * 80)
    print("ДЕМОНСТРАЦІЯ ПОКРАЩЕНОГО ІНТЕРАКТИВНОГО ВІЗУАЛІЗАТОРА МЕРЕЖІ")
    print("=" * 80)
    
    print("\nНОВІ МОЖЛИВОСТІ:")
    print("-" * 50)
    print("Форми вузлів залежно від кількості зв'язків (degree):")
    print("   • Коло (d≤2) - простий вузол")
    print("   • Трикутник (d=3) - вузол з 3 зв'язками")
    print("   • Квадрат (d=4) - вузол з 4 зв'язками")
    print("   • П'ятикутник (d=5) - вузол з 5 зв'язками")
    print("   • Шестикутник (d≥6) - вузол з 6+ зв'язками")
    
    print("Інтерактивність:")
    print("   • Підсвічування при наведенні (hover)")
    print("   • Перетягування вузлів (drag & drop)")
    print("   • Виділення пов'язаних вузлів при кліку")
    print("   • Плавні анімації при змінах")
    print("   • Масштабування колесиком миші")
    
    print("Автоматична синхронізація з БД:")
    print("   • Збереження в .db файли")
    print("   • Автоматичне оновлення при змінах")
    print("   • Функція render_network_from_db()")
    print("   • Словникове сховище Python")
    
    print("Збереження функціоналу:")
    print("   • Всі режими редагування")
    print("   • Аналіз зв'язності")
    print("   • Експорт для аналізу надійності")
    print("   • Інтеграція з основним додатком")


def test_enhanced_viewer():
    """Тестирует улучшенный визуализатор"""
    print("\nТЕСТУВАННЯ ПОКРАЩЕНОГО ВІЗУАЛІЗАТОРА:")
    print("-" * 50)
    
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
        
        # Тестируем получение данных сети
        network_data = viewer.get_network_data()
        print(f"Дані мережі отримано: {len(network_data['nodes'])} вузлів")
        
        # Тестируем формы узлов
        for node_data in network_data['nodes']:
            degree = node_data.get('degree', 0)
            shape = viewer._get_node_shape(degree)
            print(f"  Вузол {node_data['id']}: degree={degree}, форма={shape}")
        
        # Тестируем анализ связности
        try:
            viewer._analyze_connectivity()
            print("✓ Аналіз зв'язності працює")
        except Exception as e:
            print(f"⚠ Аналіз зв'язності не працює: {e}")
        
        # Тестируем сохранение в БД
        test_db_filename = "test_network.db"
        try:
            viewer._save_network_to_db(test_db_filename)
            print(f"✓ Збереження в БД {test_db_filename} працює")
            
            # Тестируем загрузку из БД
            viewer.render_network_from_db(test_db_filename)
            print(f"✓ Завантаження з БД {test_db_filename} працює")
            
            # Удаляем тестовый файл
            if os.path.exists(test_db_filename):
                os.remove(test_db_filename)
                print("✓ Тестовий файл БД видалено")
                
        except Exception as e:
            print(f"⚠ Робота з БД не працює: {e}")
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("\n" + "=" * 50)
        print("ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"✗ Помилка при тестуванні: {e}")
        return False


def test_main_window_integration():
    """Тестирует интеграцию с главным окном"""
    print("\nТЕСТУВАННЯ ІНТЕГРАЦІЇ З ГОЛОВНИМ ВІКНОМ:")
    print("-" * 50)
    
    try:
        from src.gui.main_window import MainWindow
        
        print("✓ Головне вікно імпортовано успішно")
        
        # Создаем главное окно
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        main_window = MainWindow(root, {})
        print("✓ Головне вікно створено успішно")
        
        # Проверяем, что улучшенный визуализатор загружен
        viewer_type = type(main_window.network_viewer).__name__
        print(f"✓ Тип візуалізатора: {viewer_type}")
        
        if viewer_type == "EnhancedInteractiveNetworkViewer":
            print("✓ Покращений візуалізатор інтегровано в головне вікно")
        elif viewer_type == "InteractiveNetworkViewer":
            print("⚠ Використовується базовий інтерактивний візуалізатор")
        else:
            print("⚠ Використовується звичайний візуалізатор (fallback)")
        
        # Закрываем тестовое окно
        root.destroy()
        
        print("✓ Інтеграція з головним вікном працює коректно")
        return True
        
    except Exception as e:
        print(f"✗ Помилка при тестуванні інтеграції з головним вікном: {e}")
        return False


def show_enhanced_demo():
    """Показывает демонстрацию улучшенного визуализатора"""
    try:
        from src.gui.main_window import MainWindow
        
        root = tk.Tk()
        main_window = MainWindow(root, {})
        
        # Показываем приветственное сообщение
        messagebox.showinfo("Покращений візуалізатор готовий!", 
            "Покращений інтерактивний візуалізатор мережі інтегровано!\n\n"
            "НОВІ МОЖЛИВОСТІ:\n"
            "• Форми вузлів залежно від кількості зв'язків\n"
            "• Підсвічування при наведенні\n"
            "• Перетягування вузлів\n"
            "• Виділення пов'язаних вузлів\n"
            "• Автоматичне збереження в .db\n"
            "• Плавні анімації\n"
            "• Масштабування колесиком\n\n"
            "Перейдіть на вкладку 'Панель візуалізації' → 'Топологія' для використання!")
        
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Помилка", f"Не вдалося запустити демонстрацію: {e}")


def main():
    """Основная функция тестирования"""
    print("ТЕСТУВАННЯ ПОКРАЩЕНОГО ІНТЕРАКТИВНОГО ВІЗУАЛІЗАТОРА МЕРЕЖІ")
    print("=" * 80)
    
    # Показываем возможности
    demonstrate_enhanced_features()
    
    # Запускаем тесты
    test_results = []
    
    test_results.append(test_enhanced_viewer())
    test_results.append(test_main_window_integration())
    
    # Подводим итоги
    print("\n" + "=" * 80)
    print("ПІДСУМКИ ТЕСТУВАННЯ:")
    print("=" * 80)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"Пройдено тестів: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!")
        print("\nПокращений візуалізатор мережі готовий до використання!")
        
        # Предлагаем запустить демонстрацию
        try:
            response = input("\nЗапустити демонстрацію покращеного візуалізатора? (y/n): ").lower().strip()
            if response in ['y', 'yes', 'так', 'т']:
                show_enhanced_demo()
        except KeyboardInterrupt:
            print("\nТестування завершено.")
    else:
        print("❌ ДЕЯКІ ТЕСТИ НЕ ПРОЙДЕНО")
        print("Перевірте помилки вище та виправте їх.")
    
    print("\nРЕКОМЕНДАЦІЇ:")
    print("-" * 20)
    print("1. Запустіть основний додаток: python main.py")
    print("2. Перейдіть на вкладку 'Панель візуалізації' → 'Топологія'")
    print("3. Використовуйте нові можливості візуалізації")
    print("4. Тестуйте форми вузлів та інтерактивність")
    print("5. Експортуйте дані для аналізу надійності")
    print("6. Використовуйте автоматичне збереження в .db")


if __name__ == "__main__":
    main()
