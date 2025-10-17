"""
Модуль для локального хранения сетей в виде словарных файлов .db
NetworkStorage - управление локальными файлами сетей
"""

import os
import pickle
import shelve
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class NetworkStorage:
    """
    Класс для управления локальным хранением сетей в файлах .db
    
    Каждая сеть сохраняется в отдельный файл <имя_сети>.db
    Формат хранения: словарь Python, где ключ - имя узла, значение - список связанных узлов
    """
    
    def __init__(self, storage_dir: str = "networks"):
        """
        Инициализация хранилища сетей
        
        Args:
            storage_dir: Директория для хранения файлов сетей
        """
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Создает директорию для хранения, если она не существует"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
            logger.info(f"Создана директория для хранения сетей: {self.storage_dir}")
    
    def save_network(self, network_name: str, network_data: Dict[str, List[str]]) -> bool:
        """
        Сохраняет сеть в файл <имя_сети>.db
        
        Args:
            network_name: Имя сети (будет использовано как имя файла)
            network_data: Словарь сети {узел: [список_связанных_узлов]}
            
        Returns:
            bool: True если сохранение успешно, False в случае ошибки
        """
        try:
            # Очищаем имя файла от недопустимых символов
            safe_name = self._sanitize_filename(network_name)
            file_path = os.path.join(self.storage_dir, f"{safe_name}.db")
            
            # Сохраняем используя pickle для надежности
            with open(file_path, 'wb') as f:
                pickle.dump(network_data, f)
            
            logger.info(f"Сеть '{network_name}' сохранена в файл: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении сети '{network_name}': {e}")
            return False
    
    def load_network(self, network_name: str) -> Optional[Dict[str, List[str]]]:
        """
        Загружает сеть из файла <имя_сети>.db
        
        Args:
            network_name: Имя сети для загрузки
            
        Returns:
            Dict[str, List[str]]: Словарь сети или None в случае ошибки
        """
        try:
            safe_name = self._sanitize_filename(network_name)
            file_path = os.path.join(self.storage_dir, f"{safe_name}.db")
            
            if not os.path.exists(file_path):
                logger.warning(f"Файл сети '{network_name}' не найден: {file_path}")
                return None
            
            with open(file_path, 'rb') as f:
                network_data = pickle.load(f)
            
            logger.info(f"Сеть '{network_name}' загружена из файла: {file_path}")
            return network_data
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке сети '{network_name}': {e}")
            return None
    
    def delete_network(self, network_name: str) -> bool:
        """
        Удаляет файл сети
        
        Args:
            network_name: Имя сети для удаления
            
        Returns:
            bool: True если удаление успешно, False в случае ошибки
        """
        try:
            safe_name = self._sanitize_filename(network_name)
            file_path = os.path.join(self.storage_dir, f"{safe_name}.db")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Сеть '{network_name}' удалена: {file_path}")
                return True
            else:
                logger.warning(f"Файл сети '{network_name}' не найден для удаления: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка при удалении сети '{network_name}': {e}")
            return False
    
    def list_networks(self) -> List[str]:
        """
        Возвращает список всех сохраненных сетей
        
        Returns:
            List[str]: Список имен сетей
        """
        try:
            networks = []
            if os.path.exists(self.storage_dir):
                for filename in os.listdir(self.storage_dir):
                    if filename.endswith('.db'):
                        # Убираем расширение .db
                        network_name = filename[:-3]
                        networks.append(network_name)
            
            logger.info(f"Найдено сетей: {len(networks)}")
            return sorted(networks)
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка сетей: {e}")
            return []
    
    def network_exists(self, network_name: str) -> bool:
        """
        Проверяет, существует ли сеть с указанным именем
        
        Args:
            network_name: Имя сети для проверки
            
        Returns:
            bool: True если сеть существует, False в противном случае
        """
        safe_name = self._sanitize_filename(network_name)
        file_path = os.path.join(self.storage_dir, f"{safe_name}.db")
        return os.path.exists(file_path)
    
    def get_network_info(self, network_name: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о сети (размер файла, количество узлов и связей)
        
        Args:
            network_name: Имя сети
            
        Returns:
            Dict[str, Any]: Информация о сети или None в случае ошибки
        """
        try:
            network_data = self.load_network(network_name)
            if network_data is None:
                return None
            
            safe_name = self._sanitize_filename(network_name)
            file_path = os.path.join(self.storage_dir, f"{safe_name}.db")
            
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            node_count = len(network_data)
            connection_count = sum(len(connections) for connections in network_data.values())
            
            return {
                'name': network_name,
                'file_size': file_size,
                'node_count': node_count,
                'connection_count': connection_count,
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о сети '{network_name}': {e}")
            return None
    
    def clear_all_networks(self) -> bool:
        """
        Удаляет все сохраненные сети
        
        Returns:
            bool: True если очистка успешна, False в случае ошибки
        """
        try:
            networks = self.list_networks()
            success_count = 0
            
            for network_name in networks:
                if self.delete_network(network_name):
                    success_count += 1
            
            logger.info(f"Удалено сетей: {success_count} из {len(networks)}")
            return success_count == len(networks)
            
        except Exception as e:
            logger.error(f"Ошибка при очистке всех сетей: {e}")
            return False
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Очищает имя файла от недопустимых символов
        
        Args:
            filename: Исходное имя файла
            
        Returns:
            str: Очищенное имя файла
        """
        # Заменяем недопустимые символы на подчеркивания
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Убираем пробелы в начале и конце
        filename = filename.strip()
        
        # Если имя пустое, используем default
        if not filename:
            filename = 'default'
        
        return filename
    
    def export_network_to_text(self, network_name: str, output_file: str = None) -> bool:
        """
        Экспортирует сеть в текстовый файл для просмотра
        
        Args:
            network_name: Имя сети для экспорта
            output_file: Путь к выходному файлу (опционально)
            
        Returns:
            bool: True если экспорт успешен, False в случае ошибки
        """
        try:
            network_data = self.load_network(network_name)
            if network_data is None:
                return False
            
            if output_file is None:
                safe_name = self._sanitize_filename(network_name)
                output_file = os.path.join(self.storage_dir, f"{safe_name}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Сеть: {network_name}\n")
                f.write("=" * 50 + "\n\n")
                
                for node, connections in network_data.items():
                    f.write(f"Узел '{node}':\n")
                    if connections:
                        f.write(f"  Связан с: {', '.join(connections)}\n")
                    else:
                        f.write("  Нет связей\n")
                    f.write("\n")
            
            logger.info(f"Сеть '{network_name}' экспортирована в: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте сети '{network_name}': {e}")
            return False


# Пример использования
if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)
    
    # Создание экземпляра хранилища
    storage = NetworkStorage("test_networks")
    
    # Пример сети
    example_network = {
        'a': ['b', 'c'],
        'b': ['c'],
        'c': []
    }
    
    # Сохранение сети
    print("Сохранение примера сети...")
    storage.save_network("example_network", example_network)
    
    # Загрузка сети
    print("Загрузка сети...")
    loaded_network = storage.load_network("example_network")
    print(f"Загруженная сеть: {loaded_network}")
    
    # Получение информации
    print("Информация о сети:")
    info = storage.get_network_info("example_network")
    print(f"Узлов: {info['node_count']}, Связей: {info['connection_count']}")
    
    # Список сетей
    print(f"Сохраненные сети: {storage.list_networks()}")
    
    # Экспорт в текст
    storage.export_network_to_text("example_network")
