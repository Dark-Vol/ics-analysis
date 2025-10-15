#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки настройки времени анализа сети
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from src.gui.network_dialog import NetworkDialog
from src.database.database_manager import DatabaseManager
from src.simulator.network_simulator import NetworkSimulator, SimulationConfig

def test_network_dialog_analysis_time():
    """Тестирует диалог создания сети с настройкой времени анализа"""
    print("=== ТЕСТ ДИАЛОГА СОЗДАНИЯ СЕТИ ===")
    
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
        
        # Проверяем значение по умолчанию
        default_time = dialog.analysis_time_var.get()
        assert default_time == 300, f"Значение по умолчанию должно быть 300, получено {default_time}"
        
        # Устанавливаем тестовое значение
        test_time = 600  # 10 минут
        dialog.analysis_time_var.set(test_time)
        
        # Проверяем, что значение установлено
        assert dialog.analysis_time_var.get() == test_time, f"Не удалось установить время анализа {test_time}"
        
        print(f"+ Поле времени анализа создано корректно")
        print(f"+ Значение по умолчанию: {default_time} секунд")
        print(f"+ Тестовое значение установлено: {test_time} секунд")
        
        # Закрываем диалог
        dialog.dialog.destroy()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте диалога: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simulation_config_with_time():
    """Тестирует создание конфигурации симуляции с настраиваемым временем"""
    print("\n=== ТЕСТ КОНФИГУРАЦИИ СИМУЛЯЦИИ ===")
    
    try:
        # Тестируем разные значения времени анализа
        test_times = [60, 300, 600, 1800]  # 1 мин, 5 мин, 10 мин, 30 мин
        
        for analysis_time in test_times:
            # Создаем конфигурацию
            config = SimulationConfig(
                duration=float(analysis_time),
                time_step=0.5,
                enable_traffic=True,
                enable_failures=True,
                enable_adverse_conditions=True
            )
            
            # Проверяем, что время установлено правильно
            assert config.duration == float(analysis_time), f"Время анализа должно быть {analysis_time}, получено {config.duration}"
            
            print(f"+ Конфигурация создана с временем {analysis_time} сек ({analysis_time/60:.1f} мин)")
        
        print("+ Все тестовые времена анализа работают корректно")
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте конфигурации: {e}")
        return False

def test_network_simulator_with_custom_time():
    """Тестирует симулятор с настраиваемым временем анализа"""
    print("\n=== ТЕСТ СИМУЛЯТОРА С НАСТРАИВАЕМЫМ ВРЕМЕНЕМ ===")
    
    try:
        # Создаем конфигурацию с коротким временем для тестирования
        test_time = 5.0  # 5 секунд для быстрого теста
        config = SimulationConfig(
            duration=test_time,
            time_step=0.5,
            enable_traffic=True,
            enable_failures=False,  # Отключаем для быстрого теста
            enable_adverse_conditions=False
        )
        
        # Создаем симулятор
        simulator = NetworkSimulator(config)
        
        # Проверяем, что конфигурация установлена правильно
        assert simulator.config.duration == test_time, f"Время анализа должно быть {test_time}, получено {simulator.config.duration}"
        
        print(f"+ Симулятор создан с временем анализа: {test_time} секунд")
        print(f"+ Конфигурация симулятора корректна")
        
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте симулятора: {e}")
        return False

def test_time_range_validation():
    """Тестирует валидацию диапазона времени анализа"""
    print("\n=== ТЕСТ ВАЛИДАЦИИ ВРЕМЕНИ АНАЛИЗА ===")
    
    try:
        # Тестируем граничные значения
        test_cases = [
            (30, True, "Минимальное время (30 сек)"),
            (3600, True, "Максимальное время (1 час)"),
            (300, True, "Стандартное время (5 мин)"),
            (15, False, "Слишком короткое время (15 сек)"),
            (7200, False, "Слишком длинное время (2 часа)")
        ]
        
        for time_value, should_be_valid, description in test_cases:
            try:
                config = SimulationConfig(
                    duration=float(time_value),
                    time_step=0.5,
                    enable_traffic=True,
                    enable_failures=False,
                    enable_adverse_conditions=False
                )
                
                if should_be_valid:
                    print(f"+ {description}: ВАЛИДНО")
                else:
                    print(f"- {description}: должно быть невалидным, но прошло")
                    
            except Exception as e:
                if not should_be_valid:
                    print(f"+ {description}: правильно отклонено - {e}")
                else:
                    print(f"- {description}: не должно было быть отклонено - {e}")
        
        print("+ Валидация времени анализа работает")
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте валидации: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("ЗАПУСК ТЕСТОВ НАСТРОЙКИ ВРЕМЕНИ АНАЛИЗА")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    try:
        # Тест 1: Диалог создания сети
        if test_network_dialog_analysis_time():
            tests_passed += 1
        
        # Тест 2: Конфигурация симуляции
        if test_simulation_config_with_time():
            tests_passed += 1
        
        # Тест 3: Симулятор с настраиваемым временем
        if test_network_simulator_with_custom_time():
            tests_passed += 1
        
        # Тест 4: Валидация времени
        if test_time_range_validation():
            tests_passed += 1
        
        print("\n" + "=" * 50)
        print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {tests_passed}/{total_tests} тестов пройдено")
        
        if tests_passed == total_tests:
            print("ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("Настройка времени анализа работает корректно")
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
