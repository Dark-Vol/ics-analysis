"""
Демонстрация сохранения сети, созданной пользователем/программой
Показывает, как сохраняется реальная сеть из приложения в файл .db
"""

import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.network_storage import NetworkStorage
from src.system_model import SystemModel, Node, NodeType, Link, LinkType

def create_user_network():
    """Создает сеть, как это делает пользователь в приложении"""
    
    print("Создание сети пользователем/программой")
    print("=" * 50)
    
    # Создаем сеть через SystemModel (как в приложении)
    network = SystemModel("Пользовательская сеть")
    
    # Добавляем узлы (как создает пользователь)
    nodes_data = [
        ("server1", NodeType.SERVER, 1000.0, 0.95, 0.0, 0.0, 0.0, 0.1, True, 100.0, 200.0),
        ("server2", NodeType.SERVER, 1500.0, 0.98, 0.0, 0.0, 0.0, 0.1, True, 300.0, 200.0),
        ("router1", NodeType.ROUTER, 2000.0, 0.99, 0.0, 0.0, 0.0, 0.05, True, 200.0, 100.0),
        ("client1", NodeType.CLIENT, 500.0, 0.90, 0.0, 0.0, 0.0, 0.2, True, 100.0, 300.0),
        ("client2", NodeType.CLIENT, 500.0, 0.90, 0.0, 0.0, 0.0, 0.2, True, 300.0, 300.0),
    ]
    
    print("Добавление узлов:")
    for node_data in nodes_data:
        node = Node(
            id=node_data[0],
            node_type=node_data[1],
            capacity=node_data[2],
            reliability=node_data[3],
            cpu_load=node_data[4],
            memory_usage=node_data[5],
            load=node_data[6],
            threat_level=node_data[7],
            encryption=node_data[8],
            x=node_data[9],
            y=node_data[10]
        )
        network.add_node(node)
        print(f"  Добавлен узел: {node.id} ({node.node_type.value})")
    
    # Добавляем связи (как создает пользователь)
    links_data = [
        ("router1", "server1", 1000.0, 5.0, 0.99, LinkType.ETHERNET, 0.0, 0.0, True, 0.05),
        ("router1", "server2", 1000.0, 5.0, 0.99, LinkType.ETHERNET, 0.0, 0.0, True, 0.05),
        ("server1", "client1", 100.0, 10.0, 0.95, LinkType.WIFI, 0.0, 0.0, True, 0.1),
        ("server2", "client2", 100.0, 10.0, 0.95, LinkType.WIFI, 0.0, 0.0, True, 0.1),
        ("server1", "server2", 500.0, 2.0, 0.98, LinkType.FIBER, 0.0, 0.0, True, 0.02),
    ]
    
    print(f"\nДобавление связей:")
    for link_data in links_data:
        link = Link(
            source=link_data[0],
            target=link_data[1],
            bandwidth=link_data[2],
            latency=link_data[3],
            reliability=link_data[4],
            link_type=link_data[5],
            utilization=link_data[6],
            load=link_data[7],
            encryption=link_data[8],
            threat_level=link_data[9]
        )
        network.add_link(link)
        print(f"  Добавлена связь: {link.source} -> {link.target}")
    
    print(f"\nСоздана сеть:")
    print(f"  Название: {network.name}")
    print(f"  Узлов: {len(network.nodes)}")
    print(f"  Связей: {len(network.links)}")
    
    return network


def convert_to_storage_format(network):
    """Конвертирует сеть из SystemModel в формат для хранения"""
    
    print(f"\nКонвертация в формат хранения...")
    
    # Создаем словарь связей (как требует формат .db)
    network_data = {}
    
    # Инициализируем все узлы
    for node_id, node in network.nodes.items():
        network_data[node_id] = []
    
    # Добавляем связи
    for (source, target), link in network.links.items():
        if source in network_data:
            network_data[source].append(target)
    
    print("Структура для сохранения в .db файл:")
    print("-" * 40)
    for node_id, connections in network_data.items():
        if connections:
            print(f"{node_id} связан с: {', '.join(connections)}")
        else:
            print(f"{node_id} не имеет исходящих связей")
    
    return network_data


