#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный интерактивный визуализатор сети с динамической визуализацией
и автоматической синхронизацией с базой данных
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


class EnhancedInteractiveNetworkViewer:
    """Улучшенный интерактивный визуализатор топологии сети с динамической визуализацией"""
    
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
        
        # Данные для редактирования
        self.editable_network_data = {
            'nodes': [],
            'connections': {},
            'node_properties': {},
            'edge_properties': {}
        }
        
        # База данных для синхронизации
        self.db_filename = None
        self.auto_save_enabled = True
        
        # Анимация и обновления
        self.animation_enabled = True
        self.update_queue = []
        self.is_updating = False
        
        # Создание виджетов
        self._create_widgets()
        
        # Показываем промпт по умолчанию
        self._show_default_prompt()
    
    def _create_widgets(self):
        """Создает виджеты улучшенного интерактивного визуализатора"""
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
        
        nodes_count = len(self.editable_network_data['nodes'])
        edges_count = sum(len(connections) for connections in self.editable_network_data['connections'].values()) // 2
        
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
        node_id = f"node_{len(self.editable_network_data['nodes'])}"
        
        # Добавляем узел в данные
        self.editable_network_data['nodes'].append({
            'id': node_id,
            'x': x,
            'y': y,
            'type': 'server',
            'capacity': 1000,
            'reliability': 0.95,
            'degree': 0
        })
        
        # Добавляем в связи
        self.editable_network_data['connections'][node_id] = []
        
        # Обновляем отображение с анимацией
        self._draw_network_with_animation()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    def _start_edge_creation(self, x, y):
        """Начинает создание связи"""
        # Находим ближайший узел
        node = self._find_nearest_node(x, y)
        if node:
            if not hasattr(self, 'edge_start_node'):
                self.edge_start_node = node
                self._select_node(node)
            else:
                # Создаем связь
                if self.edge_start_node != node:
                    self._add_edge(self.edge_start_node, node)
                self.edge_start_node = None
                self._clear_selection()
    
    def _add_edge(self, from_node, to_node):
        """Добавляет связь между узлами"""
        # Проверяем, что связь не существует
        if to_node in self.editable_network_data['connections'].get(from_node, []):
            messagebox.showwarning("Попередження", "Зв'язок вже існує")
            return
        
        # Добавляем связь в обе стороны
        if from_node not in self.editable_network_data['connections']:
            self.editable_network_data['connections'][from_node] = []
        if to_node not in self.editable_network_data['connections']:
            self.editable_network_data['connections'][to_node] = []
        
        self.editable_network_data['connections'][from_node].append(to_node)
        self.editable_network_data['connections'][to_node].append(from_node)
        
        # Обновляем степени узлов
        self._update_node_degrees()
        
        # Добавляем свойства связи по умолчанию
        edge_key = f"{from_node}-{to_node}"
        self.editable_network_data['edge_properties'][edge_key] = {
            'bandwidth': 100,
            'latency': 5.0,
            'reliability': 0.98
        }
        
        # Обновляем отображение с анимацией
        self._draw_network_with_animation()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    def _update_node_degrees(self):
        """Обновляет степени узлов"""
        for node_data in self.editable_network_data['nodes']:
            node_id = node_data['id']
            degree = len(self.editable_network_data['connections'].get(node_id, []))
            node_data['degree'] = degree
    
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
        
        for node_data in self.editable_network_data['nodes']:
            node_x, node_y = node_data['x'], node_data['y']
            distance = np.sqrt((x - node_x)**2 + (y - node_y)**2)
            
            if distance < threshold and distance < min_distance:
                min_distance = distance
                nearest_node = node_data['id']
        
        return nearest_node
    
    def _find_edge_at_position(self, x, y, threshold=0.2):
        """Находит связь в указанной позиции"""
        for from_node, connections in self.editable_network_data['connections'].items():
            for to_node in connections:
                from_pos = self._get_node_position(from_node)
                to_pos = self._get_node_position(to_node)
                
                if from_pos and to_pos:
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
    
    def _get_node_position(self, node_id):
        """Получает позицию узла"""
        for node_data in self.editable_network_data['nodes']:
            if node_data['id'] == node_id:
                return (node_data['x'], node_data['y'])
        return None
    
    def _move_node(self, node_id, x, y):
        """Перемещает узел в новую позицию"""
        for node_data in self.editable_network_data['nodes']:
            if node_data['id'] == node_id:
                node_data['x'] = x
                node_data['y'] = y
                break
        
        self._draw_network()
    
    def _select_node(self, node_id):
        """Выбирает узел и все связанные узлы"""
        self.selected_nodes = {node_id}
        
        # Добавляем все связанные узлы для анализа хрупкости
        connected_nodes = self.editable_network_data['connections'].get(node_id, [])
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
        # Удаляем узел из списка
        self.editable_network_data['nodes'] = [n for n in self.editable_network_data['nodes'] 
                                              if n['id'] != node_id]
        
        # Удаляем все связи с этим узлом
        if node_id in self.editable_network_data['connections']:
            del self.editable_network_data['connections'][node_id]
        
        # Удаляем связи к этому узлу
        for from_node, connections in self.editable_network_data['connections'].items():
            if node_id in connections:
                connections.remove(node_id)
        
        # Обновляем степени узлов
        self._update_node_degrees()
        
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
        if from_node in self.editable_network_data['connections']:
            if to_node in self.editable_network_data['connections'][from_node]:
                self.editable_network_data['connections'][from_node].remove(to_node)
        
        if to_node in self.editable_network_data['connections']:
            if from_node in self.editable_network_data['connections'][to_node]:
                self.editable_network_data['connections'][to_node].remove(from_node)
        
        # Обновляем степени узлов
        self._update_node_degrees()
        
        # Удаляем свойства связи
        edge_key = f"{from_node}-{to_node}"
        if edge_key in self.editable_network_data['edge_properties']:
            del self.editable_network_data['edge_properties'][edge_key]
        
        # Очищаем выбор
        self._clear_selection()
        
        # Обновляем отображение с анимацией
        self._draw_network_with_animation()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    def _get_node_shape(self, degree):
        """Возвращает форму узла в зависимости от степени"""
        if degree <= 2:
            return 'circle'
        elif degree == 3:
            return 'triangle'
        elif degree == 4:
            return 'square'
        elif degree == 5:
            return 'pentagon'
        else:  # degree >= 6
            return 'hexagon'
    
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
        for node_data in self.editable_network_data['nodes']:
            if node_data['id'] in self.selected_nodes:
                # Добавляем эффект выделения
                pass
    
    def _draw_network(self):
        """Отрисовывает сеть"""
        self.network_ax.clear()
        self.network_ax.set_title("╔═══ ІНТЕРАКТИВНА ТОПОЛОГІЯ МЕРЕЖІ ═══╗", 
                                color=self.theme.COLORS['text_secondary'],
                                fontweight='bold', fontsize=12)
        self.network_ax.set_aspect('equal')
        
        if not self.editable_network_data['nodes']:
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
        for from_node, connections in self.editable_network_data['connections'].items():
            from_pos = self._get_node_position(from_node)
            if not from_pos:
                continue
            
            for to_node in connections:
                to_pos = self._get_node_position(to_node)
                if not to_pos:
                    continue
                
                # Определяем цвет связи
                edge_color = self.theme.COLORS['text_secondary']
                linewidth = 2
                alpha = 0.7
                
                # Эффекты hover и selection
                if self.hovered_edge == (from_node, to_node) or self.hovered_edge == (to_node, from_node):
                    edge_color = self.theme.COLORS['accent_gold']
                    linewidth = 4
                    alpha = 1.0
                elif self.selected_edge == (from_node, to_node) or self.selected_edge == (to_node, from_node):
                    edge_color = self.theme.COLORS['accent_gold']
                    linewidth = 3
                    alpha = 0.9
                
                # Отрисовываем линию
                self.network_ax.plot([from_pos[0], to_pos[0]], [from_pos[1], to_pos[1]], 
                                   color=edge_color, linewidth=linewidth, alpha=alpha)
                
                # Добавляем стрелку (направление)
                mid_x = (from_pos[0] + to_pos[0]) / 2
                mid_y = (from_pos[1] + to_pos[1]) / 2
                
                # Вычисляем направление стрелки
                dx = to_pos[0] - from_pos[0]
                dy = to_pos[1] - from_pos[1]
                length = np.sqrt(dx**2 + dy**2)
                
                if length > 0:
                    dx_norm = dx / length
                    dy_norm = dy / length
                    
                    # Рисуем стрелку
                    self.network_ax.arrow(mid_x, mid_y, dx_norm * 0.2, dy_norm * 0.2,
                                        head_width=0.1, head_length=0.1, 
                                        fc=edge_color, ec=edge_color, alpha=alpha)
    
    def _draw_nodes(self):
        """Отрисовывает узлы с формами в зависимости от степени"""
        for node_data in self.editable_network_data['nodes']:
            node_id = node_data['id']
            x, y = node_data['x'], node_data['y']
            node_type = node_data.get('type', 'server')
            degree = node_data.get('degree', 0)
            
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
            
            # Определяем форму узла в зависимости от степени
            shape = self._get_node_shape(degree)
            
            # Отрисовываем узел в зависимости от формы
            if shape == 'circle':
                circle = patches.Circle((x, y), 0.3, color=node_color, alpha=alpha)
                self.network_ax.add_patch(circle)
            elif shape == 'triangle':
                triangle = patches.RegularPolygon((x, y), 3, radius=0.3, 
                                                color=node_color, alpha=alpha)
                self.network_ax.add_patch(triangle)
            elif shape == 'square':
                square = patches.Rectangle((x-0.3, y-0.3), 0.6, 0.6, 
                                         color=node_color, alpha=alpha)
                self.network_ax.add_patch(square)
            elif shape == 'pentagon':
                pentagon = patches.RegularPolygon((x, y), 5, radius=0.3, 
                                                color=node_color, alpha=alpha)
                self.network_ax.add_patch(pentagon)
            else:  # hexagon
                hexagon = patches.RegularPolygon((x, y), 6, radius=0.3, 
                                               color=node_color, alpha=alpha)
                self.network_ax.add_patch(hexagon)
            
            # Добавляем текст с ID узла
            self.network_ax.text(x, y, node_id, ha='center', va='center', 
                               fontsize=8, fontweight='bold', color='white')
            
            # Добавляем иконку типа узла
            icon_text = self._get_node_type_icon(node_type)
            self.network_ax.text(x, y-0.5, icon_text, ha='center', va='center', fontsize=12)
            
            # Добавляем информацию о степени
            self.network_ax.text(x+0.4, y+0.4, f"d:{degree}", ha='center', va='center', 
                               fontsize=6, color='yellow')
    
    def _get_node_type_icon(self, node_type):
        """Возвращает иконку для типа узла"""
        icons = {
            'server': '🖥️',
            'router': '📡',
            'switch': '🔀',
            'firewall': '🛡️',
            'client': '💻'
        }
        return icons.get(node_type, '●')
    
    def _add_legend(self):
        """Добавляет легенду"""
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=10, label='Вузол (d≤2)'),
            plt.Line2D([0], [0], marker='^', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=10, label='Трикутник (d=3)'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=10, label='Квадрат (d=4)'),
            plt.Line2D([0], [0], marker='p', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=10, label='П\'ятикутник (d=5)'),
            plt.Line2D([0], [0], marker='h', color='w', markerfacecolor=self.theme.COLORS['text_secondary'], 
                      markersize=10, label='Шестикутник (d≥6)'),
            plt.Line2D([0], [0], color=self.theme.COLORS['text_secondary'], linewidth=2, label='Зв\'язок'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.theme.COLORS['accent_gold'], 
                      markersize=10, label='Вибраний елемент')
        ]
        
        self.network_ax.legend(handles=legend_elements, loc='upper right')
    
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
        
        self.network_ax.set_xlim(0, 10)
        self.network_ax.set_ylim(0, 10)
        self.network_ax.grid(True, alpha=0.3)
        self.network_canvas.draw()
    
    def _clear_network(self):
        """Очищает сеть"""
        self.editable_network_data = {
            'nodes': [],
            'connections': {},
            'node_properties': {},
            'edge_properties': {}
        }
        
        self._clear_selection()
        self._draw_network()
        
        # Автосохранение
        if self.auto_save_enabled and self.db_filename:
            self._auto_save()
    
    def _load_sample_network(self):
        """Загружает пример сети"""
        self.editable_network_data = {
            'nodes': [
                {'id': 'server1', 'x': 2, 'y': 8, 'type': 'server', 'capacity': 1000, 'reliability': 0.99, 'degree': 3},
                {'id': 'server2', 'x': 8, 'y': 8, 'type': 'server', 'capacity': 800, 'reliability': 0.98, 'degree': 3},
                {'id': 'router1', 'x': 2, 'y': 5, 'type': 'router', 'capacity': 500, 'reliability': 0.95, 'degree': 3},
                {'id': 'router2', 'x': 8, 'y': 5, 'type': 'router', 'capacity': 500, 'reliability': 0.96, 'degree': 3},
                {'id': 'switch1', 'x': 2, 'y': 2, 'type': 'switch', 'capacity': 300, 'reliability': 0.97, 'degree': 2},
                {'id': 'switch2', 'x': 8, 'y': 2, 'type': 'switch', 'capacity': 300, 'reliability': 0.94, 'degree': 2},
                {'id': 'firewall', 'x': 5, 'y': 6.5, 'type': 'firewall', 'capacity': 200, 'reliability': 0.92, 'degree': 2}
            ],
            'connections': {
                'server1': ['server2', 'router1', 'firewall'],
                'server2': ['server1', 'router2', 'firewall'],
                'router1': ['server1', 'router2', 'switch1'],
                'router2': ['server2', 'router1', 'switch2'],
                'switch1': ['router1', 'switch2'],
                'switch2': ['router2', 'switch1'],
                'firewall': ['server1', 'server2']
            },
            'edge_properties': {
                'server1-server2': {'bandwidth': 1000, 'latency': 2.0, 'reliability': 0.99},
                'server1-router1': {'bandwidth': 100, 'latency': 1.0, 'reliability': 0.98},
                'server1-firewall': {'bandwidth': 100, 'latency': 1.5, 'reliability': 0.97},
                'server2-router2': {'bandwidth': 100, 'latency': 1.0, 'reliability': 0.98},
                'server2-firewall': {'bandwidth': 100, 'latency': 1.5, 'reliability': 0.97},
                'router1-router2': {'bandwidth': 50, 'latency': 3.0, 'reliability': 0.95},
                'router1-switch1': {'bandwidth': 50, 'latency': 2.0, 'reliability': 0.96},
                'router2-switch2': {'bandwidth': 50, 'latency': 2.0, 'reliability': 0.96},
                'switch1-switch2': {'bandwidth': 25, 'latency': 5.0, 'reliability': 0.94}
            }
        }
        
        self._draw_network()
    
    def _save_changes(self):
        """Сохраняет изменения"""
        messagebox.showinfo("Інформація", "Зміни збережені в пам'яті. Використовуйте 'Зберегти в .db' для збереження в базу даних.")
    
    def _analyze_connectivity(self):
        """Анализирует связность сети"""
        try:
            import networkx as nx
            
            # Создаем граф
            G = nx.Graph()
            
            # Добавляем узлы
            for node_data in self.editable_network_data['nodes']:
                G.add_node(node_data['id'])
            
            # Добавляем связи
            for from_node, connections in self.editable_network_data['connections'].items():
                for to_node in connections:
                    G.add_edge(from_node, to_node)
            
            # Анализируем связность
            is_connected = nx.is_connected(G)
            components = list(nx.connected_components(G))
            
            # Вычисляем метрики
            if is_connected:
                diameter = nx.diameter(G)
                avg_path_length = nx.average_shortest_path_length(G)
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
            
        except ImportError:
            messagebox.showerror("Помилка", "NetworkX не встановлено")
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при аналізі зв'язності: {e}")
    
    def _export_for_reliability_analysis(self):
        """Экспортирует данные для анализа надежности"""
        try:
            # Преобразуем данные в формат для анализа надежности
            probabilities = {}
            for node_data in self.editable_network_data['nodes']:
                probabilities[node_data['id']] = node_data.get('reliability', 0.95)
            
            # Создаем структуру для анализа
            network_structure = {
                'nodes': self.editable_network_data['nodes'],
                'connections': self.editable_network_data['connections']
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
        """Сохраняет сеть в базу данных"""
        # Используем shelve для простого словарного хранения
        with shelve.open(filename, 'c') as db:
            db['network_data'] = self.editable_network_data
            db['timestamp'] = time.time()
    
    def render_network_from_db(self, filename):
        """Загружает сеть из .db и строит визуализацию"""
        try:
            # Загружаем данные из базы
            with shelve.open(filename, 'r') as db:
                if 'network_data' in db:
                    self.editable_network_data = db['network_data']
                else:
                    raise ValueError("Файл бази даних не містить даних мережі")
            
            # Обновляем степени узлов
            self._update_node_degrees()
            
            # Устанавливаем имя файла базы данных
            self.db_filename = filename
            self.db_filename_var.set(filename)
            
            # Обновляем отображение
            self._draw_network()
            
        except Exception as e:
            raise Exception(f"Помилка завантаження з бази даних: {e}")
    
    def load_network_from_model(self, network_model: NetworkModel):
        """Загружает сеть из модели NetworkModel"""
        self.editable_network_data = {
            'nodes': [],
            'connections': {},
            'node_properties': {},
            'edge_properties': {}
        }
        
        # Преобразуем узлы
        for i, node in enumerate(network_model.nodes):
            # Проверяем, что node является объектом, а не строкой
            if isinstance(node, str):
                # Если node - это строка, создаем простой узел
                node_data = {
                    'id': node if node else f"node_{i}",
                    'x': i * 2 / 10,  # Нормализуем координаты
                    'y': 5 / 10,
                    'type': 'server',  # По умолчанию
                    'capacity': 1000,
                    'reliability': 0.95,
                    'degree': 0
                }
            else:
                # Если node - это объект, извлекаем его свойства
                node_data = {
                    'id': f"node_{i}",
                    'x': getattr(node, 'x', i * 2) / 10,  # Нормализуем координаты
                    'y': getattr(node, 'y', 5) / 10,
                    'type': 'server',  # По умолчанию
                    'capacity': getattr(node, 'capacity', 1000),
                    'reliability': getattr(node, 'reliability', 0.95),
                    'degree': 0
                }
            self.editable_network_data['nodes'].append(node_data)
            self.editable_network_data['connections'][f"node_{i}"] = []
        
        # Преобразуем связи
        for link in network_model.links:
            # Проверяем, что link является объектом, а не строкой
            if isinstance(link, str):
                # Если link - это строка, пропускаем
                continue
            
            source = getattr(link, 'source', 0)
            target = getattr(link, 'target', 1)
            source_id = f"node_{source}"
            target_id = f"node_{target}"
            
            # Добавляем связи в обе стороны
            if source_id in self.editable_network_data['connections']:
                self.editable_network_data['connections'][source_id].append(target_id)
            if target_id in self.editable_network_data['connections']:
                self.editable_network_data['connections'][target_id].append(source_id)
            
            # Сохраняем свойства связи
            edge_key = f"{source_id}-{target_id}"
            self.editable_network_data['edge_properties'][edge_key] = {
                'bandwidth': getattr(link, 'bandwidth', 100),
                'latency': getattr(link, 'latency', 5.0),
                'reliability': getattr(link, 'reliability', 0.98)
            }
        
        # Обновляем степени узлов
        self._update_node_degrees()
        
        # Обновляем отображение
        self._draw_network()
    
    def get_network_data(self):
        """Возвращает данные сети для экспорта"""
        return self.editable_network_data.copy()
    
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
                self._update_node_degrees()
                self._draw_network()
                return
        
        # Для других типов данных пытаемся преобразовать
        try:
            # Создаем простую сеть из переданных данных
            self.editable_network_data = {
                'nodes': [],
                'connections': {},
                'node_properties': {},
                'edge_properties': {}
            }
            
            # Если есть атрибуты nodes и links, обрабатываем их
            if hasattr(network, 'nodes'):
                for i, node in enumerate(getattr(network, 'nodes', [])):
                    # Проверяем тип узла
                    if isinstance(node, str):
                        # Если узел - это строка, создаем простой узел
                        node_data = {
                            'id': node if node else f"node_{i}",
                            'x': i * 2 / 10,
                            'y': 5 / 10,
                            'type': 'server',
                            'capacity': 1000,
                            'reliability': 0.95,
                            'degree': 0
                        }
                    else:
                        # Если узел - это объект, извлекаем его свойства
                        node_data = {
                            'id': f"node_{i}",
                            'x': getattr(node, 'x', i * 2) / 10,
                            'y': getattr(node, 'y', 5) / 10,
                            'type': 'server',
                            'capacity': getattr(node, 'capacity', 1000),
                            'reliability': getattr(node, 'reliability', 0.95),
                            'degree': 0
                        }
                    self.editable_network_data['nodes'].append(node_data)
                    self.editable_network_data['connections'][f"node_{i}"] = []
            
            # Обрабатываем связи
            if hasattr(network, 'links'):
                for link in getattr(network, 'links', []):
                    # Проверяем тип связи
                    if isinstance(link, str):
                        # Если связь - это строка, пропускаем
                        continue
                    
                    source = getattr(link, 'source', 0)
                    target = getattr(link, 'target', 1)
                    source_id = f"node_{source}"
                    target_id = f"node_{target}"
                    
                    if source_id in self.editable_network_data['connections']:
                        self.editable_network_data['connections'][source_id].append(target_id)
                    if target_id in self.editable_network_data['connections']:
                        self.editable_network_data['connections'][target_id].append(source_id)
            
            # Обновляем степени узлов
            self._update_node_degrees()
            
            self._draw_network()
            
        except Exception as e:
            print(f"Ошибка при обновлении сети в EnhancedInteractiveNetworkViewer: {e}")
            self._clear_network()
    
    def reset_network_display(self):
        """Сбрасывает отображение сети (совместимость с NetworkViewer)"""
        self._clear_network()
