#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладочный скрипт для проверки базы данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from src.database.database_manager import DatabaseManager

def check_database_structure():
    """Проверяет структуру базы данных"""
    print("=== ПРОВЕРКА СТРУКТУРЫ БАЗЫ ДАННЫХ ===")
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect("networks.db")
        cursor = conn.cursor()
        
        # Получаем информацию о таблице networks
        cursor.execute("PRAGMA table_info(networks)")
        columns = cursor.fetchall()
        
        print("Структура таблицы networks:")
        for column in columns:
            print(f"  {column[1]} ({column[2]}) - default: {column[4]}")
        
        # Проверяем, есть ли поле analysis_time
        column_names = [col[1] for col in columns]
        if 'analysis_time' in column_names:
            print("+ Поле analysis_time найдено")
        else:
            print("- Поле analysis_time НЕ найдено!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Ошибка при проверке структуры: {e}")
        return False

def check_network_data():
    """Проверяет данные сетей в базе"""
    print("\n=== ПРОВЕРКА ДАННЫХ СЕТЕЙ ===")
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect("networks.db")
        cursor = conn.cursor()
        
        # Получаем все сети
        cursor.execute("SELECT id, name, analysis_time FROM networks")
        networks = cursor.fetchall()
        
        if networks:
            print("Сети в базе данных:")
            for network in networks:
                print(f"  ID: {network[0]}, Имя: {network[1]}, Время анализа: {network[2]}")
        else:
            print("Нет сетей в базе данных")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Ошибка при проверке данных: {e}")
        return False

def test_database_manager():
    """Тестирует DatabaseManager"""
    print("\n=== ТЕСТ DATABASE_MANAGER ===")
    
    try:
        db_manager = DatabaseManager()
        
        # Получаем все сети через DatabaseManager
        networks = db_manager.get_all_networks()
        
        if networks:
            print("Сети через DatabaseManager:")
            for network in networks:
                print(f"  ID: {network['id']}, Имя: {network['name']}, Время анализа: {network.get('analysis_time', 'НЕ УСТАНОВЛЕНО')}")
        else:
            print("Нет сетей в базе данных")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при тестировании DatabaseManager: {e}")
        return False

def main():
    """Основная функция"""
    print("ОТЛАДКА БАЗЫ ДАННЫХ")
    print("=" * 40)
    
    try:
        # Проверка структуры
        check_database_structure()
        
        # Проверка данных
        check_network_data()
        
        # Тест DatabaseManager
        test_database_manager()
        
        print("\n" + "=" * 40)
        print("Отладка завершена")
        
    except Exception as e:
        print(f"Ошибка в отладке: {e}")

if __name__ == "__main__":
    main()
