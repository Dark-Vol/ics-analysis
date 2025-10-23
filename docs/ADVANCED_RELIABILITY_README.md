# Расширенный анализ надежности ИКС

## Реализованные функции

### ✅ 1. Оценка по критерию Бирнбаума
- Функция: `calculate_birnbaum_criterion(probabilities, structure_matrix)`
- Рассчитывает коэффициенты значимости каждого узла системы
- Возвращает словарь с коэффициентами для каждого узла

### ✅ 2. Теория вероятностей
- Функция: `system_reliability(probabilities, connections)`
- Вычисляет общую вероятность безотказной работы системы
- Дополнительно: вероятности отказа узлов и распределение состояний

### ✅ 3. Тест Дарбина-Уотсона
- Функция: `durbin_watson_test(residuals)`
- Проверяет наличие автокорреляции остатков
- Возвращает статистику и интерпретацию результата

### ✅ 4. Оценка хрупкости системы
- Функция: `remove_nodes(network, nodes_to_remove)`
- Пошаговое удаление узлов с анализом влияния
- Проверка критического порога системы (минимум 3 узла)

### ✅ 5. Моделирование внешних воздействий
- Функция: `simulate_external_events(network)`
- Имитация хакерских атак, отключений питания, отказов оборудования
- Обновление вероятностей отказов узлов

## Быстрый старт

```python
from src.analytics.advanced_reliability_analyzer import AdvancedReliabilityAnalyzer, create_sample_network

# Создание анализатора
analyzer = AdvancedReliabilityAnalyzer()

# Загрузка примера сети
probabilities, structure_matrix, network = create_sample_network()

# Анализ по критерию Бирнбаума
birnbaum_coeffs = analyzer.calculate_birnbaum_criterion(probabilities, structure_matrix)

# Надежность системы
connections = analyzer._get_connections_from_matrix()
reliability = analyzer.system_reliability(probabilities, connections)

# Тест Дарбина-Уотсона
import numpy as np
residuals = np.random.normal(0, 1, 20)
dw_stat, interpretation = analyzer.durbin_watson_test(residuals.tolist())

# Удаление узлов
updated_network = analyzer.remove_nodes(network, ['switch1'])
is_critical, message = analyzer.check_critical_threshold(updated_network)

# Внешние воздействия
final_network = analyzer.simulate_external_events(network)
```

## Демонстрация

Запустите полную демонстрацию всех функций:
```bash
python scripts/demos/demo_advanced_reliability.py
```

Запустите тесты:
```bash
python scripts/tests/test_advanced_reliability.py
```

## Результаты

- ✅ Все функции реализованы и протестированы
- ✅ Модульная архитектура с docstring-комментариями
- ✅ Примеры использования и демонстрационные скрипты
- ✅ Полная совместимость с существующей системой
- ✅ Подробная документация

## Файлы

- `src/analytics/advanced_reliability_analyzer.py` - основной модуль
- `scripts/demos/demo_advanced_reliability.py` - демонстрация
- `scripts/tests/test_advanced_reliability.py` - тесты
- `docs/ADVANCED_RELIABILITY_ANALYSIS.md` - документация
