#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для отладки ошибки генерации отчетов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.program_state_manager import ProgramStateManager
from src.database.database_manager import DatabaseManager
from src.reports.word_report_generator import WordReportGenerator
from src.models.network_model import NetworkModel

def test_report_generation_debug():
    """Тестирует генерацию отчетов с отладочной информацией"""
    print("=== ОТЛАДКА ГЕНЕРАЦИИ ОТЧЕТОВ ===")
    
    try:
        # Создаем менеджер состояния
        state_manager = ProgramStateManager()
        print("+ ProgramStateManager создан")
        
        # Создаем базу данных
        db_manager = DatabaseManager()
        print("+ DatabaseManager создан")
        
        # Добавляем тестовые данные
        state_manager.log_network_created(1, "Тестовая сеть 1")
        state_manager.log_network_created(2, "Тестовая сеть 2")
        state_manager.start_program()
        state_manager.pause_program()
        state_manager.resume_program()
        state_manager.stop_program()
        print("+ Тестовые данные добавлены")
        
        # Проверяем action_log
        action_log = state_manager.get_action_log()
        print(f"+ action_log type: {type(action_log)}")
        print(f"+ action_log length: {len(action_log)}")
        print(f"+ action_log content: {action_log}")
        
        # Создаем тестовую сеть в базе данных
        test_network = NetworkModel(nodes=3, connection_probability=0.3)
        test_network.name = "Сеть для отчета"
        test_network.description = "Тестовая сеть для генерации отчета"
        network_id = db_manager.save_network(test_network, test_network.name, test_network.description)
        print(f"+ Тестовая сеть создана с ID: {network_id}")
        
        # Проверяем get_networks_status
        networks_status = state_manager.get_networks_status(db_manager)
        print(f"+ networks_status type: {type(networks_status)}")
        print(f"+ networks_status content: {networks_status}")
        
        # Проверяем networks
        networks = networks_status.get('networks', [])
        print(f"+ networks type: {type(networks)}")
        print(f"+ networks length: {len(networks)}")
        print(f"+ networks content: {networks}")
        
        # Генерируем отчет
        print("+ Начинаем генерацию отчета...")
        report_generator = WordReportGenerator()
        report_path = report_generator.create_report(state_manager, db_manager, "debug_test_report.docx")
        
        print(f"+ Отчет создан: {report_path}")
        
        # Удаляем тестовые файлы
        if os.path.exists(report_path):
            os.remove(report_path)
            print("+ Тестовый файл удален")
        
        # Удаляем тестовую сеть
        db_manager.delete_network(network_id)
        print("+ Тестовая сеть удалена")
        
        print("+ Генерация отчета прошла успешно!")
        return True
        
    except Exception as e:
        print(f"- Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("ЗАПУСК ОТЛАДКИ ГЕНЕРАЦИИ ОТЧЕТОВ")
    print("=" * 50)
    
    success = test_report_generation_debug()
    
    if success:
        print("\n+ ОТЛАДКА ЗАВЕРШЕНА УСПЕШНО!")
    else:
        print("\n- ОТЛАДКА ВЫЯВИЛА ПРОБЛЕМЫ!")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
