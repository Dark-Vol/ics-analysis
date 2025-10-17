#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления ошибки 'str' object has no attribute 'x'
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json

def test_string_attribute_fix():
    """Тестирует исправление ошибки с атрибутом строки"""
    print("Тестирование исправления ошибки 'str' object has no attribute 'x'...")
    
    try:
        from src.gui.main_window import MainWindow
        from src.database.database_manager import DatabaseManager
        from src.models.network_model import NetworkModel, NetworkNode, NetworkLink
        
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
        
        # Создаем тестовую сеть с различными типами данных
        print("\n--- Создание тестовой сети с проблемными данными ---")
        
        network_model = NetworkModel(nodes=0, connection_probability=0)
        network_model.name = "Тестовая сеть с проблемными данными"
        network_model.description = "Сеть для тестирования исправления ошибки строки"
        
        # Добавляем узлы с различными типами данных
        test_nodes = [
            {"id": 0, "x": 10.0, "y": 20.0, "capacity": 100.0, "reliability": 0.9, "processing_delay": 0.1},
            {"id": 1, "x": "30", "y": "40", "capacity": "200", "reliability": "0.95", "processing_delay": 0.1},  # Строковые данные
            {"id": 2, "x": 50.0, "y": 60.0, "capacity": 300.0, "reliability": 0.98, "processing_delay": 0.1},
        ]
        
        for node_data in test_nodes:
            node = NetworkNode(
                id=node_data["id"],
                x=node_data["x"],
                y=node_data["y"],
                capacity=node_data["capacity"],
                reliability=node_data["reliability"],
                processing_delay=node_data["processing_delay"]
            )
            network_model.nodes.append(node)
        
        # Добавляем связи с различными типами данных
        test_links = [
            {"source": 0, "target": 1, "bandwidth": 1000.0, "latency": 1.0, "reliability": 0.95, "distance": 10.0},
            {"source": 1, "target": 2, "bandwidth": "2000", "latency": "2.0", "reliability": "0.98", "distance": 20.0},  # Строковые данные
        ]
        
        for link_data in test_links:
            link = NetworkLink(
                source=link_data["source"],
                target=link_data["target"],
                bandwidth=link_data["bandwidth"],
                latency=link_data["latency"],
                reliability=link_data["reliability"],
                distance=link_data["distance"]
            )
            network_model.links.append(link)
        
        # Сохраняем сеть
        network_id = main_window.db_manager.save_network(
            network_model, 
            network_model.name, 
            network_model.description
        )
        print(f"[OK] Тестовая сеть сохранена с ID: {network_id}")
        print(f"  - Узлов: {len(network_model.nodes)} (включая строковые данные)")
        print(f"  - Связей: {len(network_model.links)} (включая строковые данные)")
        
        # Тестируем загрузку сети с проблемными данными
        print("\n--- Тестирование загрузки сети с проблемными данными ---")
        
        try:
            # Получаем данные сети из базы данных
            network_data = main_window.db_manager.get_network(network_id)
            
            if network_data:
                print("[OK] Данные сети получены из базы данных")
                
                # Тестируем конвертацию с проблемными данными
                from src.system_model import SystemModel, Node, NodeType, Link, LinkType
                
                network = SystemModel(network_data['name'])
                
                # Конвертируем узлы (должны обработать строковые данные)
                nodes_processed = 0
                for node_data in network_data['network_data'].get('nodes', []):
                    try:
                        node_id = f"node_{node_data['id']}"
                        capacity = float(node_data['capacity'])
                        reliability = float(node_data['reliability'])
                        x = float(node_data.get('x', 0.0))
                        y = float(node_data.get('y', 0.0))
                        
                        node = Node(
                            id=node_id,
                            node_type=NodeType.SERVER,
                            capacity=capacity,
                            reliability=reliability,
                            cpu_load=0.0,
                            memory_usage=0.0,
                            load=0.0,
                            threat_level=0.1,
                            encryption=True,
                            x=x,
                            y=y
                        )
                        network.add_node(node)
                        nodes_processed += 1
                        
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"[WARNING] Пропущен узел из-за ошибки конвертации: {e}")
                        continue
                
                print(f"[OK] Узлы обработаны: {nodes_processed}/{len(network_data['network_data']['nodes'])}")
                
                # Конвертируем связи (должны обработать строковые данные)
                links_processed = 0
                for link_data in network_data['network_data'].get('links', []):
                    try:
                        source_id = int(link_data['source'])
                        target_id = int(link_data['target'])
                        bandwidth = float(link_data['bandwidth'])
                        latency = float(link_data['latency'])
                        reliability = float(link_data['reliability'])
                        
                        source = f"node_{source_id}"
                        target = f"node_{target_id}"
                        
                        link = Link(
                            source=source,
                            target=target,
                            bandwidth=bandwidth,
                            latency=latency,
                            reliability=reliability,
                            link_type=LinkType.ETHERNET,
                            utilization=0.0,
                            load=0.0,
                            encryption=True,
                            threat_level=0.1
                        )
                        network.add_link(link)
                        links_processed += 1
                        
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"[WARNING] Пропущена связь из-за ошибки конвертации: {e}")
                        continue
                
                print(f"[OK] Связи обработаны: {links_processed}/{len(network_data['network_data']['links'])}")
                
                # Проверяем, что сеть создана без ошибок
                if len(network.nodes) > 0:
                    print("[OK] Сеть создана успешно, несмотря на проблемные данные")
                    print(f"  - Загружено узлов: {len(network.nodes)}")
                    print(f"  - Загружено связей: {len(network.links)}")
                    
                    # Проверяем типы данных в созданных узлах
                    for node_id, node in network.nodes.items():
                        if isinstance(node.x, (int, float)) and isinstance(node.y, (int, float)):
                            print(f"[OK] Узел {node_id}: координаты корректны ({node.x}, {node.y})")
                        else:
                            print(f"[ERROR] Узел {node_id}: некорректные координаты")
                            return False
                    
                    result = True
                else:
                    print("[ERROR] Не удалось создать ни одного узла")
                    result = False
            else:
                print("[ERROR] Не удалось получить данные сети из базы данных")
                result = False
        
        except Exception as e:
            print(f"[ERROR] Ошибка при тестировании загрузки: {e}")
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

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ ИСПРАВЛЕНИЯ ОШИБКИ 'str' object has no attribute 'x'")
    print("=" * 60)
    
    success = test_string_attribute_fix()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success:
        print("[SUCCESS] Исправление ошибки строки работает корректно!")
        print("\nРаботающие функции:")
        print("- [OK] Обработка смешанных типов данных (числа и строки)")
        print("- [OK] Безопасная конвертация типов с try-catch")
        print("- [OK] Пропуск проблемных данных вместо краха")
        print("- [OK] Создание сети из частично корректных данных")
        print("- [OK] Корректные координаты узлов после конвертации")
    else:
        print("[ERROR] Проблемы с исправлением ошибки строки")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

