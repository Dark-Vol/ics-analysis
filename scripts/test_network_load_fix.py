#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест исправления загрузки сети
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json

def test_network_load_fix():
    """Тестирует исправление загрузки сети"""
    print("Тестирование исправления загрузки сети...")
    
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
        
        # Создаем тестовую сеть и сохраняем её
        print("\n--- Создание и сохранение тестовой сети ---")
        
        # Создаем NetworkModel для сохранения
        network_model = NetworkModel(nodes=0, connection_probability=0)
        network_model.name = "Тестовая сеть для загрузки"
        network_model.description = "Сеть для тестирования исправления загрузки"
        
        # Добавляем узлы
        for i in range(3):
            node = NetworkNode(
                id=i,
                x=10.0 * i,
                y=10.0 * i,
                capacity=100.0 + i * 50,
                reliability=0.9 + i * 0.02,
                processing_delay=0.1
            )
            network_model.nodes.append(node)
        
        # Добавляем связи
        for i in range(2):
            link = NetworkLink(
                source=i,
                target=i + 1,
                bandwidth=1000.0,
                latency=1.0 + i * 0.5,
                reliability=0.95,
                distance=10.0
            )
            network_model.links.append(link)
        
        # Сохраняем сеть
        network_id = main_window.db_manager.save_network(
            network_model, 
            network_model.name, 
            network_model.description
        )
        print(f"[OK] Тестовая сеть сохранена с ID: {network_id}")
        print(f"  - Узлов: {len(network_model.nodes)}")
        print(f"  - Связей: {len(network_model.links)}")
        
        # Тестируем загрузку сети
        print("\n--- Тестирование загрузки сети ---")
        
        try:
            # Получаем данные сети из базы данных
            network_data = main_window.db_manager.get_network(network_id)
            
            if network_data:
                print("[OK] Данные сети получены из базы данных")
                print(f"  - Название: {network_data['name']}")
                print(f"  - Описание: {network_data['description']}")
                
                # Проверяем структуру данных
                network_info = network_data['network_data']
                if 'nodes' in network_info:
                    print(f"  - Узлов в данных: {len(network_info['nodes'])}")
                    if network_info['nodes']:
                        first_node = network_info['nodes'][0]
                        print(f"  - Поля первого узла: {list(first_node.keys())}")
                else:
                    print("[ERROR] Поле 'nodes' не найдено в данных сети")
                    return False
                
                if 'links' in network_info:
                    print(f"  - Связей в данных: {len(network_info['links'])}")
                    if network_info['links']:
                        first_link = network_info['links'][0]
                        print(f"  - Поля первой связи: {list(first_link.keys())}")
                else:
                    print("[ERROR] Поле 'links' не найдено в данных сети")
                    return False
                
                # Тестируем конвертацию данных
                print("\n--- Тестирование конвертации данных ---")
                
                from src.system_model import SystemModel, Node, NodeType, Link, LinkType
                
                network = SystemModel(network_data['name'])
                
                # Конвертируем узлы
                for node_data in network_info.get('nodes', []):
                    node = Node(
                        id=f"node_{node_data['id']}",
                        node_type=NodeType.SERVER,
                        capacity=node_data['capacity'],
                        reliability=node_data['reliability'],
                        cpu_load=0.0,
                        memory_usage=0.0,
                        load=0.0,
                        threat_level=0.1,
                        encryption=True,
                        x=node_data['x'],
                        y=node_data['y']
                    )
                    network.add_node(node)
                
                print(f"[OK] Узлы сконвертированы: {len(network.nodes)}")
                
                # Конвертируем связи
                for link_data in network_info.get('links', []):
                    link = Link(
                        source=f"node_{link_data['source']}",
                        target=f"node_{link_data['target']}",
                        bandwidth=link_data['bandwidth'],
                        latency=link_data['latency'],
                        reliability=link_data['reliability'],
                        link_type=LinkType.ETHERNET,
                        utilization=0.0,
                        load=0.0,
                        encryption=True,
                        threat_level=0.1
                    )
                    network.add_link(link)
                
                print(f"[OK] Связи сконвертированы: {len(network.links)}")
                
                # Проверяем, что сеть создана корректно
                if len(network.nodes) == len(network_model.nodes):
                    print("[OK] Количество узлов совпадает")
                else:
                    print(f"[ERROR] Количество узлов не совпадает: {len(network.nodes)} != {len(network_model.nodes)}")
                    return False
                
                if len(network.links) == len(network_model.links):
                    print("[OK] Количество связей совпадает")
                else:
                    print(f"[ERROR] Количество связей не совпадает: {len(network.links)} != {len(network_model.links)}")
                    return False
                
                print("[SUCCESS] Конвертация данных работает корректно!")
                result = True
                
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
        print(f"[ERROR] Ошибка при тестировании исправления загрузки: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("=" * 60)
    print("ТЕСТ ИСПРАВЛЕНИЯ ЗАГРУЗКИ СЕТИ")
    print("=" * 60)
    
    success = test_network_load_fix()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ ТЕСТА")
    print("=" * 60)
    
    if success:
        print("[SUCCESS] Исправление загрузки сети работает корректно!")
        print("\nРаботающие функции:")
        print("- [OK] Создание и сохранение NetworkModel")
        print("- [OK] Получение данных из базы данных")
        print("- [OK] Конвертация NetworkNode в Node")
        print("- [OK] Конвертация NetworkLink в Link")
        print("- [OK] Создание SystemModel из сохраненных данных")
        print("- [OK] Сохранение количества узлов и связей")
    else:
        print("[ERROR] Проблемы с исправлением загрузки сети")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
