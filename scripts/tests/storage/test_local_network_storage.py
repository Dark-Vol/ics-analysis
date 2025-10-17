"""
Тестовый скрипт для проверки локального хранилища сетей
test_local_network_storage.py - тестирование NetworkStorage
"""

import os
import sys
import logging
from typing import Dict, List

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.network_storage import NetworkStorage


def test_network_storage():
    """Тестирует функциональность NetworkStorage"""
    
    # Настройка логирования
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("Тестирование локального хранилища сетей")
    print("=" * 50)
    
    # Создание экземпляра хранилища
    storage = NetworkStorage("test_networks")
    
    # Тестовые сети
    test_networks = {
        "simple_network": {
            'a': ['b', 'c'],
            'b': ['c'],
            'c': []
        },
        "complex_network": {
            'node1': ['node2', 'node3', 'node4'],
            'node2': ['node3'],
            'node3': ['node4', 'node5'],
            'node4': ['node5'],
            'node5': []
        },
        "ring_network": {
            'A': ['B'],
            'B': ['C'],
            'C': ['D'],
            'D': ['A']
        }
    }
    
    print("\nТест 1: Сохранение сетей")
    print("-" * 30)
    
    for name, network_data in test_networks.items():
        success = storage.save_network(name, network_data)
        print(f"Сохранение '{name}': {'Успех' if success else 'Ошибка'}")
    
    print("\n📋 Тест 2: Список сетей")
    print("-" * 30)
    
    networks = storage.list_networks()
    print(f"Найдено сетей: {len(networks)}")
    for network in networks:
        print(f"  - {network}")
    
    print("\n📖 Тест 3: Загрузка сетей")
    print("-" * 30)
    
    for network_name in networks:
        network_data = storage.load_network(network_name)
        if network_data:
            node_count = len(network_data)
            connection_count = sum(len(connections) for connections in network_data.values())
            print(f"Загрузка '{network_name}': ✅ Узлов: {node_count}, Связей: {connection_count}")
        else:
            print(f"Загрузка '{network_name}': ❌ Ошибка")
    
    print("\nℹ️ Тест 4: Информация о сетях")
    print("-" * 30)
    
    for network_name in networks:
        info = storage.get_network_info(network_name)
        if info:
            print(f"Сеть '{network_name}':")
            print(f"  Размер файла: {info['file_size']} байт")
            print(f"  Узлов: {info['node_count']}")
            print(f"  Связей: {info['connection_count']}")
            print(f"  Путь: {info['file_path']}")
        else:
            print(f"Информация о '{network_name}': ❌ Ошибка")
    
    print("\n🔍 Тест 5: Проверка существования")
    print("-" * 30)
    
    test_names = ["simple_network", "nonexistent_network", "complex_network"]
    for name in test_names:
        exists = storage.network_exists(name)
        print(f"Сеть '{name}' существует: {'✅ Да' if exists else '❌ Нет'}")
    
    print("\n📄 Тест 6: Экспорт в текст")
    print("-" * 30)
    
    for network_name in networks[:2]:  # Экспортируем только первые две сети
        success = storage.export_network_to_text(network_name)
        print(f"Экспорт '{network_name}': {'✅ Успех' if success else '❌ Ошибка'}")
    
    print("\n🗑️ Тест 7: Удаление сети")
    print("-" * 30)
    
    # Удаляем одну сеть
    network_to_delete = networks[0] if networks else "simple_network"
    success = storage.delete_network(network_to_delete)
    print(f"Удаление '{network_to_delete}': {'✅ Успех' if success else '❌ Ошибка'}")
    
    # Проверяем, что сеть удалена
    exists_after_delete = storage.network_exists(network_to_delete)
    print(f"Сеть '{network_to_delete}' после удаления: {'❌ Все еще существует' if exists_after_delete else '✅ Удалена'}")
    
    print("\n📊 Тест 8: Финальная статистика")
    print("-" * 30)
    
    final_networks = storage.list_networks()
    print(f"Осталось сетей: {len(final_networks)}")
    for network in final_networks:
        print(f"  - {network}")
    
    print("\n🧹 Тест 9: Очистка всех сетей")
    print("-" * 30)
    
    success = storage.clear_all_networks()
    print(f"Очистка всех сетей: {'✅ Успех' if success else '❌ Ошибка'}")
    
    # Проверяем, что все сети удалены
    final_count = len(storage.list_networks())
    print(f"Сетей после очистки: {final_count}")
    
    print("\n✅ Тестирование завершено!")
    print("=" * 50)


