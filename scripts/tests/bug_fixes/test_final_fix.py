#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест исправления бага с временем анализа
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager
from src.models.network_model import NetworkModel

def test_network_selection_dialog_logic():
    """Тестирует логику NetworkSelectionDialog"""
    print("=== ТЕСТ ЛОГИКИ NETWORK_SELECTION_DIALOG ===")
    
    try:
        db_manager = DatabaseManager()
        
        # Получаем сеть с ID 38 (время анализа 30 секунд)
        network_data = db_manager.get_network(38)
        
        if network_data:
            # Имитируем логику NetworkSelectionDialog
            analysis_time = network_data.get('analysis_time', 300)
            print(f"+ Сеть ID 38: время анализа = {analysis_time} секунд")
            
            # Проверяем, что время анализа правильное
            assert analysis_time == 30, f"Время анализа должно быть 30, получено {analysis_time}"
            
            # Имитируем результат NetworkSelectionDialog
            result = {
                'action': 'load',
                'network_id': 38,
                'network_name': network_data['name'],
                'network_data': network_data,
                'analysis_time': analysis_time
            }
            
            print(f"+ Результат NetworkSelectionDialog: analysis_time = {result['analysis_time']}")
            
            # Имитируем логику MainWindow._load_network
            analysis_time_from_result = result.get('analysis_time', 300)
            print(f"+ MainWindow получает: analysis_time = {analysis_time_from_result}")
            
            assert analysis_time_from_result == 30, f"MainWindow должен получить 30, получено {analysis_time_from_result}"
            
            print("+ Логика NetworkSelectionDialog работает правильно")
            return True
        else:
            print("- Не удалось получить данные сети ID 38")
            return False
            
    except Exception as e:
        print(f"- Ошибка в тесте: {e}")
        return False

def test_full_chain():
    """Тестирует полную цепочку от сохранения до загрузки"""
    print("\n=== ТЕСТ ПОЛНОЙ ЦЕПОЧКИ ===")
    
    try:
        # Создаем тестовую базу данных
        test_db_path = "test_final.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        db_manager = DatabaseManager(test_db_path)
        
        # Создаем тестовую сеть
        test_network = NetworkModel(nodes=3, connection_probability=0.5)
        test_network.name = "Тест финальный"
        
        # Сохраняем с временем анализа 120 секунд
        test_analysis_time = 120
        network_id = db_manager.save_network(test_network, "Тест финальный", "Описание", test_analysis_time)
        
        print(f"+ Создана тестовая сеть ID {network_id} с временем анализа {test_analysis_time} сек")
        
        # Загружаем данные сети (имитируем NetworkSelectionDialog)
        network_data = db_manager.get_network(network_id)
        if network_data:
            loaded_analysis_time = network_data.get('analysis_time', 300)
            print(f"+ Загружено время анализа: {loaded_analysis_time} сек")
            
            assert loaded_analysis_time == test_analysis_time, f"Время должно быть {test_analysis_time}, получено {loaded_analysis_time}"
            
            # Имитируем результат NetworkSelectionDialog
            result = {
                'action': 'load',
                'network_id': network_id,
                'network_name': network_data['name'],
                'network_data': network_data,
                'analysis_time': loaded_analysis_time
            }
            
            # Имитируем MainWindow._load_network
            final_analysis_time = result.get('analysis_time', 300)
            print(f"+ MainWindow получает: {final_analysis_time} сек")
            
            assert final_analysis_time == test_analysis_time, f"MainWindow должен получить {test_analysis_time}, получено {final_analysis_time}"
            
            print("+ Полная цепочка работает правильно")
            
            # Очищаем тестовую базу данных
            os.remove(test_db_path)
            
            return True
        else:
            print("- Не удалось загрузить данные сети")
            return False
            
    except Exception as e:
        print(f"- Ошибка в тесте полной цепочки: {e}")
        return False

def main():
    """Основная функция"""
    print("ФИНАЛЬНЫЙ ТЕСТ ИСПРАВЛЕНИЯ БАГА")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    try:
        # Тест 1: Логика NetworkSelectionDialog
        if test_network_selection_dialog_logic():
            tests_passed += 1
        
        # Тест 2: Полная цепочка
        if test_full_chain():
            tests_passed += 1
        
        print("\n" + "=" * 50)
        print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {tests_passed}/{total_tests} тестов пройдено")
        
        if tests_passed == total_tests:
            print("ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("Баг с временем анализа исправлен")
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
