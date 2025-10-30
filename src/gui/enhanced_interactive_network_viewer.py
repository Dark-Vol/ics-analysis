#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Покращений інтерактивний візуалізатор мережі з усіма вимогами:
- Покращене відображення зв'язків
- Force-directed layout
- Автоматичне збереження в .db
- Матриця інцидентності
- Критерій Бірнбаума
- Ручне створення мережі з ймовірністю з'єднання
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
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
import random

from ..models.network_model import NetworkModel, NetworkNode, NetworkLink
from .themes.blood_angels_theme import BloodAngelsTheme
from .network_dialog import NetworkDialog
from ..database.database_manager import DatabaseManager
from ..utils.incidence_matrix import IncidenceMatrixManager
from ..analytics.birnbaum_reliability import BirnbaumReliabilityAnalyzer


class EnhancedInteractiveNetworkViewer:
    """Покращений інтерактивний візуалізатор топології мережі"""
    
    def __init__(self, parent, topology_frame=None):
        self.parent = parent
        self.network = None
        self.theme = BloodAngelsTheme()
        self.db_manager = DatabaseManager()
        self.matrix_manager = IncidenceMatrixManager()
        self.birnbaum_analyzer = None
        
        # Використовуємо переданий фрейм або створюємо новий
        if topology_frame:
            self.frame = topology_frame
        else:
            parent_widget = parent.root if hasattr(parent, 'root') else parent
            self.frame = self.theme.create_military_frame(parent_widget, 
                                                         title="ПОКРАЩЕНА ІНТЕРАКТИВНА ТОПОЛОГІЯ МЕРЕЖІ")
        
        # Стан редактора
        self.selected_nodes = set()
        self.selected_edge = None
        self.hovered_node = None
        self.hovered_edge = None
        self.dragging = False
        self.drag_node = None
        
        # Дані мережі
        self.network_dict = {}
        self.main_node = None
        self.connection_probability = 0.3
        
        # NetworkX граф для візуалізації
        self.G = nx.Graph()
        self.pos = {}  # Позиції вузлів
        
        # Створення віджетів
        self._create_widgets()
        
        # Ініціалізація аналізатора надійності
        self._update_birnbaum_analyzer()
    
    def _create_widgets(self):
        """Створює інтерфейс користувача"""
        # Панель керування
        control_frame = self.theme.create_military_frame(self.frame, title="КЕРУВАННЯ")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопки створення мережі
        create_frame = tk.Frame(control_frame)
        create_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(create_frame, text="Створити мережу вручну", 
                 command=self._create_manual_network,
                 **self.theme.BUTTON_STYLE).pack(side=tk.LEFT, padx=2)
        
        tk.Button(create_frame, text="Створити випадкову мережу", 
                 command=self._create_random_network,
                 **self.theme.BUTTON_STYLE).pack(side=tk.LEFT, padx=2)
        
        tk.Button(create_frame, text="Завантажити мережу", 
                 command=self._load_network,
                 **self.theme.BUTTON_STYLE).pack(side=tk.LEFT, padx=2)
        
        # Кнопки аналізу
        analysis_frame = tk.Frame(control_frame)
        analysis_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(analysis_frame, text="Матриця інцидентності", 
                 command=self._show_incidence_matrix,
                 **self.theme.BUTTON_STYLE).pack(side=tk.LEFT, padx=2)
        
        tk.Button(analysis_frame, text="Аналіз надійності", 
                 command=self._show_reliability_analysis,
                 **self.theme.BUTTON_STYLE).pack(side=tk.LEFT, padx=2)
        
        tk.Button(analysis_frame, text="Зберегти мережу", 
                 command=self._save_network,
                 **self.theme.BUTTON_STYLE).pack(side=tk.LEFT, padx=2)
        
        # Створення matplotlib фігури
        self._create_network_canvas()
        
        # Статусна панель
        self._create_status_panel()
    
    def _create_network_canvas(self):
        """Створює canvas для відображення мережі"""
        # Створюємо фігуру matplotlib
        self.network_fig = Figure(figsize=(12, 8), facecolor=self.theme.COLORS['background'])
        self.network_ax = self.network_fig.add_subplot(111)
        self.network_ax.set_facecolor(self.theme.COLORS['background'])
        
        # Налаштовуємо осі
        self.network_ax.set_xlim(0, 10)
        self.network_ax.set_ylim(0, 10)
        self.network_ax.set_aspect('equal')
        self.network_ax.axis('off')
        
        # Створюємо canvas
        self.network_canvas = FigureCanvasTkAgg(self.network_fig, self.frame)
        self.network_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Підключаємо події миші
        self.network_canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.network_canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.network_canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
    
    def _create_status_panel(self):
        """Створює панель статусу"""
        status_frame = self.theme.create_military_frame(self.frame, title="СТАТУС")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Готово до роботи", 
                                    **self.theme.LABEL_STYLE)
        self.status_label.pack(padx=5, pady=5)
    
    def _create_manual_network(self):
        """Створює мережу вручну"""
        dialog = ManualNetworkDialog(self.frame, self.theme)
        if dialog.result:
            self.network_dict = dialog.result['network_dict']
            self.main_node = dialog.result['main_node']
            self.connection_probability = dialog.result['connection_probability']
            
            self._update_network_display()
            self._auto_save_network()
            self._update_birnbaum_analyzer()
            self._update_status("Мережу створено вручну")
    
    def _create_random_network(self):
        """Створює випадкову мережу"""
        try:
            num_nodes = simpledialog.askinteger("Кількість вузлів", 
                                              "Введіть кількість вузлів:", 
                                              initialvalue=10, minvalue=2, maxvalue=50)
            if num_nodes is None:
                return
            
            connection_prob = simpledialog.askfloat("Ймовірність з'єднання", 
                                                  "Введіть ймовірність з'єднання (0.0-1.0):", 
                                                  initialvalue=0.3, minvalue=0.0, maxvalue=1.0)
            if connection_prob is None:
                return
            
            # Створюємо випадкову мережу
            self.network_dict = self._generate_random_network(num_nodes, connection_prob)
            self.main_node = list(self.network_dict.keys())[0]  # Перший вузол як головний
            self.connection_probability = connection_prob
            
            self._update_network_display()
            self._auto_save_network()
            self._update_birnbaum_analyzer()
            self._update_status(f"Випадкову мережу створено: {num_nodes} вузлів, ймовірність {connection_prob}")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка створення мережі: {e}")
    
    def _generate_random_network(self, num_nodes: int, connection_prob: float) -> Dict[str, List[str]]:
        """Генерує випадкову мережу"""
        nodes = [f"node_{i}" for i in range(num_nodes)]
        network_dict = {node: [] for node in nodes}
        
        # Створюємо зв'язки з заданою ймовірністю
        for i, from_node in enumerate(nodes):
            for j, to_node in enumerate(nodes):
                if i != j and random.random() < connection_prob:
                    network_dict[from_node].append(to_node)
        
        return network_dict
    
    def _update_network_display(self):
        """Оновлює відображення мережі"""
        # Очищуємо граф
        self.G.clear()
        self.pos = {}
        
        # Додаємо вузли
        for node in self.network_dict.keys():
            self.G.add_node(node)
        
        # Додаємо ребра
        for from_node, connections in self.network_dict.items():
            for to_node in connections:
                if from_node < to_node:  # Уникаємо дублювання
                    self.G.add_edge(from_node, to_node)
        
        # Обчислюємо позиції з покращеним force-directed layout
        if len(self.G.nodes()) > 0:
            pos_dict = nx.spring_layout(self.G, k=2, iterations=100, seed=42)
            # Перетворюємо numpy масиви в кортежі для безпеки
            self.pos = {node: tuple(pos) for node, pos in pos_dict.items()}
        
        # Очищуємо вибір
        self._clear_selection()
        
        # Перемальовуємо
        self._draw_network()
    
    def _draw_network(self):
        """Малює мережу"""
        self.network_ax.clear()
        self.network_ax.set_xlim(0, 10)
        self.network_ax.set_ylim(0, 10)
        self.network_ax.set_aspect('equal')
        self.network_ax.axis('off')
        
        # Малюємо ребра
        self._draw_edges()
        
        # Малюємо вузли
        self._draw_nodes()
        
        # Додаємо легенду
        self._add_legend()
        
        # Оновлюємо canvas
        self.network_canvas.draw()
        
        # Оновлюємо статус
        self._update_status()
    
    def _draw_edges(self):
        """Малює зв'язки з покращеними стилями"""
        for edge in self.G.edges():
            from_node, to_node = edge
            from_pos = self.pos.get(from_node)
            to_pos = self.pos.get(to_node)
            
            if from_pos is None or to_pos is None:
                continue
            
            # Визначаємо колір зв'язку
            edge_color = self.theme.COLORS['text_secondary']
            linewidth = 1.5
            alpha = 0.7
            
            # Ефекти hover та selection
            if self.hovered_edge == (from_node, to_node) or self.hovered_edge == (to_node, from_node):
                edge_color = self.theme.COLORS['accent_gold']
                linewidth = 3
                alpha = 1.0
            elif self.selected_edge == (from_node, to_node) or self.selected_edge == (to_node, from_node):
                edge_color = self.theme.COLORS['accent_gold']
                linewidth = 2.5
                alpha = 0.9
            
            # Малюємо лінію з плавною анімацією
            self.network_ax.plot([from_pos[0], to_pos[0]], [from_pos[1], to_pos[1]], 
                               color=edge_color, linewidth=linewidth, alpha=alpha,
                               solid_capstyle='round')
    
    def _draw_nodes(self):
        """Малює вузли з зменшеними розмірами"""
        for node_id in self.G.nodes():
            if node_id not in self.pos:
                continue
            
            x, y = self.pos[node_id]
            
            # Визначаємо колір вузла
            if node_id in self.selected_nodes:
                node_color = self.theme.COLORS['accent_gold']
                alpha = 1.0
            elif node_id == self.hovered_node:
                node_color = self.theme.COLORS['accent_gold']
                alpha = 0.8
            elif node_id == self.main_node:
                node_color = self.theme.COLORS['accent_red']
                alpha = 0.9
            else:
                node_color = self.theme.COLORS['text_secondary']
                alpha = 0.8
            
            # Зменшені розміри вузлів
            node_size = 0.12  # Ще більше зменшено для кращого сприйняття
            
            # Малюємо вузол як коло
            circle = patches.Circle((x, y), node_size, color=node_color, alpha=alpha)
            self.network_ax.add_patch(circle)
            
            # Додаємо підпис вузла
            self.network_ax.text(x, y-node_size*1.5, str(node_id), 
                               ha='center', va='top', fontsize=8, 
                               color=self.theme.COLORS['text_primary'],
                               weight='bold')
    
    
    def _add_legend(self):
        """Додає легенду"""
        legend_elements = [
            patches.Patch(color=self.theme.COLORS['accent_red'], label='Головний вузол'),
            patches.Patch(color=self.theme.COLORS['accent_gold'], label='Вибраний вузол'),
            patches.Patch(color=self.theme.COLORS['text_secondary'], label='Звичайний вузол')
        ]
        
        self.network_ax.legend(handles=legend_elements, loc='upper right', 
                             frameon=True, fancybox=True, shadow=True)
    
    def _auto_save_network(self):
        """Автоматично зберігає мережу"""
        try:
            # Зберігаємо в .db форматі
            filename = f"auto_saved_network_{int(time.time())}.db"
            filepath = os.path.join("user_networks", filename)
            
            # Створюємо директорію якщо не існує
            os.makedirs("user_networks", exist_ok=True)
            
            with shelve.open(filepath.replace('.db', '')) as db:
                db['network_dict'] = self.network_dict
                db['main_node'] = self.main_node
                db['connection_probability'] = self.connection_probability
                db['timestamp'] = time.time()
            
            # Створюємо матрицю інцидентності
            self.matrix_manager.create_matrix_from_network(self.network_dict)
            matrix_filename = filepath.replace('.db', '_matrix.db')
            self.matrix_manager.matrix_file = matrix_filename
            self.matrix_manager.save_matrix()
            
            self._update_status(f"Мережу збережено: {filename}")
            
        except Exception as e:
            print(f"Помилка автоматичного збереження: {e}")
    
    def _show_incidence_matrix(self):
        """Показує матрицю інцидентності"""
        if not self.network_dict:
            messagebox.showwarning("Попередження", "Спочатку створіть мережу")
            return
        
        # Створюємо матрицю інцидентності
        matrix = self.matrix_manager.create_matrix_from_network(self.network_dict)
        
        # Показуємо у новому вікні
        matrix_window = tk.Toplevel(self.frame)
        matrix_window.title("Матриця інцидентності")
        matrix_window.geometry("600x400")
        
        # Створюємо текстовий віджет для відображення матриці
        text_widget = tk.Text(matrix_window, wrap=tk.NONE)
        scrollbar_v = tk.Scrollbar(matrix_window, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar_h = tk.Scrollbar(matrix_window, orient=tk.HORIZONTAL, command=text_widget.xview)
        
        text_widget.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Форматуємо матрицю для відображення
        matrix_text = "Матриця інцидентності:\n\n"
        
        # Заголовки рядків і стовпців
        nodes = sorted(self.matrix_manager.node_mapping.keys())
        matrix_text += "   " + " ".join(f"{node:>6}" for node in nodes) + "\n"
        
        # Рядки матриці
        for i, node in enumerate(nodes):
            row = f"{node:>2} " + " ".join(f"{self.matrix_manager.matrix[i][j]:>6}" for j in range(len(nodes)))
            matrix_text += row + "\n"
        
        # Додаємо інформацію про матрицю
        matrix_info = self.matrix_manager.get_matrix_info()
        matrix_text += f"\nІнформація про матрицю:\n"
        matrix_text += f"Розмір: {matrix_info['size']}\n"
        matrix_text += f"Загальна кількість ребер: {matrix_info['total_edges']}\n"
        matrix_text += f"Кількість вузлів: {matrix_info['node_count']}\n"
        
        # Додаємо метрики зв'язності
        connectivity_metrics = self.matrix_manager.calculate_connectivity_metrics()
        matrix_text += f"\nМетрики зв'язності:\n"
        for key, value in connectivity_metrics.items():
            matrix_text += f"{key}: {value}\n"
        
        text_widget.insert(tk.END, matrix_text)
        text_widget.config(state=tk.DISABLED)
        
        # Розміщуємо віджети
        text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        
        matrix_window.grid_rowconfigure(0, weight=1)
        matrix_window.grid_columnconfigure(0, weight=1)
    
    def _show_reliability_analysis(self):
        """Показує аналіз надійності"""
        if not self.birnbaum_analyzer:
            messagebox.showwarning("Попередження", "Спочатку створіть мережу")
            return
        
        # Генеруємо звіт про надійність
        report = self.birnbaum_analyzer.generate_reliability_report()
        
        # Показуємо у новому вікні
        report_window = tk.Toplevel(self.frame)
        report_window.title("Аналіз надійності за критерієм Бірнбаума")
        report_window.geometry("800x600")
        
        # Створюємо текстовий віджет
        text_widget = tk.Text(report_window, wrap=tk.WORD)
        scrollbar = tk.Scrollbar(report_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, report)
        text_widget.config(state=tk.DISABLED)
        
        # Розміщуємо віджети
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _update_birnbaum_analyzer(self):
        """Оновлює аналізатор надійності"""
        if self.network_dict:
            self.birnbaum_analyzer = BirnbaumReliabilityAnalyzer(
                self.network_dict, self.main_node
            )
    
    def _load_network(self):
        """Завантажує мережу з файлу"""
        # Тут можна реалізувати діалог вибору файлу
        # Поки що використовуємо простий приклад
        messagebox.showinfo("Інформація", "Функція завантаження буде реалізована в наступній версії")
    
    def _save_network(self):
        """Зберігає мережу"""
        if not self.network_dict:
            messagebox.showwarning("Попередження", "Немає мережі для збереження")
            return
        
        filename = simpledialog.askstring("Збереження", "Введіть ім'я файлу:", initialvalue="my_network")
        if filename:
            try:
                filepath = os.path.join("user_networks", f"{filename}.db")
                os.makedirs("user_networks", exist_ok=True)
                
                with shelve.open(filepath.replace('.db', '')) as db:
                    db['network_dict'] = self.network_dict
                    db['main_node'] = self.main_node
                    db['connection_probability'] = self.connection_probability
                    db['timestamp'] = time.time()
                
                self._update_status(f"Мережу збережено: {filename}.db")
                
            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка збереження: {e}")
    
    def _update_status(self, message: str = None):
        """Оновлює статус"""
        if message:
            self.status_label.config(text=message)
        else:
            if self.network_dict:
                node_count = len(self.network_dict)
                edge_count = sum(len(connections) for connections in self.network_dict.values())
                self.status_label.config(text=f"Вузлів: {node_count}, Зв'язків: {edge_count}")
            else:
                self.status_label.config(text="Готово до роботи")
    
    def _clear_selection(self):
        """Очищає вибір"""
        self.selected_nodes.clear()
        self.selected_edge = None
        self.hovered_node = None
        self.hovered_edge = None
    
    # Методи обробки подій миші (аналогічні до попередньої версії)
    def _on_mouse_press(self, event):
        """Обробляє натискання миші"""
        if event.inaxes != self.network_ax:
            return
        
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        
        # Знаходимо найближчий вузол
        nearest_node = self._find_nearest_node(x, y)
        
        if nearest_node:
            self.dragging = True
            self.drag_node = nearest_node
            self._select_node(nearest_node)
        else:
            self._clear_selection()
            self._draw_network()
    
    def _on_mouse_release(self, event):
        """Обробляє відпускання миші"""
        if self.dragging and self.drag_node:
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                self._move_node(self.drag_node, x, y)
        
        self.dragging = False
        self.drag_node = None
    
    def _on_mouse_move(self, event):
        """Обробляє рух миші"""
        if event.inaxes != self.network_ax:
            return
        
        x, y = event.xdata, event.ydata
        if x is None or y is None:
            return
        
        if self.dragging and self.drag_node:
            self._move_node(self.drag_node, x, y)
        else:
            self._handle_hover(x, y)
    
    def _handle_hover(self, x, y):
        """Обробляє наведення миші"""
        # Знаходимо найближчий вузол
        nearest_node = self._find_nearest_node(x, y, threshold=0.3)
        
        # Знаходимо найближче ребро
        nearest_edge = self._find_edge_at_position(x, y, threshold=0.2)
        
        # Оновлюємо hover стан
        if nearest_node != self.hovered_node or nearest_edge != self.hovered_edge:
            self.hovered_node = nearest_node
            self.hovered_edge = nearest_edge
            self._draw_network()
    
    def _find_nearest_node(self, x, y, threshold=0.5):
        """Знаходить найближчий вузол"""
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
        """Знаходить зв'язок в указаній позиції"""
        for edge in self.G.edges():
            from_node, to_node = edge
            from_pos = self.pos.get(from_node)
            to_pos = self.pos.get(to_node)
            
            if from_pos is not None and to_pos is not None:
                distance = self._point_to_line_distance(x, y, from_pos[0], from_pos[1], 
                                                      to_pos[0], to_pos[1])
                if distance < threshold:
                    return (from_node, to_node)
        
        return None
    
    def _point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Обчислює відстань від точки до лінії"""
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
    
    def _select_node(self, node_id):
        """Вибирає вузол"""
        self.selected_nodes = {node_id}
        self._draw_network()
    
    def _move_node(self, node_id, x, y):
        """Переміщує вузол"""
        if node_id in self.pos:
            self.pos[node_id] = (x, y)
            self._draw_network()


class ManualNetworkDialog:
    """Діалог для ручного створення мережі"""
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.result = None
        
        self._create_dialog()
    
    def _create_dialog(self):
        """Створює діалог"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Створення мережі вручну")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        
        # Основна рамка
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кількість вузлів
        tk.Label(main_frame, text="Кількість вузлів:", **self.theme.LABEL_STYLE).pack(anchor=tk.W)
        self.num_nodes_var = tk.StringVar(value="10")
        tk.Entry(main_frame, textvariable=self.num_nodes_var, **self.theme.ENTRY_STYLE).pack(fill=tk.X, pady=2)
        
        # Головний вузол
        tk.Label(main_frame, text="Головний вузол:", **self.theme.LABEL_STYLE).pack(anchor=tk.W, pady=(10,0))
        self.main_node_var = tk.StringVar(value="node_0")
        tk.Entry(main_frame, textvariable=self.main_node_var, **self.theme.ENTRY_STYLE).pack(fill=tk.X, pady=2)
        
        # Ймовірність з'єднання
        tk.Label(main_frame, text="Ймовірність з'єднання (0.0-1.0):", **self.theme.LABEL_STYLE).pack(anchor=tk.W, pady=(10,0))
        self.connection_prob_var = tk.StringVar(value="0.3")
        tk.Entry(main_frame, textvariable=self.connection_prob_var, **self.theme.ENTRY_STYLE).pack(fill=tk.X, pady=2)
        
        # Кнопки
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="Створити", command=self._create_network,
                 **self.theme.BUTTON_STYLE).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Скасувати", command=self._cancel,
                 **self.theme.BUTTON_STYLE).pack(side=tk.LEFT, padx=5)
        
        # Центруємо діалог
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Центруємо на екрані
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
    
    def _create_network(self):
        """Створює мережу"""
        try:
            num_nodes = int(self.num_nodes_var.get())
            main_node = self.main_node_var.get()
            connection_prob = float(self.connection_prob_var.get())
            
            if num_nodes < 2:
                messagebox.showerror("Помилка", "Кількість вузлів повинна бути не менше 2")
                return
            
            if not (0.0 <= connection_prob <= 1.0):
                messagebox.showerror("Помилка", "Ймовірність з'єднання повинна бути від 0.0 до 1.0")
                return
            
            # Створюємо мережу
            nodes = [f"node_{i}" for i in range(num_nodes)]
            network_dict = {node: [] for node in nodes}
            
            # Додаємо зв'язки з заданою ймовірністю
            for i, from_node in enumerate(nodes):
                for j, to_node in enumerate(nodes):
                    if i != j and random.random() < connection_prob:
                        network_dict[from_node].append(to_node)
            
            self.result = {
                'network_dict': network_dict,
                'main_node': main_node,
                'connection_probability': connection_prob
            }
            
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Помилка", f"Неправильний формат даних: {e}")
    
    def _cancel(self):
        """Скасовує створення"""
        self.dialog.destroy()