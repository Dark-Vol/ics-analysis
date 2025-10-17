#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест загрузки конкретной сети
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database_manager import DatabaseManager

def test_network_38():
    """Тестирует загрузку сети с ID 38"""
    print("=== ТЕСТ ЗАГРУЗКИ СЕТИ ID 38 ===")
    
    try:
        db_manager = DatabaseManager()
        
        # Получаем данные сети
        network_data = db_manager.get_network(38)
        if network_data:
            print(f"Данные сети ID 38:")
            print(f"  ID: {network_data['id']}")
            print(f"  Имя: {network_data['name']}")
            print(f"  Описание: {network_data['description']}")
            print(f"  Время анализа: {network_data.get('analysis_time', 'НЕ УСТАНОВЛЕНО')}")
            print(f"  Создана: {network_data['created_at']}")
            print(f"  Обновлена: {network_data['updated_at']}")
            
            # Загружаем саму сеть
            network = db_manager.load_network(38)
            if network:
                print(f"  Сеть загружена: {len(network.nodes)} узлов, {len(network.links)} связей")
                return True
            else:
                print("- Не удалось загрузить сеть")
                return False
        else:
            print("- Не удалось получить данные сети")
            return False
            
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("ТЕСТ ЗАГРУЗКИ КОНКРЕТНОЙ СЕТИ")
    print("=" * 40)
    
    test_network_38()

if __name__ == "__main__":
    main()
