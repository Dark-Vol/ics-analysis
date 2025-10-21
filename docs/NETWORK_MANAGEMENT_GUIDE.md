# 🌐 Руководство по управлению сетями

[![Network Management](https://img.shields.io/badge/Network%20Management-v1.0-blue.svg)](README.md)
[![Features](https://img.shields.io/badge/Features-Complete-brightgreen.svg)](README.md)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-orange.svg)](README.md)

**Подробное руководство по созданию, управлению и анализу сетевых топологий в ИКС Анализаторе Системы**

---

## 📋 Содержание

- [🎯 Обзор системы](#-обзор-системы)
- [🏗️ Создание сетей](#️-создание-сетей)
- [💾 Сохранение и загрузка](#-сохранение-и-загрузка)
- [🗑️ Удаление сетей](#️-удаление-сетей)
- [🔧 Настройка параметров](#-настройка-параметров)
- [📊 Анализ и визуализация](#-анализ-и-визуализация)
- [⚙️ Конфигурация](#️-конфигурация)
- [❓ Решение проблем](#-решение-проблем)

---

## 🎯 Обзор системы

Система управления сетями позволяет создавать, сохранять, загружать и анализировать сетевые топологии в ИКС Анализаторе Системы.

### ✨ Основные возможности

#### 🏗️ Создание сетей
- **Настройка количества узлов**: 3-100 узлов
- **Настройка вероятности соединения**: 0.1-1.0
- **Настройка параметров узлов**: Пропускная способность, надежность, тип
- **Настройка параметров связей**: Пропускная способность, задержка, надежность

#### 💾 Управление данными
- **Сохранение в локальную БД**: SQLite база данных
- **Добавление метаданных**: Имя, описание, дата создания
- **Автоматическое обновление**: Существующих сетей
- **Массовые операции**: Удаление всех сетей

#### 🔍 Анализ и визуализация
- **Интерактивная визуализация**: Топология с цветовым кодированием
- **Анализ связности**: Критические узлы и пути
- **Метрики производительности**: Пропускная способность, задержка
- **Экспорт результатов**: Excel, Word отчеты

---

## 🏗️ Создание сетей

### 🎮 Через графический интерфейс

#### Основной процесс создания
1. **Откройте диалог создания сети**:
   - Нажмите кнопку **"СОЗДАТЬ/ЗАГРУЗИТЬ СЕТЬ"** в панели визуализатора
   - Или используйте меню **"Файл"** → **"Создать/Загрузить сеть"**

2. **Выберите тип сети**:
   - **"Создать новую сеть"** - пользовательская конфигурация
   - **"Готовая система"** - предустановленная топология

3. **Настройте параметры сети**:
   - **Количество узлов**: 5-100 (рекомендуется 10-50)
   - **Вероятность соединения**: 0.1-1.0 (рекомендуется 0.3-0.7)
   - **Типы узлов**: Серверы, маршрутизаторы, коммутаторы
   - **Типы каналов**: Ethernet, WiFi, оптоволокно

4. **Создайте сеть**:
   - Нажмите **"СОЗДАТЬ СЕТЬ"**
   - Дождитесь завершения генерации
   - Сеть будет отображена в визуализаторе

#### Детальная настройка параметров

##### Параметры узлов
```json
{
    "server": {
        "capacity_range": [500, 2000],
        "reliability_range": [0.95, 0.99],
        "threat_level_range": [0.05, 0.15]
    },
    "router": {
        "capacity_range": [200, 1000],
        "reliability_range": [0.90, 0.98],
        "threat_level_range": [0.10, 0.20]
    },
    "switch": {
        "capacity_range": [100, 500],
        "reliability_range": [0.92, 0.97],
        "threat_level_range": [0.08, 0.18]
    }
}
```

##### Параметры каналов
```json
{
    "ethernet": {
        "bandwidth_range": [10, 1000],
        "latency_range": [0.1, 2.0],
        "reliability_range": [0.95, 0.99]
    },
    "fiber": {
        "bandwidth_range": [100, 10000],
        "latency_range": [0.1, 1.0],
        "reliability_range": [0.98, 0.999]
    },
    "wifi": {
        "bandwidth_range": [1, 100],
        "latency_range": [1.0, 10.0],
        "reliability_range": [0.80, 0.95]
    }
}
```

### 💻 Через командную строку

#### Базовое создание
```bash
# Создание сети с 15 узлами
python main.py --custom-system --nodes 15 --connection-prob 0.4

# Создание с анализом надежности
python main.py --custom-system --nodes 20 --reliability

# Создание с полным анализом
python main.py --custom-system --nodes 25 --full-analysis
```

#### Продвинутое создание
```bash
# Создание с экспортом результатов
python main.py --custom-system --nodes 30 --connection-prob 0.6 --export results.xlsx

# Создание с анализом неблагоприятных условий
python main.py --custom-system --nodes 20 --adverse-conditions --duration 600
```

### 🐍 Программный интерфейс

#### Создание базовой сети
```python
from src.system_model import SystemModel

# Создание системы
system = SystemModel("Моя тестовая сеть")

# Генерация случайной сети
system.generate_random_network(
    num_nodes=15,
    connection_probability=0.4
)

# Настройка параметров узлов
for node_id, node in system.nodes.items():
    node.capacity = 1000  # Мбит/с
    node.reliability = 0.95
    node.threat_level = 0.1

# Настройка параметров каналов
for (source, target), link in system.links.items():
    link.bandwidth = 100  # Мбит/с
    link.latency = 10  # мс
    link.reliability = 0.98
```

#### Создание специализированной сети
```python
from src.system_model import SystemModel, NodeType, LinkType

# Создание системы
system = SystemModel("Серверная ферма")

# Добавление узлов
system.add_node("web_server_1", NodeType.SERVER, capacity=2000)
system.add_node("web_server_2", NodeType.SERVER, capacity=2000)
system.add_node("db_server", NodeType.SERVER, capacity=1500)
system.add_node("load_balancer", NodeType.ROUTER, capacity=1000)

# Добавление связей
system.add_link("web_server_1", "load_balancer", LinkType.ETHERNET, bandwidth=1000)
system.add_link("web_server_2", "load_balancer", LinkType.ETHERNET, bandwidth=1000)
system.add_link("load_balancer", "db_server", LinkType.FIBER, bandwidth=2000)
```

---

## 💾 Сохранение и загрузка

### 💾 Сохранение сетей

#### Через графический интерфейс
1. **Создайте или настройте сеть**
2. **Откройте диалог сохранения**:
   - Меню **"Файл"** → **"Сохранить текущую сеть"**
   - Или используйте горячую клавишу **Ctrl+S**

3. **Введите метаданные**:
   - **Имя сети**: Уникальное название
   - **Описание**: Подробное описание назначения
   - **Теги**: Ключевые слова для поиска

4. **Сохраните сеть**:
   - Нажмите **"СОХРАНИТЬ"**
   - Сеть будет сохранена в локальную БД

#### Программный интерфейс
```python
from src.storage.network_storage import NetworkStorage

# Создание хранилища
storage = NetworkStorage()

# Сохранение сети
network_data = {
    'name': 'Производственная сеть',
    'description': 'Сеть для анализа производственных процессов',
    'system': system,  # Объект SystemModel
    'metadata': {
        'created_by': 'admin',
        'version': '1.0',
        'tags': ['production', 'enterprise']
    }
}

storage.save_network(network_data)
```

### 📂 Загрузка сетей

#### Через графический интерфейс
1. **Откройте диалог загрузки**:
   - Меню **"Файл"** → **"Создать/Загрузить сеть"**
   - Или используйте горячую клавишу **Ctrl+O**

2. **Выберите вкладку "Загрузить сеть"**

3. **Просмотрите список сетей**:
   - **Имя**: Название сети
   - **Дата создания**: Когда была создана
   - **Размер**: Количество узлов и каналов
   - **Описание**: Краткое описание

4. **Загрузите сеть**:
   - Выберите нужную сеть
   - Нажмите **"ЗАГРУЗИТЬ"**
   - Сеть будет загружена в основной интерфейс

#### Программный интерфейс
```python
from src.storage.network_storage import NetworkStorage

# Создание хранилища
storage = NetworkStorage()

# Получение списка сетей
networks = storage.get_all_networks()

# Загрузка конкретной сети
network = storage.load_network("network_id")

# Загрузка по имени
network = storage.load_network_by_name("Производственная сеть")
```

---

## 🗑️ Удаление сетей

### 🗑️ Удаление одной сети

#### Через графический интерфейс
1. **Откройте диалог управления сетями**:
   - Меню **"Файл"** → **"Создать/Загрузить сеть"**

2. **Выберите вкладку "Загрузить сеть"**

3. **Найдите нужную сеть** в списке

4. **Удалите сеть**:
   - Выберите сеть
   - Нажмите кнопку **"УДАЛИТЬ"**
   - Подтвердите удаление в диалоге

#### Программный интерфейс
```python
from src.database.database_manager import DatabaseManager

# Создание менеджера БД
db_manager = DatabaseManager()

# Удаление сети по ID
success = db_manager.delete_network("network_id")

# Удаление сети по имени
success = db_manager.delete_network_by_name("Имя сети")
```

### 🗑️ Массовое удаление

#### Удаление всех сетей
1. **Откройте диалог управления сетями**

2. **Нажмите кнопку "УДАЛИТЬ ВСЕ"**

3. **Внимательно прочитайте предупреждение**:
   ```
   ВНИМАНИЕ!
   Вы собираетесь удалить ВСЕ сохраненные сети.
   Это действие нельзя отменить!
   
   Продолжить?
   ```

4. **Подтвердите удаление**:
   - Нажмите **"ДА"** для подтверждения
   - Или **"НЕТ"** для отмены

#### Программный интерфейс
```python
from src.database.database_manager import DatabaseManager

# Создание менеджера БД
db_manager = DatabaseManager()

# Массовое удаление всех сетей
success = db_manager.delete_all_networks()

if success:
    print("Все сети успешно удалены")
else:
    print("Ошибка при удалении сетей")
```

### ⚠️ Безопасность удаления

#### Защита от случайного удаления
- **Диалоги подтверждения** для всех операций удаления
- **Детальные предупреждения** о последствиях
- **Логирование всех операций** удаления
- **Возможность отмены** до подтверждения

#### Логирование операций
```python
# Пример лога операции удаления
{
    "timestamp": "2024-12-19T10:30:00",
    "action": "delete_network",
    "network_id": "net_123",
    "network_name": "Тестовая сеть",
    "user": "admin",
    "result": "success"
}
```

---

## 🔧 Настройка параметров

### ⚙️ Конфигурация узлов

#### Типы узлов и их параметры

##### Серверы
```python
server_config = {
    "capacity_range": [500, 2000],      # Мбит/с
    "reliability_range": [0.95, 0.99],  # 0-1
    "threat_level_range": [0.05, 0.15], # 0-1
    "default_capacity": 1000,
    "default_reliability": 0.97,
    "default_threat_level": 0.1
}
```

##### Маршрутизаторы
```python
router_config = {
    "capacity_range": [200, 1000],
    "reliability_range": [0.90, 0.98],
    "threat_level_range": [0.10, 0.20],
    "default_capacity": 500,
    "default_reliability": 0.94,
    "default_threat_level": 0.15
}
```

##### Коммутаторы
```python
switch_config = {
    "capacity_range": [100, 500],
    "reliability_range": [0.92, 0.97],
    "threat_level_range": [0.08, 0.18],
    "default_capacity": 250,
    "default_reliability": 0.95,
    "default_threat_level": 0.12
}
```

### 🔗 Конфигурация каналов

#### Типы каналов и их параметры

##### Ethernet
```python
ethernet_config = {
    "bandwidth_range": [10, 1000],      # Мбит/с
    "latency_range": [0.1, 2.0],       # мс
    "reliability_range": [0.95, 0.99],  # 0-1
    "default_bandwidth": 100,
    "default_latency": 1.0,
    "default_reliability": 0.97
}
```

##### Оптоволокно
```python
fiber_config = {
    "bandwidth_range": [100, 10000],
    "latency_range": [0.1, 1.0],
    "reliability_range": [0.98, 0.999],
    "default_bandwidth": 1000,
    "default_latency": 0.5,
    "default_reliability": 0.995
}
```

##### WiFi
```python
wifi_config = {
    "bandwidth_range": [1, 100],
    "latency_range": [1.0, 10.0],
    "reliability_range": [0.80, 0.95],
    "default_bandwidth": 50,
    "default_latency": 5.0,
    "default_reliability": 0.88
}
```

### 🎛️ Настройка через конфигурационный файл

#### Обновление config.json
```json
{
    "node_types": {
        "server": {
            "capacity_range": [500, 2000],
            "reliability_range": [0.95, 0.99],
            "threat_level_range": [0.05, 0.15]
        },
        "router": {
            "capacity_range": [200, 1000],
            "reliability_range": [0.90, 0.98],
            "threat_level_range": [0.10, 0.20]
        }
    },
    "link_types": {
        "ethernet": {
            "bandwidth_range": [10, 1000],
            "latency_range": [0.1, 2.0],
            "reliability_range": [0.95, 0.99]
        },
        "fiber": {
            "bandwidth_range": [100, 10000],
            "latency_range": [0.1, 1.0],
            "reliability_range": [0.98, 0.999]
        }
    }
}
```

---

## 📊 Анализ и визуализация

### 🎨 Визуализация топологии

#### Цветовое кодирование узлов
- 🟢 **Зеленый**: Нормальное состояние
- 🟡 **Желтый**: Предупреждение
- 🟠 **Оранжевый**: Деградация
- 🔴 **Красный**: Критическое состояние
- ⚫ **Серый**: Отключен

#### Цветовое кодирование каналов
- 🟢 **Зеленый**: Низкая загрузка (< 50%)
- 🟡 **Желтый**: Средняя загрузка (50-80%)
- 🟠 **Оранжевый**: Высокая загрузка (80-95%)
- 🔴 **Красный**: Перегрузка (> 95%)

#### Размеры элементов
- **Узлы**: Размер пропорционален пропускной способности
- **Каналы**: Толщина пропорциональна пропускной способности
- **Подписи**: Автоматическое масштабирование

### 📈 Метрики и анализ

#### Основные метрики
- **Пропускная способность**: Мбит/с
- **Задержка**: мс
- **Надежность**: 0-1
- **Доступность**: 0-1
- **Коэффициент связности**: 0-1

#### Анализ связности
- **Критические узлы**: Узлы, отказ которых критичен
- **Критические пути**: Пути, отказ которых критичен
- **Избыточность**: Резервные пути и связи
- **Устойчивость**: Способность противостоять атакам

#### Анализ производительности
- **Пропускная способность сети**: Общая производительность
- **Задержка сети**: Средняя задержка
- **Потери данных**: Процент потерянных пакетов
- **Использование ресурсов**: Загрузка узлов и каналов

### 📊 Экспорт результатов

#### Экспорт в Excel
```python
# Экспорт метрик в Excel
system.export_metrics_to_excel("network_metrics.xlsx")

# Экспорт топологии в Excel
system.export_topology_to_excel("network_topology.xlsx")
```

#### Экспорт в Word
```python
# Генерация отчета Word
from src.reports.word_report_generator import WordReportGenerator

report_generator = WordReportGenerator()
filename = report_generator.generate_report(system_data, analysis_results)
```

---

## ⚙️ Конфигурация

### 🔧 Настройка базы данных

#### SQLite конфигурация
```python
database_config = {
    "type": "sqlite",
    "path": "networks.db",
    "backup_enabled": True,
    "backup_interval": 3600,  # секунды
    "max_backups": 10
}
```

#### Настройка подключения
```python
# Создание подключения к БД
from src.database.database_manager import DatabaseManager

db_config = {
    "database_path": "networks.db",
    "timeout": 30,
    "isolation_level": "DEFERRED"
}

db_manager = DatabaseManager(db_config)
```

### 📁 Управление файлами

#### Структура файлов
```
user_networks/
├── home_network.db
├── office_network.db
├── server_farm.db
└── user_network_1.db

complex_networks/
├── complex_enterprise_network.db
└── complex_enterprise_network.txt

demo_networks/
├── demo_network.db
└── demo_network.txt
```

#### Автоматическое резервное копирование
```python
backup_config = {
    "enabled": True,
    "interval": 3600,  # 1 час
    "max_backups": 10,
    "backup_path": "backups/",
    "compress": True
}
```

---

## ❓ Решение проблем

### 🚨 Частые проблемы

#### Проблема: Сеть не создается
**Причины и решения:**
1. **Недостаточно памяти**:
   - Уменьшите количество узлов
   - Закройте другие приложения

2. **Некорректные параметры**:
   - Проверьте диапазоны значений
   - Убедитесь в корректности типов данных

3. **Ошибки конфигурации**:
   - Проверьте файл `config.json`
   - Восстановите конфигурацию по умолчанию

#### Проблема: Сеть не сохраняется
**Причины и решения:**
1. **Проблемы с БД**:
   - Проверьте права доступа к файлу БД
   - Пересоздайте БД при необходимости

2. **Недостаточно места**:
   - Освободите место на диске
   - Очистите старые резервные копии

3. **Ошибки валидации**:
   - Проверьте корректность данных
   - Убедитесь в уникальности имени сети

#### Проблема: Сеть не загружается
**Причины и решения:**
1. **Повреждение файла БД**:
   - Восстановите из резервной копии
   - Пересоздайте сеть при необходимости

2. **Несовместимость версий**:
   - Обновите систему
   - Используйте совместимые форматы

3. **Ошибки доступа**:
   - Проверьте права доступа к файлам
   - Запустите от имени администратора

### 🔍 Диагностика

#### Проверка состояния БД
```python
from src.database.database_manager import DatabaseManager

# Создание менеджера БД
db_manager = DatabaseManager()

# Проверка состояния
status = db_manager.check_database_status()
print(f"Статус БД: {status}")

# Проверка целостности
integrity = db_manager.check_integrity()
print(f"Целостность: {integrity}")

# Получение статистики
stats = db_manager.get_database_stats()
print(f"Статистика: {stats}")
```

#### Логирование и отладка
```python
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_management.log'),
        logging.StreamHandler()
    ]
)

# Логирование операций
logger = logging.getLogger('NetworkManagement')
logger.info("Начало создания сети")
logger.debug(f"Параметры сети: {network_params}")
logger.error(f"Ошибка создания сети: {error}")
```

---

## 🎉 Заключение

### ✅ Достижения

Система управления сетями предоставляет мощные возможности для:

- **🏗️ Создания** сложных сетевых топологий
- **💾 Управления** сетевыми конфигурациями
- **🗑️ Безопасного удаления** ненужных сетей
- **📊 Анализа** и визуализации топологий
- **⚙️ Гибкой настройки** параметров

### 🚀 Следующие шаги

1. **Изучите примеры** создания сетей
2. **Экспериментируйте** с различными конфигурациями
3. **Анализируйте результаты** с помощью встроенных инструментов
4. **Создавайте отчеты** для документирования исследований

---

**🌐 Система управления сетями готова к использованию! Удачи в создании и анализе сетевых топологий!**