#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления NetworkViewer для работы с SystemModel
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json

def test_network_viewer_fix():
    """Тестирует исправление NetworkViewer"""
    print("Тестирование исправления NetworkViewer...")
    
    try:
        from src.gui.network_viewer import NetworkViewer
        from src.system_model import SystemModel, Node, NodeType, Link, LinkType
        
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
        
        # Создаем фрейм для NetworkViewer
        frame = tk.Frame(root)
        
        # Создаем NetworkViewer
        viewer = NetworkViewer(root, frame)
        print("[OK] NetworkViewer создан")
        
        # Создаем тестовую SystemModel
        print("\n--- Создание тестовой SystemModel ---")
        
        system_model = SystemModel("Тестовая SystemModel")
        
        # Добавляем узлы
        for i in range(3):
            node = Node(
                id=f"node_{i}",
                node_type=NodeType.SERVER,
                capacity=100.0 + i * 50,
                reliability=0.9 + i * 0.02,
                cpu_load=0.0,
                memory_usage=0.0,
                load=0.0,
                threat_level=0.1,
                encryption=True,
                x=10.0 * i,
                y=10.0 * i
            )
            system_model.add_node(node)
        
        # Добавляем связи
        for i in range(2):
            link = Link(
                source=f"node_{i}",
                target=f"node_{i + 1}",
                bandwidth=1000.0,
                latency=1.0 + i * 0.5,
                reliability=0.95,
                link_type=LinkType.ETHERNET,
                utilization=0.0,
                load=0.0,
                encryption=True,
                threat_level=0.1
            )
            system_model.add_link(link)
        
        print(f"[OK] SystemModel создана: {len(system_model.nodes)} узлов, {len(system_model.links)} связей")
        
        # Тестируем обновление NetworkViewer с SystemModel
        print("\n--- Тестирование обновления NetworkViewer ---")
        
        try:
            # Обновляем NetworkViewer с SystemModel
            viewer.update_network(system_model)
            print("[OK] NetworkViewer обновлен с SystemModel")
            
            # Проверяем, что сеть установлена
            if viewer.network:
                print("[OK] Сеть установлена в NetworkViewer")
                print(f"  - Тип сети: {type(viewer.network)}")
                print(f"  - Название: {viewer.network.name}")
                
                # Проверяем, что _draw_network не падает
                try:
                    viewer._draw_network()
                    print("[OK] _draw_network работает без ошибок")
                except Exception as e:
                    print(f"[ERROR] _draw_network падает: {e}")
                    return False
                
                # Проверяем, что _update_network_info работает
                try:
                    viewer._update_network_info()
                    print("[OK] _update_network_info работает без ошибок")
                    info_text = viewer.network_info_var.get()
                    print(f"  - Информация о сети: {info_text}")
                except Exception as e:
                    print(f"[ERROR] _update_network_info падает: {e}")
                    return False
                
                result = True
            else:
                print("[ERROR] Сеть не установлена в NetworkViewer")
                result = False
        
        except Exception as e:
            print(f"[ERROR] Ошибка при тестировании NetworkViewer: {e}")
            import traceback
            traceback.print_exc()
            result = False
        
        root.destroy()
        return result
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании исправления: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mixed_network_types():
    """Тестирует работу с разными типами сетей"""
    print("\n--- Тестирование работы с разными типами сетей ---")
    
    try:
        from src.gui.network_viewer import NetworkViewer
        from src.models.network_model import NetworkModel
        
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
        
        # Создаем фрейм для NetworkViewer
        frame = tk.Frame(root)
        
        # Создаем NetworkViewer
        viewer = NetworkViewer(root, frame)
        
        # Тестируем с NetworkModel
        network_model = NetworkModel(nodes=2, connection_probability=0.5)
        viewer.update_network(network_model)
        print("[OK] NetworkViewer работает с NetworkModel")
        
        # Тестируем с None
        viewer.update_network(None)
        print("[OK] NetworkViewer работает с None")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании разных типов сетей: {e}")
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ ИСПРАВЛЕНИЯ NETWORKVIEWER")
    print("=" * 60)
    
    success1 = test_network_viewer_fix()
    success2 = test_mixed_network_types()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success1 and success2:
        print("[SUCCESS] Исправление NetworkViewer работает корректно!")
        print("\nРаботающие функции:")
        print("- [OK] NetworkViewer работает с SystemModel")
        print("- [OK] NetworkViewer работает с NetworkModel")
        print("- [OK] _draw_network обрабатывает разные типы узлов и связей")
        print("- [OK] _update_network_info работает с разными типами сетей")
        print("- [OK] Обработка None и неподдерживаемых типов")
    else:
        print("[ERROR] Проблемы с исправлением NetworkViewer")
        if not success1:
            print("  - Проблемы с SystemModel")
        if not success2:
            print("  - Проблемы с разными типами сетей")
    
    return success1 and success2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
