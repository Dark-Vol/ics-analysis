#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Виправлений інтерактивний візуалізатор мережі з коректним відображенням зв'язків,
force-directed layout та автоматичним збереженням у .db
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Tuple, Set
import json
import pickle
import shelve
import os
import threading
import time

from ..models.network_model import NetworkModel, NetworkNode, NetworkLink
from .themes.blood_angels_theme import BloodAngelsTheme
from .network_dialog import NetworkDialog
from ..database.database_manager import DatabaseManager


class FixedInteractiveNetworkViewer:
    """Виправлений інтерактивний візуалізатор топології мережі"""
    
    def __init__(self, parent, topology_frame=None):
        self.parent = parent
        self.network = None
        self.theme = BloodAngelsTheme()
        self.db_manager = DatabaseManager()
        
        # Используем переданный фрейм или создаем новый
        if topology_frame:
            self.frame = topology_frame
        else:
            # Определяем правильный родительский виджет
            parent_widget = parent.root if hasattr(parent, 'root') else parent
            self.frame = self.theme.create_military_frame(parent_widget, 
                                                         title="ІНТЕРАКТИВНА ТОПОЛОГІЯ МЕРЕЖІ")
        
        # Состояние редактора
        self.selected_nodes = set()
        self.selected_edge = None
        self.hovered_node = None
        self.hovered_edge = None
        self.drag_node = None
        self.drag_start_pos = None
        self.edit_mode = 'view'  # 'view', 'add_node', 'add_edge', 'delete'
        self.edge_start_node = None  # Узел для начала создания связи
        
        # Данные для редактирования в форматі словника Python
        self.network_dict = {}  # {'a': ['b', 'c'], 'b': ['c'], 'c': []}
        
        # База данных для синхронизации
        self.db_filename = None
        self.auto_save_enabled = True
        
        # Анимация и обновления
        self.animation_enabled = True
        self.update_queue = []
        self.is_updating = False
        
        # NetworkX граф для візуалізації
        self.G = nx.Graph()
        self.pos = {}  # Позиції вузлів
        
        # Создание виджетов
        self._create_widgets()
        
        # Показываем промпт по умолчанию
        self._show_default_prompt()
    
    def _create_widgets(self):
        """Создает виджеты визуализатора"""
        # Панель управления редактированием
        self._create_edit_control_panel()
        
        # Создание фигуры для графа в стиле Кровавых Ангелов
        self.network_fig = Figure(figsize=(12, 10), dpi=100, 
                                facecolor=self.theme.COLORS['bg_primary'])
        self.network_ax = self.network_fig.add_subplot(111)
        self.network_ax.set_title("╔═══ ІНТЕРАКТИВНА ТОПОЛОГІЯ МЕРЕЖІ ═══╗", 
                                color=self.theme.COLORS['text_secondary'],
                                fontweight='bold', fontsize=12)
        self.network_ax.set_aspect('equal')
        
        # Создание canvas с поддержкой событий мыши
        self.network_canvas = FigureCanvasTkAgg(self.network_fig, self.frame)
        self.network_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Подключение событий мыши
        self.network_canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.network_canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.network_canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.network_canvas.mpl_connect('scroll_event', self._on_scroll)
        
        # Панель управления визуализацией
        self._create_control_panel()
        
        # Панель статуса
        self._create_status_panel()
    
    def _create_edit_control_panel(self):
        """Создает панель управления редактированием"""
        edit_frame = ttk.LabelFrame(self.frame, text="Режим редагування")
        edit_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Переключатели режимов
        self.edit_mode_var = tk.StringVar(value='view')
        
        mode_frame = ttk.Frame(edit_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Перегляд", variable=self.edit_mode_var, 
                       value='view', command=self._set_edit_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Додати вузол", variable=self.edit_mode_var, 
                       value='add_node', command=self._set_edit_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Додати зв'язок", variable=self.edit_mode_var, 
                       value='add_edge', command=self._set_edit_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Видалити", variable=self.edit_mode_var, 
                       value='delete', command=self._set_edit_mode).pack(side=tk.LEFT, padx=5)
        
        # Кнопки действий
        actions_frame = ttk.Frame(edit_frame)
        actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(actions_frame, text="Очистити мережу", 
                  command=self._clear_network).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Завантажити приклад", 
                  command=self._load_sample_network).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Тестова мережа", 
                  command=self.create_test_network).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Діагностика", 
                  command=self._run_diagnostics).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Зберегти зміни", 
                  command=self._save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Аналіз зв'язності", 
                  command=self._analyze_connectivity).pack(side=tk.LEFT, padx=5)
    
    def _create_control_panel(self):
        """Создает панель управления визуализацией"""
        control_frame = ttk.LabelFrame(self.frame, text="Управління візуалізацією")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(buttons_frame, text="Оновити", 
                  command=self._refresh_visualization).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Експорт для аналізу надійності", 
                  command=self._export_for_reliability_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Імпорт з симулятора", 
                  command=self._import_from_simulator).pack(side=tk.LEFT, padx=5)
        
        # Настройки базы данных
        db_frame = ttk.Frame(control_frame)
        db_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(db_frame, text="База даних:").pack(side=tk.LEFT, padx=5)
        self.db_filename_var = tk.StringVar()
        self.db_entry = ttk.Entry(db_frame, textvariable=self.db_filename_var, width=30)
        self.db_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(db_frame, text="Завантажити з .db", 
                  command=self._load_from_db).pack(side=tk.LEFT, padx=5)
        ttk.Button(db_frame, text="Зберегти в .db", 
                  command=self._save_to_db).pack(side=tk.LEFT, padx=5)
        
        # Настройки автосохранения
        auto_save_frame = ttk.Frame(control_frame)
        auto_save_frame.pack(fill=tk.X, pady=5)
        
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_save_frame, text="Автоматичне збереження", 
                       variable=self.auto_save_var).pack(side=tk.LEFT, padx=5)
        
        self.animation_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_save_frame, text="Анімації", 
                       variable=self.animation_var).pack(side=tk.LEFT, padx=5)
    
    def _create_status_panel(self):
        """Создает панель статуса"""
        status_frame = ttk.LabelFrame(self.frame, text="Статус")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Статус сети
        self.status_text = tk.Text(status_frame, height=3, width=80)
        self.status_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Обновляем статус
        self._update_status()
    
    def _update_status(self):
        """Обновляет статус сети"""
        self.status_text.delete(1.0, tk.END)
        
        nodes_count = len(self.network_dict)
        edges_count = sum(len(connections) for connections in self.network_dict.values()) // 2
        
        status_info = f"Вузлів: {nodes_count}, Зв'язків: {edges_count}"
        if self.db_filename:
            status_info += f", База даних: {os.path.basename(self.db_filename)}"
        
        self.status_text.insert(1.0, status_info)
    
    def _set_edit_mode(self):
        """Устанавливает режим редактирования"""
        self.edit_mode = self.edit_mode_var.get()
        
        # Обновляем курсор
        if self.edit_mode == 'view':
            self.network_canvas.get_tk_widget().configure(cursor='arrow')
        elif self.edit_mode == 'add_node':
            self.network_canvas.get_tk_widget().configure(cursor='crosshair')
        elif self.edit_mode == 'add_edge':
            self.network_canvas.get_tk_widget().configure(cursor='plus')
        elif self.edit_mode == 'delete':
            self.network_canvas.get_tk_widget().configure(cursor='X_cursor')
    
    def _on_mouse_press(self, event):
        """Обработчик нажатия мыши"""
        if event.inaxes != self.network_ax:
            return
        
        x, y = event.xdata, event.ydata
        
        if self.edit_mode == 'add_node':
            self._add_node_at_position(x, y)
        elif self.edit_mode == 'add_edge':
            self._start_edge_creation(x, y)
        elif self.edit_mode == 'delete':
            self._delete_at_position(x, y)
        elif self.edit_mode == 'view':
            self._select_at_position(x, y)
    
    def _on_mouse_release(self, event):
        """Обработчик отпускания мыши"""
        if self.drag_node:
            self.drag_node = None
            self.drag_start_pos = None
            # Автосохранение после перетаскивания
            if self.auto_save_enabled and self.db_filename:
                self._auto_save()
    
    def _on_mouse_move(self, event):
        """Обработчик движения мыши"""
        if event.inaxes != self.network_ax:
            return
        
        x, y = event.xdata, event.ydata
        
        # Обработка перетаскивания
        if self.drag_node and self.edit_mode == 'view':
            self._move_node(self.drag_node, x, y)
            return
        
        # Обработка hover эффектов
        self._handle_hover(x, y)
    
    def _on_scroll(self, event):
        """Обработчик прокрутки колесика мыши"""
        if event.inaxes != self.network_ax:
            return
        
        # Масштабирование
        scale_factor = 1.1 if event.button == 'up' else 0.9
        current_xlim = self.network_ax.get_xlim()
        current_ylim = self.network_ax.get_ylim()
        
        new_xlim = [current_xlim[0] * scale_factor, current_xlim[1] * scale_factor]
        new_ylim = [current_ylim[0] * scale_factor, current_ylim[1] * scale_factor]
        
        self.network_ax.set_xlim(new_xlim)
        self.network_ax.set_ylim(new_ylim)
        self.network_canvas.draw()
    
    def _handle_hover(self, x, y):
        """Обрабатывает эффекты наведения"""
        # Проверяем узлы
        node = self._find_nearest_node(x, y, threshold=0.3)
        if node != self.hovered_node:
            self.hovered_node = node
            self._draw_network()
        
        # Проверяем связи
        edge = self._find_edge_at_position(x, y, threshold=0.2)
        if edge != self.hovered_edge:
            self.hovered_edge = edge
            self._draw_network()
    
    def _add_node_at_position(self, x, y):
        """Добавляет узел в указанной позиции"""
        # Генерируем уникальный ID
        node_id = f"node_{len(self.network_dict)}"
        
        # Добавляем узел в словарь
        self.network_dict[node_id] = []
        
        # Обновляем NetworkX граф
        self._update_networkx_graph()
        
        # Обновляем отображение с анимацией
        self._draw_network_with_animation()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    def _start_edge_creation(self, x, y):
        """Начинает создание связи"""
        # Находим ближайший узел
        node = self._find_nearest_node(x, y)
        if node is not None:
            if not hasattr(self, 'edge_start_node'):
                self.edge_start_node = node
                self._select_node(node)
            else:
                # Создаем связь
                if self.edge_start_node is not None and self.edge_start_node != node:
                    self._add_edge(self.edge_start_node, node)
                self.edge_start_node = None
                self._clear_selection()
    
    def _add_edge(self, from_node, to_node):
        """Добавляет связь между узлами"""
        # Проверяем валидность узлов
        if from_node is None or to_node is None:
            messagebox.showerror("Помилка", "Неможливо створити зв'язок з невалідними вузлами")
            return
        
        # Проверяем, что связь не существует
        if to_node in self.network_dict.get(from_node, []):
            messagebox.showwarning("Попередження", "Зв'язок вже існує")
            return
        
        # Добавляем связь в обе стороны
        if from_node not in self.network_dict:
            self.network_dict[from_node] = []
        if to_node not in self.network_dict:
            self.network_dict[to_node] = []
        
        self.network_dict[from_node].append(to_node)
        self.network_dict[to_node].append(from_node)
        
        # Обновляем NetworkX граф
        self._update_networkx_graph()
        
        # Обновляем отображение с анимацией
        self._draw_network_with_animation()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    def _update_networkx_graph(self):
        """Обновляет NetworkX граф из словаря Python"""
        self.G.clear()
        
        # Добавляем узлы (пропускаем None значения)
        for node_id in self.network_dict.keys():
            if node_id is not None:
                self.G.add_node(node_id)
        
        # Добавляем связи
        added_edges = set()  # Для избежания дублирования
        for from_node, connections in self.network_dict.items():
            if from_node is not None:
                for to_node in connections:
                    if to_node is not None:
                        # Создаем уникальный ключ для ребра
                        edge_key = tuple(sorted([from_node, to_node]))
                        if edge_key not in added_edges:
                            self.G.add_edge(from_node, to_node)
                            added_edges.add(edge_key)
        
        # Вычисляем позиции с помощью force-directed layout
        if len(self.G.nodes()) > 0:
            pos_dict = nx.spring_layout(self.G, k=3, iterations=50)
            # Преобразуем numpy массивы в кортежи для безопасности
            self.pos = {node: tuple(pos) for node, pos in pos_dict.items()}
            
    
    def _delete_at_position(self, x, y):
        """Удаляет элемент в указанной позиции"""
        # Сначала проверяем связи
        edge = self._find_edge_at_position(x, y)
        if edge:
            self._delete_edge(edge[0], edge[1])
            return
        
        # Затем узлы
        node = self._find_nearest_node(x, y)
        if node:
            self._delete_node(node)
    
    def _select_at_position(self, x, y):
        """Выбирает элемент в указанной позиции"""
        # Сначала проверяем связи
        edge = self._find_edge_at_position(x, y)
        if edge:
            self._select_edge(edge[0], edge[1])
            return
        
        # Затем узлы
        node = self._find_nearest_node(x, y)
        if node:
            self._select_node(node)
            # Начинаем перетаскивание
            self.drag_node = node
            self.drag_start_pos = (x, y)
    
    def _find_nearest_node(self, x, y, threshold=0.5):
        """Находит ближайший узел к указанной позиции"""
        min_distance = float('inf')
        nearest_node = None
        
        for node_id in self.G.nodes():
            if node_id in self.pos:
                node_x, node_y = self.pos[node_id]
                distance = np.sqrt((x - node_x)**2 + (y - node_y)**2)
                
                if distance < threshold and distance < min_distance:
                    min_distance = distance
                    nearest_node = node_id
        
        return nearest_node
    
    def _find_edge_at_position(self, x, y, threshold=0.2):
        """Находит связь в указанной позиции"""
        for edge in self.G.edges():
            from_node, to_node = edge
            from_pos = self.pos.get(from_node)
            to_pos = self.pos.get(to_node)
            
            # Проверяем, что позиции существуют
            if from_pos is not None and to_pos is not None:
                # Вычисляем расстояние от точки до линии
                distance = self._point_to_line_distance(x, y, from_pos[0], from_pos[1], 
                                                      to_pos[0], to_pos[1])
                if distance < threshold:
                    return (from_node, to_node)
        
        return None
    
    def _point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Вычисляет расстояние от точки до линии"""
        A = px - x1
        B = py - y1
        C = x2 - x1
        D = y2 - y1
        
        dot = A * C + B * D
        len_sq = C * C + D * D
        
        if len_sq == 0:
            return np.sqrt(A * A + B * B)
        
        param = dot / len_sq
        
        if param < 0:
            xx, yy = x1, y1
        elif param > 1:
            xx, yy = x2, y2
        else:
            xx = x1 + param * C
            yy = y1 + param * D
        
        dx = px - xx
        dy = py - yy
        return np.sqrt(dx * dx + dy * dy)
    
    def _move_node(self, node_id, x, y):
        """Перемещает узел в новую позицию"""
        if node_id in self.pos:
            self.pos[node_id] = (x, y)
            self._draw_network()
    
    def _select_node(self, node_id):
        """Выбирает узел и все связанные узлы"""
        self.selected_nodes = {node_id}
        
        # Добавляем все связанные узлы для анализа хрупкости
        connected_nodes = self.network_dict.get(node_id, [])
        self.selected_nodes.update(connected_nodes)
        
        self.selected_edge = None
        self._draw_network()
    
    def _select_edge(self, from_node, to_node):
        """Выбирает связь"""
        self.selected_edge = (from_node, to_node)
        self.selected_nodes = set()
        self._draw_network()
    
    def _clear_selection(self):
        """Очищает выбор"""
        self.selected_nodes = set()
        self.selected_edge = None
        self._draw_network()
    
    def _delete_node(self, node_id):
        """Удаляет узел и все связанные с ним связи"""
        # Удаляем узел из словаря
        if node_id in self.network_dict:
            del self.network_dict[node_id]
        
        # Удаляем связи к этому узлу
        for from_node, connections in self.network_dict.items():
            if node_id in connections:
                connections.remove(node_id)
        
        # Обновляем NetworkX граф
        self._update_networkx_graph()
        
        # Очищаем выбор
        self._clear_selection()
        
        # Обновляем отображение с анимацией
        self._draw_network_with_animation()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    def _delete_edge(self, from_node, to_node):
        """Удаляет связь между узлами"""
        # Удаляем связь в обе стороны
        if from_node in self.network_dict and to_node in self.network_dict[from_node]:
            self.network_dict[from_node].remove(to_node)
        
        if to_node in self.network_dict and from_node in self.network_dict[to_node]:
            self.network_dict[to_node].remove(from_node)
        
        # Обновляем NetworkX граф
        self._update_networkx_graph()
        
        # Очищаем выбор
        self._clear_selection()
        
        # Обновляем отображение с анимацией
        self._draw_network_with_animation()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    
    def _draw_network_with_animation(self):
        """Отрисовывает сеть с анимацией"""
        if self.animation_enabled and self.animation_var.get():
            # Плавное обновление
            self._animate_update()
        else:
            self._draw_network()
    
    def _animate_update(self):
        """Анимированное обновление сети"""
        # Простая анимация - постепенное появление элементов
        self._draw_network()
        
        # Добавляем эффект "пульсации" для новых элементов
        if hasattr(self, '_last_update_time'):
            current_time = time.time()
            if current_time - self._last_update_time < 0.5:  # В течение 0.5 секунд
                self._add_pulse_effect()
        
        self._last_update_time = time.time()
    
    def _add_pulse_effect(self):
        """Добавляет эффект пульсации для новых элементов"""
        # Простая реализация - изменение прозрачности
        for node_id in self.selected_nodes:
            # Добавляем эффект выделения
            pass
    
    def _draw_network(self):
        """Отрисовывает сеть"""
        self.network_ax.clear()
        self.network_ax.set_title("╔═══ ІНТЕРАКТИВНА ТОПОЛОГІЯ МЕРЕЖІ ═══╗", 
                                color=self.theme.COLORS['text_secondary'],
                                fontweight='bold', fontsize=12)
        self.network_ax.set_aspect('equal')
        
        if not self.network_dict:
            self._show_default_prompt()
            return
        
        # Отрисовываем связи
        self._draw_edges()
        
        # Отрисовываем узлы
        self._draw_nodes()
        
        # Добавляем легенду
        self._add_legend()
        
        # Обновляем холст
        self.network_canvas.draw()
        
        # Обновляем статус
        self._update_status()
    
    def _draw_edges(self):
        """Отрисовывает связи"""
        edges_count = 0
        for edge in self.G.edges():
            from_node, to_node = edge
            from_pos = self.pos.get(from_node)
            to_pos = self.pos.get(to_node)
            
            if from_pos is None or to_pos is None:
                continue
            
            edges_count += 1
            
            # Определяем цвет связи
            edge_color = self.theme.COLORS['text_secondary']
            linewidth = 1.5  # Зменшена товщина
            alpha = 0.7
            
            # Эффекты hover и selection
            if self.hovered_edge == (from_node, to_node) or self.hovered_edge == (to_node, from_node):
                edge_color = self.theme.COLORS['accent_gold']
                linewidth = 3
                alpha = 1.0
            elif self.selected_edge == (from_node, to_node) or self.selected_edge == (to_node, from_node):
                edge_color = self.theme.COLORS['accent_gold']
                linewidth = 2.5
                alpha = 0.9
            
            # Отрисовываем линию
            self.network_ax.plot([from_pos[0], to_pos[0]], [from_pos[1], to_pos[1]], 
                               color=edge_color, linewidth=linewidth, alpha=alpha)
        
        
    
    def _draw_nodes(self):
        """Отрисовывает узлы как круги"""
        for node_id in self.G.nodes():
            if node_id not in self.pos:
                continue
                
            x, y = self.pos[node_id]
            
            # Определяем цвет узла
            if node_id in self.selected_nodes:
                node_color = self.theme.COLORS['accent_gold']
                alpha = 1.0
            elif node_id == self.hovered_node:
                node_color = self.theme.COLORS['accent_gold']
                alpha = 0.8
            else:
                node_color = self.theme.COLORS['text_secondary']
                alpha = 0.8
            
            # Зменшені розміри вузлів
            node_size = 0.15  # Зменшено з 0.3 до 0.15
            
            # Отрисовываем узел как круг
            circle = patches.Circle((x, y), node_size, color=node_color, alpha=alpha)
            self.network_ax.add_patch(circle)
            
            # Добавляем текст с ID узла (зменшений шрифт)
            self.network_ax.text(x, y, node_id, ha='center', va='center', 
                               fontsize=6, fontweight='bold', color='white')  # Зменшено з 8 до 6
    
    def _add_legend(self):
        """Добавляет легенду"""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=8, label='Вузол (d≤2)'),
            plt.Line2D([0], [0], marker='^', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=8, label='Трикутник (d=3)'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=8, label='Квадрат (d=4)'),
            plt.Line2D([0], [0], marker='p', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=8, label='П\'ятикутник (d=5)'),
            plt.Line2D([0], [0], marker='h', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=8, label='Шестикутник (d≥6)'),
            plt.Line2D([0], [0], color=self.theme.COLORS['text_secondary'], linewidth=1.5, label='Зв\'язок'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.theme.COLORS['accent_gold'], 
                      markersize=8, label='Вибраний елемент')
        ]
        
        self.network_ax.legend(handles=legend_elements, loc='upper right', fontsize=8)
    
    def _show_default_prompt(self):
        """Показывает промпт по умолчанию"""
        self.network_ax.text(0.5, 0.5, 'ІНТЕРАКТИВНИЙ РЕДАКТОР ТОПОЛОГІЇ\n\n'
                                      'Виберіть режим редагування:\n'
                                      '• Додати вузол - клік по холсту\n'
                                      '• Додати зв\'язок - клік по двох вузлах\n'
                                      '• Видалити - клік по елементу\n'
                                      '• Перегляд - вибір і переміщення елементів\n\n'
                                      'Або завантажте приклад мережі',
                            ha='center', va='center', transform=self.network_ax.transAxes,
                            fontsize=12, color=self.theme.COLORS['text_secondary'],
                            bbox=dict(boxstyle="round,pad=0.3", facecolor=self.theme.COLORS['bg_secondary'], alpha=0.8))
        
        self.network_ax.set_xlim(-2, 2)
        self.network_ax.set_ylim(-2, 2)
        self.network_ax.grid(True, alpha=0.3)
        self.network_canvas.draw()
    
    def _clear_network(self):
        """Очищает сеть"""
        self.network_dict = {}
        self.G.clear()
        self.pos = {}
        
        self._clear_selection()
        self._draw_network()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    def _load_sample_network(self):
        """Загружает пример сети"""
        # Створюємо приклад мережі у форматі словника Python
        self.network_dict = {
            'a': ['b', 'c'],
            'b': ['a', 'c', 'd'],
            'c': ['a', 'b', 'd'],
            'd': ['b', 'c', 'e'],
            'e': ['d', 'f'],
            'f': ['e']
        }
        
        # Обновляем NetworkX граф
        self._update_networkx_graph()
        
        self._draw_network()
    
    def _save_changes(self):
        """Сохраняет изменения"""
        messagebox.showinfo("Інформація", "Зміни збережені в пам'яті. Використовуйте 'Зберегти в .db' для збереження в базу даних.")
    
    def _analyze_connectivity(self):
        """Анализирует связность сети"""
        try:
            # Анализируем связность
            is_connected = nx.is_connected(self.G)
            components = list(nx.connected_components(self.G))
            
            # Вычисляем метрики
            if is_connected:
                diameter = nx.diameter(self.G)
                avg_path_length = nx.average_shortest_path_length(self.G)
            else:
                diameter = "N/A (граф не связен)"
                avg_path_length = "N/A (граф не связен)"
            
            # Показываем результаты
            result_text = f"""
