#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест создания симулятора после создания сети
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json

def test_simulator_creation():
    """Тестирует создание симулятора после создания сети"""
    print("Тестирование создания симулятора...")
    
    try:
        from src.gui.main_window import MainWindow
        
        # Загружаем конфигурацию
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {
                "simulation": {"time_steps": 1000, "dt": 0.1, "random_seed": 42},
                "network": {"nodes": 10, "connections": 0.3, "bandwidth": 1000, "latency": 10, "reliability": 0.95}
            }
        
        # Создаем корневое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Создаем MainWindow
        main_window = MainWindow(root, config)
        print("[OK] MainWindow создан")
        
        # Проверяем, что симулятор изначально не создан
        if hasattr(main_window, 'simulator') and main_window.simulator:
            print("[WARNING] Симулятор уже создан при инициализации")
        else:
            print("[OK] Симулятор не создан при инициализации (ожидаемо)")
        
        # Создаем тестовую сеть
        from src.system_model import SystemModel, Node, NodeType, Link, LinkType
        import random
        
        network = SystemModel("Тестовая сеть")
        
        # Создаем несколько узлов
        for i in range(3):
            node = Node(
                id=f"node_{i}",
                node_type=random.choice(list(NodeType)),
                capacity=random.uniform(100, 1000),
                reliability=random.uniform(0.85, 0.99),
                x=random.uniform(0, 100),
                y=random.uniform(0, 100),
                threat_level=random.uniform(0.1, 0.3),
                load=random.uniform(0.2, 0.8)
            )
            network.add_node(node)
        
        # Создаем связь
        nodes = list(network.nodes.keys())
        if len(nodes) >= 2:
            link = Link(
                source=nodes[0],
                target=nodes[1],
                bandwidth=random.uniform(10, 100),
                latency=random.uniform(1, 50),
                reliability=random.uniform(0.90, 0.99),
                link_type=random.choice(list(LinkType)),
                threat_level=random.uniform(0.05, 0.2),
                load=random.uniform(0.1, 0.6)
            )
            network.add_link(link)
        
        print(f"[OK] Тестовая сеть создана: {len(network.nodes)} узлов, {len(network.links)} связей")
        
        # Тестируем создание симулятора
        try:
            main_window._create_simulator_for_network(network)
            
            # Проверяем, что симулятор создан
            if hasattr(main_window, 'simulator') and main_window.simulator:
                print("[OK] Симулятор создан успешно")
                
                # Проверяем методы симулятора
                if hasattr(main_window.simulator, 'start_simulation'):
                    print("[OK] Симулятор имеет метод start_simulation")
                else:
                    print("[ERROR] Симулятор не имеет метода start_simulation")
                    return False
                
                if hasattr(main_window.simulator, 'is_running'):
                    print("[OK] Симулятор имеет атрибут is_running")
                else:
                    print("[ERROR] Симулятор не имеет атрибута is_running")
                    return False
                
                result = True
            else:
                print("[ERROR] Симулятор не создан")
                result = False
                
        except Exception as e:
            print(f"[ERROR] Ошибка создания симулятора: {e}")
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании создания симулятора: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ СОЗДАНИЯ СИМУЛЯТОРА")
    print("=" * 60)
    
    success = test_simulator_creation()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success:
        print("[SUCCESS] Создание симулятора работает корректно!")
        print("\nРаботающие функции:")
        print("- [OK] Создание MainWindow")
        print("- [OK] Создание тестовой сети")
        print("- [OK] Создание симулятора для сети")
        print("- [OK] Методы симулятора доступны")
    else:
        print("[ERROR] Проблемы с созданием симулятора")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