def save_user_network():
    """Сохраняет пользовательскую сеть в файл .db"""
    
    print(f"\nСохранение пользовательской сети в файл .db")
    print("=" * 50)
    
    # Создаем сеть (как пользователь)
    user_network = create_user_network()
    
    # Конвертируем в формат хранения
    storage_data = convert_to_storage_format(user_network)
    
    # Создаем хранилище
    storage = NetworkStorage("user_networks")
    
    # Сохраняем сеть
    network_name = "user_network_1"
    success = storage.save_network(network_name, storage_data)
    
    if success:
        print(f"\nСеть сохранена в файл: user_networks/{network_name}.db")
        
        # Получаем информацию о файле
        info = storage.get_network_info(network_name)
        if info:
            print(f"\nИнформация о сохраненном файле:")
            print(f"  Имя файла: {info['name']}.db")
            print(f"  Размер файла: {info['file_size']} байт")
            print(f"  Количество узлов: {info['node_count']}")
            print(f"  Количество связей: {info['connection_count']}")
            print(f"  Полный путь: {info['file_path']}")
        
        # Загружаем обратно для проверки
        print(f"\nЗагрузка сети из файла для проверки...")
        loaded_data = storage.load_network(network_name)
        
        if loaded_data:
            print("Сеть загружена успешно")
            
            # Проверяем целостность
            if loaded_data == storage_data:
                print("Данные сохранены и загружены без изменений")
            else:
                print("ВНИМАНИЕ: Данные изменились при сохранении/загрузке")
            
            # Показываем загруженные данные
            print(f"\nЗагруженные данные из файла .db:")
            print("-" * 35)
            for node_id, connections in loaded_data.items():
                if connections:
                    print(f"{node_id} связан с: {', '.join(connections)}")
                else:
                    print(f"{node_id} не имеет исходящих связей")
        
        # Экспортируем в текст для просмотра
        print(f"\nЭкспорт в текстовый формат...")
        export_success = storage.export_network_to_text(network_name)
        if export_success:
            print("Экспорт выполнен успешно")
            
            # Показываем содержимое текстового файла
            txt_file = f"user_networks/{network_name}.txt"
            if os.path.exists(txt_file):
                print(f"\nСодержимое текстового файла:")
                print("-" * 30)
                with open(txt_file, 'r', encoding='utf-8') as f:
                    print(f.read())
    
    else:
        print("Ошибка при сохранении сети")


def demonstrate_multiple_networks():
    """Демонстрирует сохранение нескольких пользовательских сетей"""
    
    print(f"\n\nДемонстрация сохранения нескольких сетей")
    print("=" * 50)
    
    storage = NetworkStorage("user_networks")
    
    # Создаем несколько разных сетей
    networks = [
        {
            "name": "office_network",
            "data": {
                'main_server': ['workstation1', 'workstation2', 'printer'],
                'workstation1': ['main_server'],
                'workstation2': ['main_server'],
                'printer': []
            }
        },
        {
            "name": "home_network", 
            "data": {
                'router': ['laptop', 'phone', 'tv'],
                'laptop': ['router'],
                'phone': ['router'],
                'tv': ['router']
            }
        },
        {
            "name": "server_farm",
            "data": {
                'load_balancer': ['web1', 'web2', 'web3'],
                'web1': ['db1'],
                'web2': ['db1'],
                'web3': ['db1'],
                'db1': ['backup_server'],
                'backup_server': []
            }
        }
    ]
    
    print("Создание и сохранение нескольких сетей:")
    for network_info in networks:
        print(f"\nСохранение сети: {network_info['name']}")
        success = storage.save_network(network_info['name'], network_info['data'])
        if success:
            print(f"  Сеть '{network_info['name']}' сохранена успешно")
        else:
            print(f"  Ошибка при сохранении сети '{network_info['name']}'")
    
    # Показываем список всех сохраненных сетей
    print(f"\nСписок всех сохраненных сетей:")
    print("-" * 35)
    all_networks = storage.list_networks()
    for i, network_name in enumerate(all_networks, 1):
        info = storage.get_network_info(network_name)
        if info:
            print(f"{i}. {network_name}")
            print(f"   Узлов: {info['node_count']}, Связей: {info['connection_count']}")
            print(f"   Размер: {info['file_size']} байт")


if __name__ == "__main__":
    try:
        # Сохраняем одну пользовательскую сеть
        save_user_network()
        
        # Демонстрируем сохранение нескольких сетей
        demonstrate_multiple_networks()
        
        print(f"\n\nДемонстрация завершена!")
        print("=" * 50)
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
