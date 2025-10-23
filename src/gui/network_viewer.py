#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Визуализатор сети в стиле Кровавых Ангелов
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import networkx as nx
from ..models.network_model import NetworkModel
from .themes.blood_angels_theme import BloodAngelsTheme
from .network_dialog import NetworkDialog
from ..database.database_manager import DatabaseManager

class NetworkViewer:
    """Визуализатор топологии сети в стиле Кровавых Ангелов"""
    
    def __init__(self, parent, topology_frame=None):
        self.parent = parent
        self.network = None
        self.theme = BloodAngelsTheme()
        self.db_manager = DatabaseManager()
        
        # Используем переданный фрейм или создаем новый
        if topology_frame:
            self.frame = topology_frame
        else:
            # Создание фрейма в военном стиле
            self.frame = self.theme.create_military_frame(parent.root, 
                                                       title="ВИЗУАЛИЗАТОР СЕТИ")
        
        # Создание виджетов
        self._create_widgets()
    
    def _create_widgets(self):
        """Создает виджеты визуализатора в военном стиле"""
        # Создание фигуры для графа в стиле Кровавых Ангелов
        self.network_fig = Figure(figsize=(8, 6), dpi=100, 
                                facecolor=self.theme.COLORS['bg_primary'])
        self.network_ax = self.network_fig.add_subplot(111)
        self.network_ax.set_title("╔═══ ТОПОЛОГИЯ СЕТИ ═══╗", 
                                color=self.theme.COLORS['text_secondary'],
                                fontweight='bold', fontsize=12)
        self.network_ax.set_aspect('equal')
        
        # Создание canvas
        self.network_canvas = FigureCanvasTkAgg(self.network_fig, self.frame)
        self.network_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Показываем промпт по умолчанию
        self._show_default_prompt()
        
        # Панель управления визуализацией
        self._create_control_panel()
    
    def _create_control_panel(self):
        """Создает панель управления визуализацией в военном стиле"""
        control_frame = ttk.Frame(self.frame, style='BloodAngels.TFrame')
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0), padx=10)
        
        # Кнопка создания/загрузки сети
        create_load_button = ttk.Button(control_frame, text="╔═══ СОЗДАТЬ/ЗАГРУЗИТЬ СЕТЬ ═══╗", 
                                       command=self._open_network_dialog,
                                       style='BloodAngels.TButton')
        create_load_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Кнопка обновления
        refresh_button = ttk.Button(control_frame, text="╔═══ ОБНОВИТЬ ═══╗", 
                                   command=self._refresh_network,
                                   style='BloodAngels.TButton')
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сохранения
        save_button = ttk.Button(control_frame, text="╔═══ СОХРАНИТЬ ═══╗", 
                                command=self._save_network_image,
                                style='BloodAngels.Gold.TButton')
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Информация о сети
        self.network_info_var = tk.StringVar(value="╔═══ СЕТЬ НЕ ЗАГРУЖЕНА ═══╗")
        info_label = ttk.Label(control_frame, textvariable=self.network_info_var,
                             style='BloodAngels.TLabel')
        info_label.pack(side=tk.RIGHT)
    
    def update_network(self, network):
        """Обновляет отображение сети"""
        self.network = network
        self._draw_network()
        self._update_network_info()
        # Принудительное обновление интерфейса
        self.network_canvas.draw_idle()
        if hasattr(self.parent, 'root'):
            self.parent.root.update_idletasks()
        else:
            self.parent.update_idletasks()
    
    def reset_network_display(self):
        """Сбрасывает отображение сети"""
        try:
            # Очищаем график сети
            if hasattr(self, 'network_ax'):
                self.network_ax.clear()
                self.network_ax.set_title("ТОПОЛОГИЯ СЕТИ", 
                                        fontsize=14, fontweight='bold', 
                                        color=self.theme.COLORS['text_primary'])
                self.network_ax.set_aspect('equal')
                self.network_ax.axis('off')
                
                # Добавляем заглушку
                self.network_ax.text(0.5, 0.5, "СЕТЬ НЕ ЗАГРУЖЕНА", 
                                   ha='center', va='center', 
                                   fontsize=16, fontweight='bold',
                                   color=self.theme.COLORS['text_secondary'],
                                   transform=self.network_ax.transAxes)
            
            # Сбрасываем информацию о сети
            if hasattr(self, 'network_info_var'):
                self.network_info_var.set("╔═══ СЕТЬ НЕ ЗАГРУЖЕНА ═══╗")
            
            # Сбрасываем данные сети
            self.network = None
            
            # Перерисовываем canvas
            if hasattr(self, 'network_canvas'):
                self.network_canvas.draw_idle()
                
        except Exception as e:
            print(f"Ошибка при сбросе отображения сети: {str(e)}")
    
    def _draw_network(self):
        """Отрисовывает сеть"""
        if not self.network:
            return
        
        # Очистка графика
        self.network_ax.clear()
        
        # Получение позиций узлов
        pos = {}
        node_colors = []
        node_sizes = []
        
        # Проверяем тип сети и обрабатываем соответственно
        if hasattr(self.network, 'nodes') and isinstance(self.network.nodes, dict):
            # SystemModel: nodes это словарь {id: Node}
            for node_id, node in self.network.nodes.items():
                pos[node_id] = (node.x, node.y)
                
                # Цвет узла зависит от надежности (в стиле Кровавых Ангелов)
                if node.reliability >= 0.95:
                    node_colors.append(self.theme.COLORS['success'])
                elif node.reliability >= 0.9:
                    node_colors.append(self.theme.COLORS['primary_gold'])
                elif node.reliability >= 0.8:
                    node_colors.append(self.theme.COLORS['warning'])
                else:
                    node_colors.append(self.theme.COLORS['danger'])
                
                # Размер узла зависит от пропускной способности
                size = max(50, node.capacity / 10)
                node_sizes.append(size)
        elif hasattr(self.network, 'nodes') and isinstance(self.network.nodes, list):
            # NetworkModel: nodes это список NetworkNode
            for node in self.network.nodes:
                pos[node.id] = (node.x, node.y)
                
                # Цвет узла зависит от надежности (в стиле Кровавых Ангелов)
                if node.reliability >= 0.95:
                    node_colors.append(self.theme.COLORS['success'])
                elif node.reliability >= 0.9:
                    node_colors.append(self.theme.COLORS['primary_gold'])
                elif node.reliability >= 0.8:
                    node_colors.append(self.theme.COLORS['warning'])
                else:
                    node_colors.append(self.theme.COLORS['danger'])
                
                # Размер узла зависит от пропускной способности
                size = max(50, node.capacity / 10)
                node_sizes.append(size)
        else:
            print(f"[ERROR] Неподдерживаемый тип сети: {type(self.network)}")
            return
        
        # Отрисовка связей
        edge_colors = []
        edge_widths = []
        edges = []
        
        # Проверяем тип связей и обрабатываем соответственно
        if hasattr(self.network, 'links') and isinstance(self.network.links, dict):
            # SystemModel: links это словарь {(source, target): Link}
            for (source, target), link in self.network.links.items():
                edges.append((source, target))
                
                # Цвет связи зависит от надежности (в стиле Кровавых Ангелов)
                if link.reliability >= 0.95:
                    edge_colors.append(self.theme.COLORS['success'])
                elif link.reliability >= 0.9:
                    edge_colors.append(self.theme.COLORS['primary_gold'])
                elif link.reliability >= 0.8:
                    edge_colors.append(self.theme.COLORS['warning'])
                else:
                    edge_colors.append(self.theme.COLORS['danger'])
                
                # Толщина связи зависит от пропускной способности
                width = max(1, link.bandwidth / 20)
                edge_widths.append(width)
        elif hasattr(self.network, 'links') and isinstance(self.network.links, list):
            # NetworkModel: links это список NetworkLink
            for link in self.network.links:
                edges.append((link.source, link.target))
                
                # Цвет связи зависит от надежности (в стиле Кровавых Ангелов)
                if link.reliability >= 0.95:
                    edge_colors.append(self.theme.COLORS['success'])
                elif link.reliability >= 0.9:
                    edge_colors.append(self.theme.COLORS['primary_gold'])
                elif link.reliability >= 0.8:
                    edge_colors.append(self.theme.COLORS['warning'])
                else:
                    edge_colors.append(self.theme.COLORS['danger'])
                
                # Толщина связи зависит от пропускной способности
                width = max(1, link.bandwidth / 20)
                edge_widths.append(width)
        
        # Создание графа NetworkX
        G = nx.Graph()
        G.add_nodes_from(pos.keys())
        G.add_edges_from(edges)
        
        # Отрисовка графа
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, 
                              alpha=0.7, ax=self.network_ax)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, 
                              alpha=0.6, ax=self.network_ax)
        nx.draw_networkx_labels(G, pos, font_size=8, font_color='black', ax=self.network_ax)
        
        # Настройка графика
        self.network_ax.set_title("╔═══ ТОПОЛОГИЯ СЕТИ ═══╗", 
                                color=self.theme.COLORS['text_secondary'],
                                fontweight='bold', fontsize=12)
        self.network_ax.set_aspect('equal')
        
        # Включаем оси для отображения координат
        self.network_ax.set_xlabel("X координата", color=self.theme.COLORS['text_primary'])
        self.network_ax.set_ylabel("Y координата", color=self.theme.COLORS['text_primary'])
        self.network_ax.tick_params(colors=self.theme.COLORS['text_primary'])
        
        # Добавление легенды
        self._add_legend()
        
        # Обновление canvas
        self.network_canvas.draw()
        self.network_canvas.flush_events()
    
    def _add_legend(self):
        """Добавляет легенду к графику"""
        # Легенда для узлов
        node_legend = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Высокая надежность (≥95%)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markersize=8, label='Хорошая надежность (90-95%)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=8, label='Средняя надежность (80-90%)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Низкая надежность (<80%)')
        ]
        
        # Легенда для связей
        edge_legend = [
            plt.Line2D([0], [0], color='green', linewidth=3, label='Высокая надежность связи'),
            plt.Line2D([0], [0], color='yellow', linewidth=3, label='Хорошая надежность связи'),
            plt.Line2D([0], [0], color='orange', linewidth=3, label='Средняя надежность связи'),
            plt.Line2D([0], [0], color='red', linewidth=3, label='Низкая надежность связи')
        ]
        
        # Объединение легенд
        all_legend = node_legend + edge_legend
        
        # Добавление легенды
        self.network_ax.legend(handles=all_legend, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    def _update_network_info(self):
        """Обновляет информацию о сети"""
        if not self.network:
            self.network_info_var.set("Сеть не загружена")
            return
        
        # Проверяем тип сети и получаем метрики соответственно
        if hasattr(self.network, 'get_network_metrics'):
            # NetworkModel
            metrics = self.network.get_network_metrics()
            nodes_count = metrics.get('nodes_count', 0)
            links_count = metrics.get('links_count', 0)
            density = metrics.get('density', 0)
        else:
            # SystemModel
            nodes_count = len(self.network.nodes) if hasattr(self.network, 'nodes') else 0
            links_count = len(self.network.links) if hasattr(self.network, 'links') else 0
            density = 0.0  # Для SystemModel плотность не вычисляется
        
        info_text = f"Узлы: {nodes_count}, Связи: {links_count}, Плотность: {density:.2f}"
        self.network_info_var.set(info_text)
    
    def _refresh_network(self):
        """Обновляет отображение сети"""
        if self.network:
            self._draw_network()
    
    def _save_network_image(self):
        """Сохраняет изображение сети"""
        if not self.network:
            return
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            title="Сохранить изображение сети",
            defaultextension=".png",
            filetypes=[("PNG файлы", "*.png"), ("PDF файлы", "*.pdf"), ("SVG файлы", "*.svg")]
        )
        
        if filename:
            try:
                self.network_fig.savefig(filename, dpi=300, bbox_inches='tight')
                self.parent.status_var.set(f"Изображение сохранено: {filename}")
            except Exception as e:
                tk.messagebox.showerror("Ошибка", f"Не удалось сохранить изображение: {str(e)}")
    
    def highlight_path(self, path):
        """Подсвечивает путь в сети"""
        if not self.network or not path:
            return
        
        # Очистка графика
        self.network_ax.clear()
        
        # Отрисовка обычной сети
        self._draw_network()
        
        # Подсветка пути
        if len(path) > 1:
            # Подсветка узлов пути
            pos = {node.id: (node.x, node.y) for node in self.network.nodes}
            
            path_nodes = path
            path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            
            # Отрисовка подсвеченного пути
            nx.draw_networkx_nodes(self.network.graph, pos, nodelist=path_nodes, 
                                  node_color='blue', node_size=200, alpha=0.8, ax=self.network_ax)
            nx.draw_networkx_edges(self.network.graph, pos, edgelist=path_edges, 
                                  edge_color='blue', width=4, alpha=0.8, ax=self.network_ax)
        
        # Обновление canvas
        self.network_canvas.draw()
    
    def clear_highlight(self):
        """Убирает подсветку пути"""
        if self.network:
            self._draw_network()
    
    def _show_default_prompt(self):
        """Показывает промпт по умолчанию когда сеть не загружена"""
        self.network_ax.clear()
        self.network_ax.set_title("╔═══ ТОПОЛОГИЯ СЕТИ ═══╗", 
                                color=self.theme.COLORS['text_secondary'],
                                fontweight='bold', fontsize=12)
        
        # Отключаем оси
        self.network_ax.set_xticks([])
        self.network_ax.set_yticks([])
        
        # Добавляем промпт
        self.network_ax.text(0.5, 0.5, "Создайте систему для отображения", 
                           transform=self.network_ax.transAxes,
                           ha='center', va='center',
                           color=self.theme.COLORS['primary_gold'],
                           fontsize=16, fontweight='bold')
        
        self.network_canvas.draw()
    
    def _open_network_dialog(self):
        """Открывает диалог создания/загрузки сети"""
        try:
            dialog = NetworkDialog(self.parent.root, self.db_manager)
            result = dialog.show()
            
            if result and result['network']:
                self.update_network(result['network'])
                self.parent.status_var.set("╔═══ СЕТЬ ЗАГРУЖЕНА ═══╗")
                
                # Обновляем симулятор если он есть
                if hasattr(self.parent, 'simulator') and self.parent.simulator:
                    self.parent.simulator.network = result['network']
                    
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Не удалось открыть диалог сети: {str(e)}")
    
    def save_current_network(self, name: str, description: str = "") -> bool:
        """Сохраняет текущую сеть в базу данных"""
        if not self.network:
            return False
        
        try:
            self.db_manager.save_network(self.network, name, description)
            return True
        except Exception as e:
            tk.messagebox.showerror("Ошибка", f"Не удалось сохранить сеть: {str(e)}")
            return False

