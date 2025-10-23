# Исправление ошибки InteractiveNetworkViewer

## Проблема

При попытке создать новую сеть или загрузить существующую сеть возникала ошибка:

```text
'InteractiveNetworkViewer' object has no attribute 'update_network'
```

## Причина

В классе `InteractiveNetworkViewer` отсутствовал метод `update_network`, который вызывался из главного окна приложения при работе с сетями.

## Решение

### 1. Добавлен метод `update_network`

В файле `src/gui/interactive_network_viewer.py` добавлен метод `update_network`, который обеспечивает совместимость с интерфейсом `NetworkViewer`:

```python
def update_network(self, network):
    """Обновляет отображение сети (совместимость с NetworkViewer)"""
    if network is None:
        self._clear_network()
        return
    
    # Если это объект NetworkModel, используем специальный метод
    if hasattr(network, 'nodes') and hasattr(network, 'links'):
        self.load_network_from_model(network)
        return
    
    # Если это словарь с данными сети
    if isinstance(network, dict):
        if 'nodes' in network and 'connections' in network:
            self.editable_network_data = network.copy()
            self._draw_network()
            return
    
    # Для других типов данных пытаемся преобразовать
    # ... (обработка различных форматов данных)
```

### 2. Добавлен метод `reset_network_display`

Добавлен метод для сброса отображения сети:

```python
def reset_network_display(self):
    """Сбрасывает отображение сети (совместимость с NetworkViewer)"""
    self._clear_network()
```

### 3. Исправлена проблема с родительским виджетом

Исправлена проблема с определением родительского виджета в конструкторе:

```python
# Определяем правильный родительский виджет
parent_widget = parent.root if hasattr(parent, 'root') else parent
self.frame = self.theme.create_military_frame(parent_widget, 
                                             title="ИНТЕРАКТИВНЫЙ ВИЗУАЛИЗАТОР СЕТИ")
```

## Результат

Теперь при создании новой сети или загрузке существующей сети ошибка больше не возникает. InteractiveNetworkViewer корректно обрабатывает различные типы сетевых данных и обеспечивает совместимость с остальным интерфейсом приложения.

## Тестирование

Исправление протестировано и подтверждено, что:

- Метод `update_network` работает с различными типами данных
- Метод `reset_network_display` корректно сбрасывает отображение
- Создание и загрузка сетей работают без ошибок
