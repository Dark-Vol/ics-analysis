#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест создания сети
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json

def test_network_creation():
    """Тестирует создание сети"""
    print("Тестирование создания сети...")
    
    try:
        from src.gui.network_dialog import NetworkDialog
        from src.database.database_manager import DatabaseManager
        from src.models.network_model import NetworkModel, NetworkNode, NetworkLink
        
        # Проверяем импорты
        print("[OK] NetworkDialog импортирован")
        print("[OK] NetworkNode импортирован")
        print("[OK] NetworkLink импортирован")
        
        # Создаем корневое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Создаем DatabaseManager
        db_manager = DatabaseManager()
        
        # Создаем NetworkDialog
        dialog = NetworkDialog(root, db_manager)
        print("[OK] NetworkDialog создан")
        
        # Тестируем создание простой сети программно
        try:
            # Создаем простую тестовую сеть (NetworkModel автоматически создает узлы и связи)
            network = NetworkModel(nodes=2, connection_probability=0.5)
            
            print("[OK] Сеть создана успешно")
            print(f"  - Узлов: {len(network.nodes)}")
            print(f"  - Связей: {len(network.links)}")
            
            result = True
            
        except Exception as e:
            print(f"[ERROR] Ошибка создания сети: {e}")
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании создания сети: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ СЕТИ")
    print("=" * 60)
    
    success = test_network_creation()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success:
        print("[SUCCESS] Создание сети работает корректно!")
        print("\nРаботающие функции:")
        print("- [OK] Импорт NetworkDialog")
        print("- [OK] Импорт NetworkNode и NetworkLink")
        print("- [OK] Создание NetworkDialog")
        print("- [OK] Создание тестовой сети")
    else:
        print("[ERROR] Проблемы с созданием сети")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
