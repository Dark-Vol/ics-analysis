#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки новых функций:
1. Удаление сетей
2. Управление выполнением программы
3. Генерация отчетов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager
from src.utils.program_state_manager import ProgramStateManager
from src.models.network_model import NetworkModel, NetworkNode, NetworkLink
from src.reports.word_report_generator import WordReportGenerator

def test_network_deletion():
    """Тестирует удаление сетей"""
    print("=== ТЕСТ УДАЛЕНИЯ СЕТЕЙ ===")
    
    # Создаем базу данных
    db_manager = DatabaseManager()
    
    # Создаем тестовую сеть
    network = NetworkModel(nodes=5, connection_probability=0.3)
    network.name = "Тестовая сеть для удаления"
    network.description = "Сеть для тестирования удаления"
    
    # Сохраняем сеть
    network_id = db_manager.save_network(network, network.name, network.description)
    print(f"Создана тестовая сеть с ID: {network_id}")
    
    # Получаем список сетей
    networks = db_manager.get_all_networks()
    print(f"Количество сетей до удаления: {len(networks)}")
    
    # Удаляем сеть
    success = db_manager.delete_network(network_id)
    print(f"Удаление сети: {'Успешно' if success else 'Ошибка'}")
    
    # Проверяем результат
    networks_after = db_manager.get_all_networks()
    print(f"Количество сетей после удаления: {len(networks_after)}")
    
    assert len(networks_after) == len(networks) - 1, "Количество сетей должно уменьшиться на 1"
    print("+ Тест удаления одной сети прошел успешно")
    
    # Тестируем удаление всех сетей
    # Создаем несколько сетей
    for i in range(3):
        test_network = NetworkModel(nodes=3, connection_probability=0.2)
        test_network.name = f"Тестовая сеть {i+1}"
        db_manager.save_network(test_network, test_network.name, f"Описание {i+1}")
    
    networks_before_all = db_manager.get_all_networks()
    print(f"Количество сетей перед удалением всех: {len(networks_before_all)}")
    
    # Удаляем все сети
    deleted_count = db_manager.delete_all_networks()
    print(f"Удалено сетей: {deleted_count}")
    
    networks_after_all = db_manager.get_all_networks()
    print(f"Количество сетей после удаления всех: {len(networks_after_all)}")
    
    assert len(networks_after_all) == 0, "Все сети должны быть удалены"
    assert deleted_count == len(networks_before_all), "Количество удаленных сетей должно совпадать"
    print("+ Тест удаления всех сетей прошел успешно")

def test_program_state_manager():
    """Тестирует менеджер состояния программы"""
    print("\n=== ТЕСТ МЕНЕДЖЕРА СОСТОЯНИЯ ПРОГРАММЫ ===")
    
    # Создаем менеджер состояния
    state_manager = ProgramStateManager()
    
    # Проверяем начальное состояние
    initial_state = state_manager.state.value
    print(f"Начальное состояние: {initial_state}")
    assert initial_state == 'stopped', "Начальное состояние должно быть 'stopped'"
    
    # Запускаем программу
    success = state_manager.start_program()
    print(f"Запуск программы: {'Успешно' if success else 'Ошибка'}")
    assert success, "Запуск программы должен быть успешным"
    assert state_manager.state.value == 'running', "Состояние должно быть 'running'"
    
    # Логируем создание сети
    state_manager.log_network_created(1, "Тестовая сеть")
    state_manager.log_network_deleted(1, "Тестовая сеть")
    state_manager.log_simulation_started(2, "Другая сеть")
    
    # Приостанавливаем программу
    success = state_manager.pause_program()
    print(f"Пауза программы: {'Успешно' if success else 'Ошибка'}")
    assert success, "Пауза программы должна быть успешной"
    assert state_manager.state.value == 'paused', "Состояние должно быть 'paused'"
    
    # Возобновляем программу
    success = state_manager.resume_program()
    print(f"Возобновление программы: {'Успешно' if success else 'Ошибка'}")
    assert success, "Возобновление программы должно быть успешным"
    assert state_manager.state.value == 'running', "Состояние должно быть 'running'"
    
    # Останавливаем программу
    success = state_manager.stop_program()
    print(f"Остановка программы: {'Успешно' if success else 'Ошибка'}")
    assert success, "Остановка программы должна быть успешной"
    assert state_manager.state.value == 'stopped', "Состояние должно быть 'stopped'"
    
    # Проверяем статус
    status_info = state_manager.get_status_info()
    print(f"Информация о состоянии: {status_info['state_display']}")
    print(f"Время выполнения: {status_info['runtime_display']}")
    print(f"Количество пауз: {status_info['pause_count']}")
    
    # Проверяем журнал действий
    action_log = state_manager.get_action_log()
    print(f"Количество записей в журнале: {len(action_log)}")
    assert len(action_log) > 0, "Журнал действий не должен быть пустым"
    
    print("+ Тест менеджера состояния программы прошел успешно")

def test_word_report_generator():
    """Тестирует генератор отчетов в Word"""
    print("\n=== ТЕСТ ГЕНЕРАТОРА ОТЧЕТОВ ===")
    
    try:
        # Создаем менеджер состояния
        state_manager = ProgramStateManager()
        
        # Создаем базу данных
        db_manager = DatabaseManager()
        
        # Добавляем тестовые данные
        state_manager.log_network_created(1, "Тестовая сеть 1")
        state_manager.log_network_created(2, "Тестовая сеть 2")
        state_manager.log_simulation_started(1, "Тестовая сеть 1")
        state_manager.pause_program()
        state_manager.resume_program()
        state_manager.stop_program()
        
        # Создаем тестовую сеть в базе данных
        test_network = NetworkModel(nodes=3, connection_probability=0.3)
        test_network.name = "Сеть для отчета"
        test_network.description = "Тестовая сеть для генерации отчета"
        db_manager.save_network(test_network, test_network.name, test_network.description)
        
        # Генерируем отчет
        report_generator = WordReportGenerator()
        report_path = report_generator.create_report(state_manager, db_manager, "test_report.docx")
        
        # Проверяем, что файл создан
        assert os.path.exists(report_path), "Файл отчета должен быть создан"
        print(f"Отчет создан: {report_path}")
        
        # Проверяем размер файла
        file_size = os.path.getsize(report_path)
        print(f"Размер файла отчета: {file_size} байт")
        assert file_size > 0, "Файл отчета не должен быть пустым"
        
        # Удаляем тестовый файл
        os.remove(report_path)
        print("Тестовый файл отчета удален")
        
        print("+ Тест генератора отчетов прошел успешно")
        
    except ImportError:
        print("Модуль python-docx не установлен. Пропускаем тест генератора отчетов.")
        print("Установите: pip install python-docx")
    except Exception as e:
        print(f"Ошибка в тесте генератора отчетов: {e}")
        raise

def main():
    """Основная функция тестирования"""
    print("ЗАПУСК ТЕСТОВ НОВЫХ ФУНКЦИЙ")
    print("=" * 50)
    
    try:
        # Тестируем удаление сетей
        test_network_deletion()
        
        # Тестируем менеджер состояния программы
        test_program_state_manager()
        
        # Тестируем генератор отчетов
        test_word_report_generator()
        
        print("\n" + "=" * 50)
        print("ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("Новые функции готовы к использованию:")
        print("+ Удаление сетей (одной или всех)")
        print("+ Управление выполнением программы (пауза/продолжение/стоп)")
        print("+ Генерация отчетов в формате Word")
        print("+ Отслеживание состояния программы")
        print("+ Журнал действий")
        
    except Exception as e:
        print(f"\nОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
