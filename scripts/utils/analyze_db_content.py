"""
Показывает содержимое файла .db
Демонстрирует, что файл содержит именно информацию о связях между узлами
"""

import os
import sys
import pickle

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.network_storage import NetworkStorage

def show_db_file_content():
    """Показывает содержимое файла .db"""
    
    print("Анализ содержимого файла demo_network.db")
    print("=" * 50)
    
    file_path = 'demo_networks/demo_network.db'
    
    if not os.path.exists(file_path):
        print("Файл demo_network.db не найден")
        return
    
    # Показываем информацию о файле
    file_size = os.path.getsize(file_path)
    print(f"Файл: {file_path}")
    print(f"Размер: {file_size} байт")
    
    # Читаем содержимое файла
    print(f"\nЧтение содержимого файла...")
    try:
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        print("Данные успешно загружены из файла")
        print(f"\nТип данных: {type(data)}")
        print(f"Содержимое:")
        print("-" * 30)
        
        # Показываем содержимое словаря
        for node, connections in data.items():
            print(f"'{node}': {connections}")
        
        print(f"\nСтруктура связей:")
        print("-" * 20)
        for node, connections in data.items():
            if connections:
                print(f"{node} -> {', '.join(connections)}")
            else:
                print(f"{node} -> (нет связей)")
        
        # Статистика
        total_nodes = len(data)
        total_connections = sum(len(connections) for connections in data.values())
        
        print(f"\nСтатистика:")
        print(f"Всего узлов: {total_nodes}")
        print(f"Всего связей: {total_connections}")
        
        # Показываем, как это выглядит в виде матрицы связей
        print(f"\nМатрица связей:")
        print("-" * 20)
        nodes = list(data.keys())
        
        # Заголовок
        print("     ", end="")
        for node in nodes:
            print(f"{node:>8}", end="")
        print()
        
        # Строки матрицы
        for source in nodes:
            print(f"{source:>5}", end="")
            for target in nodes:
                if target in data[source]:
                    print(f"{'1':>8}", end="")
                else:
                    print(f"{'0':>8}", end="")
            print()
        
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")


def demonstrate_network_operations():
    """Демонстрирует операции с сетью"""
    
    print(f"\n\nДемонстрация операций с сетью")
    print("=" * 40)
    
    # Создаем хранилище
    storage = NetworkStorage('demo_networks')
    
    # Загружаем сеть
    network = storage.load_network('demo_network')
    
    if network:
        print("Сеть загружена успешно")
        
        # Показываем различные операции
        print(f"\n1. Поиск узлов с наибольшим количеством связей:")
        max_connections = max(len(connections) for connections in network.values())
        for node, connections in network.items():
            if len(connections) == max_connections:
                print(f"   {node}: {len(connections)} связей")
        
        print(f"\n2. Поиск изолированных узлов:")
        isolated_nodes = [node for node, connections in network.items() if len(connections) == 0]
        if isolated_nodes:
            print(f"   Изолированные узлы: {', '.join(isolated_nodes)}")
        else:
            print("   Изолированных узлов нет")
        
        print(f"\n3. Поиск узлов, связанных с конкретным узлом:")
        target_node = 'server3'
        connected_to_target = [node for node, connections in network.items() if target_node in connections]
        print(f"   Узлы, связанные с {target_node}: {', '.join(connected_to_target)}")
        
        print(f"\n4. Создание обратной карты связей:")
        reverse_map = {}
        for node, connections in network.items():
            for target in connections:
                if target not in reverse_map:
                    reverse_map[target] = []
                reverse_map[target].append(node)
        
        print("   Обратная карта (кто связан с каждым узлом):")
        for node, sources in reverse_map.items():
            print(f"   {node} <- {', '.join(sources)}")
    
    else:
        print("Не удалось загрузить сеть")


if __name__ == "__main__":
    try:
        show_db_file_content()
        demonstrate_network_operations()
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
