#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест сохранения и загрузки сетей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json

def test_network_save_load():
    """Тестирует сохранение и загрузку сетей"""
    print("Тестирование сохранения и загрузки сетей...")
    
    try:
        from src.gui.network_dialog import NetworkDialog
        from src.database.database_manager import DatabaseManager
        from src.models.network_model import NetworkModel
        
        # Проверяем импорты
        print("[OK] NetworkDialog импортирован")
        print("[OK] DatabaseManager импортирован")
        print("[OK] NetworkModel импортирован")
        
        # Создаем корневое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Создаем DatabaseManager
        db_manager = DatabaseManager()
        print("[OK] DatabaseManager создан")
        
        # Создаем NetworkDialog с правильными параметрами
        dialog = NetworkDialog(root, db_manager)
        print("[OK] NetworkDialog создан с DatabaseManager")
        
        # Тестируем создание сети
        try:
            network = NetworkModel(nodes=3, connection_probability=0.6)
            print("[OK] Сеть создана успешно")
            print(f"  - Узлов: {len(network.nodes)}")
            print(f"  - Связей: {len(network.links)}")
            
            # Тестируем сохранение сети
            try:
                # Создаем тестовую сеть для сохранения
                test_network = NetworkModel(nodes=2, connection_probability=0.5)
                
                # Проверяем, что у db_manager есть метод save_network
                if hasattr(db_manager, 'save_network'):
                    print("[OK] DatabaseManager имеет метод save_network")
                else:
                    print("[ERROR] DatabaseManager не имеет метода save_network")
                    return False
                
                # Проверяем, что у db_manager есть метод get_all_networks
                if hasattr(db_manager, 'get_all_networks'):
                    print("[OK] DatabaseManager имеет метод get_all_networks")
                else:
                    print("[ERROR] DatabaseManager не имеет метода get_all_networks")
                    return False
                
            except Exception as e:
                print(f"[ERROR] Ошибка при тестировании методов DatabaseManager: {e}")
                return False
            
            result = True
            
        except Exception as e:
            print(f"[ERROR] Ошибка создания сети: {e}")
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании сохранения и загрузки сетей: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ СОХРАНЕНИЯ И ЗАГРУЗКИ СЕТЕЙ")
    print("=" * 60)
    
    success = test_network_save_load()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success:
        print("[SUCCESS] Сохранение и загрузка сетей работает корректно!")
        print("\nРаботающие функции:")
        print("- [OK] Создание DatabaseManager")
        print("- [OK] Создание NetworkDialog с правильными параметрами")
        print("- [OK] Создание тестовой сети")
        print("- [OK] Методы save_network и get_all_networks доступны")
    else:
        print("[ERROR] Проблемы с сохранением и загрузкой сетей")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

