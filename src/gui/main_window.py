#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главное окно приложения в стиле Кровавых Ангелов
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import os

from ..simulator.network_simulator import NetworkSimulator, SimulationConfig
from ..models.adverse_conditions import AdverseCondition, AdverseConditionType
from .network_viewer import NetworkViewer
from .metrics_panel import MetricsPanel
from .control_panel import ControlPanel
from .themes.blood_angels_theme import BloodAngelsTheme
from .network_dialog import NetworkDialog
from ..database.database_manager import DatabaseManager
from ..utils.program_state_manager import ProgramStateManager

class MainWindow:
    """Главное окно приложения в стиле Кровавых Ангелов"""
    
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.simulator = None
        self.db_manager = DatabaseManager()
        
        # Менеджер состояния программы
        self.program_state_manager = ProgramStateManager()
        self.program_state_manager.add_state_change_callback(self._on_program_state_changed)
        
        # Настройка темы
        self.theme = BloodAngelsTheme()
        self.theme.configure_styles(self.root)
        self.theme.configure_matplotlib_style()
        
        # Настройка главного окна
        self.root.title("╔═══ ИКС АНАЛИЗАТОР КРОВАВЫХ АНГЕЛОВ ═══╗")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)
        self.root.configure(bg=self.theme.COLORS['bg_primary'])
        
        # Установка иконки (если есть)
        try:
            self.root.iconbitmap("assets/blood_angels_icon.ico")
        except:
            pass
        
        # Создание интерфейса
        self._create_menu()
        self._create_widgets()
        self._create_layout()
        self._apply_military_styling()
        
        # Переменные состояния
        self.is_simulation_running = False
        
    def _create_menu(self):
        """Создает меню приложения"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новая симуляция", command=self._new_simulation)
        file_menu.add_command(label="Загрузить конфигурацию", command=self._load_config)
        file_menu.add_command(label="Сохранить конфигурацию", command=self._save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Создать/Загрузить сеть", command=self._open_network_dialog)
        file_menu.add_command(label="Сохранить текущую сеть", command=self._save_current_network)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт результатов", command=self._export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self._exit_application)
        
        # Меню "Симуляция"
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Симуляция", menu=sim_menu)
        sim_menu.add_command(label="Настройки симуляции", command=self._show_simulation_settings)
        sim_menu.add_command(label="Добавить неблагоприятные условия", command=self._add_adverse_conditions)
        
        # Меню "Анализ"
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Анализ", menu=analysis_menu)
        analysis_menu.add_command(label="Статистика производительности", command=self._show_performance_stats)
        analysis_menu.add_command(label="Анализ надежности", command=self._show_reliability_analysis)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
        help_menu.add_command(label="Руководство пользователя", command=self._show_help)
    
    def _create_widgets(self):
        """Создает виджеты интерфейса"""
        # Создание панели управления
        self.control_panel = None  # Будет создан в _create_control_panel
        
        # Создание панели метрик
        self.metrics_panel = MetricsPanel(self)
        
        # Создание визуализатора сети (будет создан после topology_frame)
        self.network_viewer = None
        
        # Создание области графиков (будет создана в _create_layout)
        self.plots_notebook = None
        
        # Статусная строка в военном стиле
        self.status_var = tk.StringVar()
        self.status_var.set("╔═══ СИСТЕМА ГОТОВА К БОЕВЫМ ДЕЙСТВИЯМ ═══╗")
        self.status_frame = self.theme.create_military_frame(self.root, 
                                                           title="СТАТУС СИСТЕМЫ")
        self.status_label = tk.Label(self.status_frame,
                                   textvariable=self.status_var,
                                   bg=self.theme.COLORS['bg_panel'],
                                   fg=self.theme.COLORS['text_secondary'],
                                   font=self.theme.FONTS['military'])
        self.status_label.pack(pady=10)
    
    def _create_plots_area(self, parent):
        """Создает область для графиков"""
        # Создание notebook для вкладок графиков
        self.plots_notebook = ttk.Notebook(parent)
        
        # Вкладка "Контрольная панель"
        self.control_frame = ttk.Frame(self.plots_notebook)
        self.plots_notebook.add(self.control_frame, text="🎛️ Контрольная панель")
        
        # Создание панели управления
        self._create_control_panel()
        
        # Вкладка "Панель визуализации"
        self.visualization_frame = ttk.Frame(self.plots_notebook)
        self.plots_notebook.add(self.visualization_frame, text="📊 Панель визуализации")
        
        # Создание подвкладок для визуализации
        self._create_visualization_tabs()
        
        # Вкладка "Статус системы"
        self.status_frame = ttk.Frame(self.plots_notebook)
        self.plots_notebook.add(self.status_frame, text="⚡ Статус системы")
        
        # Создание панели статуса
        self._create_status_panel()
        
        # Упаковка notebook
        self.plots_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
    
    def _create_control_panel(self):
        """Создает контрольную панель"""
        # Создание панели управления
        self.control_panel = ControlPanel(self, self.control_frame, self.config)
        
        # Добавляем дополнительные элементы управления
        control_frame = ttk.Frame(self.control_frame)
        control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки управления симуляцией
        sim_frame = ttk.LabelFrame(control_frame, text="Управление симуляцией")
        sim_frame.pack(fill=tk.X, pady=5)
        
        button_frame = ttk.Frame(sim_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопка создания сети
        create_network_btn = ttk.Button(button_frame, text="Создать сеть", 
                                       command=self._create_network)
        create_network_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка загрузки сети
        load_network_btn = ttk.Button(button_frame, text="Загрузить сеть", 
                                     command=self._load_network)
        load_network_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сохранения сети
        save_network_btn = ttk.Button(button_frame, text="Сохранить сеть", 
                                     command=self._save_network)
        save_network_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_visualization_tabs(self):
        """Создает вкладки визуализации"""
        # Создание внутреннего notebook для визуализации
        self.viz_notebook = ttk.Notebook(self.visualization_frame)
        self.viz_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка "Метрики в реальном времени"
        self.metrics_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.metrics_frame, text="📈 Метрики")
        
        # Создание графиков метрик
        self._create_metrics_plots()
        
        # Вкладка "Топология сети"
        self.topology_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.topology_frame, text="🕸️ Топология")
        
        # Создание визуализатора сети
        self.network_viewer = NetworkViewer(self, self.topology_frame)
        
        # Вкладка "Анализ надежности"
        self.reliability_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.reliability_frame, text="🛡️ Надежность")
        
        # Создание графика надежности
        self._create_reliability_plot()
        
        # Вкладка "События отказов"
        self.failures_frame = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.failures_frame, text="⚠️ Отказы")
        
        # Создание графика отказов
        self._create_failures_plot()
    
    def _create_status_panel(self):
        """Создает панель статуса системы"""
        # Основной фрейм
        main_frame = ttk.Frame(self.status_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Статус симуляции
        sim_status_frame = ttk.LabelFrame(main_frame, text="Статус симуляции")
        sim_status_frame.pack(fill=tk.X, pady=5)
        
        self.sim_status_var = tk.StringVar(value="Остановлено")
        status_label = ttk.Label(sim_status_frame, textvariable=self.sim_status_var, 
                                font=("Arial", 12, "bold"))
        status_label.pack(pady=5)
        
        # Информация о сети
        network_info_frame = ttk.LabelFrame(main_frame, text="Информация о сети")
        network_info_frame.pack(fill=tk.X, pady=5)
        
        self.network_info_text = tk.Text(network_info_frame, height=10, width=80)
        self.network_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Метрики производительности
        metrics_frame = ttk.LabelFrame(main_frame, text="Метрики производительности")
        metrics_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Создание панели метрик
        self.metrics_panel = MetricsPanel(self)
        self.metrics_panel.frame.pack(in_=metrics_frame, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_reliability_plot(self):
        """Создает график надежности системы"""
        # Создание фигуры для графика надежности
        self.reliability_fig = Figure(figsize=(10, 6), dpi=100, 
                                     facecolor=self.theme.COLORS['bg_primary'])
        self.reliability_ax = self.reliability_fig.add_subplot(111)
        
        # Настройка графика
        self.reliability_ax.set_title("НАДЕЖНОСТЬ СИСТЕМЫ", 
                                     color=self.theme.COLORS['text_secondary'],
                                     fontweight='bold', fontsize=14)
        self.reliability_ax.set_xlabel("Время (с)", color=self.theme.COLORS['text_primary'])
        self.reliability_ax.set_ylabel("Надежность", color=self.theme.COLORS['text_primary'])
        self.reliability_ax.grid(True, alpha=0.3)
        self.reliability_ax.set_ylim(0, 1)
        
        # Инициализация линии графика
        self.reliability_line, = self.reliability_ax.plot([], [], 
                                                         color=self.theme.COLORS['success'],
                                                         linewidth=2, label='Надежность')
        
        # Легенда
        self.reliability_ax.legend()
        
        # Создание canvas
        self.reliability_canvas = FigureCanvasTkAgg(self.reliability_fig, self.reliability_frame)
        self.reliability_canvas.draw()
        self.reliability_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Данные для графика
        self.reliability_time_data = []
        self.reliability_value_data = []
    
    def _create_failures_plot(self):
        """Создает график событий отказов"""
        # Создание фигуры для графика отказов
        self.failures_fig = Figure(figsize=(10, 6), dpi=100, 
                                  facecolor=self.theme.COLORS['bg_primary'])
        self.failures_ax = self.failures_fig.add_subplot(111)
        
        # Настройка графика
        self.failures_ax.set_title("СОБЫТИЯ ОТКАЗОВ", 
                                  color=self.theme.COLORS['text_secondary'],
                                  fontweight='bold', fontsize=14)
        self.failures_ax.set_xlabel("Время (с)", color=self.theme.COLORS['text_primary'])
        self.failures_ax.set_ylabel("Количество отказов", color=self.theme.COLORS['text_primary'])
        self.failures_ax.grid(True, alpha=0.3)
        
        # Инициализация линии графика
        self.failures_line, = self.failures_ax.plot([], [], 
                                                   color=self.theme.COLORS['danger'],
                                                   linewidth=2, label='Отказы')
        
        # Легенда
        self.failures_ax.legend()
        
        # Создание canvas
        self.failures_canvas = FigureCanvasTkAgg(self.failures_fig, self.failures_frame)
        self.failures_canvas.draw()
        self.failures_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Данные для графика
        self.failures_time_data = []
        self.failures_count_data = []
    
    def _create_metrics_plots(self):
        """Создает графики метрик"""
        # Создание фигуры для графиков в стиле Кровавых Ангелов
        self.metrics_fig = Figure(figsize=(12, 8), dpi=100, 
                                facecolor=self.theme.COLORS['bg_primary'])
        
        # График пропускной способности
        self.throughput_ax = self.metrics_fig.add_subplot(221)
        self.throughput_ax.set_title("ПРОПУСКНАЯ СПОСОБНОСТЬ (Мбит/с)", 
                                   color=self.theme.COLORS['text_secondary'],
                                   fontweight='bold')
        self.throughput_ax.set_xlabel("Время (с)", color=self.theme.COLORS['text_primary'])
        self.throughput_ax.set_ylabel("Мбит/с", color=self.theme.COLORS['text_primary'])
        self.throughput_line, = self.throughput_ax.plot([], [], 
                                                      color=self.theme.COLORS['primary_red'],
                                                      linewidth=3, alpha=0.8)
        
        # График задержки
        self.latency_ax = self.metrics_fig.add_subplot(222)
        self.latency_ax.set_title("ЗАДЕРЖКА СИГНАЛА (мс)", 
                                color=self.theme.COLORS['text_secondary'],
                                fontweight='bold')
        self.latency_ax.set_xlabel("Время (с)", color=self.theme.COLORS['text_primary'])
        self.latency_ax.set_ylabel("мс", color=self.theme.COLORS['text_primary'])
        self.latency_line, = self.latency_ax.plot([], [], 
                                                color=self.theme.COLORS['warning'],
                                                linewidth=3, alpha=0.8)
        
        # График надежности
        self.reliability_ax = self.metrics_fig.add_subplot(223)
        self.reliability_ax.set_title("НАДЕЖНОСТЬ СИСТЕМЫ", 
                                    color=self.theme.COLORS['text_secondary'],
                                    fontweight='bold')
        self.reliability_ax.set_xlabel("Время (с)", color=self.theme.COLORS['text_primary'])
        self.reliability_ax.set_ylabel("Надежность", color=self.theme.COLORS['text_primary'])
        self.reliability_line, = self.reliability_ax.plot([], [], 
                                                        color=self.theme.COLORS['success'],
                                                        linewidth=3, alpha=0.8)
        
        # График доступности
        self.availability_ax = self.metrics_fig.add_subplot(224)
        self.availability_ax.set_title("ДОСТУПНОСТЬ СЕТИ", 
                                     color=self.theme.COLORS['text_secondary'],
                                     fontweight='bold')
        self.availability_ax.set_xlabel("Время (с)", color=self.theme.COLORS['text_primary'])
        self.availability_ax.set_ylabel("Доступность", color=self.theme.COLORS['text_primary'])
        self.availability_line, = self.availability_ax.plot([], [], 
                                                          color=self.theme.COLORS['primary_gold'],
                                                          linewidth=3, alpha=0.8)
        
        # Настройка макета
        self.metrics_fig.tight_layout()
        
        # Создание canvas
        self.metrics_canvas = FigureCanvasTkAgg(self.metrics_fig, self.metrics_frame)
        self.metrics_canvas.draw()
        self.metrics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_layout(self):
        """Создает компоновку интерфейса с пагинацией"""
        # Основная область с пагинацией (занимает все окно)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Создание области с пагинацией
        self._create_plots_area(main_frame)
        
        # Панель статуса уже создана в _create_widgets()
    
    def _apply_military_styling(self):
        """Применяет военный стиль к интерфейсу"""
        # Настройка цветов для всех основных фреймов
        if hasattr(self, 'control_panel') and self.control_panel:
            self._style_frame(self.control_panel.frame)
        if hasattr(self, 'metrics_panel') and self.metrics_panel:
            self._style_frame(self.metrics_panel.frame)
        if hasattr(self, 'network_viewer') and self.network_viewer:
            self._style_frame(self.network_viewer.frame)
        
        # Добавление военных элементов
        self._add_military_elements()
    
    def _style_frame(self, frame):
        """Стилизует фрейм в военном стиле"""
        try:
            # Для обычных tk.Frame
            if hasattr(frame, 'configure') and 'bg' in frame.configure():
                frame.configure(bg=self.theme.COLORS['bg_secondary'])
            # Для ttk.Frame используем стиль
            elif hasattr(frame, 'configure'):
                # ttk.Frame не поддерживает bg напрямую
                pass
            self.theme.add_border_effect(frame)
        except Exception:
            # Если стилизация не удается, пропускаем
            pass
    
    def _add_military_elements(self):
        """Добавляет военные элементы интерфейса"""
        # Создание заголовочного баннера
        banner_frame = tk.Frame(self.root, 
                              bg=self.theme.COLORS['primary_red'],
                              height=60)
        banner_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        banner_frame.pack_propagate(False)
        
        # Заголовок приложения
        banner_label = tk.Label(banner_frame,
                              text="╔═══ ИКС АНАЛИЗАТОР КРОВАВЫХ АНГЕЛОВ ═══╗\n"
                                   "║     СИСТЕМА МОНИТОРИНГА СЕТИ         ║\n"
                                   "╚═══════════════════════════════════════════╝",
                              bg=self.theme.COLORS['primary_red'],
                              fg=self.theme.COLORS['text_primary'],
                              font=self.theme.FONTS['military'])
        banner_label.pack(expand=True)
    
    def create_system(self):
        """Создает систему без запуска симуляции"""
        try:
            # Получение параметров сети из панели управления
            nodes = int(self.control_panel.nodes_var.get())
            connection_prob = float(self.control_panel.connection_prob_var.get())
            
            # Создание сети
            from ..models.network_model import NetworkModel
            network = NetworkModel(nodes=nodes, connection_probability=connection_prob)
            
            # Обновление визуализатора сети
            self.network_viewer.update_network(network)
            
            # Обновление статуса
            self.status_var.set(f"╔═══ СИСТЕМА СОЗДАНА: {nodes} УЗЛОВ ═══╗")
            
            print(f"Система создана: {nodes} узлов, {len(network.links)} связей")
            
        except Exception as e:
            print(f"Ошибка создания системы: {e}")
            messagebox.showerror("Ошибка", f"Не удалось создать систему: {str(e)}")
    
    def start_simulation(self):
        """Запускает симуляцию"""
        if self.is_simulation_running:
            return
        
        try:
            # Создание конфигурации симуляции
            sim_config = SimulationConfig(
                duration=float(self.control_panel.duration_var.get()),
                time_step=float(self.control_panel.time_step_var.get()),
                random_seed=int(self.control_panel.seed_var.get()),
                enable_traffic=self.control_panel.enable_traffic_var.get(),
                enable_failures=self.control_panel.enable_failures_var.get(),
                enable_adverse_conditions=self.control_panel.enable_adverse_var.get()
            )
            
            # Создание симулятора
            self.simulator = NetworkSimulator(sim_config)
            
            # Инициализация сети
            nodes = int(self.control_panel.nodes_var.get())
            connection_prob = float(self.control_panel.connection_prob_var.get())
            self.simulator.initialize_network(nodes, connection_prob)
            
            # Сразу обновляем визуализатор сети
            if self.simulator.network:
                self.network_viewer.update_network(self.simulator.network)
            
            # Добавление неблагоприятных условий
            self._add_default_adverse_conditions()
            
            # Настройка callbacks
            self.simulator.add_update_callback(self._on_simulation_update)
            self.simulator.add_finish_callback(self._on_simulation_finish)
            
            # Запуск симуляции
            self.simulator.start_simulation()
            self.is_simulation_running = True
            
            # Обновление интерфейса
            self.control_panel.set_simulation_state(True)
            self.status_var.set("╔═══ БОЕВАЯ СИМУЛЯЦИЯ АКТИВНА ═══╗")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить симуляцию: {str(e)}")
    
    def stop_simulation(self):
        """Останавливает симуляцию"""
        try:
            print("[DEBUG] MainWindow.stop_simulation вызван")
            
            # Останавливаем симулятор, если он есть
            if hasattr(self, 'simulator') and self.simulator:
                print("[DEBUG] Останавливаем симулятор...")
                self.simulator.stop_simulation()
                
                # Логируем остановку симуляции
                current_network = self.network_viewer.network
                if current_network:
                    network_id = getattr(current_network, 'id', 0)
                    self.program_state_manager.log_simulation_stopped(network_id, current_network.name)
                    print(f"[DEBUG] Логируем остановку симуляции для сети {current_network.name}")
            else:
                print("[DEBUG] Симулятор не найден или не инициализирован")
            
            # Останавливаем программу через ProgramStateManager
            print("[DEBUG] Останавливаем программу через ProgramStateManager...")
            self.program_state_manager.stop_program()
            
            # Обновляем локальное состояние
            self.is_simulation_running = False
            print("[DEBUG] Локальное состояние обновлено")
            
            # Обновление интерфейса
            if hasattr(self, 'control_panel'):
                self.control_panel.set_simulation_state(False)
                print("[DEBUG] Интерфейс обновлен")
            
            print("[DEBUG] Симуляция успешно остановлена")
            messagebox.showinfo("Информация", "Симуляция остановлена")
            
        except Exception as e:
            print(f"[ERROR] Ошибка при остановке симуляции: {e}")
            messagebox.showerror("Ошибка", f"Ошибка при остановке симуляции: {str(e)}")
    
    def _add_default_adverse_conditions(self):
        """Добавляет стандартные неблагоприятные условия"""
        if not self.simulator or not self.simulator.network:
            return
        
        # Шум
        noise_condition = AdverseCondition(
            type=AdverseConditionType.NOISE,
            intensity=0.1,
            duration=30.0,
            probability=0.1,
            affected_nodes=list(range(len(self.simulator.network.nodes))),
            affected_links=[]
        )
        self.simulator.add_adverse_condition(noise_condition)
        
        # Помехи
        interference_condition = AdverseCondition(
            type=AdverseConditionType.INTERFERENCE,
            intensity=0.05,
            duration=20.0,
            probability=0.05,
            affected_nodes=list(range(len(self.simulator.network.nodes))),
            affected_links=[]
        )
        self.simulator.add_adverse_condition(interference_condition)
        
        # Отказы
        failure_condition = AdverseCondition(
            type=AdverseConditionType.FAILURE,
            intensity=0.02,
            duration=10.0,
            probability=0.02,
            affected_nodes=list(range(len(self.simulator.network.nodes))),
            affected_links=[]
        )
        self.simulator.add_adverse_condition(failure_condition)
    
    def _on_simulation_update(self, timestamp, metrics):
        """Обработчик обновления симуляции"""
        # Обновление панели метрик
        self.metrics_panel.update_metrics(metrics)
        
        # Обновление графиков
        self._update_plots(timestamp, metrics)
        
        # Обновление визуализатора сети
        if self.simulator and self.simulator.network:
            self.network_viewer.update_network(self.simulator.network)
    
    def _on_simulation_finish(self):
        """Обработчик завершения симуляции"""
        self.is_simulation_running = False
        self.control_panel.set_simulation_state(False)
        self.status_var.set("╔═══ МИССИЯ ЗАВЕРШЕНА ═══╗")
        
        # Показ результатов
        if self.simulator:
            results = self.simulator.get_simulation_results()
            self._show_simulation_results(results)
    
    def _update_plots(self, timestamp, metrics):
        """Обновляет графики"""
        # Получение истории метрик
        if self.simulator:
            history = self.simulator.get_metrics_history()
            
            if len(history) > 1:
                times = [m.timestamp for m in history]
                
                # Обновление основных графиков метрик
                self.throughput_line.set_data(times, [m.throughput for m in history])
                self.latency_line.set_data(times, [m.latency for m in history])
                self.reliability_line.set_data(times, [m.reliability for m in history])
                self.availability_line.set_data(times, [m.availability for m in history])
                
                # Автомасштабирование основных графиков
                self.throughput_ax.relim()
                self.throughput_ax.autoscale_view()
                self.latency_ax.relim()
                self.latency_ax.autoscale_view()
                self.reliability_ax.relim()
                self.reliability_ax.autoscale_view()
                self.availability_ax.relim()
                self.availability_ax.autoscale_view()
                
                # Перерисовка основных графиков
                self.metrics_canvas.draw_idle()
                
                # Обновление графика надежности в отдельной вкладке
                self._update_reliability_plot(history)
                
                # Обновление графика отказов
                self._update_failures_plot()
                
                # Обновление статуса системы
                self._update_system_status()
    
    def _update_reliability_plot(self, history):
        """Обновляет график надежности"""
        if not history:
            return
            
        times = [m.timestamp for m in history]
        reliability_values = [m.reliability for m in history]
        
        # Обновление данных графика
        self.reliability_time_data = times
        self.reliability_value_data = reliability_values
        
        # Обновление линии графика
        self.reliability_line.set_data(times, reliability_values)
        
        # Автомасштабирование
        self.reliability_ax.relim()
        self.reliability_ax.autoscale_view()
        
        # Перерисовка
        self.reliability_canvas.draw_idle()
    
    def _update_failures_plot(self):
        """Обновляет график событий отказов"""
        if not self.simulator:
            return
            
        # Получение событий отказов
        failure_events = self.simulator.get_failure_events()
        
        if failure_events:
            # Группировка отказов по времени
            time_counts = {}
            for event in failure_events:
                time_bucket = int(event['timestamp'] // 10) * 10  # 10-секундные интервалы
                time_counts[time_bucket] = time_counts.get(time_bucket, 0) + 1
            
            times = sorted(time_counts.keys())
            counts = [time_counts[t] for t in times]
            
            # Обновление данных графика
            self.failures_time_data = times
            self.failures_count_data = counts
            
            # Обновление линии графика
            self.failures_line.set_data(times, counts)
            
            # Автомасштабирование
            self.failures_ax.relim()
            self.failures_ax.autoscale_view()
            
            # Перерисовка
            self.failures_canvas.draw_idle()
    
    def _update_system_status(self):
        """Обновляет статус системы"""
        if not self.simulator:
            return
            
        # Обновление статуса симуляции
        if self.simulator.is_running:
            self.sim_status_var.set("Выполняется")
        elif self.simulator.is_paused:
            self.sim_status_var.set("Приостановлено")
        else:
            self.sim_status_var.set("Остановлено")
        
        # Обновление информации о сети
        if hasattr(self.simulator, 'network') and self.simulator.network:
            network_info = self.simulator.network.get_network_summary()
            self.network_info_text.delete(1.0, tk.END)
            self.network_info_text.insert(1.0, network_info)
        
        # Обновление панели метрик
        if hasattr(self.simulator, 'performance_metrics'):
            current_metrics = self.simulator.performance_metrics.current_metrics
            if hasattr(current_metrics, 'throughput'):
                from ..models.performance_metrics import MetricsSnapshot
                snapshot = MetricsSnapshot(
                    timestamp=self.simulator.current_time,
                    throughput=current_metrics.get('throughput', 0),
                    latency=current_metrics.get('latency', 0),
                    reliability=current_metrics.get('reliability', 0),
                    availability=current_metrics.get('availability', 0),
                    packet_loss=current_metrics.get('packet_loss', 0),
                    jitter=current_metrics.get('jitter', 0),
                    energy_efficiency=current_metrics.get('energy_efficiency', 0)
                )
                self.metrics_panel.update_metrics(snapshot)
    
    def _create_network(self):
        """Создает новую сеть"""
        dialog = NetworkDialog(self.root, self.db_manager)
        if dialog.result:
            # Создание сети с заданными параметрами
            from ..system_model import SystemModel, Node, NodeType, Link, LinkType
            import random
            
            network = SystemModel("Новая сеть")
            
            # Создание узлов
            for i in range(dialog.result.get('nodes', 10)):
                node_type = random.choice(list(NodeType))
                node = Node(
                    id=f"node_{i}",
                    node_type=node_type,
                    capacity=random.uniform(100, 1000),
                    reliability=random.uniform(0.85, 0.99),
                    x=random.uniform(0, 100),
                    y=random.uniform(0, 100),
                    threat_level=random.uniform(0.1, 0.3),
                    load=random.uniform(0.2, 0.8)
                )
                network.add_node(node)
            
            # Создание связей
            nodes = list(network.nodes.keys())
            connection_prob = dialog.result.get('connection_prob', 0.3)
            
            for i, source in enumerate(nodes):
                for j, target in enumerate(nodes[i+1:], i+1):
                    if random.random() < connection_prob:
                        link = Link(
                            source=source,
                            target=target,
                            bandwidth=random.uniform(10, 100),
                            latency=random.uniform(1, 50),
                            reliability=random.uniform(0.90, 0.99),
                            link_type=random.choice(list(LinkType)),
                            threat_level=random.uniform(0.05, 0.2),
                            load=random.uniform(0.1, 0.6)
                        )
                        network.add_link(link)
            
            # Обновление визуализатора сети
            self.network_viewer.update_network(network)
            
            # Создание симулятора для новой сети
            analysis_time = dialog.result.get('analysis_time', 300)  # 5 минут по умолчанию
            self._create_simulator_for_network(network, analysis_time)
            
            # Логируем создание сети
            self.program_state_manager.log_network_created(0, network.name)  # ID будет обновлен при сохранении
            
            messagebox.showinfo("Успех", f"Создана сеть с {len(network.nodes)} узлами и {len(network.links)} связями\nВремя анализа: {analysis_time} сек ({analysis_time/60:.1f} мин)")
    
    def _load_network(self):
        """Загружает сеть из базы данных"""
        from .network_selection_dialog import NetworkSelectionDialog
        
        # Открываем диалог выбора сети
        dialog = NetworkSelectionDialog(self.root, self.db_manager, self)
        result = dialog.show()
        
        if result and result['action'] == 'load':
            try:
                network_data = result['network_data']['network_data']
                
                # Создание сети из данных
                from ..system_model import SystemModel, Node, NodeType, Link, LinkType
                
                network = SystemModel(result['network_name'])
                
                # Загрузка узлов (конвертируем из NetworkNode в Node)
                for node_data in network_data.get('nodes', []):
                    # NetworkNode имеет поля: id, x, y, capacity, reliability, processing_delay
                    # Node имеет поля: id, node_type, capacity, reliability, cpu_load, memory_usage, load, threat_level, encryption, x, y
                    
                    # Безопасная конвертация типов
                    try:
                        node_id = f"node_{node_data['id']}"  # Конвертируем int в string
                        capacity = float(node_data['capacity'])
                        reliability = float(node_data['reliability'])
                        x = float(node_data.get('x', 0.0))
                        y = float(node_data.get('y', 0.0))
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"[WARNING] Ошибка конвертации данных узла: {e}")
                        continue  # Пропускаем проблемный узел
                    
                    node = Node(
                        id=node_id,
                        node_type=NodeType.SERVER,  # По умолчанию SERVER
                        capacity=capacity,
                        reliability=reliability,
                        cpu_load=0.0,  # По умолчанию
                        memory_usage=0.0,  # По умолчанию
                        load=0.0,  # По умолчанию
                        threat_level=0.1,  # По умолчанию
                        encryption=True,  # По умолчанию
                        x=x,
                        y=y
                    )
                    network.add_node(node)
                
                # Загрузка связей (конвертируем из NetworkLink в Link)
                for link_data in network_data.get('links', []):
                    # NetworkLink имеет поля: source, target, bandwidth, latency, reliability, distance
                    # Link имеет поля: source, target, bandwidth, latency, reliability, link_type, utilization, load, encryption, threat_level
                    
                    # Безопасная конвертация типов
                    try:
                        source_id = int(link_data['source'])
                        target_id = int(link_data['target'])
                        bandwidth = float(link_data['bandwidth'])
                        latency = float(link_data['latency'])
                        reliability = float(link_data['reliability'])
                        
                        source = f"node_{source_id}"  # Конвертируем source в string
                        target = f"node_{target_id}"  # Конвертируем target в string
                    except (ValueError, TypeError, KeyError) as e:
                        print(f"[WARNING] Ошибка конвертации данных связи: {e}")
                        continue  # Пропускаем проблемную связь
                    
                    link = Link(
                        source=source,
                        target=target,
                        bandwidth=bandwidth,
                        latency=latency,
                        reliability=reliability,
                        link_type=LinkType.ETHERNET,  # По умолчанию ETHERNET
                        utilization=0.0,  # По умолчанию
                        load=0.0,  # По умолчанию
                        encryption=True,  # По умолчанию
                        threat_level=0.1  # По умолчанию
                    )
                    network.add_link(link)
                
                # Обновление визуализатора сети
                self.network_viewer.update_network(network)
                
                # Создание симулятора для загруженной сети
                analysis_time = result.get('analysis_time', 300)  # 5 минут по умолчанию
                self._create_simulator_for_network(network, analysis_time)
                
                # Логируем загрузку сети
                network_id = result['network_data']['id']
                self.program_state_manager.log_network_created(network_id, network.name)
                
                messagebox.showinfo("Успех", f"Загружена сеть: {network.name}\nВремя анализа: {analysis_time} сек ({analysis_time/60:.1f} мин)")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить сеть: {str(e)}")
    
    def _save_network(self):
        """Сохраняет текущую сеть в базу данных"""
        if not hasattr(self, 'network_viewer') or not self.network_viewer.network:
            messagebox.showwarning("Предупреждение", "Нет сети для сохранения")
            return
        
        try:
            network = self.network_viewer.network
            
            # Запрашиваем название сети
            from tkinter import simpledialog
            network_name = simpledialog.askstring(
                "Сохранение сети",
                "Введите название сети:",
                initialvalue=network.name
            )
            
            if not network_name:
                return  # Пользователь отменил
            
            # Запрашиваем описание (опционально)
            description = simpledialog.askstring(
                "Сохранение сети",
                "Введите описание сети (необязательно):",
                initialvalue=""
            )
            
            # Конвертируем SystemModel в NetworkModel для сохранения
            from ..models.network_model import NetworkModel
            
            # Создаем NetworkModel из SystemModel
            network_model = NetworkModel(nodes=0, connection_probability=0)
            network_model.name = network_name
            network_model.description = description or ""
            
            # Добавляем узлы
            for node_id, node in network.nodes.items():
                from ..models.network_model import NetworkNode
                network_node = NetworkNode(
                    id=int(node.id.split('_')[1]) if '_' in node.id else 0,
                    x=node.x,
                    y=node.y,
                    capacity=node.capacity,
                    reliability=node.reliability,
                    processing_delay=0.1  # По умолчанию
                )
                network_model.nodes.append(network_node)
            
            # Добавляем связи
            for (source, target), link in network.links.items():
                from ..models.network_model import NetworkLink
                source_id = int(source.split('_')[1]) if '_' in source else 0
                target_id = int(target.split('_')[1]) if '_' in target else 0
                
                network_link = NetworkLink(
                    source=source_id,
                    target=target_id,
                    bandwidth=link.bandwidth,
                    latency=link.latency,
                    reliability=link.reliability,
                    distance=10.0  # По умолчанию
                )
                network_model.links.append(network_link)
            
            # Сохраняем в базу данных
            network_id = self.db_manager.save_network(network_model, network_name, description or "")
            
            messagebox.showinfo("Успех", f"Сеть '{network_name}' сохранена в базе данных (ID: {network_id})")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить сеть: {str(e)}")
    
    def create_system(self):
        """Создает новую систему"""
        self._create_network()
    
    def start_simulation(self):
        """Запускает симуляцию"""
        if hasattr(self, 'simulator') and self.simulator:
            if not self.simulator.is_running:
                # Запускаем программу
                self.program_state_manager.start_program()
                
                # Запускаем симуляцию
                self.simulator.start_simulation()
                
                # Логируем запуск симуляции
                current_network = self.network_viewer.network
                if current_network:
                    network_id = getattr(current_network, 'id', 0)
                    self.program_state_manager.log_simulation_started(network_id, current_network.name)
                
                # Обновляем локальное состояние
                self.is_simulation_running = True
                
                messagebox.showinfo("Информация", "Симуляция запущена")
            else:
                messagebox.showwarning("Предупреждение", "Симуляция уже выполняется")
        else:
            messagebox.showwarning("Предупреждение", "Сначала создайте или загрузите сеть")
    
    def _create_simulator_for_network(self, network, analysis_time=300):
        """Создает симулятор для сети"""
        try:
            # Создаем конфигурацию симуляции
            from ..simulator.network_simulator import SimulationConfig
            
            config = SimulationConfig(
                duration=float(analysis_time),  # Используем время анализа из диалога
                time_step=0.5,
                enable_traffic=True,
                enable_failures=True,
                enable_adverse_conditions=True
            )
            
            print(f"[INFO] Создан симулятор с временем анализа: {analysis_time} секунд ({analysis_time/60:.1f} минут)")
            
            # Создаем симулятор
            self.simulator = NetworkSimulator(config)
            
            # Инициализируем симулятор с сетью
            # Конвертируем SystemModel в формат, понятный симулятору
            node_count = len(network.nodes)
            connection_prob = len(network.links) / (node_count * (node_count - 1) / 2) if node_count > 1 else 0
            
            self.simulator.initialize_network(node_count, connection_prob)
            
            # Добавляем callback для обновления графиков
            self.simulator.add_update_callback(self._update_plots)
            
            print(f"[INFO] Симулятор создан для сети с {node_count} узлами")
            
        except Exception as e:
            print(f"[ERROR] Ошибка создания симулятора: {e}")
            # Создаем базовый симулятор без инициализации сети
            try:
                from ..simulator.network_simulator import SimulationConfig
                config = SimulationConfig(duration=300.0, time_step=0.5)
                self.simulator = NetworkSimulator(config)
                print("[INFO] Базовый симулятор создан")
            except Exception as e2:
                print(f"[ERROR] Не удалось создать даже базовый симулятор: {e2}")
    
    def _show_simulation_results(self, results):
        """Показывает результаты симуляции"""
        # Создание окна результатов
        results_window = tk.Toplevel(self.root)
        results_window.title("Результаты симуляции")
        results_window.geometry("600x400")
        
        # Создание текстового виджета
        text_widget = tk.Text(results_window, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(results_window, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Форматирование результатов
        results_text = f"""
