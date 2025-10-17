#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест диалога выбора сети
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json

def test_network_selection_dialog():
    """Тестирует диалог выбора сети"""
    print("Тестирование диалога выбора сети...")
    
    try:
        from src.gui.network_selection_dialog import NetworkSelectionDialog
        from src.database.database_manager import DatabaseManager
        from src.models.network_model import NetworkModel
        
        # Проверяем импорты
        print("[OK] NetworkSelectionDialog импортирован")
        print("[OK] DatabaseManager импортирован")
        print("[OK] NetworkModel импортирован")
        
        # Создаем корневое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Создаем DatabaseManager
        db_manager = DatabaseManager()
        print("[OK] DatabaseManager создан")
        
        # Создаем тестовую сеть и сохраняем её
        test_network = NetworkModel(nodes=3, connection_probability=0.6)
        test_network.name = "Тестовая сеть для выбора"
        test_network.description = "Сеть для тестирования диалога выбора"
        
        network_id = db_manager.save_network(test_network, test_network.name, test_network.description)
        print(f"[OK] Тестовая сеть сохранена с ID: {network_id}")
        
        # Создаем NetworkSelectionDialog
        dialog = NetworkSelectionDialog(root, db_manager)
        print("[OK] NetworkSelectionDialog создан")
        
        # Проверяем, что диалог создан корректно
        if hasattr(dialog, 'networks_tree'):
            print("[OK] Treeview для списка сетей создан")
        else:
            print("[ERROR] Treeview для списка сетей не найден")
            return False
        
        if hasattr(dialog, 'load_button'):
            print("[OK] Кнопка загрузки создана")
        else:
            print("[ERROR] Кнопка загрузки не найдена")
            return False
        
        if hasattr(dialog, 'delete_button'):
            print("[OK] Кнопка удаления создана")
        else:
            print("[ERROR] Кнопка удаления не найдена")
            return False
        
        # Проверяем методы DatabaseManager
        networks = db_manager.get_all_networks()
        print(f"[OK] Получен список сетей: {len(networks)} сетей")
        
        if networks:
            first_network = networks[0]
            print(f"  - Первая сеть: {first_network.get('name', 'Без названия')}")
            
            # Тестируем получение конкретной сети
            network_data = db_manager.get_network(first_network['id'])
            if network_data:
                print("[OK] Получение конкретной сети работает")
            else:
                print("[ERROR] Не удалось получить данные конкретной сети")
                return False
        
        # Закрываем диалог
        dialog.dialog.destroy()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании диалога выбора сети: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_network_save_load_integration():
    """Тестирует интеграцию сохранения и загрузки сетей"""
    print("\nТестирование интеграции сохранения и загрузки...")
    
    try:
        from src.database.database_manager import DatabaseManager
        from src.models.network_model import NetworkModel
        
        # Создаем DatabaseManager
        db_manager = DatabaseManager()
        
        # Создаем несколько тестовых сетей
        networks_to_save = [
            ("Сеть 1", "Первая тестовая сеть"),
            ("Сеть 2", "Вторая тестовая сеть"),
            ("Сеть 3", "Третья тестовая сеть")
        ]
        
        saved_ids = []
        for name, description in networks_to_save:
            network = NetworkModel(nodes=2, connection_probability=0.5)
            network.name = name
            network.description = description
            
            network_id = db_manager.save_network(network, name, description)
            saved_ids.append(network_id)
            print(f"[OK] Сохранена сеть '{name}' с ID: {network_id}")
        
        # Получаем список всех сетей
        all_networks = db_manager.get_all_networks()
        print(f"[OK] Всего сетей в базе: {len(all_networks)}")
        
        # Проверяем, что все наши сети есть в списке
        saved_names = [n[0] for n in networks_to_save]
        found_names = [n.get('name') for n in all_networks]
        
        for name in saved_names:
            if name in found_names:
                print(f"[OK] Сеть '{name}' найдена в списке")
            else:
                print(f"[ERROR] Сеть '{name}' не найдена в списке")
                return False
        
        # Тестируем загрузку конкретной сети
        first_network = all_networks[0]
        network_data = db_manager.get_network(first_network['id'])
        
        if network_data:
            print(f"[OK] Загружена сеть '{network_data['name']}'")
            if 'network_data' in network_data:
                print("[OK] Данные сети содержат network_data")
            else:
                print("[ERROR] Данные сети не содержат network_data")
                return False
        else:
            print("[ERROR] Не удалось загрузить данные сети")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании интеграции: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ ДИАЛОГА ВЫБОРА СЕТИ")
    print("=" * 60)
    
    success1 = test_network_selection_dialog()
    success2 = test_network_save_load_integration()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success1 and success2:
        print("[SUCCESS] Диалог выбора сети работает корректно!")
        print("\nРаботающие функции:")
        print("- [OK] Создание NetworkSelectionDialog")
        print("- [OK] Создание Treeview для списка сетей")
        print("- [OK] Кнопки загрузки и удаления")
        print("- [OK] Сохранение сетей в базу данных")
        print("- [OK] Получение списка всех сетей")
        print("- [OK] Загрузка конкретной сети по ID")
        print("- [OK] Интеграция с DatabaseManager")
    else:
        print("[ERROR] Проблемы с диалогом выбора сети")
        if not success1:
            print("  - Проблемы с созданием диалога")
        if not success2:
            print("  - Проблемы с интеграцией сохранения/загрузки")
    
    return success1 and success2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

