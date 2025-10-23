# 🎯 Расширенный анализ надежности ИКС - Быстрый старт

## 🚀 Быстрый запуск

### 1. Консольный режим (без GUI)
```bash
python scripts/demos/demo_advanced_reliability_gui.py --console
```

### 2. GUI режим (требует PyQt5)
```bash
# Установка PyQt5
pip install PyQt5

# Запуск GUI
python scripts/demos/demo_advanced_reliability_gui.py
```

### 3. Тестирование
```bash
python scripts/tests/test_reliability_integration.py
```

## 📋 Реализованные функции

| Функция | Статус | Описание |
|---------|--------|----------|
| **Критерий Бирнбаума** | ✅ | Коэффициенты значимости узлов с визуализацией |
| **Теория вероятностей** | ✅ | Надежность системы, отказы, распределения |
| **Тест Дарбина-Уотсона** | ✅ | Проверка автокорреляции с графиком ACF |
| **Fragility Analysis** | ✅ | Пошаговое удаление узлов с критическим порогом |
| **Визуализация топологии** | ✅ | Граф сети с цветовой индикацией состояний |
| **Внешние угрозы** | ✅ | Симуляция атак, отключений, сбоев |

## 🎨 Визуализация

### Цветовая индикация узлов
- 🟢 **Зеленый**: Узел работает нормально
- 🔴 **Красный**: Узел атакован
- ⚫ **Серый**: Узел отказал
- 🟠 **Оранжевый**: Узел отключен

### Графики
- **Коэффициенты Бирнбаума**: Столбчатая диаграмма с уровнями критичности
- **Топология сети**: Интерактивный граф с состояниями узлов
- **ACF график**: Автокорреляционная функция остатков

## ⚙️ Настройки

### Критический порог системы
```python
CRITICAL_NODE_THRESHOLD = 3  # Минимальное количество узлов
```

### Вероятности внешних угроз
- **Хакерская атака**: 10% вероятность, 30% компрометация
- **Отключение питания**: 5% вероятность, 80% отказ
- **Сбой коммуникации**: 15% вероятность, 20% отказ

## 📊 Примеры результатов

### Коэффициенты Бирнбаума
```
1. router1     :   0.1122 (ВЫСОКИЙ)
2. router2     :   0.0819 (СРЕДНИЙ)
3. server1     :   0.0536 (СРЕДНИЙ)
4. server2     :   0.0535 (СРЕДНИЙ)
5. switch2     :   0.0444 (НИЗКИЙ)
6. switch1     :   0.0324 (НИЗКИЙ)
7. firewall    :  -0.0002 (НИЗКИЙ)
```

### Анализ хрупкости
```
Шаг 1: Удаляем 'switch1'
  Количество узлов: 6
  Надежность системы: 0.000000
  Связность: Да

Шаг 2: Удаляем 'switch2'
  Количество узлов: 5
  Надежность системы: 0.000006
  Связность: Да

Шаг 3: Удаляем 'router1'
  Количество узлов: 4
  Надежность системы: 0.000117
  Связность: Да

Шаг 4: Удаляем 'router2'
  Количество узлов: 3
  Надежность системы: 0.002552
  Связность: Да

Шаг 5: Удаляем 'server1'
  ВНИМАНИЕ: ДОСТИГНУТ КРИТИЧЕСКИЙ ПОРОГ!
  Система перестает функционировать.
```

## 🔧 Интеграция в код

### Простое использование
```python
from src.gui.reliability_integration import ConsoleReliabilityAnalyzer

# Создание анализатора
analyzer = ConsoleReliabilityAnalyzer()

# Загрузка данных сети
network, probabilities = create_sample_network_for_integration()
analyzer.set_network_data(network, probabilities)

# Анализ Бирнбаума
birnbaum_results = analyzer.run_birnbaum_analysis()

# Анализ надежности системы
reliability_results = analyzer.run_system_reliability_analysis()

# Анализ хрупкости
fragility_results = analyzer.run_fragility_analysis(['switch1', 'router1'])

# Симуляция угроз
updated_probs, events = analyzer.run_threats_simulation()
```

### GUI интеграция
```python
from src.gui.reliability_integration import ReliabilityAnalysisDialog

# Создание диалога
dialog = ReliabilityAnalysisDialog(parent_window, network_data, probabilities)
dialog.show()
```

## 📁 Основные файлы

- `src/analytics/advanced_reliability_analyzer.py` - Основной модуль анализа
- `src/gui/advanced_reliability_panel.py` - GUI панель
- `src/gui/reliability_integration.py` - Интеграция с приложением
- `scripts/demos/demo_advanced_reliability_gui.py` - Демонстрация
- `scripts/tests/test_reliability_integration.py` - Тесты

## 🆘 Решение проблем

### PyQt5 не установлен
```bash
pip install PyQt5
```

### Ошибки импорта
Убедитесь, что все зависимости установлены:
```bash
pip install numpy pandas scipy statsmodels networkx matplotlib
```

### Проблемы с кодировкой
Используйте консольный режим или установите правильную кодировку терминала.

## 📚 Дополнительная документация

- [Подробная документация](docs/ADVANCED_RELIABILITY_ANALYSIS.md)
- [Полное описание реализации](docs/COMPLETE_RELIABILITY_ANALYSIS.md)
- [Руководство по интеграции](docs/ADVANCED_RELIABILITY_README.md)

---

**Все функции реализованы и протестированы!** 🎉
