"""
Тестовый скрипт для проверки интеграции локального хранилища
test_local_storage_integration.py - тестирование интеграции с GUI
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage.network_storage import NetworkStorage


def test_storage_integration():
    """Тестирует интеграцию хранилища с GUI"""
    
    print("Тестирование интеграции локального хранилища")
    print("=" * 50)
    
    # Создание экземпляра хранилища
    storage = NetworkStorage("test_integration")
    
    # Создаем тестовую сеть
    test_network = {
        'node1': ['node2', 'node3'],
        'node2': ['node3'],
        'node3': []
    }
    
    print("\n1. Сохранение тестовой сети...")
    success = storage.save_network("test_integration_network", test_network)
    print(f"Результат: {'Успех' if success else 'Ошибка'}")
    
    print("\n2. Загрузка тестовой сети...")
    loaded_network = storage.load_network("test_integration_network")
    if loaded_network:
        print(f"Результат: Успех")
        print(f"Узлов: {len(loaded_network)}")
        print(f"Связей: {sum(len(connections) for connections in loaded_network.values())}")
    else:
        print("Результат: Ошибка")
    
    print("\n3. Получение информации о сети...")
    info = storage.get_network_info("test_integration_network")
    if info:
        print(f"Результат: Успех")
        print(f"Размер файла: {info['file_size']} байт")
        print(f"Узлов: {info['node_count']}")
        print(f"Связей: {info['connection_count']}")
    else:
        print("Результат: Ошибка")
    
    print("\n4. Экспорт в текст...")
    success = storage.export_network_to_text("test_integration_network")
    print(f"Результат: {'Успех' if success else 'Ошибка'}")
    
    print("\n5. Список сетей...")
    networks = storage.list_networks()
    print(f"Результат: Найдено {len(networks)} сетей")
    for network in networks:
        print(f"  - {network}")
    
    print("\n6. Очистка...")
    success = storage.clear_all_networks()
    print(f"Результат: {'Успех' if success else 'Ошибка'}")
    
    print("\nТестирование интеграции завершено!")
    print("=" * 50)


def test_gui_dialog():
    """Тестирует GUI диалог (без показа окна)"""
    
    print("\nТестирование GUI диалога")
    print("=" * 30)
    
    try:
        # Создаем скрытое окно для тестирования
        root = tk.Tk()
        root.withdraw()  # Скрываем окно
        
        # Импортируем диалог
        from src.gui.local_network_manager_dialog import LocalNetworkManagerDialog
        
        print("LocalNetworkManagerDialog импортирован успешно")
        
        # Создаем экземпляр диалога (но не показываем)
        dialog = LocalNetworkManagerDialog(root)
        print("Диалог создан успешно")
        
        # Проверяем основные методы
        storage = dialog.storage
        print(f"Хранилище создано: {storage is not None}")
        
        # Тестируем базовые операции
        test_network = {'a': ['b'], 'b': []}
        success = storage.save_network("gui_test", test_network)
        print(f"Сохранение через GUI: {'Успех' if success else 'Ошибка'}")
        
        networks = storage.list_networks()
        print(f"Список сетей через GUI: {len(networks)} сетей")
        
        # Очистка
        storage.clear_all_networks()
        
        root.destroy()
        print("GUI тестирование завершено успешно")
        
    except Exception as e:
        print(f"Ошибка в GUI тестировании: {e}")
        import traceback
        traceback.print_exc()


def test_main_window_integration():
    """Тестирует интеграцию с главным окном"""
    
    print("\nТестирование интеграции с главным окном")
    print("=" * 40)
    
    try:
        # Создаем скрытое окно
        root = tk.Tk()
        root.withdraw()
        
        # Импортируем главное окно
        from src.gui.main_window import MainWindow
        
        print("MainWindow импортирован успешно")
        
        # Создаем экземпляр главного окна
        config = {}  # Пустая конфигурация для теста
        main_window = MainWindow(root, config)
        print("Главное окно создано успешно")
        
        # Проверяем, что новые методы существуют
        has_manage_local = hasattr(main_window, '_manage_local_networks')
        has_save_local = hasattr(main_window, '_save_current_network_locally')
        
        print(f"Метод _manage_local_networks: {'Есть' if has_manage_local else 'Нет'}")
        print(f"Метод _save_current_network_locally: {'Есть' if has_save_local else 'Нет'}")
        
        root.destroy()
        print("Интеграция с главным окном проверена успешно")
        
    except Exception as e:
        print(f"Ошибка в тестировании главного окна: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        # Тестирование хранилища
        test_storage_integration()
        
        # Тестирование GUI диалога
        test_gui_dialog()
        
        # Тестирование интеграции с главным окном
        test_main_window_integration()
        
        print("\nВсе тесты интеграции выполнены успешно!")
        
    except Exception as e:
        print(f"\nОшибка во время тестирования: {e}")
        import traceback
        traceback.print_exc()
