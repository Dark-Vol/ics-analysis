# Скрипты запуска ИКС Анализатора

Эта папка содержит скрипты для запуска приложения ИКС Анализатора.

## Файлы

### `run_blood_angels.bat`
Windows batch-файл для запуска приложения через командную строку.
- Двойной клик для запуска
- Автоматически переходит в корневую папку проекта
- Запускает `main.py`

### `run_blood_angels_demo.py`
Python скрипт для демонстрации приложения.
- Запуск: `python run_blood_angels_demo.py`
- Использует модули из папки `src/`
- Автоматически настраивает пути к модулям

## Использование

### Windows
1. Двойной клик на `run_blood_angels.bat`
2. Или запуск через командную строку: `scripts\run_blood_angels.bat`

### Python
```bash
cd scripts
python run_blood_angels_demo.py
```

## Структура проекта
```
ics/
├── main.py                    # Основной файл приложения
├── src/                       # Исходный код
├── scripts/                   # Скрипты запуска
│   ├── run_blood_angels.bat
│   └── run_blood_angels_demo.py
└── README.md
```
