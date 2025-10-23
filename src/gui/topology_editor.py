#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интерактивный редактор топологии сети
Позволяет добавлять, удалять и изменять связи между узлами
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
import json
import os

# Цвета для визуализации
NODE_COLORS = {
    'default': '#2E8B57',      # Зеленый - по умолчанию
    'selected': '#FFD700',      # Золотой - выбранный
    'hover': '#87CEEB',        # Голубой - при наведении
    'connected': '#32CD32',    # Лайм - подключенный
    'disconnected': '#DC143C', # Красный - отключенный
    'server': '#4169E1',       # Синий - сервер
    'router': '#FF6347',       # Томатный - маршрутизатор
    'switch': '#9370DB',       # Фиолетовый - коммутатор
    'firewall': '#FF4500'      # Оранжево-красный - файрвол
}

EDGE_COLORS = {
    'default': '#808080',      # Серый - по умолчанию
    'selected': '#FFD700',     # Золотой - выбранная связь
    'new': '#00FF00',          # Зеленый - новая связь
    'removed': '#FF0000'       # Красный - удаленная связь
}


class InteractiveNetworkEditor:
    """Интерактивный редактор топологии сети"""
    
    def __init__(self, parent):
        self.parent = parent
        self.network_data = {
            'nodes': [],
            'connections': {},
            'node_properties': {}
        }
        
        # Состояние редактора
        self.selected_nodes = set()
        self.selected_edge = None
        self.drag_node = None
        self.drag_start_pos = None
        self.mode = 'select'  # 'select', 'add_node', 'add_edge', 'delete'
        
        # Создаем интерфейс
        self.create_interface()
        
        # Загружаем пример сети
        self.load_sample_network()
    
    def create_interface(self):
        """Создает пользовательский интерфейс редактора"""
        # Главный фрейм
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Панель инструментов
        self.create_toolbar(main_frame)
        
        # Разделитель
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=5)
        
        # Основная область
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - инструменты и свойства
        self.create_left_panel(content_frame)
        
        # Центральная область - график сети
        self.create_network_canvas(content_frame)
        
        # Правая панель - список узлов и связей
        self.create_right_panel(content_frame)
    
    def create_toolbar(self, parent):
        """Создает панель инструментов"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Режимы редактирования
        mode_frame = ttk.LabelFrame(toolbar, text="Режим редактирования")
        mode_frame.pack(side=tk.LEFT, padx=5)
        
        self.mode_var = tk.StringVar(value='select')
        
        ttk.Radiobutton(mode_frame, text="Выбор", variable=self.mode_var, 
                       value='select', command=self.set_mode).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(mode_frame, text="Добавить узел", variable=self.mode_var, 
                       value='add_node', command=self.set_mode).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(mode_frame, text="Добавить связь", variable=self.mode_var, 
                       value='add_edge', command=self.set_mode).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(mode_frame, text="Удалить", variable=self.mode_var, 
                       value='delete', command=self.set_mode).pack(side=tk.LEFT, padx=2)
        
        # Кнопки действий
        actions_frame = ttk.LabelFrame(toolbar, text="Действия")
        actions_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="Очистить сеть", 
                  command=self.clear_network).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Загрузить пример", 
                  command=self.load_sample_network).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Сохранить", 
                  command=self.save_network).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Загрузить", 
                  command=self.load_network).pack(side=tk.LEFT, padx=2)
        
        # Кнопки анализа
        analysis_frame = ttk.LabelFrame(toolbar, text="Анализ")
        analysis_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(analysis_frame, text="Анализ связности", 
                  command=self.analyze_connectivity).pack(side=tk.LEFT, padx=2)
        ttk.Button(analysis_frame, text="Анализ надежности", 
                  command=self.run_reliability_analysis).pack(side=tk.LEFT, padx=2)
    
    def create_left_panel(self, parent):
        """Создает левую панель с инструментами"""
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Свойства узла
        node_props_frame = ttk.LabelFrame(left_frame, text="Свойства узла")
        node_props_frame.pack(fill=tk.X, pady=5)
        
        # ID узла
        ttk.Label(node_props_frame, text="ID:").pack(anchor=tk.W)
        self.node_id_var = tk.StringVar()
        self.node_id_entry = ttk.Entry(node_props_frame, textvariable=self.node_id_var, 
                                     state='readonly')
        self.node_id_entry.pack(fill=tk.X, pady=2)
        
        # Тип узла
        ttk.Label(node_props_frame, text="Тип:").pack(anchor=tk.W)
        self.node_type_var = tk.StringVar()
        node_type_combo = ttk.Combobox(node_props_frame, textvariable=self.node_type_var,
                                      values=['server', 'router', 'switch', 'firewall', 'client'])
        node_type_combo.pack(fill=tk.X, pady=2)
        node_type_combo.bind('<<ComboboxSelected>>', self.update_node_type)
        
        # Надежность
        ttk.Label(node_props_frame, text="Надежность:").pack(anchor=tk.W)
        self.reliability_var = tk.DoubleVar(value=0.95)
        reliability_scale = ttk.Scale(node_props_frame, from_=0.0, to=1.0, 
                                    variable=self.reliability_var, orient=tk.HORIZONTAL)
        reliability_scale.pack(fill=tk.X, pady=2)
        
        reliability_label = ttk.Label(node_props_frame, textvariable=self.reliability_var)
        reliability_label.pack(anchor=tk.W)
        
        # Пропускная способность
        ttk.Label(node_props_frame, text="Пропускная способность:").pack(anchor=tk.W)
        self.capacity_var = tk.IntVar(value=1000)
        capacity_entry = ttk.Entry(node_props_frame, textvariable=self.capacity_var)
        capacity_entry.pack(fill=tk.X, pady=2)
        
        # Кнопки управления узлом
        node_buttons_frame = ttk.Frame(node_props_frame)
        node_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(node_buttons_frame, text="Обновить", 
                  command=self.update_node_properties).pack(side=tk.LEFT, padx=2)
        ttk.Button(node_buttons_frame, text="Удалить", 
                  command=self.delete_selected_node).pack(side=tk.LEFT, padx=2)
        
        # Свойства связи
        edge_props_frame = ttk.LabelFrame(left_frame, text="Свойства связи")
        edge_props_frame.pack(fill=tk.X, pady=5)
        
        # Связь
        ttk.Label(edge_props_frame, text="Связь:").pack(anchor=tk.W)
        self.edge_info_var = tk.StringVar()
        edge_info_label = ttk.Label(edge_props_frame, textvariable=self.edge_info_var)
        edge_info_label.pack(anchor=tk.W)
        
        # Пропускная способность связи
        ttk.Label(edge_props_frame, text="Пропускная способность:").pack(anchor=tk.W)
        self.edge_bandwidth_var = tk.IntVar(value=100)
        edge_bandwidth_entry = ttk.Entry(edge_props_frame, textvariable=self.edge_bandwidth_var)
        edge_bandwidth_entry.pack(fill=tk.X, pady=2)
        
        # Задержка
        ttk.Label(edge_props_frame, text="Задержка (мс):").pack(anchor=tk.W)
        self.edge_latency_var = tk.DoubleVar(value=5.0)
        edge_latency_entry = ttk.Entry(edge_props_frame, textvariable=self.edge_latency_var)
        edge_latency_entry.pack(fill=tk.X, pady=2)
        
        # Надежность связи
        ttk.Label(edge_props_frame, text="Надежность:").pack(anchor=tk.W)
        self.edge_reliability_var = tk.DoubleVar(value=0.98)
        edge_reliability_scale = ttk.Scale(edge_props_frame, from_=0.0, to=1.0, 
                                         variable=self.edge_reliability_var, orient=tk.HORIZONTAL)
        edge_reliability_scale.pack(fill=tk.X, pady=2)
        
        # Кнопки управления связью
        edge_buttons_frame = ttk.Frame(edge_props_frame)
        edge_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(edge_buttons_frame, text="Обновить", 
                  command=self.update_edge_properties).pack(side=tk.LEFT, padx=2)
        ttk.Button(edge_buttons_frame, text="Удалить", 
                  command=self.delete_selected_edge).pack(side=tk.LEFT, padx=2)
    
    def create_network_canvas(self, parent):
        """Создает холст для отображения сети"""
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Создаем matplotlib фигуру
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Подключаем события мыши
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Создаем ось для графика
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # Переменные для рисования
        self.node_positions = {}
        self.node_circles = {}
        self.edge_lines = {}
        
        # Отрисовываем начальную сеть
        self.draw_network()
    
    def create_right_panel(self, parent):
        """Создает правую панель со списками"""
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # Список узлов
        nodes_frame = ttk.LabelFrame(right_frame, text="Узлы")
        nodes_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview для узлов
        columns = ('ID', 'Тип', 'Надежность', 'Пропускная способность')
        self.nodes_tree = ttk.Treeview(nodes_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.nodes_tree.heading(col, text=col)
            self.nodes_tree.column(col, width=100)
        
        # Скроллбар для узлов
        nodes_scrollbar = ttk.Scrollbar(nodes_frame, orient=tk.VERTICAL, command=self.nodes_tree.yview)
        self.nodes_tree.configure(yscrollcommand=nodes_scrollbar.set)
        
        self.nodes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        nodes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Обработчик выбора узла
        self.nodes_tree.bind('<<TreeviewSelect>>', self.on_node_select)
        
        # Список связей
        edges_frame = ttk.LabelFrame(right_frame, text="Связи")
        edges_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview для связей
        edge_columns = ('От', 'К', 'Пропускная способность', 'Задержка', 'Надежность')
        self.edges_tree = ttk.Treeview(edges_frame, columns=edge_columns, show='headings', height=8)
        
        for col in edge_columns:
            self.edges_tree.heading(col, text=col)
            self.edges_tree.column(col, width=80)
        
        # Скроллбар для связей
        edges_scrollbar = ttk.Scrollbar(edges_frame, orient=tk.VERTICAL, command=self.edges_tree.yview)
        self.edges_tree.configure(yscrollcommand=edges_scrollbar.set)
        
        self.edges_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        edges_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Обработчик выбора связи
        self.edges_tree.bind('<<TreeviewSelect>>', self.on_edge_select)
    
    def set_mode(self):
        """Устанавливает режим редактирования"""
        self.mode = self.mode_var.get()
        
        # Обновляем курсор
        if self.mode == 'select':
            self.canvas.get_tk_widget().configure(cursor='arrow')
        elif self.mode == 'add_node':
            self.canvas.get_tk_widget().configure(cursor='crosshair')
        elif self.mode == 'add_edge':
            self.canvas.get_tk_widget().configure(cursor='plus')
        elif self.mode == 'delete':
            self.canvas.get_tk_widget().configure(cursor='X_cursor')
    
    def on_mouse_press(self, event):
        """Обработчик нажатия мыши"""
        if event.inaxes != self.ax:
            return
        
        x, y = event.xdata, event.ydata
        
        if self.mode == 'add_node':
            self.add_node_at_position(x, y)
        elif self.mode == 'add_edge':
            self.start_edge_creation(x, y)
        elif self.mode == 'delete':
            self.delete_at_position(x, y)
        elif self.mode == 'select':
            self.select_at_position(x, y)
    
    def on_mouse_release(self, event):
        """Обработчик отпускания мыши"""
        if self.drag_node:
            self.drag_node = None
            self.drag_start_pos = None
    
    def on_mouse_move(self, event):
        """Обработчик движения мыши"""
        if event.inaxes != self.ax:
            return
        
        if self.drag_node and self.mode == 'select':
            x, y = event.xdata, event.ydata
            self.move_node(self.drag_node, x, y)
    
    def add_node_at_position(self, x, y):
        """Добавляет узел в указанной позиции"""
        # Генерируем уникальный ID
        node_id = f"node_{len(self.network_data['nodes']) + 1}"
        
        # Добавляем узел в данные
        self.network_data['nodes'].append({
            'id': node_id,
            'x': x,
            'y': y,
            'type': 'server',
            'capacity': 1000,
            'reliability': 0.95
        })
        
        # Добавляем в связи
        self.network_data['connections'][node_id] = []
        
        # Обновляем отображение
        self.update_nodes_list()
        self.draw_network()
    
    def start_edge_creation(self, x, y):
        """Начинает создание связи"""
        # Находим ближайший узел
        node = self.find_nearest_node(x, y)
        if node:
            if not hasattr(self, 'edge_start_node'):
                self.edge_start_node = node
                self.select_node(node)
            else:
                # Создаем связь
                if self.edge_start_node != node:
                    self.add_edge(self.edge_start_node, node)
                self.edge_start_node = None
                self.clear_selection()
    
    def add_edge(self, from_node, to_node):
        """Добавляет связь между узлами"""
        # Проверяем, что связь не существует
        if to_node in self.network_data['connections'].get(from_node, []):
            messagebox.showwarning("Предупреждение", "Связь уже существует")
            return
        
        # Добавляем связь в обе стороны
        if from_node not in self.network_data['connections']:
            self.network_data['connections'][from_node] = []
        if to_node not in self.network_data['connections']:
            self.network_data['connections'][to_node] = []
        
        self.network_data['connections'][from_node].append(to_node)
        self.network_data['connections'][to_node].append(from_node)
        
        # Обновляем отображение
        self.update_edges_list()
        self.draw_network()
    
    def delete_at_position(self, x, y):
        """Удаляет элемент в указанной позиции"""
        # Сначала проверяем связи
        edge = self.find_edge_at_position(x, y)
        if edge:
            self.delete_edge(edge[0], edge[1])
            return
        
        # Затем узлы
        node = self.find_nearest_node(x, y)
        if node:
            self.delete_node(node)
    
    def select_at_position(self, x, y):
        """Выбирает элемент в указанной позиции"""
        # Сначала проверяем связи
        edge = self.find_edge_at_position(x, y)
        if edge:
            self.select_edge(edge[0], edge[1])
            return
        
        # Затем узлы
        node = self.find_nearest_node(x, y)
        if node:
            self.select_node(node)
            # Начинаем перетаскивание
            self.drag_node = node
            self.drag_start_pos = (x, y)
    
    def find_nearest_node(self, x, y, threshold=0.5):
        """Находит ближайший узел к указанной позиции"""
        min_distance = float('inf')
        nearest_node = None
        
        for node_data in self.network_data['nodes']:
            node_x, node_y = node_data['x'], node_data['y']
            distance = np.sqrt((x - node_x)**2 + (y - node_y)**2)
            
            if distance < threshold and distance < min_distance:
                min_distance = distance
                nearest_node = node_data['id']
        
        return nearest_node
    
    def find_edge_at_position(self, x, y, threshold=0.2):
        """Находит связь в указанной позиции"""
        for from_node, connections in self.network_data['connections'].items():
            for to_node in connections:
                from_pos = self.get_node_position(from_node)
                to_pos = self.get_node_position(to_node)
                
                if from_pos and to_pos:
                    # Вычисляем расстояние от точки до линии
                    distance = self.point_to_line_distance(x, y, from_pos[0], from_pos[1], 
                                                          to_pos[0], to_pos[1])
                    if distance < threshold:
                        return (from_node, to_node)
        
        return None
    
    def point_to_line_distance(self, px, py, x1, y1, x2, y2):
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
    
    def get_node_position(self, node_id):
        """Получает позицию узла"""
        for node_data in self.network_data['nodes']:
            if node_data['id'] == node_id:
                return (node_data['x'], node_data['y'])
        return None
    
    def move_node(self, node_id, x, y):
        """Перемещает узел в новую позицию"""
        for node_data in self.network_data['nodes']:
            if node_data['id'] == node_id:
                node_data['x'] = x
                node_data['y'] = y
                break
        
        self.draw_network()
    
    def select_node(self, node_id):
        """Выбирает узел"""
        self.selected_nodes = {node_id}
        self.selected_edge = None
        self.update_node_properties_display(node_id)
        self.draw_network()
    
    def select_edge(self, from_node, to_node):
        """Выбирает связь"""
        self.selected_edge = (from_node, to_node)
        self.selected_nodes = set()
        self.update_edge_properties_display(from_node, to_node)
        self.draw_network()
    
    def clear_selection(self):
        """Очищает выбор"""
        self.selected_nodes = set()
        self.selected_edge = None
        self.draw_network()
    
    def update_node_properties_display(self, node_id):
        """Обновляет отображение свойств узла"""
        for node_data in self.network_data['nodes']:
            if node_data['id'] == node_id:
                self.node_id_var.set(node_id)
                self.node_type_var.set(node_data.get('type', 'server'))
                self.reliability_var.set(node_data.get('reliability', 0.95))
                self.capacity_var.set(node_data.get('capacity', 1000))
                break
    
    def update_edge_properties_display(self, from_node, to_node):
        """Обновляет отображение свойств связи"""
        self.edge_info_var.set(f"{from_node} → {to_node}")
        
        # Получаем свойства связи (если есть)
        edge_key = f"{from_node}-{to_node}"
        if 'edge_properties' in self.network_data:
            props = self.network_data['edge_properties'].get(edge_key, {})
            self.edge_bandwidth_var.set(props.get('bandwidth', 100))
            self.edge_latency_var.set(props.get('latency', 5.0))
            self.edge_reliability_var.set(props.get('reliability', 0.98))
        else:
            self.edge_bandwidth_var.set(100)
            self.edge_latency_var.set(5.0)
            self.edge_reliability_var.set(0.98)
    
    def update_node_properties(self):
        """Обновляет свойства выбранного узла"""
        if not self.selected_nodes:
            return
        
        node_id = list(self.selected_nodes)[0]
        
        for node_data in self.network_data['nodes']:
            if node_data['id'] == node_id:
                node_data['type'] = self.node_type_var.get()
                node_data['reliability'] = self.reliability_var.get()
                node_data['capacity'] = self.capacity_var.get()
                break
        
        self.update_nodes_list()
        self.draw_network()
    
    def update_edge_properties(self):
        """Обновляет свойства выбранной связи"""
        if not self.selected_edge:
            return
        
        from_node, to_node = self.selected_edge
        
        if 'edge_properties' not in self.network_data:
            self.network_data['edge_properties'] = {}
        
        edge_key = f"{from_node}-{to_node}"
        self.network_data['edge_properties'][edge_key] = {
            'bandwidth': self.edge_bandwidth_var.get(),
            'latency': self.edge_latency_var.get(),
            'reliability': self.edge_reliability_var.get()
        }
        
        self.update_edges_list()
        self.draw_network()
    
    def delete_selected_node(self):
        """Удаляет выбранный узел"""
        if not self.selected_nodes:
            return
        
        node_id = list(self.selected_nodes)[0]
        self.delete_node(node_id)
    
    def delete_node(self, node_id):
        """Удаляет узел и все связанные с ним связи"""
        # Удаляем узел из списка
        self.network_data['nodes'] = [n for n in self.network_data['nodes'] if n['id'] != node_id]
        
        # Удаляем все связи с этим узлом
        if node_id in self.network_data['connections']:
            del self.network_data['connections'][node_id]
        
        # Удаляем связи к этому узлу
        for from_node, connections in self.network_data['connections'].items():
            if node_id in connections:
                connections.remove(node_id)
        
        # Очищаем выбор
        self.clear_selection()
        
        # Обновляем отображение
        self.update_nodes_list()
        self.update_edges_list()
        self.draw_network()
    
    def delete_selected_edge(self):
        """Удаляет выбранную связь"""
        if not self.selected_edge:
            return
        
        from_node, to_node = self.selected_edge
        self.delete_edge(from_node, to_node)
    
    def delete_edge(self, from_node, to_node):
        """Удаляет связь между узлами"""
        # Удаляем связь в обе стороны
        if from_node in self.network_data['connections']:
            if to_node in self.network_data['connections'][from_node]:
                self.network_data['connections'][from_node].remove(to_node)
        
        if to_node in self.network_data['connections']:
            if from_node in self.network_data['connections'][to_node]:
                self.network_data['connections'][to_node].remove(from_node)
        
        # Удаляем свойства связи
        if 'edge_properties' in self.network_data:
            edge_key = f"{from_node}-{to_node}"
            if edge_key in self.network_data['edge_properties']:
                del self.network_data['edge_properties'][edge_key]
        
        # Очищаем выбор
        self.clear_selection()
        
        # Обновляем отображение
        self.update_edges_list()
        self.draw_network()
    
    def update_node_type(self, event=None):
        """Обновляет тип узла"""
        self.update_node_properties()
    
    def draw_network(self):
        """Отрисовывает сеть"""
        self.ax.clear()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # Отрисовываем связи
        self.draw_edges()
        
        # Отрисовываем узлы
        self.draw_nodes()
        
        # Обновляем холст
        self.canvas.draw()
    
    def draw_edges(self):
        """Отрисовывает связи"""
        for from_node, connections in self.network_data['connections'].items():
            from_pos = self.get_node_position(from_node)
            if not from_pos:
                continue
            
            for to_node in connections:
                to_pos = self.get_node_position(to_node)
                if not to_pos:
                    continue
                
                # Определяем цвет связи
                edge_color = EDGE_COLORS['default']
                if self.selected_edge == (from_node, to_node) or self.selected_edge == (to_node, from_node):
                    edge_color = EDGE_COLORS['selected']
                
                # Отрисовываем линию
                self.ax.plot([from_pos[0], to_pos[0]], [from_pos[1], to_pos[1]], 
                           color=edge_color, linewidth=2, alpha=0.7)
                
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
                    arrow_length = 0.2
                    self.ax.arrow(mid_x, mid_y, dx_norm * arrow_length, dy_norm * arrow_length,
                                head_width=0.1, head_length=0.1, fc=edge_color, ec=edge_color)
    
    def draw_nodes(self):
        """Отрисовывает узлы"""
        for node_data in self.network_data['nodes']:
            node_id = node_data['id']
            x, y = node_data['x'], node_data['y']
            node_type = node_data.get('type', 'server')
            
            # Определяем цвет узла
            if node_id in self.selected_nodes:
                node_color = NODE_COLORS['selected']
            else:
                node_color = NODE_COLORS.get(node_type, NODE_COLORS['default'])
            
            # Отрисовываем круг узла
            circle = patches.Circle((x, y), 0.3, color=node_color, alpha=0.8)
            self.ax.add_patch(circle)
            
            # Добавляем текст с ID узла
            self.ax.text(x, y, node_id, ha='center', va='center', fontsize=8, fontweight='bold')
            
            # Добавляем иконку типа узла
            icon_text = self.get_node_type_icon(node_type)
            self.ax.text(x, y-0.5, icon_text, ha='center', va='center', fontsize=12)
    
    def get_node_type_icon(self, node_type):
        """Возвращает иконку для типа узла"""
        icons = {
            'server': '🖥️',
            'router': '📡',
            'switch': '🔀',
            'firewall': '🛡️',
            'client': '💻'
        }
        return icons.get(node_type, '●')
    
    def update_nodes_list(self):
        """Обновляет список узлов"""
        # Очищаем список
        for item in self.nodes_tree.get_children():
            self.nodes_tree.delete(item)
        
        # Добавляем узлы
        for node_data in self.network_data['nodes']:
            self.nodes_tree.insert('', 'end', values=(
                node_data['id'],
                node_data.get('type', 'server'),
                f"{node_data.get('reliability', 0.95):.3f}",
                node_data.get('capacity', 1000)
            ))
    
    def update_edges_list(self):
        """Обновляет список связей"""
        # Очищаем список
        for item in self.edges_tree.get_children():
            self.edges_tree.delete(item)
        
        # Добавляем связи
        added_edges = set()
        for from_node, connections in self.network_data['connections'].items():
            for to_node in connections:
                # Избегаем дублирования (связи двунаправленные)
                edge_key = tuple(sorted([from_node, to_node]))
                if edge_key not in added_edges:
                    added_edges.add(edge_key)
                    
                    # Получаем свойства связи
                    edge_props_key = f"{from_node}-{to_node}"
                    if 'edge_properties' in self.network_data and edge_props_key in self.network_data['edge_properties']:
                        props = self.network_data['edge_properties'][edge_props_key]
                        bandwidth = props.get('bandwidth', 100)
                        latency = props.get('latency', 5.0)
                        reliability = props.get('reliability', 0.98)
                    else:
                        bandwidth = 100
                        latency = 5.0
                        reliability = 0.98
                    
                    self.edges_tree.insert('', 'end', values=(
                        from_node,
                        to_node,
                        bandwidth,
                        f"{latency:.1f}",
                        f"{reliability:.3f}"
                    ))
    
    def on_node_select(self, event):
        """Обработчик выбора узла в списке"""
        selection = self.nodes_tree.selection()
        if selection:
            item = self.nodes_tree.item(selection[0])
            node_id = item['values'][0]
            self.select_node(node_id)
    
    def on_edge_select(self, event):
        """Обработчик выбора связи в списке"""
        selection = self.edges_tree.selection()
        if selection:
            item = self.edges_tree.item(selection[0])
            from_node = item['values'][0]
            to_node = item['values'][1]
            self.select_edge(from_node, to_node)
    
    def load_sample_network(self):
        """Загружает пример сети"""
        self.network_data = {
            'nodes': [
                {'id': 'server1', 'x': 2, 'y': 8, 'type': 'server', 'capacity': 1000, 'reliability': 0.99},
                {'id': 'server2', 'x': 8, 'y': 8, 'type': 'server', 'capacity': 800, 'reliability': 0.98},
                {'id': 'router1', 'x': 2, 'y': 5, 'type': 'router', 'capacity': 500, 'reliability': 0.95},
                {'id': 'router2', 'x': 8, 'y': 5, 'type': 'router', 'capacity': 500, 'reliability': 0.96},
                {'id': 'switch1', 'x': 2, 'y': 2, 'type': 'switch', 'capacity': 300, 'reliability': 0.97},
                {'id': 'switch2', 'x': 8, 'y': 2, 'type': 'switch', 'capacity': 300, 'reliability': 0.94},
                {'id': 'firewall', 'x': 5, 'y': 6.5, 'type': 'firewall', 'capacity': 200, 'reliability': 0.92}
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
        
        self.update_nodes_list()
        self.update_edges_list()
        self.draw_network()
    
    def clear_network(self):
        """Очищает сеть"""
        self.network_data = {
            'nodes': [],
            'connections': {},
            'edge_properties': {}
        }
        
        self.clear_selection()
        self.update_nodes_list()
        self.update_edges_list()
        self.draw_network()
    
    def save_network(self):
        """Сохраняет сеть в файл"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.network_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Успех", f"Сеть сохранена в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить сеть: {e}")
    
    def load_network(self):
        """Загружает сеть из файла"""
        from tkinter import filedialog
        
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.network_data = json.load(f)
                
                self.clear_selection()
                self.update_nodes_list()
                self.update_edges_list()
                self.draw_network()
                messagebox.showinfo("Успех", f"Сеть загружена из {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить сеть: {e}")
    
    def analyze_connectivity(self):
        """Анализирует связность сети"""
        try:
            import networkx as nx
            
            # Создаем граф
            G = nx.Graph()
            
            # Добавляем узлы
            for node_data in self.network_data['nodes']:
                G.add_node(node_data['id'])
            
            # Добавляем связи
            for from_node, connections in self.network_data['connections'].items():
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
Анализ связности сети:

