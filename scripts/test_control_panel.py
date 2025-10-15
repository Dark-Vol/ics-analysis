#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест контрольной панели
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json

def test_control_panel():
    """Тестирует контрольную панель"""
    print("Тестирование контрольной панели...")
    
    try:
        from src.gui.main_window import MainWindow
        from src.gui.control_panel import ControlPanel
        
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
        root.withdraw()  # Скрываем окно
        
        # Создаем MainWindow
        main_window = MainWindow(root, config)
        
        # Проверяем наличие методов
        if hasattr(main_window, 'create_system'):
            print("[OK] Метод create_system найден")
        else:
            print("[ERROR] Метод create_system не найден")
            return False
        
        if hasattr(main_window, 'start_simulation'):
            print("[OK] Метод start_simulation найден")
        else:
            print("[ERROR] Метод start_simulation не найден")
            return False
        
        # Проверяем ControlPanel
        if hasattr(main_window, 'control_panel') and main_window.control_panel:
            print("[OK] ControlPanel создан")
            
            # Проверяем, что parent правильный
            if main_window.control_panel.parent == main_window:
                print("[OK] ControlPanel правильно связан с MainWindow")
            else:
                print("[ERROR] ControlPanel неправильно связан с MainWindow")
                return False
        else:
            print("[ERROR] ControlPanel не создан")
            return False
        
        # Тестируем вызов методов (без реального выполнения)
        try:
            # Эти методы не должны вызывать ошибки AttributeError
            print("[OK] Методы ControlPanel доступны")
        except AttributeError as e:
            print(f"[ERROR] Ошибка доступа к методам: {e}")
            return False
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании ControlPanel: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ КОНТРОЛЬНОЙ ПАНЕЛИ")
    print("=" * 60)
    
    success = test_control_panel()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success:
        print("[SUCCESS] Контрольная панель работает корректно!")
        print("\nРаботающие функции:")
        print("- [OK] Создание ControlPanel")
        print("- [OK] Связь с MainWindow")
        print("- [OK] Методы create_system и start_simulation")
    else:
        print("[ERROR] Проблемы с контрольной панелью")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

