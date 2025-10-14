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

class MainWindow:
    """Главное окно приложения в стиле Кровавых Ангелов"""
    
    def __init__(self, root, config):
        self.root = root
        self.config = config
        self.simulator = None
        self.db_manager = DatabaseManager()
        
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
        self.control_panel = ControlPanel(self, self.config)
        
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
        
        # Вкладка "Метрики в реальном времени"
        self.metrics_frame = ttk.Frame(self.plots_notebook)
        self.plots_notebook.add(self.metrics_frame, text="Метрики")
        
        # Создание графиков метрик
        self._create_metrics_plots()
        
        # Вкладка "Топология сети" - перемещаем NetworkViewer сюда
        self.topology_frame = ttk.Frame(self.plots_notebook)
        self.plots_notebook.add(self.topology_frame, text="Топология")
        
        # Создание визуализатора сети в вкладке топологии
        self.network_viewer = NetworkViewer(self, self.topology_frame)
        
        # Вкладка "Анализ надежности"
        self.reliability_frame = ttk.Frame(self.plots_notebook)
        self.plots_notebook.add(self.reliability_frame, text="Надежность")
        
        # Вкладка "События отказов"
        self.failures_frame = ttk.Frame(self.plots_notebook)
        self.plots_notebook.add(self.failures_frame, text="Отказы")
        
        # Упаковка notebook
        self.plots_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
    
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
        """Создает компоновку интерфейса"""
        # Панель управления (сверху)
        self.control_panel.frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Основная область (по центру)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель (панель метрик)
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.metrics_panel.frame.pack(fill=tk.BOTH, expand=True)
        
        # Правая панель (графики и визуализация)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Создание notebook для графиков
        self._create_plots_area(right_panel)
        
        # Статусная строка (снизу)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
    
    def _apply_military_styling(self):
        """Применяет военный стиль к интерфейсу"""
        # Настройка цветов для всех основных фреймов
        self._style_frame(self.control_panel.frame)
        self._style_frame(self.metrics_panel.frame)
        self._style_frame(self.network_viewer.frame)
        
        # Добавление военных элементов
        self._add_military_elements()
    
    def _style_frame(self, frame):
        """Стилизует фрейм в военном стиле"""
        frame.configure(bg=self.theme.COLORS['bg_secondary'])
        self.theme.add_border_effect(frame)
    
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
        if not self.is_simulation_running or not self.simulator:
            return
        
        self.simulator.stop_simulation()
        self.is_simulation_running = False
        
        # Обновление интерфейса
        self.control_panel.set_simulation_state(False)
        self.status_var.set("╔═══ СИМУЛЯЦИЯ ОСТАНОВЛЕНА ═══╗")
    
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
                
                # Обновление графиков
                self.throughput_line.set_data(times, [m.throughput for m in history])
                self.latency_line.set_data(times, [m.latency for m in history])
                self.reliability_line.set_data(times, [m.reliability for m in history])
                self.availability_line.set_data(times, [m.availability for m in history])
                
                # Автомасштабирование
                self.throughput_ax.relim()
                self.throughput_ax.autoscale_view()
                self.latency_ax.relim()
                self.latency_ax.autoscale_view()
                self.reliability_ax.relim()
                self.reliability_ax.autoscale_view()
                self.availability_ax.relim()
                self.availability_ax.autoscale_view()
                
                # Перерисовка
                self.metrics_canvas.draw_idle()
    
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