Связность: {'Да' if is_connected else 'Нет'}
Количество компонент: {len(components)}
Диаметр: {diameter}
Средняя длина пути: {avg_path_length}

Компоненты связности:
"""
            
            for i, component in enumerate(components, 1):
                result_text += f"{i}. {', '.join(sorted(component))}\n"
            
            messagebox.showinfo("Анализ связности", result_text)
            
        except ImportError:
            messagebox.showerror("Ошибка", "NetworkX не установлен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при анализе связности: {e}")
    
    def run_reliability_analysis(self):
        """Запускает анализ надежности"""
        try:
            # Преобразуем данные в формат для анализа надежности
            probabilities = {}
            for node_data in self.network_data['nodes']:
                probabilities[node_data['id']] = node_data.get('reliability', 0.95)
            
            # Создаем структуру для анализа
            network_structure = {
                'nodes': self.network_data['nodes'],
                'connections': self.network_data['connections']
            }
            
            # Импортируем анализатор надежности
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
            
            from src.gui.reliability_integration import ReliabilityAnalysisDialog
            
            # Создаем диалог анализа надежности
            dialog = ReliabilityAnalysisDialog(self.parent, network_structure, probabilities)
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить анализ надежности: {e}")
    
    def get_network_data(self):
        """Возвращает данные сети"""
        return self.network_data.copy()


def create_topology_editor_window():
    """Создает окно редактора топологии"""
    root = tk.Tk()
    root.title("Интерактивный редактор топологии сети")
    root.geometry("1400x900")
    
    editor = InteractiveNetworkEditor(root)
    
    return root, editor


if __name__ == "__main__":
    root, editor = create_topology_editor_window()
    root.mainloop()
