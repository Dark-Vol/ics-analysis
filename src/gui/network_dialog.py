#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диалог для создания и выбора сетей
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from typing import Optional, Callable
from ..models.network_model import NetworkModel, NetworkNode, NetworkLink
from ..database.database_manager import DatabaseManager
from .themes.blood_angels_theme import BloodAngelsTheme
from .network_details_window import NetworkDetailsWindow

class NetworkDialog:
    """Диалог для создания и выбора сетей"""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        self.parent = parent
        self.db_manager = db_manager
        self.result = None
        self.theme = BloodAngelsTheme()
        
        # Создание диалогового окна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("╔═══ УПРАВЛЕНИЕ СЕТЯМИ ═══╗")
        self.dialog.geometry("600x500")
        self.dialog.configure(bg=self.theme.COLORS['bg_primary'])
        
        # Центрирование окна
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Создание интерфейса
        self._create_widgets()
        self._load_saved_networks()
        
        # Фокус на диалоге
        self.dialog.focus_set()
    
    def _create_widgets(self):
        """Создает виджеты диалога"""
        # Основной фрейм
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = tk.Label(main_frame,
                             text="╔═══ УПРАВЛІННЯ МЕРЕЖАМИ ═══╗",
                             bg=self.theme.COLORS['bg_primary'],
                             fg=self.theme.COLORS['text_secondary'],
                             font=self.theme.FONTS['military'])
        title_label.pack(pady=(0, 20))
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка "Создать новую сеть"
        self._create_new_network_tab()
        
        # Вкладка "Выбрать сохраненную сеть"
        self._create_load_network_tab()
    
    def _create_new_network_tab(self):
        """Создает вкладку для создания новой сети"""
        new_frame = ttk.Frame(self.notebook)
        self.notebook.add(new_frame, text="Створити мережу")
        
        # Параметры сети
        params_frame = ttk.LabelFrame(new_frame, text="Параметри мережі", padding=10)
        params_frame.pack(fill=tk.X, pady=10)
        
        # Количество узлов
        tk.Label(params_frame, text="Кількість вузлів:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nodes_var = tk.IntVar(value=10)
        nodes_spinbox = ttk.Spinbox(params_frame, from_=3, to=50, textvariable=self.nodes_var)
        nodes_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Вероятность соединения
        tk.Label(params_frame, text="Ймовірність з'єднання:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.connection_prob_var = tk.DoubleVar(value=0.3)
        prob_scale = ttk.Scale(params_frame, from_=0.1, to=1.0, variable=self.connection_prob_var, orient=tk.HORIZONTAL)
        prob_scale.grid(row=1, column=1, sticky=tk.W+tk.E, padx=(10, 0), pady=5)
        
        # Дисплей вероятности
        self.prob_label = tk.Label(params_frame, text="0.3")
        self.prob_label.grid(row=1, column=2, padx=(10, 0), pady=5)
        prob_scale.configure(command=lambda v: self.prob_label.configure(text=f"{float(v):.2f}"))
        
        # Время анализа сети
        tk.Label(params_frame, text="Час аналізу (сек):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.analysis_time_var = tk.IntVar(value=300)  # 5 минут по умолчанию
        time_spinbox = ttk.Spinbox(params_frame, from_=30, to=3600, textvariable=self.analysis_time_var, width=10)
        time_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Подсказка для времени анализа
        time_hint_label = tk.Label(params_frame, text="(30 сек - 1 час)", font=("Arial", 8), fg="gray")
        time_hint_label.grid(row=2, column=2, padx=(10, 0), pady=5)
        
        # Настройки узлов
        nodes_frame = ttk.LabelFrame(new_frame, text="Настройки узлов", padding=10)
        nodes_frame.pack(fill=tk.X, pady=10)
        
        # Пропускная способность узлов
        tk.Label(nodes_frame, text="Пропускная способность (Мбит/с):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.node_capacity_var = tk.StringVar(value="100-1000")
        capacity_entry = ttk.Entry(nodes_frame, textvariable=self.node_capacity_var, width=15)
        capacity_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Надежность узлов
        tk.Label(nodes_frame, text="Надежность:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.node_reliability_var = tk.StringVar(value="0.9-0.99")
        reliability_entry = ttk.Entry(nodes_frame, textvariable=self.node_reliability_var, width=15)
        reliability_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Настройки связей
        links_frame = ttk.LabelFrame(new_frame, text="Настройки связей", padding=10)
        links_frame.pack(fill=tk.X, pady=10)
        
        # Пропускная способность связей
        tk.Label(links_frame, text="Пропускная способность (Мбит/с):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.link_bandwidth_var = tk.StringVar(value="10-100")
        bandwidth_entry = ttk.Entry(links_frame, textvariable=self.link_bandwidth_var, width=15)
        bandwidth_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Надежность связей
        tk.Label(links_frame, text="Надежность:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.link_reliability_var = tk.StringVar(value="0.85-0.98")
        link_reliability_entry = ttk.Entry(links_frame, textvariable=self.link_reliability_var, width=15)
        link_reliability_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Кнопка создания сети
        create_button = ttk.Button(new_frame, text="╔═══ СОЗДАТЬ СЕТЬ ═══╗",
                                 command=self._create_network)
        create_button.pack(pady=20)
    
    def _create_load_network_tab(self):
        """Создает вкладку для загрузки сохраненных сетей"""
        load_frame = ttk.Frame(self.notebook)
        self.notebook.add(load_frame, text="Загрузить сеть")
        
        # Список сохраненных сетей
        list_frame = ttk.LabelFrame(load_frame, text="Сохраненные сети", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview для списка сетей
        columns = ('name', 'description', 'created_at')
        self.networks_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        # Настройка колонок
        self.networks_tree.heading('name', text='Имя сети')
        self.networks_tree.heading('description', text='Описание')
        self.networks_tree.heading('created_at', text='Создано')
        
        self.networks_tree.column('name', width=150)
        self.networks_tree.column('description', width=200)
        self.networks_tree.column('created_at', width=120)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.networks_tree.yview)
        self.networks_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.networks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления
        buttons_frame = ttk.Frame(load_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        load_button = ttk.Button(buttons_frame, text="╔═══ ЗАГРУЗИТЬ ═══╗",
                               command=self._load_selected_network)
        load_button.pack(side=tk.LEFT, padx=(0, 5))
        
        details_button = ttk.Button(buttons_frame, text="╔═══ ДЕТАЛИ ═══╗",
                                  command=self._show_network_details)
        details_button.pack(side=tk.LEFT, padx=5)
        
        delete_button = ttk.Button(buttons_frame, text="╔═══ УДАЛИТЬ ═══╗",
                                 command=self._delete_selected_network)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(buttons_frame, text="╔═══ ОБНОВИТЬ ═══╗",
                                  command=self._load_saved_networks)
        refresh_button.pack(side=tk.RIGHT)
    
    def _create_network(self):
        """Создает новую сеть"""
        try:
            # Получение параметров
            nodes_count = self.nodes_var.get()
            connection_prob = self.connection_prob_var.get()
            analysis_time = self.analysis_time_var.get()
            
            # Парсинг диапазонов для узлов
            node_capacity_range = self._parse_range(self.node_capacity_var.get())
            node_reliability_range = self._parse_range(self.node_reliability_var.get())
            
            # Парсинг диапазонов для связей
            link_bandwidth_range = self._parse_range(self.link_bandwidth_var.get())
            link_reliability_range = self._parse_range(self.link_reliability_var.get())
            
            # Создание сети
            network = self._generate_custom_network(
                nodes_count, connection_prob,
                node_capacity_range, node_reliability_range,
                link_bandwidth_range, link_reliability_range
            )
            
            # Диалог сохранения
            self._save_network_dialog(network, analysis_time)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать сеть: {str(e)}")
    
    def _parse_range(self, range_str: str) -> tuple:
        """Парсит диапазон вида 'min-max'"""
        try:
            parts = range_str.split('-')
            if len(parts) == 2:
                return (float(parts[0]), float(parts[1]))
            else:
                value = float(range_str)
                return (value, value)
        except ValueError:
            raise ValueError(f"Неверный формат диапазона: {range_str}")
    
    def _generate_custom_network(self, nodes_count: int, connection_prob: float,
                               node_capacity_range: tuple, node_reliability_range: tuple,
                               link_bandwidth_range: tuple, link_reliability_range: tuple) -> NetworkModel:
        """Генерирует сеть с пользовательскими параметрами"""
        # Создание узлов
        nodes = []
        for i in range(nodes_count):
            node = NetworkNode(
                id=i,
                x=np.random.uniform(0, 100),
                y=np.random.uniform(0, 100),
                capacity=np.random.uniform(node_capacity_range[0], node_capacity_range[1]),
                reliability=np.random.uniform(node_reliability_range[0], node_reliability_range[1]),
                processing_delay=np.random.uniform(1, 10)
            )
            nodes.append(node)
        
        # Создание связей
        links = []
        for i in range(nodes_count):
            for j in range(i + 1, nodes_count):
                if np.random.random() < connection_prob:
                    distance = np.sqrt(
                        (nodes[i].x - nodes[j].x)**2 + 
                        (nodes[i].y - nodes[j].y)**2
                    )
                    
                    link = NetworkLink(
                        source=i,
                        target=j,
                        bandwidth=np.random.uniform(link_bandwidth_range[0], link_bandwidth_range[1]),
                        latency=distance * 0.1 + np.random.uniform(1, 5),
                        reliability=np.random.uniform(link_reliability_range[0], link_reliability_range[1]),
                        distance=distance
                    )
                    links.append(link)
        
        # Создание объекта NetworkModel
        network = NetworkModel.__new__(NetworkModel)
        network.nodes = nodes
        network.links = links
        network.graph = self._build_graph(nodes, links)
        
        return network
    
    def _build_graph(self, nodes, links):
        """Строит граф из узлов и связей"""
        import networkx as nx
        from dataclasses import asdict
        
        graph = nx.Graph()
        
        # Добавляем узлы
        for node in nodes:
            graph.add_node(node.id, **asdict(node))
        
        # Добавляем связи
        for link in links:
            graph.add_edge(link.source, link.target, **asdict(link))
        
        return graph
    
    def _save_network_dialog(self, network: NetworkModel, analysis_time: int = 300):
        """Показывает диалог сохранения сети"""
        save_dialog = tk.Toplevel(self.dialog)
        save_dialog.title("Сохранить сеть")
        save_dialog.geometry("400x200")
        save_dialog.configure(bg=self.theme.COLORS['bg_primary'])
        save_dialog.transient(self.dialog)
        save_dialog.grab_set()
        
        # Поля ввода
        tk.Label(save_dialog, text="Имя сети:", bg=self.theme.COLORS['bg_primary']).pack(pady=5)
        name_entry = ttk.Entry(save_dialog, width=30)
        name_entry.pack(pady=5)
        
        tk.Label(save_dialog, text="Описание:", bg=self.theme.COLORS['bg_primary']).pack(pady=5)
        desc_entry = ttk.Entry(save_dialog, width=30)
        desc_entry.pack(pady=5)
        
        def save_and_close():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите имя сети")
                return
            
            try:
                network_id = self.db_manager.save_network(network, name, desc_entry.get(), analysis_time)
                self.result = {
                    'action': 'created', 
                    'network': network, 
                    'network_id': network_id,
                    'analysis_time': analysis_time
                }
                save_dialog.destroy()
                self.dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить сеть: {str(e)}")
        
        # Кнопки
        buttons_frame = ttk.Frame(save_dialog)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить", command=save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=save_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Фокус на поле имени
        name_entry.focus_set()
    
    def _load_saved_networks(self):
        """Загружает список сохраненных сетей"""
        try:
            # Очистка дерева
            for item in self.networks_tree.get_children():
                self.networks_tree.delete(item)
            
            # Загрузка сетей
            networks = self.db_manager.get_all_networks()
            for network in networks:
                self.networks_tree.insert('', tk.END, values=(
                    network['name'],
                    network['description'],
                    network['created_at'][:19]  # Обрезаем до секунд
                ), tags=(network['id'],))
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список сетей: {str(e)}")
    
    def _load_selected_network(self):
        """Загружает выбранную сеть"""
        selection = self.networks_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сеть для загрузки")
            return
        
        try:
            item = self.networks_tree.item(selection[0])
            network_id = int(item['tags'][0])
            
            # Получаем данные сети с анализом времени
            network_data = self.db_manager.get_network(network_id)
            if network_data:
                network = self.db_manager.load_network(network_id)
                if network:
                    # Используем сохраненное время анализа
                    saved_analysis_time = network_data.get('analysis_time', 300)
                    self.result = {
                        'action': 'loaded', 
                        'network': network, 
                        'network_id': network_id,
                        'analysis_time': saved_analysis_time
                    }
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить сеть")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сеть: {str(e)}")
    
    def _delete_selected_network(self):
        """Удаляет выбранную сеть"""
        selection = self.networks_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сеть для удаления")
            return
        
        try:
            item = self.networks_tree.item(selection[0])
            network_name = item['values'][0]
            network_id = int(item['tags'][0])
            
            if messagebox.askyesno("Подтверждение", f"Удалить сеть '{network_name}'?"):
                if self.db_manager.delete_network(network_id):
                    self._load_saved_networks()
                    messagebox.showinfo("Успех", "Сеть удалена")
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить сеть")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить сеть: {str(e)}")
    
    def _show_network_details(self):
        """Показывает детали выбранной сети"""
        selection = self.networks_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сеть для просмотра деталей")
            return
        
        try:
            item = self.networks_tree.item(selection[0])
            network_id = int(item['tags'][0])
            
            # Открываем окно деталей
            details_window = NetworkDetailsWindow(self.dialog, self.db_manager, network_id)
            details_window.show()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть детали сети: {str(e)}")
    
    def show(self) -> Optional[dict]:
        """Показывает диалог и возвращает результат"""
        self.dialog.wait_window()
        return self.result

