#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация интерактивного редактора топологии сети
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gui.topology_editor import create_topology_editor_window


def show_help():
    """Показывает справку по использованию редактора"""
    help_text = """
ИНТЕРАКТИВНЫЙ РЕДАКТОР ТОПОЛОГИИ СЕТИ

РЕЖИМЫ РЕДАКТИРОВАНИЯ:
• Выбор - выбор и перемещение узлов, выбор связей
• Добавить узел - клик по холсту создает новый узел
• Добавить связь - клик по двум узлам создает связь между ними
• Удалить - клик по узлу или связи удаляет их

УПРАВЛЕНИЕ УЗЛАМИ:
• Перетаскивание - в режиме "Выбор" можно перетаскивать узлы
• Свойства - выберите узел для изменения его свойств
• Типы узлов: server, router, switch, firewall, client

УПРАВЛЕНИЕ СВЯЗЯМИ:
• Выбор - клик по линии связи выбирает её
• Свойства - выберите связь для изменения её параметров
• Параметры: пропускная способность, задержка, надежность

ПАНЕЛИ:
• Левая панель - свойства выбранного узла/связи
• Центральная панель - графическое отображение сети
• Правая панель - списки узлов и связей

АНАЛИЗ:
• Анализ связности - проверка связности сети
• Анализ надежности - запуск расширенного анализа

СОХРАНЕНИЕ/ЗАГРУЗКА:
• Сохранить - экспорт сети в JSON файл
• Загрузить - импорт сети из JSON файла
• Загрузить пример - загрузка демонстрационной сети

ГОРЯЧИЕ КЛАВИШИ:
• Ctrl+S - сохранить сеть
• Ctrl+O - загрузить сеть
• Delete - удалить выбранный элемент
• Escape - очистить выбор
    """
    
    messagebox.showinfo("Справка", help_text)


def create_main_window():
    """Создает главное окно с дополнительными функциями"""
    root = tk.Tk()
    root.title("Интерактивный редактор топологии сети - Демонстрация")
    root.geometry("1500x950")
    
    # Создаем меню
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # Меню "Файл"
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Файл", menu=file_menu)
    file_menu.add_command(label="Новая сеть", command=lambda: messagebox.showinfo("Инфо", "Используйте кнопку 'Очистить сеть'"))
    file_menu.add_command(label="Загрузить пример", command=lambda: messagebox.showinfo("Инфо", "Используйте кнопку 'Загрузить пример'"))
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=root.quit)
    
    # Меню "Помощь"
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Помощь", menu=help_menu)
    help_menu.add_command(label="Справка", command=show_help)
    help_menu.add_command(label="О программе", command=lambda: messagebox.showinfo("О программе", 
        "Интерактивный редактор топологии сети\n\nВерсия: 1.0\nРазработчик: AI Assistant"))
    
    # Создаем редактор
    editor = InteractiveNetworkEditor(root)
    
    # Добавляем обработчики клавиш
    root.bind('<Control-s>', lambda e: editor.save_network())
    root.bind('<Control-o>', lambda e: editor.load_network())
    root.bind('<Delete>', lambda e: editor.delete_selected_node() if editor.selected_nodes else editor.delete_selected_edge())
    root.bind('<Escape>', lambda e: editor.clear_selection())
    
    return root, editor


class InteractiveNetworkEditor:
    """Обертка для редактора с дополнительными функциями"""
    
    def __init__(self, parent):
        from src.gui.topology_editor import InteractiveNetworkEditor as BaseEditor
        self.base_editor = BaseEditor(parent)
        
        # Копируем методы для удобства
        self.save_network = self.base_editor.save_network
        self.load_network = self.base_editor.load_network
        self.delete_selected_node = self.base_editor.delete_selected_node
        self.delete_selected_edge = self.base_editor.delete_selected_edge
        self.clear_selection = self.base_editor.clear_selection
        self.selected_nodes = self.base_editor.selected_nodes
        self.selected_edge = self.base_editor.selected_edge


def demonstrate_features():
    """Демонстрирует возможности редактора"""
    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ИНТЕРАКТИВНОГО РЕДАКТОРА ТОПОЛОГИИ")
    print("=" * 60)
    
    print("\nОСНОВНЫЕ ВОЗМОЖНОСТИ:")
    print("-" * 30)
    print("✅ Интерактивное создание и редактирование сети")
    print("✅ Добавление/удаление узлов и связей")
    print("✅ Перетаскивание узлов мышью")
    print("✅ Настройка свойств узлов и связей")
    print("✅ Визуализация с цветовой индикацией")
    print("✅ Анализ связности сети")
    print("✅ Интеграция с анализом надежности")
    print("✅ Сохранение/загрузка в JSON формате")
    
    print("\nРЕЖИМЫ РЕДАКТИРОВАНИЯ:")
    print("-" * 30)
    print("• Выбор - выбор и перемещение элементов")
    print("• Добавить узел - создание новых узлов")
    print("• Добавить связь - создание связей между узлами")
    print("• Удалить - удаление элементов")
    
    print("\nТИПЫ УЗЛОВ:")
    print("-" * 30)
    print("• 🖥️ Сервер (server) - основные вычислительные узлы")
    print("• 📡 Маршрутизатор (router) - маршрутизация трафика")
    print("• 🔀 Коммутатор (switch) - коммутация на уровне L2")
    print("• 🛡️ Файрвол (firewall) - защита сети")
    print("• 💻 Клиент (client) - конечные устройства")
    
    print("\nПАРАМЕТРЫ УЗЛОВ:")
    print("-" * 30)
    print("• ID - уникальный идентификатор")
    print("• Тип - тип устройства")
    print("• Надежность - вероятность безотказной работы (0-1)")
    print("• Пропускная способность - максимальная нагрузка")
    
    print("\nПАРАМЕТРЫ СВЯЗЕЙ:")
    print("-" * 30)
    print("• Пропускная способность - максимальная скорость передачи")
    print("• Задержка - время прохождения сигнала (мс)")
    print("• Надежность - вероятность безотказной работы связи")
    
    print("\nАНАЛИЗ:")
    print("-" * 30)
    print("• Анализ связности - проверка связности графа")
    print("• Анализ надежности - расширенный анализ с критерием Бирнбаума")
    print("• Метрики сети - диаметр, средняя длина пути")
    
    print("\n" + "=" * 60)
    print("ЗАПУСКАЕМ ИНТЕРАКТИВНЫЙ РЕДАКТОР...")
    print("=" * 60)


def main():
    """Основная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        # Консольная демонстрация
        demonstrate_features()
    else:
        # GUI режим
        try:
            root, editor = create_main_window()
            
            # Показываем приветственное сообщение
            messagebox.showinfo("Добро пожаловать!", 
                "Добро пожаловать в интерактивный редактор топологии сети!\n\n"
                "Используйте меню 'Помощь' → 'Справка' для получения подробной информации.\n"
                "Начните с загрузки примера сети или создайте свою собственную.")
            
            root.mainloop()
            
        except Exception as e:
            print(f"Ошибка при запуске редактора: {e}")
            messagebox.showerror("Ошибка", f"Не удалось запустить редактор: {e}")


if __name__ == "__main__":
    main()
