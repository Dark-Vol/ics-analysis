#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Окно для отображения детальной информации о сохраненной сети
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import networkx as nx
from typing import Dict, List, Any
from ..models.network_model import NetworkModel, NetworkNode, NetworkLink
from ..database.database_manager import DatabaseManager
from .themes.blood_angels_theme import BloodAngelsTheme

class NetworkDetailsWindow:
    """Окно с детальной информацией о сети"""
    
    def __init__(self, parent, db_manager: DatabaseManager, network_id: int = None):
        self.parent = parent
        self.db_manager = db_manager
        self.network_id = network_id
        self.network = None
        self.network_data = None
        self.theme = BloodAngelsTheme()
        
        # Создание главного окна
        self.window = tk.Toplevel(parent)
        self.window.title("╔═══ ДЕТАЛИ СЕТИ ═══╗")
        self.window.geometry("1200x800")
        self.window.configure(bg=self.theme.COLORS['bg_primary'])
        
        # Центрирование окна
        self.window.transient(parent)
        self.window.grab_set()
        
        # Загрузка данных сети
        if network_id:
            self._load_network_data(network_id)
        
        # Создание интерфейса
        self._create_widgets()
        
        # Фокус на окне
        self.window.focus_set()
    
    def _load_network_data(self, network_id: int):
        """Загружает данные сети из базы данных"""
        try:
            self.network = self.db_manager.load_network(network_id)
            self.network_data = self.db_manager.get_all_networks()
            self.network_data = next((net for net in self.network_data if net['id'] == network_id), None)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные сети: {str(e)}")
    
    def _create_widgets(self):
        """Создает виджеты окна"""
        # Основной фрейм
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        if self.network_data:
            title_text = f"╔═══ ДЕТАЛИ СЕТИ: {self.network_data['name']} ═══╗"
        else:
            title_text = "╔═══ ДЕТАЛИ СЕТИ ═══╗"
        
        title_label = tk.Label(main_frame,
                             text=title_text,
                             bg=self.theme.COLORS['bg_primary'],
                             fg=self.theme.COLORS['text_secondary'],
                             font=self.theme.FONTS['military'])
        title_label.pack(pady=(0, 20))
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Создание вкладок
        self._create_overview_tab()
        self._create_nodes_tab()
        self._create_links_tab()
        self._create_visualization_tab()
        self._create_metrics_tab()
        
        # Кнопки управления
        self._create_control_buttons(main_frame)
    
    def _create_overview_tab(self):
        """Создает вкладку обзора"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Обзор")
        
        # Информация о сети
        info_frame = ttk.LabelFrame(overview_frame, text="Информация о сети", padding=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        if self.network_data:
            info_text = f"""
Имя: {self.network_data['name']}
Описание: {self.network_data['description']}
Создано: {self.network_data['created_at']}
Обновлено: {self.network_data['updated_at']}
"""
        else:
            info_text = "Данные сети не загружены"
        
        info_label = tk.Label(info_frame, text=info_text, justify=tk.LEFT, anchor=tk.W)
        info_label.pack(fill=tk.X)
        
        # Основные метрики
        if self.network:
            metrics_frame = ttk.LabelFrame(overview_frame, text="Основные метрики", padding=10)
            metrics_frame.pack(fill=tk.X, pady=10)
            
            network_metrics = self.network.get_network_metrics()
            metrics_text = f"""
