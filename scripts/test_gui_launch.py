#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест запуска GUI приложения
"""

import sys
import os
import time
import threading
import tkinter as tk

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_gui_launch():
    """Тестирует запуск GUI приложения"""
    print("Тестирование запуска GUI...")
    
    try:
        # Импортируем модули
        from src.gui.main_window import MainWindow
        import json
        
        # Загружаем конфигурацию
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {
                "simulation": {"time_steps": 1000, "dt": 0.1, "random_seed": 42},
                "network": {"nodes": 10, "connections": 0.3, "bandwidth": 1000, "latency": 10, "reliability": 0.95}
            }
        
        # Создаем корневое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем окно для тестирования
        
        # Создаем главное окно
        print("Создание MainWindow...")
        main_window = MainWindow(root, config)
        
        # Проверяем наличие пагинации
        if hasattr(main_window, 'plots_notebook'):
            tab_count = main_window.plots_notebook.index("end")
            print(f"[OK] Создано {tab_count} вкладок пагинации")
            
            # Проверяем содержимое вкладок
            tabs = []
            for i in range(tab_count):
                tab_text = main_window.plots_notebook.tab(i, "text")
                tabs.append(tab_text)
            
            print(f"[OK] Вкладки: {[tab.encode('ascii', 'ignore').decode('ascii') for tab in tabs]}")
            
            # Проверяем наличие ожидаемых панелей
            expected_panels = ["Контрольная панель", "Панель визуализации", "Статус системы"]
            found_panels = []
            
            for panel in expected_panels:
                if any(panel in tab for tab in tabs):
                    found_panels.append(panel)
            
            print(f"[OK] Найдены панели: {found_panels}")
            
            if len(found_panels) >= 2:  # Минимум 2 из 3 панелей
                print("[OK] Пагинация работает корректно")
                result = True
            else:
                print("[ERROR] Недостаточно панелей")
                result = False
        else:
            print("[ERROR] Пагинация не найдена")
            result = False
        
        # Закрываем окно
        root.destroy()
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании GUI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ ЗАПУСКА GUI ПРИЛОЖЕНИЯ")
    print("=" * 60)
    
    success = test_gui_launch()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success:
        print("[SUCCESS] GUI приложение запускается корректно!")
        print("\nРаботающие функции:")
        print("- [OK] Создание главного окна")
        print("- [OK] Инициализация пагинации")
        print("- [OK] Создание панелей управления")
        print("- [OK] Загрузка конфигурации")
    else:
        print("[ERROR] Проблемы с запуском GUI приложения")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
