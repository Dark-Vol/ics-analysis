"""
Пример работы с более сложной сетью
Показывает, как система хранит информацию о связях в файлах .db
"""

import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.network_storage import NetworkStorage

def create_complex_network():
    """Создает более сложную сеть для демонстрации"""
    
    print("Создание сложной сети для демонстрации")
    print("=" * 50)
    
    # Создаем сложную сеть с различными типами связей
    complex_network = {
        # Центральный сервер
        'central_server': ['web_server1', 'web_server2', 'database_server', 'backup_server'],
        
        # Веб-серверы
        'web_server1': ['database_server', 'cache_server'],
        'web_server2': ['database_server', 'cache_server'],
        
        # Сервер базы данных
        'database_server': ['backup_server', 'replica_server'],
        
        # Кэш-сервер
        'cache_server': [],
        
        # Резервный сервер
        'backup_server': [],
        
        # Реплика сервера БД
        'replica_server': [],
        
        # Маршрутизаторы
        'router_main': ['central_server', 'firewall'],
        'router_backup': ['central_server'],
        
        # Файрвол
        'firewall': ['central_server'],
        
        # Клиентские станции
        'client_station1': ['router_main'],
        'client_station2': ['router_main'],
        'client_station3': ['router_backup']
    }
    
    print("Структура сложной сети:")
    print("-" * 30)
    
    # Группируем узлы по типам
    server_nodes = [node for node in complex_network.keys() if 'server' in node]
    router_nodes = [node for node in complex_network.keys() if 'router' in node]
    client_nodes = [node for node in complex_network.keys() if 'client' in node]
    other_nodes = [node for node in complex_network.keys() 
                   if node not in server_nodes and node not in router_nodes and node not in client_nodes]
    
    print(f"Серверы ({len(server_nodes)}):")
    for node in server_nodes:
        connections = complex_network[node]
        print(f"  {node}: {len(connections)} связей -> {', '.join(connections) if connections else 'нет'}")
    
    print(f"\nМаршрутизаторы ({len(router_nodes)}):")
    for node in router_nodes:
        connections = complex_network[node]
        print(f"  {node}: {len(connections)} связей -> {', '.join(connections) if connections else 'нет'}")
    
    print(f"\nКлиентские станции ({len(client_nodes)}):")
    for node in client_nodes:
        connections = complex_network[node]
        print(f"  {node}: {len(connections)} связей -> {', '.join(connections) if connections else 'нет'}")
    
    if other_nodes:
        print(f"\nДругие узлы ({len(other_nodes)}):")
        for node in other_nodes:
            connections = complex_network[node]
            print(f"  {node}: {len(connections)} связей -> {', '.join(connections) if connections else 'нет'}")
    
    return complex_network


def analyze_network_topology(network):
    """Анализирует топологию сети"""
    
    print(f"\n\nАнализ топологии сети")
    print("=" * 30)
    
    # Подсчитываем статистику
    total_nodes = len(network)
    total_connections = sum(len(connections) for connections in network.values())
    
    # Находим узлы с наибольшим количеством связей
    max_connections = max(len(connections) for connections in network.values())
    hub_nodes = [node for node, connections in network.items() if len(connections) == max_connections]
    
    # Находим изолированные узлы
    isolated_nodes = [node for node, connections in network.items() if len(connections) == 0]
    
    # Находим узлы с одной связью (концевые узлы)
    end_nodes = [node for node, connections in network.items() if len(connections) == 1]
    
    print(f"Общая статистика:")
    print(f"  Всего узлов: {total_nodes}")
    print(f"  Всего связей: {total_connections}")
    print(f"  Среднее количество связей на узел: {total_connections/total_nodes:.2f}")
    
    print(f"\nАнализ узлов:")
    print(f"  Центральные узлы (макс. связей): {', '.join(hub_nodes)} ({max_connections} связей)")
    print(f"  Изолированные узлы: {', '.join(isolated_nodes) if isolated_nodes else 'нет'}")
    print(f"  Концевые узлы: {', '.join(end_nodes) if end_nodes else 'нет'}")
    
    # Анализ связности
    print(f"\nАнализ связности:")
    
    # Проверяем, есть ли пути между всеми узлами
    def find_path(start, end, visited=None):
        if visited is None:
            visited = set()
        if start == end:
            return True
        visited.add(start)
        for neighbor in network[start]:
            if neighbor not in visited:
                if find_path(neighbor, end, visited.copy()):
                    return True
        return False
    
    # Проверяем связность для нескольких пар узлов
    nodes = list(network.keys())
    connected_pairs = 0
    total_pairs = 0
    
    for i in range(min(5, len(network))):  # Проверяем первые 5 узлов
        for j in range(i+1, min(5, len(network))):
            total_pairs += 1
            if find_path(nodes[i], nodes[j]):
                connected_pairs += 1
    
    connectivity_ratio = connected_pairs / total_pairs if total_pairs > 0 else 0
    print(f"  Коэффициент связности: {connectivity_ratio:.2f}")


def demonstrate_file_operations():
    """Демонстрирует операции с файлами"""
    
    print(f"\n\nДемонстрация операций с файлами")
    print("=" * 40)
    
    # Создаем хранилище
    storage = NetworkStorage('complex_networks')
    
    # Создаем сложную сеть
    complex_network = create_complex_network()
    
    # Сохраняем сеть
    print(f"\nСохранение сложной сети...")
    success = storage.save_network('complex_enterprise_network', complex_network)
    
    if success:
        print("Сеть сохранена успешно")
        
        # Получаем информацию о файле
        info = storage.get_network_info('complex_enterprise_network')
        if info:
            print(f"Информация о файле:")
            print(f"  Имя: {info['name']}")
            print(f"  Размер файла: {info['file_size']} байт")
            print(f"  Узлов: {info['node_count']}")
            print(f"  Связей: {info['connection_count']}")
            print(f"  Путь: {info['file_path']}")
        
        # Загружаем сеть обратно
        print(f"\nЗагрузка сети из файла...")
        loaded_network = storage.load_network('complex_enterprise_network')
        
        if loaded_network:
            print("Сеть загружена успешно")
            
            # Проверяем целостность
            if loaded_network == complex_network:
                print("Данные сохранены и загружены без изменений")
            else:
                print("ВНИМАНИЕ: Данные изменились при сохранении/загрузке")
            
            # Анализируем загруженную сеть
            analyze_network_topology(loaded_network)
        
        # Экспортируем в текст
        print(f"\nЭкспорт в текстовый формат...")
        export_success = storage.export_network_to_text('complex_enterprise_network')
        if export_success:
            print("Экспорт выполнен успешно")
            
            # Показываем размеры файлов
            db_file = 'complex_networks/complex_enterprise_network.db'
            txt_file = 'complex_networks/complex_enterprise_network.txt'
            
            if os.path.exists(db_file) and os.path.exists(txt_file):
                db_size = os.path.getsize(db_file)
                txt_size = os.path.getsize(txt_file)
                print(f"Размер .db файла: {db_size} байт")
                print(f"Размер .txt файла: {txt_size} байт")
                print(f"Коэффициент сжатия: {txt_size/db_size:.2f}x")
    
    else:
        print("Ошибка при сохранении сети")


if __name__ == "__main__":
    try:
        demonstrate_file_operations()
        print(f"\n\nДемонстрация завершена!")
        print("=" * 50)
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
