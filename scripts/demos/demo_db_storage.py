"""
Демонстрация работы с файлами .db
Показывает, как именно хранится информация о связях между узлами
"""

import os
import sys

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.network_storage import NetworkStorage

def demonstrate_db_storage():
    """Демонстрирует, как именно хранится информация о связях"""
    
    print("Демонстрация хранения связей в файле .db")
    print("=" * 50)
    
    # Создаем хранилище
    storage = NetworkStorage('demo_networks')
    
    # Создаем тестовую сеть с четкой структурой связей
    test_network = {
        'server1': ['server2', 'server3'],  # server1 связан с server2 и server3
        'server2': ['server3'],             # server2 связан только с server3
        'server3': [],                      # server3 не имеет исходящих связей
        'router1': ['server1', 'server2'],  # router1 связан с server1 и server2
        'router2': ['server3']              # router2 связан только с server3
    }
    
    print("Исходная структура сети:")
    for node, connections in test_network.items():
        if connections:
            print(f"  {node} связан с: {', '.join(connections)}")
        else:
            print(f"  {node} не имеет исходящих связей")
    
    # Сохраняем сеть
    print(f"\nСохранение сети в файл demo_network.db...")
    success = storage.save_network('demo_network', test_network)
    
    if success:
        print("Файл demo_network.db создан успешно")
        
        # Проверяем размер файла
        file_path = 'demo_networks/demo_network.db'
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"Размер файла: {file_size} байт")
        
        # Загружаем и показываем содержимое
        print(f"\nЗагрузка из файла demo_network.db...")
        loaded_network = storage.load_network('demo_network')
        
        if loaded_network:
            print("Данные загружены успешно")
            print("\nСодержимое файла demo_network.db:")
            print("-" * 40)
            for node, connections in loaded_network.items():
                if connections:
                    print(f"{node} связан с: {', '.join(connections)}")
                else:
                    print(f"{node} не имеет исходящих связей")
            
            # Показываем статистику связей
            print(f"\nСтатистика связей:")
            print("-" * 25)
            total_connections = sum(len(connections) for connections in loaded_network.values())
            print(f"Всего узлов: {len(loaded_network)}")
            print(f"Всего связей: {total_connections}")
            
            print(f"\nДетальная статистика по узлам:")
            for node, connections in loaded_network.items():
                print(f"  {node}: {len(connections)} исходящих связей")
            
            # Проверяем, что данные идентичны
            print(f"\nПроверка целостности данных:")
            if loaded_network == test_network:
                print("Данные сохранены и загружены без изменений")
            else:
                print("Данные изменились при сохранении/загрузке")
        else:
            print("Не удалось загрузить данные")
    else:
        print("Не удалось сохранить файл")
    
    # Экспортируем в текстовый формат для просмотра
    print(f"\nЭкспорт в текстовый формат...")
    export_success = storage.export_network_to_text('demo_network')
    if export_success:
        print("Экспорт в demo_networks/demo_network.txt выполнен")
        
        # Показываем содержимое текстового файла
        txt_file = 'demo_networks/demo_network.txt'
        if os.path.exists(txt_file):
            print(f"\nСодержимое текстового файла:")
            print("-" * 30)
            with open(txt_file, 'r', encoding='utf-8') as f:
                print(f.read())
    else:
        print("Не удалось экспортировать в текст")
    
    print(f"\nДемонстрация завершена!")
    print("=" * 50)


def show_file_structure():
    """Показывает структуру созданных файлов"""
    
    print(f"\nСтруктура файлов в директории demo_networks:")
    print("-" * 45)
    
    if os.path.exists('demo_networks'):
        for filename in os.listdir('demo_networks'):
            file_path = os.path.join('demo_networks', filename)
            file_size = os.path.getsize(file_path)
            print(f"{filename} - {file_size} байт")
    else:
        print("Директория demo_networks не найдена")


if __name__ == "__main__":
    try:
        demonstrate_db_storage()
        show_file_structure()
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
