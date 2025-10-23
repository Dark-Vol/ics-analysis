# Расширенный анализ надежности ИКС

## Обзор

Модуль `advanced_reliability_analyzer.py` предоставляет комплексные функции для анализа надежности информационно-коммуникационных систем, включая:

- **Критерий Бирнбаума** - оценка значимости узлов системы
- **Теория вероятностей** - расчет надежности системы и распределений состояний
- **Тест Дарбина-Уотсона** - проверка автокорреляции остатков
- **Оценка хрупкости** - анализ устойчивости при удалении узлов
- **Моделирование внешних воздействий** - симуляция атак, отключений и отказов

## Основные функции

### 1. Критерий Бирнбаума

```python
from src.analytics.advanced_reliability_analyzer import AdvancedReliabilityAnalyzer

analyzer = AdvancedReliabilityAnalyzer()

# Вероятности безотказной работы узлов
probabilities = {
    'server1': 0.99,
    'router1': 0.95,
    'switch1': 0.97
}

# Матрица связности системы
structure_matrix = [
    [0, 1, 0],  # server1
    [1, 0, 1],  # router1  
    [0, 1, 0]   # switch1
]

# Расчет коэффициентов значимости
birnbaum_coeffs = analyzer.calculate_birnbaum_criterion(probabilities, structure_matrix)
```

### 2. Надежность системы

```python
# Общая вероятность безотказной работы системы
connections = analyzer._get_connections_from_matrix()
system_reliability = analyzer.system_reliability(probabilities, connections)

# Вероятности отказа узлов
failure_probs = analyzer.calculate_node_failure_probabilities(probabilities)

# Распределение вероятностей состояний
state_distribution = analyzer.calculate_probability_distribution(probabilities)
```

### 3. Тест Дарбина-Уотсона

```python
import numpy as np

# Остатки регрессии
residuals = np.random.normal(0, 1, 20)

# Проверка автокорреляции
dw_stat, interpretation = analyzer.durbin_watson_test(residuals.tolist())
print(f"Статистика: {dw_stat:.4f}")
print(f"Интерпретация: {interpretation}")
```

### 4. Оценка хрупкости системы

```python
# Структура сети
network = {
    'nodes': [{'id': 'server1'}, {'id': 'router1'}, {'id': 'switch1'}],
    'connections': {'server1': ['router1'], 'router1': ['server1', 'switch1']}
}

# Удаление узлов
nodes_to_remove = ['switch1']
updated_network = analyzer.remove_nodes(network, nodes_to_remove)

# Проверка критического порога
is_critical, message = analyzer.check_critical_threshold(updated_network)
print(message)
```

### 5. Моделирование внешних воздействий

```python
# Симуляция внешних событий
updated_network = analyzer.simulate_external_events(network)

# Проверка произошедших событий
if 'external_events' in updated_network:
    for event in updated_network['external_events']:
        print(f"Событие: {event['description']}")
        print(f"Вероятность воздействия: {event['probability']:.2f}")
```

## Константы

- `CRITICAL_NODE_THRESHOLD = 3` - минимальное количество узлов для функционирования системы

## Типы внешних воздействий

1. **Хакерская атака** (вероятность: 10%, компрометация: 30%)
2. **Отключение электроэнергии** (вероятность: 5%, отказ: 80%)  
3. **Случайный отказ оборудования** (вероятность: 15%, отказ: 20%)

## Интерпретация результатов

### Коэффициенты Бирнбаума
- **≥ 0.5**: КРИТИЧЕСКИЙ узел
- **≥ 0.2**: ВЫСОКИЙ уровень важности
- **≥ 0.1**: СРЕДНИЙ уровень важности
- **< 0.1**: НИЗКИЙ уровень важности

### Тест Дарбина-Уотсона
- **< 1.5**: Положительная автокорреляция
- **> 2.5**: Отрицательная автокорреляция
- **1.5-2.5**: Автокорреляция отсутствует

## Примеры использования

### Демонстрационный скрипт
```bash
python scripts/demos/demo_advanced_reliability.py
```

### Тестирование функций
```bash
python scripts/tests/test_advanced_reliability.py
```

## Зависимости

Все необходимые библиотеки уже включены в `requirements.txt`:
- `numpy` - численные вычисления
- `pandas` - работа с данными
- `scipy` - статистические функции
- `statsmodels` - эконометрические тесты
- `networkx` - работа с графами

## Выходные данные

Модуль предоставляет:

1. **Таблицу коэффициентов Бирнбаума** - значимость каждого узла
2. **Общую вероятность безотказной работы** - надежность системы
3. **Статистику Дарбина-Уотсона** - наличие автокорреляции
4. **Изменения структуры** - при удалении узлов
5. **Предупреждения** - о достижении критического состояния
6. **Отчеты о воздействиях** - внешние события на сеть

## Интеграция с существующей системой

Модуль полностью совместим с существующей архитектурой проекта и может быть интегрирован в GUI через:

- `src/gui/control_panel.py` - добавление новых кнопок анализа
- `src/gui/main_window.py` - отображение результатов
- `src/reports/word_report_generator.py` - включение в отчеты