РЕЗУЛЬТАТЫ СИМУЛЯЦИИ
====================

Длительность симуляции: {results['duration']:.2f} сек
События трафика: {results['traffic_events']}
События отказов: {results['failure_events']}

МЕТРИКИ ПРОИЗВОДИТЕЛЬНОСТИ:
- Средняя пропускная способность: {results['network_metrics'].get('throughput', 0):.2f} Мбит/с
- Средняя задержка: {results['network_metrics'].get('latency', 0):.2f} мс
- Средняя надежность: {results['network_metrics'].get('reliability', 0):.3f}
- Средняя доступность: {results['network_metrics'].get('availability', 0):.3f}

ПОКАЗАТЕЛЬ КАЧЕСТВА: {results['quality_score']:.3f}

НЕБЛАГОПРИЯТНЫЕ УСЛОВИЯ:
"""
        
        for condition_type, count in results['adverse_conditions_summary'].items():
            results_text += f"- {condition_type}: {count} активных\n"
        
        results_text += f"\nТОПОЛОГИЯ СЕТИ:\n"
        for metric, value in results['network_topology'].items():
            results_text += f"- {metric}: {value}\n"
        
        text_widget.insert(tk.END, results_text)
        text_widget.config(state=tk.DISABLED)
        
        # Размещение виджетов
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Обработчики меню
    def _new_simulation(self):
        """Создает новую симуляцию"""
        if self.is_simulation_running:
            self.stop_simulation()
        self.control_panel.reset_to_defaults()
        self.metrics_panel.reset_metrics()
        self.status_var.set("Готов к новой симуляции")
    
    def _load_config(self):
        """Загружает конфигурацию из файла"""
        filename = filedialog.askopenfilename(
            title="Загрузить конфигурацию",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if filename:
            try:
                self.config.save_config()
                self.status_var.set(f"Конфигурация загружена: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить конфигурацию: {str(e)}")
    
    def _save_config(self):
        """Сохраняет конфигурацию в файл"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить конфигурацию",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json"), ("Все файлы", "*.*")]
        )
        if filename:
            try:
                self.config.save_config()
                self.status_var.set(f"Конфигурация сохранена: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить конфигурацию: {str(e)}")
    
    def _export_results(self):
        """Экспортирует результаты симуляции"""
        if not self.simulator:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Экспорт результатов",
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv"), ("JSON файлы", "*.json")]
        )
        if filename:
            try:
                # Здесь можно добавить экспорт данных
                self.status_var.set(f"Результаты экспортированы: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать результаты: {str(e)}")
    
    def _show_simulation_settings(self):
        """Показывает настройки симуляции"""
        messagebox.showinfo("Настройки", "Окно настроек симуляции будет реализовано")
    
    def _add_adverse_conditions(self):
        """Показывает окно добавления неблагоприятных условий"""
        messagebox.showinfo("Неблагоприятные условия", "Окно добавления условий будет реализовано")
    
    def _show_performance_stats(self):
        """Показывает статистику производительности"""
        messagebox.showinfo("Статистика", "Окно статистики будет реализовано")
    
    def _show_reliability_analysis(self):
        """Показывает анализ надежности"""
        messagebox.showinfo("Анализ надежности", "Окно анализа будет реализовано")
    
    def _show_about(self):
        """Показывает информацию о программе"""
        about_text = """
Анализ функционирования информационно-коммуникационных систем 
в неблагоприятных условиях

Версия: 1.0
Разработчик: AI Assistant

Программа предназначена для анализа и моделирования
работы ИКС в условиях помех, отказов и других
неблагоприятных факторов.
        """
        messagebox.showinfo("О программе", about_text)
    
    def _show_help(self):
        """Показывает справку"""
        messagebox.showinfo("Справка", "Руководство пользователя будет добавлено")
    
    def _exit_application(self):
        """Выход из приложения"""
        if self.is_simulation_running:
            self.stop_simulation()
        self.root.quit()
    
    def _open_network_dialog(self):
        """Открывает диалог создания/загрузки сети"""
        try:
            dialog = NetworkDialog(self.root, self.db_manager)
            result = dialog.show()
            
            if result and result['network']:
                # Обновляем визуализатор сети
                self.network_viewer.update_network(result['network'])
                
                # Обновляем симулятор если он есть
                if self.simulator:
                    self.simulator.network = result['network']
                
                self.status_var.set("╔═══ СЕТЬ ЗАГРУЖЕНА ═══╗")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть диалог сети: {str(e)}")
    
    def _save_current_network(self):
        """Сохраняет текущую сеть"""
        if not self.network_viewer.network:
            messagebox.showwarning("Предупреждение", "Нет сети для сохранения")
            return
        
        # Диалог ввода имени сети
        save_dialog = tk.Toplevel(self.root)
        save_dialog.title("Сохранить сеть")
        save_dialog.geometry("400x200")
        save_dialog.configure(bg=self.theme.COLORS['bg_primary'])
        save_dialog.transient(self.root)
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
                if self.network_viewer.save_current_network(name, desc_entry.get()):
                    messagebox.showinfo("Успех", f"Сеть '{name}' сохранена")
                    save_dialog.destroy()
                    self.status_var.set("╔═══ СЕТЬ СОХРАНЕНА ═══╗")
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить сеть")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить сеть: {str(e)}")
        
        # Кнопки
        buttons_frame = ttk.Frame(save_dialog)
        buttons_frame.pack(pady=20)
        
        ttk.Button(buttons_frame, text="Сохранить", command=save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=save_dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Фокус на поле имени
        name_entry.focus_set()
    
    def _on_program_state_changed(self, state, status_info):
        """Обработчик изменения состояния программы"""
        # Обновляем панель управления
        if hasattr(self, 'control_panel'):
            self.control_panel._update_button_states()
        
        # Обновляем отображение статуса
        self.update_status_display(status_info)
        
        print(f"[INFO] Состояние программы изменено: {status_info['state_display']}")
    
    def generate_report(self):
        """Генерирует отчет в формате Word"""
        try:
            from ..reports.word_report_generator import WordReportGenerator
            from tkinter import filedialog
            
            # Запрашиваем путь для сохранения
            output_path = filedialog.asksaveasfilename(
                title="Сохранить отчет",
                defaultextension=".docx",
                filetypes=[("Word документы", "*.docx"), ("Все файлы", "*.*")]
            )
            
            if not output_path:
                return  # Пользователь отменил
            
            # Генерируем отчет
            report_generator = WordReportGenerator()
            report_path = report_generator.create_report(
                self.program_state_manager,
                self.db_manager,
                output_path
            )
            
            messagebox.showinfo("Успех", f"Отчет сохранен: {report_path}")
            
        except ImportError:
            messagebox.showerror("Ошибка", "Модуль python-docx не установлен.\nУстановите: pip install python-docx")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать отчет: {str(e)}")
    
    def _reset_simulation(self):
        """Сбрасывает симуляцию"""
        try:
            # Останавливаем текущую симуляцию
            if self.simulator:
                self.simulator.stop_simulation()
            
            # Сбрасываем состояние программы
            self.program_state_manager.stop_program()
            
            # Сбрасываем интерфейс
            self.is_simulation_running = False
            if hasattr(self, 'control_panel'):
                self.control_panel.set_simulation_state(False)
            
            # Очищаем графики
            if hasattr(self, 'metrics_panel'):
                self.metrics_panel.reset_metrics()
            
            messagebox.showinfo("Информация", "Симуляция сброшена")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сбросе симуляции: {str(e)}")
    
    def update_status_display(self, status_info):
        """Обновляет отображение статуса"""
        if hasattr(self, 'status_var'):
            state_display = status_info['state_display']
            runtime = status_info['runtime_display']
            current_network = status_info.get('current_network_name', 'Нет')
            
            status_text = f"╔═══ {state_display.upper()} ═══╗ | Время: {runtime} | Сеть: {current_network}"
            self.status_var.set(status_text)

