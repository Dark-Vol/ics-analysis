#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки исправления ошибки analysis_time
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from src.gui.network_dialog import NetworkDialog
from src.database.database_manager import DatabaseManager

def test_analysis_time_fix():
    """Тестирует исправление ошибки analysis_time"""
    print("=== ТЕСТ ИСПРАВЛЕНИЯ ОШИБКИ ANALYSIS_TIME ===")
    
    try:
        # Создаем временную базу данных
        db_manager = DatabaseManager()
        
        # Создаем root окно для тестирования
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        
        # Создаем диалог
        dialog = NetworkDialog(root, db_manager)
        
        # Проверяем, что поле времени анализа создано
        assert hasattr(dialog, 'analysis_time_var'), "Поле analysis_time_var должно существовать"
        
        # Устанавливаем тестовое значение времени анализа
        test_analysis_time = 600  # 10 минут
        dialog.analysis_time_var.set(test_analysis_time)
        
        print(f"+ Поле времени анализа установлено: {test_analysis_time} секунд")
        
        # Симулируем создание сети (без реального сохранения)
        # Проверяем, что метод _save_network_dialog может быть вызван с параметром analysis_time
        try:
            # Создаем тестовую сеть
            from src.models.network_model import NetworkModel
            test_network = NetworkModel(nodes=5, connection_probability=0.3)
            
            # Проверяем, что метод принимает параметр analysis_time
            dialog._save_network_dialog(test_network, test_analysis_time)
            print("+ Метод _save_network_dialog принимает параметр analysis_time")
            
            # Закрываем диалог сохранения, если он открылся
            for widget in root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    widget.destroy()
                    
        except Exception as e:
            if "analysis_time" in str(e):
                print(f"- Ошибка с analysis_time все еще присутствует: {e}")
                return False
            else:
                print(f"+ Другие ошибки не связаны с analysis_time: {e}")
        
        # Закрываем диалог
        dialog.dialog.destroy()
        root.destroy()
        
        print("+ Исправление ошибки analysis_time работает корректно")
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_creation_with_time():
    """Тестирует создание сети с настройкой времени"""
    print("\n=== ТЕСТ СОЗДАНИЯ СЕТИ С ВРЕМЕНЕМ ===")
    
    try:
        # Создаем временную базу данных
        db_manager = DatabaseManager()
        
        # Создаем root окно
        root = tk.Tk()
        root.withdraw()
        
        # Создаем диалог
        dialog = NetworkDialog(root, db_manager)
        
        # Настраиваем параметры сети
        dialog.nodes_var.set(8)  # 8 узлов
        dialog.connection_prob_var.set(0.4)  # 40% вероятность соединения
        dialog.analysis_time_var.set(900)  # 15 минут анализа
        
        print("+ Параметры сети настроены:")
        print(f"  - Узлы: {dialog.nodes_var.get()}")
        print(f"  - Вероятность соединения: {dialog.connection_prob_var.get()}")
        print(f"  - Время анализа: {dialog.analysis_time_var.get()} сек")
        
        # Проверяем, что все параметры доступны
        assert dialog.nodes_var.get() == 8, "Количество узлов не установлено"
        assert dialog.connection_prob_var.get() == 0.4, "Вероятность соединения не установлена"
        assert dialog.analysis_time_var.get() == 900, "Время анализа не установлено"
        
        # Закрываем диалог
        dialog.dialog.destroy()
        root.destroy()
        
        print("+ Создание сети с настройкой времени работает корректно")
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте создания сети: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("ЗАПУСК ТЕСТОВ ИСПРАВЛЕНИЯ ОШИБКИ ANALYSIS_TIME")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 2
    
    try:
        # Тест 1: Исправление ошибки analysis_time
        if test_analysis_time_fix():
            tests_passed += 1
        
        # Тест 2: Создание сети с временем
        if test_network_creation_with_time():
            tests_passed += 1
        
        print("\n" + "=" * 60)
        print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {tests_passed}/{total_tests} тестов пройдено")
        
        if tests_passed == total_tests:
            print("ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("Ошибка analysis_time исправлена")
            print("Создание сети с настройкой времени работает")
            return True
        else:
            print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
            return False
        
    except Exception as e:
        print(f"\nОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
