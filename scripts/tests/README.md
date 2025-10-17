# Tests Directory

Эта папка содержит тестовые скрипты для проверки функциональности системы ИКС Анализатора Кровавых Ангелов, организованные по категориям.

## Структура тестов

### 📁 analysis/
Тесты анализа времени и производительности:
- `test_analysis_time_fix.py` - тест исправления времени анализа
- `test_analysis_time_persistence.py` - тест сохранения времени анализа
- `test_analysis_time_setting.py` - тест настройки времени анализа

### 📁 bug_fixes/
Тесты исправлений ошибок:
- `test_bug_fixes.py` - общие тесты исправлений
- `test_final_fix.py` - финальные тесты исправлений
- `test_fixes.py` - базовые тесты исправлений
- `test_string_attribute_fix.py` - тест исправления атрибутов строк

### 📁 gui/
Тесты графического интерфейса:
- `test_control_panel.py` - тесты панели управления
- `test_gui_improvements.py` - тесты улучшений GUI
- `test_gui_launch.py` - тесты запуска GUI
- `test_new_features.py` - тесты новых функций
- `test_pagination_only.py` - тесты пагинации

### 📁 network/
Тесты сетевых функций:
- `test_network_creation.py` - тесты создания сетей
- `test_network_load_fix.py` - тесты исправления загрузки сетей
- `test_network_save_load.py` - тесты сохранения и загрузки сетей
- `test_network_selection.py` - тесты выбора сетей
- `test_network_viewer_fix.py` - тесты исправления просмотрщика сетей
- `test_specific_network.py` - тесты конкретных сетей

### 📁 storage/
Тесты локального хранилища:
- `test_local_network_storage.py` - тесты локального хранилища сетей
- `test_local_network_storage_fixed.py` - исправленные тесты локального хранилища
- `test_local_storage_integration.py` - тесты интеграции локального хранилища

### 📁 simulator/
Тесты симулятора:
- `test_simulator_creation.py` - тесты создания симулятора
- `test_stop_simulation.py` - тесты остановки симуляции

### 📁 reports/
Тесты отчетов:
- `test_report_debug.py` - тесты отладки отчетов

## Запуск тестов

Все тесты запускаются из корневой папки проекта:

```bash
python scripts/tests/[категория]/[название_теста].py
```

### Примеры:
```bash
# Тесты GUI
python scripts/tests/gui/test_gui_launch.py
python scripts/tests/gui/test_control_panel.py

# Тесты сети
python scripts/tests/network/test_network_creation.py
python scripts/tests/network/test_network_save_load.py

# Тесты хранилища
python scripts/tests/storage/test_local_storage_integration.py

# Тесты анализа
python scripts/tests/analysis/test_analysis_time_fix.py

# Тесты симулятора
python scripts/tests/simulator/test_simulator_creation.py
```

## Результаты тестов

Тесты выводят результаты в консоль:
- ✅ Успешные тесты
- ❌ Неудачные тесты
- 📊 Статистика выполнения
- 🔍 Детальная информация об ошибках

## Требования

- Python 3.8+
- Установленные зависимости проекта
- Настроенная база данных
- Корректная структура проекта

## Примечания

- Тесты могут создавать и удалять тестовые данные
- Некоторые тесты требуют запущенного GUI
- Для остановки тестов используйте Ctrl+C
- Результаты тестов сохраняются в логах