Аналіз зв'язності мережі:

Зв'язність: {'Так' if is_connected else 'Ні'}
Кількість компонент: {len(components)}
Діаметр: {diameter}
Середня довжина шляху: {avg_path_length}

Компоненти зв'язності:
"""
            
            for i, component in enumerate(components, 1):
                result_text += f"{i}. {', '.join(sorted(component))}\n"
            
            messagebox.showinfo("Аналіз зв'язності", result_text)
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при аналізі зв'язності: {e}")
    
    def _export_for_reliability_analysis(self):
        """Экспортирует данные для анализа надежности"""
        try:
            # Преобразуем данные в формат для анализа надежности
            probabilities = {}
            for node_id in self.network_dict.keys():
                probabilities[node_id] = 0.95  # По умолчанию
            
            # Создаем структуру для анализа
            network_structure = {
                'nodes': list(self.network_dict.keys()),
                'connections': self.network_dict
            }
            
            # Импортируем анализатор надежности
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            
            from src.gui.reliability_integration import ReliabilityAnalysisDialog
            
            # Создаем диалог анализа надежности
            dialog = ReliabilityAnalysisDialog(self.parent.root, network_structure, probabilities)
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося запустити аналіз надійності: {e}")
    
    def _import_from_simulator(self):
        """Импортирует данные из симулятора"""
        if hasattr(self.parent, 'simulator') and self.parent.simulator:
            # Здесь нужно реализовать импорт из симулятора
            messagebox.showinfo("Інформація", "Функція імпорту з симулятора буде реалізована в наступній версії")
        else:
            messagebox.showwarning("Попередження", "Симулятор не ініціалізовано")
    
    def _refresh_visualization(self):
        """Обновляет визуализацию"""
        self._update_networkx_graph()
        self._draw_network()
    
    def _load_from_db(self):
        """Загружает сеть из базы данных .db"""
        filename = self.db_filename_var.get()
        if not filename:
            messagebox.showwarning("Попередження", "Введіть ім'я файлу бази даних")
            return
        
        try:
            self.render_network_from_db(filename)
            messagebox.showinfo("Успіх", f"Мережа завантажена з {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити мережу: {e}")
    
    def _save_to_db(self):
        """Сохраняет сеть в базу данных .db"""
        filename = self.db_filename_var.get()
        if not filename:
            messagebox.showwarning("Попередження", "Введіть ім'я файлу бази даних")
            return
        
        try:
            self._save_network_to_db(filename)
            self.db_filename = filename
            messagebox.showinfo("Успіх", f"Мережа збережена в {filename}")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти мережу: {e}")
    
    def _auto_save(self):
        """Автоматическое сохранение"""
        if self.db_filename and self.auto_save_var.get():
            try:
                self._save_network_to_db(self.db_filename)
            except Exception as e:
                print(f"Помилка автоматичного збереження: {e}")
    
    def _save_network_to_db(self, filename):
        """Сохраняет сеть в базу данных у форматі Python словника"""
        try:
            # Використовуємо стандартні засоби Python для збереження словника
            with open(filename, "w", encoding='utf-8') as f:
                f.write(repr(self.network_dict))
        except Exception as e:
            raise Exception(f"Помилка збереження в файл: {e}")
    
    def render_network_from_db(self, filename):
        """Загружает сеть из .db и строит визуализацию"""
        try:
            # Загружаем данные из файла
            with open(filename, "r", encoding='utf-8') as f:
                data = f.read()
                self.network_dict = eval(data)
            
            # Обновляем NetworkX граф
            self._update_networkx_graph()
            
            # Устанавливаем имя файла базы данных
            self.db_filename = filename
            self.db_filename_var.set(filename)
            
            # Обновляем отображение
            self._draw_network()
            
        except Exception as e:
            raise Exception(f"Помилка завантаження з файлу: {e}")
    
    def load_network_from_model(self, network_model: NetworkModel):
        """Загружает сеть из модели NetworkModel"""
        
        self.network_dict = {}
        
        # Преобразуем узлы
        for i, node in enumerate(network_model.nodes):
            node_id = f"node_{i}"
            self.network_dict[node_id] = []
        
        # Преобразуем связи
        for link in network_model.links:
            if isinstance(link, str):
                continue
            
            source = getattr(link, 'source', 0)
            target = getattr(link, 'target', 1)
            source_id = f"node_{source}"
            target_id = f"node_{target}"
            
            # Добавляем связи в обе стороны
            if source_id not in self.network_dict:
                self.network_dict[source_id] = []
            if target_id not in self.network_dict:
                self.network_dict[target_id] = []
            
            if target_id not in self.network_dict[source_id]:
                self.network_dict[source_id].append(target_id)
            if source_id not in self.network_dict[target_id]:
                self.network_dict[target_id].append(source_id)
        
        # Обновляем NetworkX граф
        self._update_networkx_graph()
        
        # Обновляем отображение
        self._draw_network()
        
        return self.network_dict
    def get_network_data(self):
        """Возвращает данные сети для экспорта"""
        return self.network_dict.copy()
    
    def create_test_network(self):
        """Создает тестовую сеть для проверки отображения"""
        self.network_dict = {
            'a': ['b', 'c'],
            'b': ['c', 'd'],
            'c': ['d'],
            'd': []
        }
        
        
        # Обновляем NetworkX граф
        self._update_networkx_graph()
        
        # Обновляем отображение
        self._draw_network()
        
        return self.network_dict
    
    def debug_network_creation(self, network_model):
        """Діагностика створення мережі з моделі"""
        print("=== ДІАГНОСТИКА СТВОРЕННЯ МЕРЕЖІ ===")
        print(f"Кількість вузлів у моделі: {len(network_model.nodes)}")
        print(f"Кількість зв'язків у моделі: {len(network_model.links)}")
        
        # Показуємо всі зв'язки
        for i, link in enumerate(network_model.links):
            print(f"Зв'язок {i}: {link.source} -> {link.target}")
        
        # Конвертуємо в словник
        self.network_dict = {}
        
        # Преобразуем узлы
        for i, node in enumerate(network_model.nodes):
            node_id = f"node_{i}"
            self.network_dict[node_id] = []
        
        print(f"Словник після створення вузлів: {self.network_dict}")
        
        # Преобразуем связи
        for link in network_model.links:
            if isinstance(link, str):
                continue
            
            source = getattr(link, 'source', 0)
            target = getattr(link, 'target', 1)
            source_id = f"node_{source}"
            target_id = f"node_{target}"
            
            print(f"Додаємо зв'язок: {source_id} -> {target_id}")
            
            # Добавляем связи в обе стороны
            if source_id not in self.network_dict:
                self.network_dict[source_id] = []
            if target_id not in self.network_dict:
                self.network_dict[target_id] = []
            
            if target_id not in self.network_dict[source_id]:
                self.network_dict[source_id].append(target_id)
            if source_id not in self.network_dict[target_id]:
                self.network_dict[target_id].append(source_id)
        
        print(f"Фінальний словник: {self.network_dict}")
        
        # Обновляем NetworkX граф
        self._update_networkx_graph()
        
        # Обновляем отображение
        self._draw_network()
        
        return self.network_dict
    
    def _run_diagnostics(self):
        """Запускає діагностику поточної мережі"""
        print("=== ДІАГНОСТИКА ПОТОЧНОЇ МЕРЕЖІ ===")
        print(f"Словник мережі: {self.network_dict}")
        print(f"Кількість вузлів у словнику: {len(self.network_dict)}")
        
        total_connections = sum(len(connections) for connections in self.network_dict.values())
        print(f"Загальна кількість зв'язків у словнику: {total_connections}")
        
        print(f"NetworkX граф: {len(self.G.nodes())} вузлів, {len(self.G.edges())} ребер")
        print(f"Вузли NetworkX: {list(self.G.nodes())}")
        print(f"Ребра NetworkX: {list(self.G.edges())}")
        
        print(f"Позиції вузлів: {self.pos}")
        
        # Перемальовуємо для діагностики
        self._draw_network()
    
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
            if 'connections' in network:
                self.network_dict = network['connections'].copy()
            else:
                self.network_dict = network.copy()
            
            # Обновляем NetworkX граф
            self._update_networkx_graph()
            
            self._draw_network()
            return
        
        # Для других типов данных пытаемся преобразовать
        try:
            # Создаем простую сеть из переданных данных
            self.network_dict = {}
            
            # Если есть атрибуты nodes и links, обрабатываем их
            if hasattr(network, 'nodes'):
                for i, node in enumerate(getattr(network, 'nodes', [])):
                    node_id = f"node_{i}"
                    self.network_dict[node_id] = []
            
            # Обрабатываем связи
            if hasattr(network, 'links'):
                for link in getattr(network, 'links', []):
                    if isinstance(link, str):
                        continue
                    
                    source = getattr(link, 'source', 0)
                    target = getattr(link, 'target', 1)
                    source_id = f"node_{source}"
                    target_id = f"node_{target}"
                    
                    if source_id not in self.network_dict:
                        self.network_dict[source_id] = []
                    if target_id not in self.network_dict:
                        self.network_dict[target_id] = []
                    
                    if target_id not in self.network_dict[source_id]:
                        self.network_dict[source_id].append(target_id)
                    if source_id not in self.network_dict[target_id]:
                        self.network_dict[target_id].append(source_id)
            
            # Обновляем NetworkX граф
            self._update_networkx_graph()
            
            self._draw_network()
            
        except Exception as e:
            print(f"Ошибка при обновлении сети в FixedInteractiveNetworkViewer: {e}")
            self._clear_network()
    
    def reset_network_display(self):
        """Сбрасывает отображение сети (совместимость с NetworkViewer)"""
        self._clear_network()