def test_edge_cases():
    """Тестирует граничные случаи"""
    
    print("\n🔬 Тестирование граничных случаев")
    print("=" * 50)
    
    storage = NetworkStorage("test_edge_cases")
    
    # Тест с пустой сетью
    print("\n📝 Тест: Пустая сеть")
    empty_network = {}
    success = storage.save_network("empty", empty_network)
    print(f"Сохранение пустой сети: {'✅ Успех' if success else '❌ Ошибка'}")
    
    # Тест с недопустимыми символами в имени
    print("\n📝 Тест: Недопустимые символы в имени")
    invalid_name = "test<>:\"/\\|?*network"
    success = storage.save_network(invalid_name, {'a': ['b']})
    print(f"Сохранение с недопустимыми символами: {'✅ Успех' if success else '❌ Ошибка'}")
    
    # Тест с очень длинным именем
    print("\n📝 Тест: Длинное имя")
    long_name = "a" * 100
    success = storage.save_network(long_name, {'a': ['b']})
    print(f"Сохранение с длинным именем: {'✅ Успех' if success else '❌ Ошибка'}")
    
    # Тест с пустым именем
    print("\n📝 Тест: Пустое имя")
    success = storage.save_network("", {'a': ['b']})
    print(f"Сохранение с пустым именем: {'✅ Успех' if success else '❌ Ошибка'}")
    
    # Очистка
    storage.clear_all_networks()
    print("\n✅ Тестирование граничных случаев завершено!")


def test_performance():
    """Тестирует производительность с большими сетями"""
    
    print("\n⚡ Тестирование производительности")
    print("=" * 50)
    
    storage = NetworkStorage("test_performance")
    
    import time
    
    # Создаем большую сеть
    print("\n📊 Создание большой сети...")
    large_network = {}
    node_count = 1000
    
    for i in range(node_count):
        node_id = f"node_{i}"
        # Каждый узел связан с несколькими случайными узлами
        connections = [f"node_{j}" for j in range(i+1, min(i+6, node_count))]
        large_network[node_id] = connections
    
    # Тест сохранения
    start_time = time.time()
    success = storage.save_network("large_network", large_network)
    save_time = time.time() - start_time
    
    print(f"Сохранение большой сети ({node_count} узлов): {'✅ Успех' if success else '❌ Ошибка'}")
    print(f"Время сохранения: {save_time:.3f} секунд")
    
    # Тест загрузки
    start_time = time.time()
    loaded_network = storage.load_network("large_network")
    load_time = time.time() - start_time
    
    print(f"Загрузка большой сети: {'✅ Успех' if loaded_network else '❌ Ошибка'}")
    print(f"Время загрузки: {load_time:.3f} секунд")
    
    # Тест получения информации
    start_time = time.time()
    info = storage.get_network_info("large_network")
    info_time = time.time() - start_time
    
    print(f"Получение информации: {'✅ Успех' if info else '❌ Ошибка'}")
    print(f"Время получения информации: {info_time:.3f} секунд")
    
    if info:
        print(f"Размер файла: {info['file_size']} байт")
        print(f"Узлов: {info['node_count']}")
        print(f"Связей: {info['connection_count']}")
    
    # Очистка
    storage.clear_all_networks()
    print("\n✅ Тестирование производительности завершено!")


if __name__ == "__main__":
    try:
        # Основное тестирование
        test_network_storage()
        
        # Тестирование граничных случаев
        test_edge_cases()
        
        # Тестирование производительности
        test_performance()
        
        print("\n🎉 Все тесты выполнены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
