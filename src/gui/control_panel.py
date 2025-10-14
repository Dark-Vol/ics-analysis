#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Панель управления симуляцией в стиле Кровавых Ангелов
"""

import tkinter as tk
from tkinter import ttk
from .themes.blood_angels_theme import BloodAngelsTheme

class ControlPanel:
    """Панель управления симуляцией в стиле Кровавых Ангелов"""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.theme = BloodAngelsTheme()
        
        # Создание фрейма в военном стиле
        self.frame = self.theme.create_military_frame(parent.root, 
                                                   title="КОНТРОЛЬНЫЙ ПАНЕЛЬ")
        
        # Переменные
        self._create_variables()
        
        # Создание виджетов
        self._create_widgets()
        
        # Загрузка значений по умолчанию
        self._load_defaults()
    
    def _create_variables(self):
        """Создает переменные для управления"""
        # Параметры сети
        self.nodes_var = tk.StringVar(value="10")
        self.connection_prob_var = tk.StringVar(value="0.3")
        
        # Параметры симуляции
        self.duration_var = tk.StringVar(value="100.0")
        self.time_step_var = tk.StringVar(value="0.1")
        self.seed_var = tk.StringVar(value="42")
        
        # Флаги
        self.enable_traffic_var = tk.BooleanVar(value=True)
        self.enable_failures_var = tk.BooleanVar(value=True)
        self.enable_adverse_var = tk.BooleanVar(value=True)
        
        # Состояние симуляции
        self.simulation_state = False
    
    def _create_widgets(self):
        """Создает виджеты панели управления в военном стиле"""
        # Создание notebook для вкладок в стиле Кровавых Ангелов
        self.notebook = ttk.Notebook(self.frame, style='BloodAngels.TNotebook')
        self.notebook.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Вкладка "Сеть"
        self.network_frame = ttk.Frame(self.notebook, style='BloodAngels.TFrame')
        self.notebook.add(self.network_frame, text="╔═══ СЕТЬ ═══╗")
        self._create_network_tab()
        
        # Вкладка "Симуляция"
        self.simulation_frame = ttk.Frame(self.notebook, style='BloodAngels.TFrame')
        self.notebook.add(self.simulation_frame, text="╔═══ СИМУЛЯЦИЯ ═══╗")
        self._create_simulation_tab()
        
        # Вкладка "Условия"
        self.conditions_frame = ttk.Frame(self.notebook, style='BloodAngels.TFrame')
        self.notebook.add(self.conditions_frame, text="╔═══ УСЛОВИЯ ═══╗")
        self._create_conditions_tab()
        
        # Панель кнопок управления
        self._create_control_buttons()
    
    def _create_network_tab(self):
        """Создает вкладку настроек сети"""
        # Количество узлов
        ttk.Label(self.network_frame, text="Количество узлов:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        nodes_spinbox = ttk.Spinbox(self.network_frame, from_=3, to=50, textvariable=self.nodes_var, width=10)
        nodes_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Вероятность соединения
        ttk.Label(self.network_frame, text="Вероятность соединения:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        prob_scale = ttk.Scale(self.network_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL, 
                              variable=self.connection_prob_var, length=150)
        prob_scale.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Отображение значения вероятности
        prob_label = ttk.Label(self.network_frame, textvariable=self.connection_prob_var)
        prob_label.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
    
    def _create_simulation_tab(self):
        """Создает вкладку настроек симуляции"""
        # Длительность симуляции
        ttk.Label(self.simulation_frame, text="Длительность (сек):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        duration_spinbox = ttk.Spinbox(self.simulation_frame, from_=10, to=1000, 
                                      textvariable=self.duration_var, width=10)
        duration_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Шаг времени
        ttk.Label(self.simulation_frame, text="Шаг времени (сек):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        time_step_spinbox = ttk.Spinbox(self.simulation_frame, from_=0.01, to=1.0, 
                                       textvariable=self.time_step_var, width=10, increment=0.01)
        time_step_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Случайное зерно
        ttk.Label(self.simulation_frame, text="Случайное зерно:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        seed_spinbox = ttk.Spinbox(self.simulation_frame, from_=1, to=10000, 
                                  textvariable=self.seed_var, width=10)
        seed_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
    
    def _create_conditions_tab(self):
        """Создает вкладку неблагоприятных условий"""
        # Включить трафик
        traffic_check = ttk.Checkbutton(self.conditions_frame, text="Включить генерацию трафика", 
                                       variable=self.enable_traffic_var)
        traffic_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Включить отказы
        failures_check = ttk.Checkbutton(self.conditions_frame, text="Включить моделирование отказов", 
                                        variable=self.enable_failures_var)
        failures_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Включить неблагоприятные условия
        adverse_check = ttk.Checkbutton(self.conditions_frame, text="Включить неблагоприятные условия", 
                                       variable=self.enable_adverse_var)
        adverse_check.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    
    def _create_control_buttons(self):
        """Создает кнопки управления в военном стиле"""
        button_frame = ttk.Frame(self.frame, style='BloodAngels.TFrame')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Кнопка создания системы
        create_button = ttk.Button(button_frame, text="╔═══ СОЗДАТЬ СИСТЕМУ ═══╗", 
                                  command=self._create_system,
                                  style='BloodAngels.TButton')
        create_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Кнопка запуска/остановки
        self.start_button = ttk.Button(button_frame, text="╔═══ ЗАПУСК ═══╗", 
                                     command=self._start_simulation,
                                     style='BloodAngels.Gold.TButton')
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка паузы
        self.pause_button = ttk.Button(button_frame, text="╔═══ ПАУЗА ═══╗", 
                                     command=self._pause_simulation, 
                                     state=tk.DISABLED,
                                     style='BloodAngels.TButton')
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка остановки
        self.stop_button = ttk.Button(button_frame, text="╔═══ СТОП ═══╗", 
                                    command=self._stop_simulation, 
                                    state=tk.DISABLED,
                                    style='BloodAngels.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сброса
        reset_button = ttk.Button(button_frame, text="╔═══ СБРОС ═══╗", 
                                command=self._reset_simulation,
                                style='BloodAngels.TButton')
        reset_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _load_defaults(self):
        """Загружает значения по умолчанию из конфигурации"""
        self.nodes_var.set(str(self.config.get('network.nodes', 10)))
        self.connection_prob_var.set(str(self.config.get('network.connections', 0.3)))
        self.duration_var.set(str(self.config.get('simulation.time_steps', 1000) * self.config.get('simulation.dt', 0.1)))
        self.time_step_var.set(str(self.config.get('simulation.dt', 0.1)))
        self.seed_var.set(str(self.config.get('simulation.random_seed', 42)))
    
    def _create_system(self):
        """Создает систему"""
        self.parent.create_system()
    
    def _start_simulation(self):
        """Запускает симуляцию"""
        self.parent.start_simulation()
    
    def _pause_simulation(self):
        """Приостанавливает симуляцию"""
        if self.simulation_state:
            if hasattr(self.parent, 'simulator') and self.parent.simulator:
                self.parent.simulator.pause_simulation()
            self.pause_button.config(text="Возобновить")
        else:
            if hasattr(self.parent, 'simulator') and self.parent.simulator:
                self.parent.simulator.resume_simulation()
            self.pause_button.config(text="Пауза")
    
    def _stop_simulation(self):
        """Останавливает симуляцию"""
        self.parent.stop_simulation()
    
    def _reset_simulation(self):
        """Сбрасывает симуляцию"""
        self.parent._new_simulation()
    
    def set_simulation_state(self, is_running):
        """Устанавливает состояние симуляции"""
        self.simulation_state = is_running
        
        if is_running:
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED, text="Пауза")
            self.stop_button.config(state=tk.DISABLED)
    
    def reset_to_defaults(self):
        """Сбрасывает настройки к значениям по умолчанию"""
        self._load_defaults()
        self.set_simulation_state(False)
    
    def get_simulation_config(self):
        """Возвращает конфигурацию симуляции"""
        return {
            'nodes': int(self.nodes_var.get()),
            'connection_probability': float(self.connection_prob_var.get()),
            'duration': float(self.duration_var.get()),
            'time_step': float(self.time_step_var.get()),
            'seed': int(self.seed_var.get()),
            'enable_traffic': self.enable_traffic_var.get(),
            'enable_failures': self.enable_failures_var.get(),
            'enable_adverse_conditions': self.enable_adverse_var.get()
        }