Количество узлов: {network_metrics.get('nodes_count', 0)}
Количество связей: {network_metrics.get('links_count', 0)}
Плотность сети: {network_metrics.get('density', 0):.3f}
Средний кластеринг: {network_metrics.get('average_clustering', 0):.3f}
Диаметр сети: {network_metrics.get('diameter', 0)}
Средняя длина пути: {network_metrics.get('average_path_length', 0):.3f}
"""
            
            metrics_label = tk.Label(metrics_frame, text=metrics_text, justify=tk.LEFT, anchor=tk.W)
            metrics_label.pack(fill=tk.X)
    
    def _create_nodes_tab(self):
        """Создает вкладку с информацией об узлах"""
        nodes_frame = ttk.Frame(self.notebook)
        self.notebook.add(nodes_frame, text="Узлы")
        
        if not self.network:
            no_data_label = tk.Label(nodes_frame, text="Сеть не загружена", 
                                   bg=self.theme.COLORS['bg_primary'])
            no_data_label.pack(expand=True)
            return
        
        # Создание Treeview для узлов
        columns = ('id', 'x', 'y', 'capacity', 'reliability', 'processing_delay')
        self.nodes_tree = ttk.Treeview(nodes_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.nodes_tree.heading('id', text='ID')
        self.nodes_tree.heading('x', text='X координата')
        self.nodes_tree.heading('y', text='Y координата')
        self.nodes_tree.heading('capacity', text='Пропускная способность')
        self.nodes_tree.heading('reliability', text='Надежность')
        self.nodes_tree.heading('processing_delay', text='Задержка обработки')
        
        self.nodes_tree.column('id', width=50)
        self.nodes_tree.column('x', width=100)
        self.nodes_tree.column('y', width=100)
        self.nodes_tree.column('capacity', width=150)
        self.nodes_tree.column('reliability', width=100)
        self.nodes_tree.column('processing_delay', width=150)
        
        # Заполнение данными
        for node in self.network.nodes:
            self.nodes_tree.insert('', tk.END, values=(
                node.id,
                f"{node.x:.2f}",
                f"{node.y:.2f}",
                f"{node.capacity:.2f} Мбит/с",
                f"{node.reliability:.3f}",
                f"{node.processing_delay:.2f} мс"
            ))
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(nodes_frame, orient=tk.VERTICAL, command=self.nodes_tree.yview)
        self.nodes_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.nodes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_links_tab(self):
        """Создает вкладку с информацией о связях"""
        links_frame = ttk.Frame(self.notebook)
        self.notebook.add(links_frame, text="Связи")
        
        if not self.network:
            no_data_label = tk.Label(links_frame, text="Сеть не загружена", 
                                   bg=self.theme.COLORS['bg_primary'])
            no_data_label.pack(expand=True)
            return
        
        # Создание Treeview для связей
        columns = ('source', 'target', 'bandwidth', 'latency', 'reliability', 'distance')
        self.links_tree = ttk.Treeview(links_frame, columns=columns, show='headings', height=15)
        
        # Настройка колонок
        self.links_tree.heading('source', text='Источник')
        self.links_tree.heading('target', text='Назначение')
        self.links_tree.heading('bandwidth', text='Пропускная способность')
        self.links_tree.heading('latency', text='Задержка')
        self.links_tree.heading('reliability', text='Надежность')
        self.links_tree.heading('distance', text='Расстояние')
        
        self.links_tree.column('source', width=80)
        self.links_tree.column('target', width=80)
        self.links_tree.column('bandwidth', width=150)
        self.links_tree.column('latency', width=100)
        self.links_tree.column('reliability', width=100)
        self.links_tree.column('distance', width=100)
        
        # Заполнение данными
        for link in self.network.links:
            self.links_tree.insert('', tk.END, values=(
                link.source,
                link.target,
                f"{link.bandwidth:.2f} Мбит/с",
                f"{link.latency:.2f} мс",
                f"{link.reliability:.3f}",
                f"{link.distance:.2f}"
            ))
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(links_frame, orient=tk.VERTICAL, command=self.links_tree.yview)
        self.links_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.links_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_visualization_tab(self):
        """Создает вкладку с визуализацией сети"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Визуализация")
        
        if not self.network:
            no_data_label = tk.Label(viz_frame, text="Сеть не загружена", 
                                   bg=self.theme.COLORS['bg_primary'])
            no_data_label.pack(expand=True)
            return
        
        # Создание фигуры для визуализации
        self.viz_fig = Figure(figsize=(10, 8), dpi=100, 
                            facecolor=self.theme.COLORS['bg_primary'])
        self.viz_ax = self.viz_fig.add_subplot(111)
        
        # Создание canvas
        self.viz_canvas = FigureCanvasTkAgg(self.viz_fig, viz_frame)
        
        # Отрисовка сети
        self._draw_network_visualization()
        
        self.viz_canvas.draw()
        self.viz_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _draw_network_visualization(self):
        """Отрисовывает визуализацию сети"""
        if not self.network:
            return
        
        # Получение позиций узлов
        pos = {}
        node_colors = []
        node_sizes = []
        
        for node in self.network.nodes:
            pos[node.id] = (node.x, node.y)
            
            # Цвет узла зависит от надежности
            if node.reliability >= 0.95:
                node_colors.append(self.theme.COLORS['success'])
            elif node.reliability >= 0.9:
                node_colors.append(self.theme.COLORS['primary_gold'])
            elif node.reliability >= 0.8:
                node_colors.append(self.theme.COLORS['warning'])
            else:
                node_colors.append(self.theme.COLORS['danger'])
            
            # Размер узла зависит от пропускной способности
            size = max(100, node.capacity / 5)
            node_sizes.append(size)
        
        # Отрисовка связей
        edge_colors = []
        edge_widths = []
        
        for link in self.network.links:
            # Цвет связи зависит от надежности
            if link.reliability >= 0.95:
                edge_colors.append(self.theme.COLORS['success'])
            elif link.reliability >= 0.9:
                edge_colors.append(self.theme.COLORS['primary_gold'])
            elif link.reliability >= 0.8:
                edge_colors.append(self.theme.COLORS['warning'])
            else:
                edge_colors.append(self.theme.COLORS['danger'])
            
            # Толщина связи зависит от пропускной способности
            width = max(2, link.bandwidth / 10)
            edge_widths.append(width)
        
        # Создание графа NetworkX
        G = nx.Graph()
        G.add_nodes_from(pos.keys())
        G.add_edges_from([(link.source, link.target) for link in self.network.links])
        
        # Отрисовка графа
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, 
                              alpha=0.7, ax=self.viz_ax)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, 
                              alpha=0.6, ax=self.viz_ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_color='black', ax=self.viz_ax)
        
        # Настройка графика
        self.viz_ax.set_title(f"Визуализация сети: {self.network_data['name'] if self.network_data else 'Неизвестная сеть'}", 
                            color=self.theme.COLORS['text_secondary'],
                            fontweight='bold', fontsize=12)
        self.viz_ax.set_xlabel("X координата", color=self.theme.COLORS['text_primary'])
        self.viz_ax.set_ylabel("Y координата", color=self.theme.COLORS['text_primary'])
        self.viz_ax.tick_params(colors=self.theme.COLORS['text_primary'])
        
        # Добавление легенды
        self._add_visualization_legend()
        
        # Обновление canvas
        self.viz_canvas.draw()
    
    def _add_visualization_legend(self):
        """Добавляет легенду к визуализации"""
        # Легенда для узлов
        node_legend = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Высокая надежность (≥95%)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markersize=10, label='Хорошая надежность (90-95%)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Средняя надежность (80-90%)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Низкая надежность (<80%)')
        ]
        
        # Легенда для связей
        edge_legend = [
            plt.Line2D([0], [0], color='green', linewidth=4, label='Высокая надежность связи'),
            plt.Line2D([0], [0], color='yellow', linewidth=4, label='Хорошая надежность связи'),
            plt.Line2D([0], [0], color='orange', linewidth=4, label='Средняя надежность связи'),
            plt.Line2D([0], [0], color='red', linewidth=4, label='Низкая надежность связи')
        ]
        
        # Объединение легенд
        all_legend = node_legend + edge_legend
        
        # Добавление легенды
        self.viz_ax.legend(handles=all_legend, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    def _create_metrics_tab(self):
        """Создает вкладку с детальными метриками"""
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="Метрики")
        
        if not self.network:
            no_data_label = tk.Label(metrics_frame, text="Сеть не загружена", 
                                   bg=self.theme.COLORS['bg_primary'])
            no_data_label.pack(expand=True)
            return
        
        # Создание графиков метрик
        self._create_metrics_plots(metrics_frame)
    
    def _create_metrics_plots(self, parent):
        """Создает графики метрик"""
        # Создание фигуры для метрик
        self.metrics_fig = Figure(figsize=(12, 8), dpi=100, 
                                facecolor=self.theme.COLORS['bg_primary'])
        
        # График распределения надежности узлов
        self.nodes_reliability_ax = self.metrics_fig.add_subplot(221)
        self._plot_nodes_reliability()
        
        # График распределения пропускной способности узлов
        self.nodes_capacity_ax = self.metrics_fig.add_subplot(222)
        self._plot_nodes_capacity()
        
        # График распределения надежности связей
        self.links_reliability_ax = self.metrics_fig.add_subplot(223)
        self._plot_links_reliability()
        
        # График распределения пропускной способности связей
        self.links_bandwidth_ax = self.metrics_fig.add_subplot(224)
        self._plot_links_bandwidth()
        
        # Настройка макета
        self.metrics_fig.tight_layout()
        
        # Создание canvas
        self.metrics_canvas = FigureCanvasTkAgg(self.metrics_fig, parent)
        self.metrics_canvas.draw()
        self.metrics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _plot_nodes_reliability(self):
        """Строит график распределения надежности узлов"""
        if not self.network:
            return
        
        reliabilities = [node.reliability for node in self.network.nodes]
        
        self.nodes_reliability_ax.hist(reliabilities, bins=10, alpha=0.7, 
                                     color=self.theme.COLORS['primary_red'])
        self.nodes_reliability_ax.set_title("Распределение надежности узлов", 
                                          color=self.theme.COLORS['text_secondary'])
        self.nodes_reliability_ax.set_xlabel("Надежность", color=self.theme.COLORS['text_primary'])
        self.nodes_reliability_ax.set_ylabel("Количество", color=self.theme.COLORS['text_primary'])
        self.nodes_reliability_ax.tick_params(colors=self.theme.COLORS['text_primary'])
    
    def _plot_nodes_capacity(self):
        """Строит график распределения пропускной способности узлов"""
        if not self.network:
            return
        
        capacities = [node.capacity for node in self.network.nodes]
        
        self.nodes_capacity_ax.hist(capacities, bins=10, alpha=0.7, 
                                  color=self.theme.COLORS['primary_gold'])
        self.nodes_capacity_ax.set_title("Распределение пропускной способности узлов", 
                                       color=self.theme.COLORS['text_secondary'])
        self.nodes_capacity_ax.set_xlabel("Пропускная способность (Мбит/с)", color=self.theme.COLORS['text_primary'])
        self.nodes_capacity_ax.set_ylabel("Количество", color=self.theme.COLORS['text_primary'])
        self.nodes_capacity_ax.tick_params(colors=self.theme.COLORS['text_primary'])
    
    def _plot_links_reliability(self):
        """Строит график распределения надежности связей"""
        if not self.network:
            return
        
        reliabilities = [link.reliability for link in self.network.links]
        
        self.links_reliability_ax.hist(reliabilities, bins=10, alpha=0.7, 
                                     color=self.theme.COLORS['success'])
        self.links_reliability_ax.set_title("Распределение надежности связей", 
                                          color=self.theme.COLORS['text_secondary'])
        self.links_reliability_ax.set_xlabel("Надежность", color=self.theme.COLORS['text_primary'])
        self.links_reliability_ax.set_ylabel("Количество", color=self.theme.COLORS['text_primary'])
        self.links_reliability_ax.tick_params(colors=self.theme.COLORS['text_primary'])
    
    def _plot_links_bandwidth(self):
        """Строит график распределения пропускной способности связей"""
        if not self.network:
            return
        
        bandwidths = [link.bandwidth for link in self.network.links]
        
        self.links_bandwidth_ax.hist(bandwidths, bins=10, alpha=0.7, 
                                   color=self.theme.COLORS['info'])
        self.links_bandwidth_ax.set_title("Распределение пропускной способности связей", 
                                        color=self.theme.COLORS['text_secondary'])
        self.links_bandwidth_ax.set_xlabel("Пропускная способность (Мбит/с)", color=self.theme.COLORS['text_primary'])
        self.links_bandwidth_ax.set_ylabel("Количество", color=self.theme.COLORS['text_primary'])
        self.links_bandwidth_ax.tick_params(colors=self.theme.COLORS['text_primary'])
    
    def _create_control_buttons(self, parent):
        """Создает кнопки управления"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Кнопка закрытия
        close_button = ttk.Button(buttons_frame, text="╔═══ ЗАКРЫТЬ ═══╗",
                                command=self.window.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)
        
        # Кнопка экспорта
        export_button = ttk.Button(buttons_frame, text="╔═══ ЭКСПОРТ ═══╗",
                                 command=self._export_data)
        export_button.pack(side=tk.RIGHT, padx=5)
        
        # Кнопка обновления
        refresh_button = ttk.Button(buttons_frame, text="╔═══ ОБНОВИТЬ ═══╗",
                                  command=self._refresh_data)
        refresh_button.pack(side=tk.LEFT, padx=5)
    
    def _export_data(self):
        """Экспортирует данные сети"""
        if not self.network_data:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            title="Экспорт данных сети",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"ДЕТАЛИ СЕТИ: {self.network_data['name']}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    f.write(f"Описание: {self.network_data['description']}\n")
                    f.write(f"Создано: {self.network_data['created_at']}\n")
                    f.write(f"Обновлено: {self.network_data['updated_at']}\n\n")
                    
                    if self.network:
                        metrics = self.network.get_network_metrics()
                        f.write("ОСНОВНЫЕ МЕТРИКИ:\n")
                        f.write(f"Количество узлов: {metrics.get('nodes_count', 0)}\n")
                        f.write(f"Количество связей: {metrics.get('links_count', 0)}\n")
                        f.write(f"Плотность сети: {metrics.get('density', 0):.3f}\n")
                        f.write(f"Средний кластеринг: {metrics.get('average_clustering', 0):.3f}\n")
                        f.write(f"Диаметр сети: {metrics.get('diameter', 0)}\n")
                        f.write(f"Средняя длина пути: {metrics.get('average_path_length', 0):.3f}\n\n")
                        
                        f.write("УЗЛЫ:\n")
                        f.write("-" * 30 + "\n")
                        for node in self.network.nodes:
                            f.write(f"ID: {node.id}, X: {node.x:.2f}, Y: {node.y:.2f}, "
                                   f"Пропускная способность: {node.capacity:.2f} Мбит/с, "
                                   f"Надежность: {node.reliability:.3f}, "
                                   f"Задержка обработки: {node.processing_delay:.2f} мс\n")
                        
                        f.write("\nСВЯЗИ:\n")
                        f.write("-" * 30 + "\n")
                        for link in self.network.links:
                            f.write(f"Источник: {link.source}, Назначение: {link.target}, "
                                   f"Пропускная способность: {link.bandwidth:.2f} Мбит/с, "
                                   f"Задержка: {link.latency:.2f} мс, "
                                   f"Надежность: {link.reliability:.3f}, "
                                   f"Расстояние: {link.distance:.2f}\n")
                
                messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {str(e)}")
    
    def _refresh_data(self):
        """Обновляет данные"""
        if self.network_id:
            self._load_network_data(self.network_id)
            # Обновляем все вкладки
            self.notebook.destroy()
            self._create_widgets()
    
    def show(self):
        """Показывает окно"""
        self.window.wait_window()
