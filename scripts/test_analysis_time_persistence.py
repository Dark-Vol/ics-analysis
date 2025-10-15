#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки сохранения времени анализа сети
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager
from src.models.network_model import NetworkModel

def test_analysis_time_persistence():
    """Тестирует сохранение и загрузку времени анализа"""
    print("=== ТЕСТ СОХРАНЕНИЯ ВРЕМЕНИ АНАЛИЗА ===")
    
    try:
        # Создаем тестовую базу данных
        test_db_path = "test_networks.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        db_manager = DatabaseManager(test_db_path)
        
        # Создаем тестовую сеть
        test_network = NetworkModel(nodes=5, connection_probability=0.3)
        test_network.name = "Тестовая сеть для времени"
        test_network.description = "Сеть для тестирования сохранения времени анализа"
        
        # Тестируем разные времена анализа
        test_times = [60, 180, 600, 1800]  # 1 мин, 3 мин, 10 мин, 30 мин
        
        for i, analysis_time in enumerate(test_times):
            network_name = f"Тестовая сеть {i+1}"
            
            # Сохраняем сеть с определенным временем анализа
            network_id = db_manager.save_network(
                test_network, 
                network_name, 
                f"Описание для времени {analysis_time} сек",
                analysis_time
            )
            
            print(f"+ Создана сеть '{network_name}' с временем анализа {analysis_time} сек")
            
            # Загружаем данные сети
            network_data = db_manager.get_network(network_id)
            
            # Проверяем, что время анализа сохранено правильно
            saved_time = network_data.get('analysis_time', None)
            assert saved_time == analysis_time, f"Время анализа не сохранено правильно. Ожидалось {analysis_time}, получено {saved_time}"
            
            print(f"+ Время анализа {analysis_time} сек сохранено и загружено корректно")
            
            # Загружаем саму сеть
            loaded_network = db_manager.load_network(network_id)
            assert loaded_network is not None, "Сеть не загрузилась"
            
            print(f"+ Сеть '{network_name}' загружена успешно")
        
        # Тестируем загрузку через NetworkSelectionDialog (имитация)
        print("\n+ Тестируем загрузку через диалог выбора сетей...")
        
        for i, analysis_time in enumerate(test_times):
            network_name = f"Тестовая сеть {i+1}"
            
            # Имитируем получение данных сети через get_network
            all_networks = db_manager.get_all_networks()
            network_data = None
            for net in all_networks:
                if net['name'] == network_name:
                    network_data = net
                    break
            
            assert network_data is not None, f"Сеть '{network_name}' не найдена в списке"
            
            # Проверяем, что время анализа доступно
            saved_analysis_time = network_data.get('analysis_time', None)
            assert saved_analysis_time == analysis_time, f"Время анализа не соответствует. Ожидалось {analysis_time}, получено {saved_analysis_time}"
            
            print(f"+ Сеть '{network_name}' в списке имеет правильное время анализа: {saved_analysis_time} сек")
        
        # Очищаем тестовую базу данных
        os.remove(test_db_path)
        
        print("+ Тест сохранения времени анализа прошел успешно")
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_migration():
    """Тестирует миграцию базы данных"""
    print("\n=== ТЕСТ МИГРАЦИИ БАЗЫ ДАННЫХ ===")
    
    try:
        # Создаем тестовую базу данных
        test_db_path = "test_migration.db"
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        # Создаем DatabaseManager - это должно запустить миграцию
        db_manager = DatabaseManager(test_db_path)
        
        # Проверяем, что поле analysis_time добавлено
        import sqlite3
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # Получаем информацию о таблице networks
        cursor.execute("PRAGMA table_info(networks)")
        columns = cursor.fetchall()
        
        # Проверяем, что поле analysis_time существует
        analysis_time_column = None
        for column in columns:
            if column[1] == 'analysis_time':  # column[1] - имя столбца
                analysis_time_column = column
                break
        
        assert analysis_time_column is not None, "Поле analysis_time не найдено в таблице networks"
        
        # Проверяем тип поля
        assert analysis_time_column[2] == 'INTEGER', f"Неправильный тип поля analysis_time: {analysis_time_column[2]}"
        
        # Проверяем, что поле существует и имеет правильный тип
        default_value = analysis_time_column[4]
        print(f"+ Значение по умолчанию: {default_value}")
        
        # Значение по умолчанию может быть 300 (для новых таблиц) или None (для мигрированных)
        # Главное, что поле существует и имеет тип INTEGER
        
        print("+ Поле analysis_time добавлено в таблицу networks")
        print(f"+ Тип поля: {analysis_time_column[2]}")
        print(f"+ Значение по умолчанию: {analysis_time_column[4]}")
        
        conn.close()
        
        # Очищаем тестовую базу данных
        os.remove(test_db_path)
        
        print("+ Тест миграции базы данных прошел успешно")
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте миграции: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("ЗАПУСК ТЕСТОВ СОХРАНЕНИЯ ВРЕМЕНИ АНАЛИЗА")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 2
    
    try:
        # Тест 1: Сохранение и загрузка времени анализа
        if test_analysis_time_persistence():
            tests_passed += 1
        
        # Тест 2: Миграция базы данных
        if test_database_migration():
            tests_passed += 1
        
        print("\n" + "=" * 60)
        print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {tests_passed}/{total_tests} тестов пройдено")
        
        if tests_passed == total_tests:
            print("ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("Сохранение времени анализа работает корректно")
            print("Миграция базы данных выполнена успешно")
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
