# -*- coding: utf-8 -*-
# coding: utf-8

"""
ИКС Анализатор Системы
Главное окно приложения анализа ИКС
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional

# Импорт модулей ИКС Анализатора
from src.system_model import SystemModel, create_sample_network, NodeType, LinkType
from src.reliability import ReliabilityAnalyzer
from src.simulation import NetworkSimulator
from src.stress_test import StressTester
from src.whatif import WhatIfAnalyzer, ParameterType, ParameterRange
from src.gui.main_window import MainWindow as NewMainWindow

# Цветовая схема приложения
BLOOD_ANGELS_COLORS = {
    'primary_red': '#8B0000',      # Темно-красный
    'secondary_red': '#DC143C',    # Кримсон
    'accent_red': '#FF4500',       # Оранжево-красный
    'blood_red': '#B22222',        # Кроваво-красный
    
    'primary_gold': '#DAA520',     # Золотой
    'secondary_gold': '#FFD700',   # Яркий золотой
    'accent_gold': '#FFA500',       # Оранжевое золото
    'dark_gold': '#B8860B',        # Темное золото
    
    'primary_black': '#1C1C1C',     # Основной черный
    'secondary_black': '#2F2F2F',   # Вторичный черный
    'dark_gray': '#404040',        # Темно-серый
    'medium_gray': '#696969',      # Средне-серый
    'light_gray': '#A9A9A9',       # Светло-серый
    
    'warning': '#FF6B6B',          # Цвет предупреждения
    'success': '#4ECDC4',          # Цвет успеха
    'info': '#45B7D1',             # Цвет информации
    'danger': '#FF4757',           # Цвет опасности
    
    'bg_primary': '#1C1C1C',       # Основной фон
    'bg_secondary': '#2F2F2F',     # Вторичный фон
    'bg_panel': '#404040',         # Фон панелей
    'bg_card': '#4A4A4A',          # Фон карточек
    
    'text_primary': '#FFFFFF',     # Основной текст
    'text_secondary': '#DAA520',   # Вторичный текст (золотой)
    'text_muted': '#A9A9A9',       # Приглушенный текст
    'text_warning': '#FFD700',     # Текст предупреждения
}

# Шрифты в военном стиле
MILITARY_FONTS = {
    'title': ('Arial', 16, 'bold'),
    'subtitle': ('Arial', 12, 'bold'),
    'body': ('Arial', 10),
    'small': ('Arial', 8),
    'monospace': ('Consolas', 9),
    'military': ('Courier New', 10, 'bold'),
}

def configure_blood_angels_theme(root):
    """Настраивает тему приложения для tkinter"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Стиль для Frame
    style.configure('BloodAngels.TFrame',
                    background=BLOOD_ANGELS_COLORS['bg_secondary'],
                    relief='raised',
                    borderwidth=2)
    
    # Стиль для Label
    style.configure('BloodAngels.TLabel',
                    background=BLOOD_ANGELS_COLORS['bg_secondary'],
                    foreground=BLOOD_ANGELS_COLORS['text_primary'],
                    font=MILITARY_FONTS['body'])
    
    # Стиль для заголовков
    style.configure('BloodAngels.Title.TLabel',
                    background=BLOOD_ANGELS_COLORS['bg_secondary'],
                    foreground=BLOOD_ANGELS_COLORS['text_secondary'],
                    font=MILITARY_FONTS['title'])
    
    # Стиль для кнопок
    style.configure('BloodAngels.TButton',
                    background=BLOOD_ANGELS_COLORS['primary_red'],
                    foreground=BLOOD_ANGELS_COLORS['text_primary'],
                    font=MILITARY_FONTS['body'],
                    borderwidth=2,
                    relief='raised')
    
    style.map('BloodAngels.TButton',
                background=[('active', BLOOD_ANGELS_COLORS['secondary_red']),
                            ('pressed', BLOOD_ANGELS_COLORS['blood_red'])],
                            relief=[('pressed', 'sunken'),
                                    ('active', 'raised')])
    
    # Стиль для золотых кнопок
    style.configure('BloodAngels.Gold.TButton',
                    background=BLOOD_ANGELS_COLORS['primary_gold'],
                    foreground=BLOOD_ANGELS_COLORS['primary_black'],
                    font=MILITARY_FONTS['body'],
                    borderwidth=2,
                    relief='raised')
    
    style.map('BloodAngels.Gold.TButton',
                background=[('active', BLOOD_ANGELS_COLORS['secondary_gold']),
                            ('pressed', BLOOD_ANGELS_COLORS['dark_gold'])],
                            relief=[('pressed', 'sunken'),
                                    ('active', 'raised')])
    
    # Стиль для Notebook
    style.configure('BloodAngels.TNotebook',
                    background=BLOOD_ANGELS_COLORS['bg_secondary'],
                    borderwidth=2)
    
    style.configure('BloodAngels.TNotebook.Tab',
                    background=BLOOD_ANGELS_COLORS['bg_panel'],
                    foreground=BLOOD_ANGELS_COLORS['text_primary'],
                    padding=[20, 10],
                    font=MILITARY_FONTS['body'])
    
    style.map('BloodAngels.TNotebook.Tab',
                background=[('selected', BLOOD_ANGELS_COLORS['primary_red']),
                            ('active', BLOOD_ANGELS_COLORS['secondary_red'])],
                            foreground=[('selected', BLOOD_ANGELS_COLORS['text_primary']),
                                        ('active', BLOOD_ANGELS_COLORS['text_primary'])])
    
    # Стиль для Progressbar
    style.configure('BloodAngels.Horizontal.TProgressbar',
                    background=BLOOD_ANGELS_COLORS['primary_gold'],
                    troughcolor=BLOOD_ANGELS_COLORS['bg_panel'],
                    borderwidth=2,
                    lightcolor=BLOOD_ANGELS_COLORS['primary_gold'],
                    darkcolor=BLOOD_ANGELS_COLORS['primary_gold'])
    
    # Стиль для Spinbox
    style.configure('BloodAngels.TSpinbox',
                    fieldbackground=BLOOD_ANGELS_COLORS['bg_panel'],
                    foreground=BLOOD_ANGELS_COLORS['text_primary'],
                    borderwidth=2,
                    arrowcolor=BLOOD_ANGELS_COLORS['text_primary'])
    
    # Стиль для Scale
    style.configure('BloodAngels.Horizontal.TScale',
                    background=BLOOD_ANGELS_COLORS['bg_secondary'],
                    troughcolor=BLOOD_ANGELS_COLORS['bg_panel'],
                    borderwidth=2,
                    sliderlength=20)

def configure_matplotlib_blood_angels():
    """Настраивает matplotlib для темы приложения"""
    plt.style.use('dark_background')
    
    plt.rcParams.update({
        'figure.facecolor': BLOOD_ANGELS_COLORS['bg_primary'],
        'axes.facecolor': BLOOD_ANGELS_COLORS['bg_panel'],
        'axes.edgecolor': BLOOD_ANGELS_COLORS['primary_gold'],
        'axes.labelcolor': BLOOD_ANGELS_COLORS['text_primary'],
        'text.color': BLOOD_ANGELS_COLORS['text_primary'],
        'xtick.color': BLOOD_ANGELS_COLORS['text_primary'],
        'ytick.color': BLOOD_ANGELS_COLORS['text_primary'],
        'grid.color': BLOOD_ANGELS_COLORS['medium_gray'],
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.linewidth': 2,
        'xtick.major.width': 2,
        'ytick.major.width': 2,
        'font.size': 10,
        'font.family': 'sans-serif',
        'axes.spines.top': False,
        'axes.spines.right': False,
    })

def create_military_frame(parent, title="", width=None, height=None):
    """Создает фрейм в военном стиле"""
    # Создаем базовую конфигурацию фрейма
    frame_config = {
        'bg': BLOOD_ANGELS_COLORS['bg_panel'],
        'relief': 'raised',
        'borderwidth': 2,
        'highlightbackground': BLOOD_ANGELS_COLORS['primary_gold'],
        'highlightthickness': 1
    }
    
    # Добавляем width и height только если они указаны
    if width is not None:
        frame_config['width'] = width
    if height is not None:
        frame_config['height'] = height
    
    frame = tk.Frame(parent, **frame_config)
    
    if title:
        title_frame = tk.Frame(frame, bg=BLOOD_ANGELS_COLORS['primary_red'], height=30)
        title_frame.pack(fill=tk.X, padx=2, pady=2)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, 
                                text=f"╔═══ {title} ═══╗",
                                bg=BLOOD_ANGELS_COLORS['primary_red'],
                                fg=BLOOD_ANGELS_COLORS['text_primary'],
                                font=MILITARY_FONTS['monospace'])
        title_label.pack(expand=True)
    
    return frame

def create_status_indicator(parent, text, status='normal', size=(100, 30)):
    """Создает индикатор статуса в военном стиле"""
    frame = tk.Frame(parent, 
                    bg=BLOOD_ANGELS_COLORS['bg_panel'],
                    relief='raised',
                    borderwidth=2,
                    width=size[0],
                    height=size[1])
    frame.pack_propagate(False)
    
    # Индикаторная полоса
    status_colors = {
        'excellent': BLOOD_ANGELS_COLORS['success'],
        'good': BLOOD_ANGELS_COLORS['primary_gold'],
        'warning': BLOOD_ANGELS_COLORS['warning'],
        'critical': BLOOD_ANGELS_COLORS['danger'],
        'error': BLOOD_ANGELS_COLORS['danger'],
        'normal': BLOOD_ANGELS_COLORS['text_primary']
    }
    
    indicator = tk.Frame(frame, 
                        bg=status_colors.get(status.lower(), BLOOD_ANGELS_COLORS['text_primary']),
                        width=5)
    indicator.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
    
    # Текст
    label = tk.Label(frame,
                    text=text,
                    bg=BLOOD_ANGELS_COLORS['bg_panel'],
                    fg=BLOOD_ANGELS_COLORS['text_primary'],
                    font=MILITARY_FONTS['small'])
    label.pack(expand=True)
    
    return frame, label


class MainWindow(tk.Frame):
    """Главное окно приложения ИКС Анализатора"""
    
    def __init__(self, root: tk.Tk, config):
        super().__init__(root)
        self.root = root
        self.config = config

        # Настройка темы приложения
        configure_blood_angels_theme(self.root)
        configure_matplotlib_blood_angels()
        
        # Настройка главного окна
        self.root.title("╔═══  ИКС АНАЛИЗАТОР СИСТЕМЫ ═══╗")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)
        self.root.configure(bg=BLOOD_ANGELS_COLORS['bg_primary'])

        # Основной фрейм
        self.pack(fill="both", expand=True)

        # Переменные состояния
        self.is_simulation_running = False
        self.system_model = None  # Созданная система
        self.simulation_data = []
        
        # Переменные ИКС Анализатора
        self.reliability_analyzer = None
        self.current_simulator = None
        self.stress_tester = None
        self.whatif_analyzer = None
        self.analysis_results = {}
        
        # Создание интерфейса
        self._create_banner()
        self._create_main_interface()
        self._create_status_panel()
        
    def _create_banner(self):
        """Создает заголовочный баннер в военном стиле"""
        banner_frame = tk.Frame(self, 
                              bg=BLOOD_ANGELS_COLORS['primary_red'],
                              height=80)
        banner_frame.pack(fill=tk.X, padx=5, pady=5)
        banner_frame.pack_propagate(False)
        
        banner_text = """╔═══  ИКС АНАЛИЗАТОР СИСТЕМЫ ═══╗
║     СИСТЕМА МОНИТОРИНГА СЕТИ         ║
║     В НЕБЛАГОПРИЯТНЫХ УСЛОВИЯХ       ║
╚═══════════════════════════════════════════╝"""
        
        banner_label = tk.Label(banner_frame,
                              text=banner_text,
                              bg=BLOOD_ANGELS_COLORS['primary_red'],
                              fg=BLOOD_ANGELS_COLORS['text_primary'],
                              font=MILITARY_FONTS['monospace'])
        banner_label.pack(expand=True)
    
    def _create_main_interface(self):
        """Создает основной интерфейс"""
        # Основной контейнер
        main_container = tk.Frame(self, bg=BLOOD_ANGELS_COLORS['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - управление
        self._create_control_panel(main_container)
        
        # Правая панель - визуализация
        self._create_visualization_panel(main_container)
    
    def _create_control_panel(self, parent):
        """Создает панель управления"""
        control_frame = create_military_frame(parent, "КОНТРОЛЬНЫЙ ПАНЕЛЬ", width=400)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Notebook для вкладок
        notebook = ttk.Notebook(control_frame, style='BloodAngels.TNotebook')
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Сеть"
        network_frame = ttk.Frame(notebook, style='BloodAngels.TFrame')
        notebook.add(network_frame, text="╔═══ СЕТЬ ═══╗")
        self._create_network_tab(network_frame)
        
        # Вкладка "Симуляция"
        sim_frame = ttk.Frame(notebook, style='BloodAngels.TFrame')
        notebook.add(sim_frame, text="╔═══ СИМУЛЯЦИЯ ═══╗")
        self._create_simulation_tab(sim_frame)
        
        # Вкладка "Анализ"
        analysis_frame = ttk.Frame(notebook, style='BloodAngels.TFrame')
        notebook.add(analysis_frame, text="╔═══ АНАЛИЗ ═══╗")
        self._create_analysis_tab(analysis_frame)
        
        # Вкладка "Надежность"
        reliability_frame = ttk.Frame(notebook, style='BloodAngels.TFrame')
        notebook.add(reliability_frame, text="╔═══ НАДЕЖНОСТЬ ═══╗")
        self._create_reliability_tab(reliability_frame)
        
        # Вкладка "Стресс-тесты"
        stress_frame = ttk.Frame(notebook, style='BloodAngels.TFrame')
        notebook.add(stress_frame, text="╔═══ СТРЕСС-ТЕСТЫ ═══╗")
        self._create_stress_test_tab(stress_frame)
        
        # Вкладка "What-if"
        whatif_frame = ttk.Frame(notebook, style='BloodAngels.TFrame')
        notebook.add(whatif_frame, text="╔═══ WHAT-IF ═══╗")
        self._create_whatif_tab(whatif_frame)
        
        # Кнопки управления
        self._create_control_buttons(control_frame)
    
    def _create_network_tab(self, parent):
        """Создает вкладку создания системы"""
        # Заголовок
        title_label = tk.Label(parent, text="СОЗДАНИЕ СИСТЕМЫ", 
                              bg=BLOOD_ANGELS_COLORS['bg_panel'],
                              fg=BLOOD_ANGELS_COLORS['text_primary'],
                              font=MILITARY_FONTS['title'])
        title_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, padx=5, pady=10)
        
        # Выбор типа системы
        system_type_frame = tk.LabelFrame(parent, text="Тип системы",
                                         bg=BLOOD_ANGELS_COLORS['bg_panel'],
                                         fg=BLOOD_ANGELS_COLORS['text_primary'],
                                         font=MILITARY_FONTS['body'])
        system_type_frame.grid(row=1, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        self.system_type_var = tk.StringVar(value="sample")
        
        ttk.Radiobutton(system_type_frame, text="Готовая система (пример)", 
                       variable=self.system_type_var, value="sample",
                       style='BloodAngels.TRadiobutton').pack(anchor='w', padx=5, pady=2)
        ttk.Radiobutton(system_type_frame, text="Создать пользовательскую систему", 
                       variable=self.system_type_var, value="custom",
                       style='BloodAngels.TRadiobutton').pack(anchor='w', padx=5, pady=2)
        
        # Параметры пользовательской системы
        self.custom_params_frame = tk.LabelFrame(parent, text="Параметры пользовательской системы",
                                                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                                                fg=BLOOD_ANGELS_COLORS['text_primary'],
                                                font=MILITARY_FONTS['body'])
        self.custom_params_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        
        # Количество узлов
        tk.Label(self.custom_params_frame, text="Количество узлов:", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.nodes_var = tk.StringVar(value="10")
        nodes_spinbox = ttk.Spinbox(self.custom_params_frame, from_=3, to=50, textvariable=self.nodes_var, width=10,
                                   style='BloodAngels.TSpinbox')
        nodes_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Вероятность соединения
        tk.Label(self.custom_params_frame, text="Вероятность соединения:", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.connection_prob_var = tk.StringVar(value="0.30")
        
        # Функция для форматирования значения
        def format_prob_value(*args):
            try:
                value = float(self.connection_prob_var.get())
                formatted_value = f"{value:.2f}"
                if self.connection_prob_var.get() != formatted_value:
                    self.connection_prob_var.set(formatted_value)
            except ValueError:
                pass
        
        # Привязка функции к изменению переменной
        self.connection_prob_var.trace('w', format_prob_value)
        
        prob_scale = ttk.Scale(self.custom_params_frame, from_=0.01, to=1.0, orient=tk.HORIZONTAL, 
                              variable=self.connection_prob_var, length=150,
                              style='BloodAngels.Horizontal.TScale')
        prob_scale.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Spinbox для точного ввода вероятности с 2 знаками после запятой
        prob_spinbox = ttk.Spinbox(self.custom_params_frame, from_=0.01, to=1.0, 
                                  textvariable=self.connection_prob_var, 
                                  width=8, increment=0.01,
                                  style='BloodAngels.TSpinbox')
        prob_spinbox.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Отображение текущего значения с форматированием
        prob_label = tk.Label(self.custom_params_frame, text="Текущее значение:",
                             bg=BLOOD_ANGELS_COLORS['bg_panel'],
                             fg=BLOOD_ANGELS_COLORS['text_primary'],
                             font=MILITARY_FONTS['small'])
        prob_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.prob_value_label = tk.Label(self.custom_params_frame, textvariable=self.connection_prob_var,
                                        bg=BLOOD_ANGELS_COLORS['bg_panel'],
                                        fg=BLOOD_ANGELS_COLORS['text_secondary'],
                                        font=MILITARY_FONTS['body'])
        self.prob_value_label.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
        # Кнопка создания системы
        create_btn = ttk.Button(parent, text="СОЗДАТЬ СИСТЕМУ", 
                               command=self.create_system,
                               style='Military.TButton')
        create_btn.grid(row=3, column=0, columnspan=3, sticky='ew', padx=5, pady=10)
        
        # Информация о системе
        self.system_info_var = tk.StringVar(value="Система не создана")
        info_label = tk.Label(parent, textvariable=self.system_info_var,
                             bg=BLOOD_ANGELS_COLORS['bg_panel'],
                             fg=BLOOD_ANGELS_COLORS['text_secondary'],
                             font=MILITARY_FONTS['body'])
        info_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Переключение видимости параметров
        def toggle_custom_params(*args):
            if self.system_type_var.get() == "custom":
                self.custom_params_frame.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
            else:
                self.custom_params_frame.grid_remove()
        
        self.system_type_var.trace('w', toggle_custom_params)
        toggle_custom_params()  # Инициализация
    
    def create_system(self):
        """Создание системы на основе выбранных параметров"""
        try:
            if self.system_type_var.get() == "sample":
                # Создаем готовую систему
                from src.system_model import create_sample_network
                self.system_model = create_sample_network()
                system_info = f"Готовая система: {len(self.system_model.nodes)} узлов, {len(self.system_model.links)} каналов"
            else:
                # Создаем пользовательскую систему
                num_nodes = int(self.nodes_var.get())
                connection_prob = float(self.connection_prob_var.get())
                
                from src.system_model import SystemModel
                self.system_model = SystemModel("Пользовательская ИКС")
                self.system_model.generate_random_network(num_nodes, connection_prob)
                system_info = f"Пользовательская система: {num_nodes} узлов, {len(self.system_model.links)} каналов (p={connection_prob:.2f})"
            
            # Обновляем информацию о системе
            self.system_info_var.set(system_info)
            
            # Обновляем визуализацию сети
            if hasattr(self, 'network_canvas'):
                self._draw_sample_network()
            
            # Выводим сообщение об успехе
            print(f"Система создана: {system_info}")
            
        except Exception as e:
            error_msg = f"Ошибка создания системы: {str(e)}"
            self.system_info_var.set(error_msg)
            print(error_msg)
    
    def _create_simulation_tab(self, parent):
        """Создает вкладку настроек симуляции"""
        # Длительность симуляции
        tk.Label(parent, text="Длительность (сек):", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.duration_var = tk.StringVar(value="100.0")
        duration_spinbox = ttk.Spinbox(parent, from_=10, to=1000, 
                                      textvariable=self.duration_var, width=10,
                                      style='BloodAngels.TSpinbox')
        duration_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Шаг времени
        tk.Label(parent, text="Шаг времени (сек):", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.time_step_var = tk.StringVar(value="0.10")
        
        # Функция для форматирования шага времени
        def format_time_step(*args):
            try:
                value = float(self.time_step_var.get())
                formatted_value = f"{value:.2f}"
                if self.time_step_var.get() != formatted_value:
                    self.time_step_var.set(formatted_value)
            except ValueError:
                pass
        
        self.time_step_var.trace('w', format_time_step)
        
        time_step_spinbox = ttk.Spinbox(parent, from_=0.01, to=1.0, 
                                       textvariable=self.time_step_var, width=10, increment=0.01,
                                       style='BloodAngels.TSpinbox')
        time_step_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Случайное зерно
        tk.Label(parent, text="Случайное зерно:", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.seed_var = tk.StringVar(value="42")
        seed_spinbox = ttk.Spinbox(parent, from_=1, to=10000, 
                                  textvariable=self.seed_var, width=10,
                                  style='BloodAngels.TSpinbox')
        seed_spinbox.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
    
    def _create_analysis_tab(self, parent):
        """Создает вкладку анализа"""
        # Флаги анализа
        self.enable_traffic_var = tk.BooleanVar(value=True)
        traffic_check = ttk.Checkbutton(parent, text="Включить генерацию трафика", 
                                       variable=self.enable_traffic_var)
        traffic_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.enable_failures_var = tk.BooleanVar(value=True)
        failures_check = ttk.Checkbutton(parent, text="Включить моделирование отказов", 
                                        variable=self.enable_failures_var)
        failures_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.enable_adverse_var = tk.BooleanVar(value=True)
        adverse_check = ttk.Checkbutton(parent, text="Включить неблагоприятные условия", 
                                       variable=self.enable_adverse_var)
        adverse_check.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    
    def _create_reliability_tab(self, parent):
        """Создает вкладку анализа надежности"""
        # Период анализа
        tk.Label(parent, text="Период анализа (часы):", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.reliability_hours_var = tk.StringVar(value="8760")
        reliability_spinbox = ttk.Spinbox(parent, from_=1, to=87600, 
                                        textvariable=self.reliability_hours_var, width=10,
                                        style='BloodAngels.TSpinbox')
        reliability_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Количество симуляций Монте-Карло
        tk.Label(parent, text="Симуляций Монте-Карло:", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.monte_carlo_sims_var = tk.StringVar(value="1000")
        monte_carlo_spinbox = ttk.Spinbox(parent, from_=100, to=10000, 
                                        textvariable=self.monte_carlo_sims_var, width=10,
                                        style='BloodAngels.TSpinbox')
        monte_carlo_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Кнопка анализа надежности
        reliability_button = ttk.Button(parent, text="╔═══ АНАЛИЗ НАДЕЖНОСТИ ═══╗",
                                      command=self.run_reliability_analysis,
                                      style='BloodAngels.Gold.TButton')
        reliability_button.grid(row=2, column=0, columnspan=2, pady=10)
    
    def _create_stress_test_tab(self, parent):
        """Создает вкладку стресс-тестирования"""
        # Длительность тестов
        tk.Label(parent, text="Длительность тестов (сек):", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.stress_duration_var = tk.StringVar(value="300")
        stress_spinbox = ttk.Spinbox(parent, from_=60, to=3600, 
                                   textvariable=self.stress_duration_var, width=10,
                                   style='BloodAngels.TSpinbox')
        stress_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Типы стресс-тестов
        self.stress_test_types = {
            'load_increase': tk.BooleanVar(value=True),
            'failure_injection': tk.BooleanVar(value=True),
            'cascade_failure': tk.BooleanVar(value=True),
            'network_congestion': tk.BooleanVar(value=True),
            'random_stress': tk.BooleanVar(value=True)
        }
        
        row = 1
        for test_type, var in self.stress_test_types.items():
            test_name = test_type.replace('_', ' ').title()
            check = ttk.Checkbutton(parent, text=test_name, variable=var)
            check.grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
            row += 1
        
        # Кнопка запуска стресс-тестов
        stress_button = ttk.Button(parent, text="╔═══ ЗАПУСК СТРЕСС-ТЕСТОВ ═══╗",
                                 command=self.run_stress_tests,
                                 style='BloodAngels.Gold.TButton')
        stress_button.grid(row=row, column=0, columnspan=2, pady=10)
    
    def _create_whatif_tab(self, parent):
        """Создает вкладку What-if анализа"""
        # Количество симуляций
        tk.Label(parent, text="Количество симуляций:", 
                bg=BLOOD_ANGELS_COLORS['bg_panel'],
                fg=BLOOD_ANGELS_COLORS['text_primary'],
                font=MILITARY_FONTS['body']).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.whatif_sims_var = tk.StringVar(value="200")
        whatif_spinbox = ttk.Spinbox(parent, from_=50, to=1000, 
                                   textvariable=self.whatif_sims_var, width=10,
                                   style='BloodAngels.TSpinbox')
        whatif_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Типы анализа
        self.whatif_analysis_types = {
            'sensitivity': tk.BooleanVar(value=True),
            'monte_carlo': tk.BooleanVar(value=True),
            'optimization': tk.BooleanVar(value=False)
        }
        
        row = 1
        for analysis_type, var in self.whatif_analysis_types.items():
            analysis_name = analysis_type.replace('_', ' ').title()
            check = ttk.Checkbutton(parent, text=analysis_name, variable=var)
            check.grid(row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
            row += 1
        
        # Кнопка What-if анализа
        whatif_button = ttk.Button(parent, text="╔═══ WHAT-IF АНАЛИЗ ═══╗",
                                 command=self.run_whatif_analysis,
                                 style='BloodAngels.Gold.TButton')
        whatif_button.grid(row=row, column=0, columnspan=2, pady=10)
    
    def _create_control_buttons(self, parent):
        """Создает кнопки управления"""
        button_frame = ttk.Frame(parent, style='BloodAngels.TFrame')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Кнопка запуска
        self.start_button = ttk.Button(button_frame, text="╔═══ ЗАПУСК ═══╗", 
                                     command=self.start_simulation,
                                     style='BloodAngels.Gold.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Кнопка остановки
        self.stop_button = ttk.Button(button_frame, text="╔═══ СТОП ═══╗", 
                                    command=self.stop_simulation, 
                                    state=tk.DISABLED,
                                    style='BloodAngels.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сброса
        reset_button = ttk.Button(button_frame, text="╔═══ СБРОС ═══╗", 
                                command=self.reset_simulation,
                                style='BloodAngels.TButton')
        reset_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Дополнительные кнопки
        additional_frame = ttk.Frame(parent, style='BloodAngels.TFrame')
        additional_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Кнопка создания системы
        self.create_system_button = ttk.Button(additional_frame, text="╔═══ СОЗДАТЬ СИСТЕМУ ═══╗", 
                                             command=self.create_system,
                                             style='BloodAngels.Gold.TButton')
        self.create_system_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Кнопка полного анализа
        self.full_analysis_button = ttk.Button(additional_frame, text="╔═══ ПОЛНЫЙ АНАЛИЗ ═══╗", 
                                             command=self.run_full_analysis,
                                             style='BloodAngels.Gold.TButton')
        self.full_analysis_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Кнопка экспорта результатов
        self.export_results_button = ttk.Button(additional_frame, text="╔═══ ЭКСПОРТ ═══╗", 
                                              command=self.export_analysis_results,
                                              style='BloodAngels.TButton')
        self.export_results_button.pack(side=tk.RIGHT)
    
    def _create_visualization_panel(self, parent):
        """Создает панель визуализации"""
        viz_frame = create_military_frame(parent, "ПАНЕЛЬ ВИЗУАЛИЗАЦИИ")
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook для графиков
        self.viz_notebook = ttk.Notebook(viz_frame, style='BloodAngels.TNotebook')
        self.viz_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Метрики"
        metrics_frame = ttk.Frame(self.viz_notebook, style='BloodAngels.TFrame')
        self.viz_notebook.add(metrics_frame, text="╔═══ МЕТРИКИ ═══╗")
        self._create_metrics_plots(metrics_frame)
        
        # Вкладка "Сеть"
        network_frame = ttk.Frame(self.viz_notebook, style='BloodAngels.TFrame')
        self.viz_notebook.add(network_frame, text="╔═══ СЕТЬ ═══╗")
        self._create_network_visualization(network_frame)
        
        # Вкладка "Надежность"
        reliability_viz_frame = ttk.Frame(self.viz_notebook, style='BloodAngels.TFrame')
        self.viz_notebook.add(reliability_viz_frame, text="╔═══ НАДЕЖНОСТЬ ═══╗")
        self._create_reliability_visualization(reliability_viz_frame)
        
        # Вкладка "Стресс-тесты"
        stress_viz_frame = ttk.Frame(self.viz_notebook, style='BloodAngels.TFrame')
        self.viz_notebook.add(stress_viz_frame, text="╔═══ СТРЕСС-ТЕСТЫ ═══╗")
        self._create_stress_test_visualization(stress_viz_frame)
        
        # Вкладка "What-if"
        whatif_viz_frame = ttk.Frame(self.viz_notebook, style='BloodAngels.TFrame')
        self.viz_notebook.add(whatif_viz_frame, text="╔═══ WHAT-IF ═══╗")
        self._create_whatif_visualization(whatif_viz_frame)
    
    def _create_metrics_plots(self, parent):
        """Создает графики метрик"""
        # Создание фигуры для графиков
        self.metrics_fig = Figure(figsize=(12, 8), dpi=100, 
                                facecolor=BLOOD_ANGELS_COLORS['bg_primary'])
        
        # График пропускной способности
        self.throughput_ax = self.metrics_fig.add_subplot(221)
        self.throughput_ax.set_title("ПРОПУСКНАЯ СПОСОБНОСТЬ (Мбит/с)", 
                                   color=BLOOD_ANGELS_COLORS['text_secondary'],
                                   fontweight='bold')
        self.throughput_ax.set_xlabel("Время (с)", color=BLOOD_ANGELS_COLORS['text_primary'])
        self.throughput_ax.set_ylabel("Мбит/с", color=BLOOD_ANGELS_COLORS['text_primary'])
        self.throughput_line, = self.throughput_ax.plot([], [], 
                                                      color=BLOOD_ANGELS_COLORS['primary_red'],
                                                      linewidth=3, alpha=0.8)
        
        # График задержки
        self.latency_ax = self.metrics_fig.add_subplot(222)
        self.latency_ax.set_title("ЗАДЕРЖКА СИГНАЛА (мс)", 
                                color=BLOOD_ANGELS_COLORS['text_secondary'],
                                fontweight='bold')
        self.latency_ax.set_xlabel("Время (с)", color=BLOOD_ANGELS_COLORS['text_primary'])
        self.latency_ax.set_ylabel("мс", color=BLOOD_ANGELS_COLORS['text_primary'])
        self.latency_line, = self.latency_ax.plot([], [], 
                                                color=BLOOD_ANGELS_COLORS['warning'],
                                                linewidth=3, alpha=0.8)
        
        # График надежности
        self.reliability_ax = self.metrics_fig.add_subplot(223)
        self.reliability_ax.set_title("НАДЕЖНОСТЬ СИСТЕМЫ", 
                                    color=BLOOD_ANGELS_COLORS['text_secondary'],
                                    fontweight='bold')
        self.reliability_ax.set_xlabel("Время (с)", color=BLOOD_ANGELS_COLORS['text_primary'])
        self.reliability_ax.set_ylabel("Надежность", color=BLOOD_ANGELS_COLORS['text_primary'])
        self.reliability_line, = self.reliability_ax.plot([], [], 
                                                        color=BLOOD_ANGELS_COLORS['success'],
                                                        linewidth=3, alpha=0.8)
        
        # График доступности
        self.availability_ax = self.metrics_fig.add_subplot(224)
        self.availability_ax.set_title("ДОСТУПНОСТЬ СЕТИ", 
                                     color=BLOOD_ANGELS_COLORS['text_secondary'],
                                     fontweight='bold')
        self.availability_ax.set_xlabel("Время (с)", color=BLOOD_ANGELS_COLORS['text_primary'])
        self.availability_ax.set_ylabel("Доступность", color=BLOOD_ANGELS_COLORS['text_primary'])
        self.availability_line, = self.availability_ax.plot([], [], 
                                                          color=BLOOD_ANGELS_COLORS['primary_gold'],
                                                          linewidth=3, alpha=0.8)
        
        # Настройка макета
        self.metrics_fig.tight_layout()
        
        # Создание canvas
        self.metrics_canvas = FigureCanvasTkAgg(self.metrics_fig, parent)
        self.metrics_canvas.draw()
        self.metrics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_network_visualization(self, parent):
        """Создает визуализацию сети"""
        # Заголовок
        title_label = tk.Label(parent, text="╔═══ ТОПОЛОГИЯ СЕТИ ═══╗",
                              bg=BLOOD_ANGELS_COLORS['bg_panel'],
                              fg=BLOOD_ANGELS_COLORS['text_secondary'],
                              font=MILITARY_FONTS['monospace'])
        title_label.pack(pady=10)
        
        # Простая визуализация сети
        network_canvas = tk.Canvas(parent, 
                                  bg=BLOOD_ANGELS_COLORS['bg_primary'],
                                  width=600, height=400)
        network_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Рисование примера сети
        self._draw_sample_network(network_canvas)
    
    def _draw_sample_network(self, canvas):
        """Рисует сеть на основе созданной системы"""
        canvas.delete("all")
        
        # Если система не создана, показываем заглушку
        if not hasattr(self, 'system_model') or self.system_model is None:
            canvas.create_text(200, 150, text="Создайте систему для отображения", 
                             fill=BLOOD_ANGELS_COLORS['text_secondary'],
                             font=MILITARY_FONTS['body'])
            return
        
        # Получаем узлы и связи из системы
        system_nodes = list(self.system_model.nodes.keys())
        system_links = list(self.system_model.links.keys())
        
        # Генерируем позиции узлов
        import random
        random.seed(42)  # Фиксированное seed для стабильности
        
        canvas_width = 400
        canvas_height = 300
        
        node_positions = {}
        for i, node_id in enumerate(system_nodes):
            # Размещаем узлы в сетке с небольшим случайным смещением
            cols = int(len(system_nodes) ** 0.5) + 1
            row = i // cols
            col = i % cols
            
            x = (col + 1) * (canvas_width // (cols + 1)) + random.randint(-20, 20)
            y = (row + 1) * (canvas_height // (max(1, len(system_nodes) // cols + 1) + 1)) + random.randint(-20, 20)
            
            # Ограничиваем позиции границами canvas
            x = max(30, min(canvas_width - 30, x))
            y = max(30, min(canvas_height - 30, y))
            
            node_positions[node_id] = (x, y)
        
        # Цвета узлов
        node_colors = [BLOOD_ANGELS_COLORS['success'], BLOOD_ANGELS_COLORS['primary_gold'], 
                      BLOOD_ANGELS_COLORS['warning'], BLOOD_ANGELS_COLORS['danger'], 
                      BLOOD_ANGELS_COLORS['info'], BLOOD_ANGELS_COLORS['primary_red'],
                      BLOOD_ANGELS_COLORS['secondary_red']]
        
        # Рисование связей
        for (source, target) in system_links:
            if source in node_positions and target in node_positions:
                x1, y1 = node_positions[source]
                x2, y2 = node_positions[target]
                canvas.create_line(x1, y1, x2, y2, 
                                 fill=BLOOD_ANGELS_COLORS['primary_gold'], width=2)
        
        # Рисование узлов
        for i, (node_id, (x, y)) in enumerate(node_positions.items()):
            color_index = i % len(node_colors)
            canvas.create_oval(x-15, y-15, x+15, y+15, 
                            fill=node_colors[color_index], 
                            outline=BLOOD_ANGELS_COLORS['primary_gold'], width=2)
            canvas.create_text(x, y, text=node_id[:3],  # Показываем первые 3 символа ID
                             fill=BLOOD_ANGELS_COLORS['text_primary'],
                             font=MILITARY_FONTS['small'])
    
    def _create_reliability_visualization(self, parent):
        """Создает визуализацию анализа надежности"""
        # Создание фигуры для надежности
        self.reliability_fig = Figure(figsize=(12, 8), dpi=100, 
                                    facecolor=BLOOD_ANGELS_COLORS['bg_primary'])
        
        # График надежности компонентов
        self.reliability_ax = self.reliability_fig.add_subplot(221)
        self.reliability_ax.set_title("НАДЕЖНОСТЬ КОМПОНЕНТОВ", 
                                    color=BLOOD_ANGELS_COLORS['text_secondary'],
                                    fontweight='bold')
        
        # График MTTF/MTTR
        self.mttf_ax = self.reliability_fig.add_subplot(222)
        self.mttf_ax.set_title("MTTF/MTTR", 
                             color=BLOOD_ANGELS_COLORS['text_secondary'],
                             fontweight='bold')
        
        # График анализа Монте-Карло
        self.monte_carlo_ax = self.reliability_fig.add_subplot(223)
        self.monte_carlo_ax.set_title("АНАЛИЗ МОНТЕ-КАРЛО", 
                                    color=BLOOD_ANGELS_COLORS['text_secondary'],
                                    fontweight='bold')
        
        # График деревьев отказов
        self.fault_tree_ax = self.reliability_fig.add_subplot(224)
        self.fault_tree_ax.set_title("ДЕРЕВЬЯ ОТКАЗОВ", 
                                   color=BLOOD_ANGELS_COLORS['text_secondary'],
                                   fontweight='bold')
        
        # Настройка осей
        for ax in [self.reliability_ax, self.mttf_ax, self.monte_carlo_ax, self.fault_tree_ax]:
            ax.set_facecolor(BLOOD_ANGELS_COLORS['bg_panel'])
            ax.tick_params(colors=BLOOD_ANGELS_COLORS['text_primary'])
        
        self.reliability_fig.tight_layout()
        
        # Canvas для отображения
        self.reliability_canvas = FigureCanvasTkAgg(self.reliability_fig, parent)
        self.reliability_canvas.draw()
        self.reliability_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_stress_test_visualization(self, parent):
        """Создает визуализацию стресс-тестирования"""
        # Создание фигуры для стресс-тестов
        self.stress_fig = Figure(figsize=(12, 8), dpi=100, 
                               facecolor=BLOOD_ANGELS_COLORS['bg_primary'])
        
        # График результатов стресс-тестов
        self.stress_results_ax = self.stress_fig.add_subplot(221)
        self.stress_results_ax.set_title("РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТОВ", 
                                       color=BLOOD_ANGELS_COLORS['text_secondary'],
                                       fontweight='bold')
        
        # График деградации производительности
        self.degradation_ax = self.stress_fig.add_subplot(222)
        self.degradation_ax.set_title("ДЕГРАДАЦИЯ ПРОИЗВОДИТЕЛЬНОСТИ", 
                                    color=BLOOD_ANGELS_COLORS['text_secondary'],
                                    fontweight='bold')
        
        # График точек отказа
        self.failure_points_ax = self.stress_fig.add_subplot(223)
        self.failure_points_ax.set_title("ТОЧКИ ОТКАЗА", 
                                       color=BLOOD_ANGELS_COLORS['text_secondary'],
                                       fontweight='bold')
        
        # График времени восстановления
        self.recovery_ax = self.stress_fig.add_subplot(224)
        self.recovery_ax.set_title("ВРЕМЯ ВОССТАНОВЛЕНИЯ", 
                                 color=BLOOD_ANGELS_COLORS['text_secondary'],
                                 fontweight='bold')
        
        # Настройка осей
        for ax in [self.stress_results_ax, self.degradation_ax, self.failure_points_ax, self.recovery_ax]:
            ax.set_facecolor(BLOOD_ANGELS_COLORS['bg_panel'])
            ax.tick_params(colors=BLOOD_ANGELS_COLORS['text_primary'])
        
        self.stress_fig.tight_layout()
        
        # Canvas для отображения
        self.stress_canvas = FigureCanvasTkAgg(self.stress_fig, parent)
        self.stress_canvas.draw()
        self.stress_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_whatif_visualization(self, parent):
        """Создает визуализацию What-if анализа"""
        # Создание фигуры для What-if анализа
        self.whatif_fig = Figure(figsize=(12, 8), dpi=100, 
                               facecolor=BLOOD_ANGELS_COLORS['bg_primary'])
        
        # График чувствительности параметров
        self.sensitivity_ax = self.whatif_fig.add_subplot(221)
        self.sensitivity_ax.set_title("ЧУВСТВИТЕЛЬНОСТЬ ПАРАМЕТРОВ", 
                                    color=BLOOD_ANGELS_COLORS['text_secondary'],
                                    fontweight='bold')
        
        # График анализа Монте-Карло
        self.whatif_monte_carlo_ax = self.whatif_fig.add_subplot(222)
        self.whatif_monte_carlo_ax.set_title("ЧТО-ЕСЛИ МОНТЕ-КАРЛО", 
                                           color=BLOOD_ANGELS_COLORS['text_secondary'],
                                           fontweight='bold')
        
        # График сценариев
        self.scenarios_ax = self.whatif_fig.add_subplot(223)
        self.scenarios_ax.set_title("СЦЕНАРИИ", 
                                  color=BLOOD_ANGELS_COLORS['text_secondary'],
                                  fontweight='bold')
        
        # График оптимизации
        self.optimization_ax = self.whatif_fig.add_subplot(224)
        self.optimization_ax.set_title("ОПТИМИЗАЦИЯ", 
                                     color=BLOOD_ANGELS_COLORS['text_secondary'],
                                     fontweight='bold')
        
        # Настройка осей
        for ax in [self.sensitivity_ax, self.whatif_monte_carlo_ax, self.scenarios_ax, self.optimization_ax]:
            ax.set_facecolor(BLOOD_ANGELS_COLORS['bg_panel'])
            ax.tick_params(colors=BLOOD_ANGELS_COLORS['text_primary'])
        
        self.whatif_fig.tight_layout()
        
        # Canvas для отображения
        self.whatif_canvas = FigureCanvasTkAgg(self.whatif_fig, parent)
        self.whatif_canvas.draw()
        self.whatif_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_status_panel(self):
        """Создает панель статуса"""
        status_frame = create_military_frame(self, "СТАТУС СИСТЕМЫ")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Статусная строка
        self.status_var = tk.StringVar()
        self.status_var.set("╔═══ СИСТЕМА ГОТОВА К БОЕВЫМ ДЕЙСТВИЯМ ═══╗")
        
        status_label = tk.Label(status_frame,
                               textvariable=self.status_var,
                               bg=BLOOD_ANGELS_COLORS['bg_panel'],
                               fg=BLOOD_ANGELS_COLORS['text_secondary'],
                               font=MILITARY_FONTS['monospace'])
        status_label.pack(pady=10)
        
        # Индикаторы статуса
        indicators_frame = tk.Frame(status_frame, bg=BLOOD_ANGELS_COLORS['bg_panel'])
        indicators_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Создание индикаторов
        self.network_indicator, _ = create_status_indicator(indicators_frame, "СЕТЬ", "good")
        self.network_indicator.pack(side=tk.LEFT, padx=5)
        
        self.simulation_indicator, _ = create_status_indicator(indicators_frame, "СИМУЛЯЦИЯ", "normal")
        self.simulation_indicator.pack(side=tk.LEFT, padx=5)
        
        self.analysis_indicator, _ = create_status_indicator(indicators_frame, "АНАЛИЗ", "normal")
        self.analysis_indicator.pack(side=tk.LEFT, padx=5)
    
    def start_simulation(self):
        """Запускает симуляцию"""
        if self.is_simulation_running:
            return
        
        # Проверяем, что система создана
        if not hasattr(self, 'system_model') or self.system_model is None:
            self.status_var.set("╔═══ ОШИБКА: СОЗДАЙТЕ СИСТЕМУ ═══╗")
            return
        
        try:
            self.is_simulation_running = True
            self.status_var.set("╔═══ БОЕВАЯ СИМУЛЯЦИЯ АКТИВНА ═══╗")
            
            # Обновление кнопок
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # Обновление индикаторов
            self.simulation_indicator.configure(bg=BLOOD_ANGELS_COLORS['success'])
            self.analysis_indicator.configure(bg=BLOOD_ANGELS_COLORS['primary_gold'])
            
            # Генерируем начальные графики на основе созданной системы
            self._generate_initial_plots()
            
            # Запуск симуляции в отдельном потоке
            simulation_thread = threading.Thread(target=self._run_simulation)
            simulation_thread.daemon = True
            simulation_thread.start()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить симуляцию: {str(e)}")
    
    def _generate_initial_plots(self):
        """Генерирует начальные графики на основе созданной системы"""
        try:
            if not hasattr(self, 'system_model') or self.system_model is None:
                return
            
            # Получаем параметры системы
            num_nodes = len(self.system_model.nodes)
            num_links = len(self.system_model.links)
            
            # Генерируем базовые данные на основе системы
            import numpy as np
            import random
            
            # Время для графиков
            time_points = np.linspace(0, 100, 50)
            
            # Пропускная способность зависит от количества каналов
            base_throughput = num_links * 20
            throughput_data = [base_throughput + 30 * np.sin(t/10) + random.uniform(-5, 5) for t in time_points]
            
            # Задержка зависит от сложности сети
            base_latency = 10 + num_nodes * 2
            latency_data = [base_latency + 8 * np.cos(t/5) + random.uniform(-3, 3) for t in time_points]
            
            # Надежность зависит от количества узлов
            base_reliability = 0.95 - (num_nodes - 5) * 0.01
            reliability_data = [max(0.8, min(1.0, base_reliability + 0.03 * np.sin(t/20) + random.uniform(-0.01, 0.01))) for t in time_points]
            
            # Доступность
            availability_data = [0.98 + 0.02 * np.cos(t/15) + random.uniform(-0.01, 0.01) for t in time_points]
            
            # Обновляем графики
            self._update_plots(time_points.tolist(), throughput_data, latency_data, reliability_data, availability_data)
            
            # Обновляем графики надежности
            self._update_reliability_plots()
            
            # Обновляем графики What-if
            self._update_whatif_plots()
            
        except Exception as e:
            print(f"Ошибка генерации начальных графиков: {e}")
    
    def _update_reliability_plots(self):
        """Обновляет графики надежности на основе созданной системы"""
        try:
            if not hasattr(self, 'system_model') or self.system_model is None:
                return
            
            # Получаем параметры системы
            num_nodes = len(self.system_model.nodes)
            num_links = len(self.system_model.links)
            
            # Генерируем данные надежности
            import numpy as np
            
            # Компоненты системы
            components = []
            reliability_values = []
            
            # Узлы
            for i, node_id in enumerate(self.system_model.nodes.keys()):
                components.append(f"Узел {node_id[:8]}")
                reliability_values.append(0.95 + np.random.uniform(-0.05, 0.03))
            
            # Каналы
            for i, (source, target) in enumerate(self.system_model.links.keys()):
                components.append(f"Канал {source[:3]}-{target[:3]}")
                reliability_values.append(0.98 + np.random.uniform(-0.03, 0.02))
            
            # Обновляем график надежности компонентов
            if hasattr(self, 'reliability_ax'):
                self.reliability_ax.clear()
                self.reliability_ax.bar(range(len(components)), reliability_values, 
                                                color=BLOOD_ANGELS_COLORS['primary_gold'], alpha=0.7)
                self.reliability_ax.set_title("НАДЕЖНОСТЬ КОМПОНЕНТОВ")
                self.reliability_ax.set_xlabel("Компоненты")
                self.reliability_ax.set_ylabel("Надежность")
                self.reliability_ax.set_ylim(0, 1)
                
                # Поворачиваем подписи для лучшей читаемости
                self.reliability_ax.set_xticks(range(len(components)))
                self.reliability_ax.set_xticklabels(components, rotation=45, ha='right')
                
                self.reliability_canvas.draw()
            
        except Exception as e:
            print(f"Ошибка обновления графиков надежности: {e}")
    
    def _update_whatif_plots(self):
        """Обновляет What-if графики на основе созданной системы"""
        try:
            if not hasattr(self, 'system_model') or self.system_model is None:
                return
            
            # Получаем параметры системы
            num_nodes = len(self.system_model.nodes)
            num_links = len(self.system_model.links)
            
            # Генерируем данные для What-if анализа
            import numpy as np
            
            # Анализ чувствительности
            parameters = ['Узлы', 'Каналы', 'Нагрузка', 'Отказы']
            sensitivity_values = [num_nodes/50.0, num_links/30.0, 0.7, 0.1]
            
            # Обновляем график чувствительности
            if hasattr(self, 'sensitivity_ax'):
                self.sensitivity_ax.clear()
                self.sensitivity_ax.bar(parameters, sensitivity_values, 
                                              color=BLOOD_ANGELS_COLORS['primary_gold'], alpha=0.7)
                self.sensitivity_ax.set_title("ЧТО-ЕСЛИ ЧУВСТВИТЕЛЬНОСТЬ")
                self.sensitivity_ax.set_ylabel("Влияние")
                self.sensitivity_ax.set_ylim(0, 1)
                
                self.whatif_canvas.draw()
            
        except Exception as e:
            print(f"Ошибка обновления What-if графиков: {e}")
    
    def stop_simulation(self):
        """Останавливает симуляцию"""
        self.is_simulation_running = False
        self.status_var.set("╔═══ СИМУЛЯЦИЯ ОСТАНОВЛЕНА ═══╗")
        
        # Обновление кнопок
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Обновление индикаторов
        self.simulation_indicator.configure(bg=BLOOD_ANGELS_COLORS['warning'])
        self.analysis_indicator.configure(bg=BLOOD_ANGELS_COLORS['medium_gray'])
    
    def reset_simulation(self):
        """Сбрасывает симуляцию"""
        self.stop_simulation()
        self.simulation_data = []
        
        # Очистка графиков
        self.throughput_line.set_data([], [])
        self.latency_line.set_data([], [])
        self.reliability_line.set_data([], [])
        self.availability_line.set_data([], [])
        
        # Перерисовка
        self.metrics_canvas.draw()
        
        self.status_var.set("╔═══ СИСТЕМА СБРОШЕНА ═══╗")
    
    def _run_simulation(self):
        """Выполняет симуляцию"""
        import random
        import numpy as np
        
        # Проверяем, что система создана
        if not hasattr(self, 'system_model') or self.system_model is None:
            print("Ошибка: Сначала создайте систему")
            self.root.after(0, self._simulation_finished)
            return
        
        duration = float(self.duration_var.get())
        time_step = float(self.time_step_var.get())
        
        time_points = []
        throughput_data = []
        latency_data = []
        reliability_data = []
        availability_data = []
        
        # Используем количество узлов из созданной системы
        num_nodes = len(self.system_model.nodes)
        num_links = len(self.system_model.links)
        
        for t in np.arange(0, duration, time_step):
            if not self.is_simulation_running:
                break
            
            # Генерация данных симуляции на основе созданной системы
            # Пропускная способность зависит от количества каналов
            base_throughput = num_links * 20  # Базовое значение
            throughput = base_throughput + 50 * np.sin(t/10) + random.uniform(-10, 10)
            
            # Задержка зависит от сложности сети
            base_latency = 10 + num_nodes * 2  # Базовая задержка
            latency = base_latency + 10 * np.cos(t/5) + random.uniform(-5, 5)
            
            # Надежность зависит от количества узлов
            base_reliability = 0.95 - (num_nodes - 5) * 0.01  # Чем больше узлов, тем ниже надежность
            reliability = base_reliability + 0.05 * np.sin(t/20) + random.uniform(-0.02, 0.02)
            
            # Доступность
            availability = 0.98 + 0.02 * np.cos(t/15) + random.uniform(-0.01, 0.01)
            
            time_points.append(t)
            throughput_data.append(max(0, throughput))
            latency_data.append(max(0, latency))
            reliability_data.append(max(0, min(1, reliability)))
            availability_data.append(max(0, min(1, availability)))
            
            # Обновление графиков каждые 10 точек
            if len(time_points) % 10 == 0:
                self.root.after(0, self._update_plots, 
                              time_points.copy(), throughput_data.copy(),
                              latency_data.copy(), reliability_data.copy(),
                              availability_data.copy())
            
            time.sleep(time_step)
        
        # Завершение симуляции
        self.root.after(0, self._simulation_finished)
    
    def _update_plots(self, times, throughput, latency, reliability, availability):
        """Обновляет графики"""
        # Обновление данных
        self.throughput_line.set_data(times, throughput)
        self.latency_line.set_data(times, latency)
        self.reliability_line.set_data(times, reliability)
        self.availability_line.set_data(times, availability)
        
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
    
    def _simulation_finished(self):
        """Обработчик завершения симуляции"""
        self.is_simulation_running = False
        self.status_var.set("╔═══ МИССИЯ ЗАВЕРШЕНА ═══╗")
        
        # Обновление кнопок
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Обновление индикаторов
        self.simulation_indicator.configure(bg=BLOOD_ANGELS_COLORS['medium_gray'])
        self.analysis_indicator.configure(bg=BLOOD_ANGELS_COLORS['success'])
        
        # Показ результатов
        messagebox.showinfo("Результаты", 
                          "╔═══ СИМУЛЯЦИЯ ЗАВЕРШЕНА ═══╗\n"
                          "║ Анализ ИКС выполнен успешно! ║\n"
                          "║ Данные сохранены в системе   ║\n"
                          "╚═══════════════════════════════╝")
    
    # Новые методы для ИКС Анализатора
    def create_system(self):
        """Создает систему для анализа"""
        try:
            nodes = int(self.nodes_var.get())
            connection_prob = float(self.connection_prob_var.get())
            
            self.status_var.set("╔═══ СОЗДАНИЕ СИСТЕМЫ ═══╗")
            
            # Создаем систему
            self.system_model = SystemModel("Пользовательская ИКС")
            self.system_model.generate_random_network(nodes, connection_prob)
            
            # Обновляем визуализацию сети
            self._update_network_visualization()
            
            self.status_var.set("╔═══ СИСТЕМА СОЗДАНА ═══╗")
            messagebox.showinfo("Успех", f"Система создана: {nodes} узлов, {len(self.system_model.links)} каналов")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка создания системы: {e}")
    
    def run_reliability_analysis(self):
        """Запускает анализ надежности"""
        if not self.system_model:
            messagebox.showwarning("Предупреждение", "Сначала создайте систему!")
            return
        
        try:
            hours = float(self.reliability_hours_var.get())
            sims = int(self.monte_carlo_sims_var.get())
            
            self.status_var.set("╔═══ АНАЛИЗ НАДЕЖНОСТИ ═══╗")
            
            # Создаем анализатор надежности
            self.reliability_analyzer = ReliabilityAnalyzer(self.system_model)
            
            # Настраиваем параметры
            self._setup_reliability_parameters()
            
            # Анализ надежности
            reliability_results = self.reliability_analyzer.calculate_system_reliability(hours)
            
            # Анализ Монте-Карло
            mc_results = self.reliability_analyzer.monte_carlo_reliability_analysis(sims)
            
            # Сохраняем результаты
            self.analysis_results['reliability'] = {
                'component_reliability': reliability_results,
                'monte_carlo': mc_results
            }
            
            # Обновляем визуализацию
            self._update_reliability_visualization(reliability_results, mc_results)
            
            self.status_var.set("╔═══ АНАЛИЗ НАДЕЖНОСТИ ЗАВЕРШЕН ═══╗")
            messagebox.showinfo("Успех", f"Анализ надежности завершен!\nНадежность системы: {reliability_results.get('system_overall', 0):.4f}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка анализа надежности: {e}")
    
    def run_stress_tests(self):
        """Запускает стресс-тестирование"""
        if not self.system_model:
            messagebox.showwarning("Предупреждение", "Сначала создайте систему!")
            return
        
        try:
            duration = float(self.stress_duration_var.get())
            
            self.status_var.set("╔═══ СТРЕСС-ТЕСТИРОВАНИЕ ═══╗")
            
            # Создаем стресс-тестер
            self.stress_tester = StressTester(self.system_model)
            
            # Запускаем выбранные тесты
            results = []
            
            if self.stress_test_types['load_increase'].get():
                results.append(self.stress_tester.run_load_increase_test(duration=duration))
            
            if self.stress_test_types['failure_injection'].get():
                results.append(self.stress_tester.run_failure_injection_test(duration=duration))
            
            if self.stress_test_types['cascade_failure'].get():
                results.append(self.stress_tester.run_cascade_failure_test(duration=duration))
            
            if self.stress_test_types['network_congestion'].get():
                results.append(self.stress_tester.run_network_congestion_test(duration=duration))
            
            if self.stress_test_types['random_stress'].get():
                results.append(self.stress_tester.run_random_stress_test(duration=duration))
            
            # Сохраняем результаты
            self.analysis_results['stress_test'] = results
            
            # Обновляем визуализацию
            self._update_stress_test_visualization(results)
            
            successful_tests = sum(1 for result in results if result.success)
            self.status_var.set("╔═══ СТРЕСС-ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ═══╗")
            messagebox.showinfo("Успех", f"Стресс-тестирование завершено!\nУспешных тестов: {successful_tests}/{len(results)}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка стресс-тестирования: {e}")
    
    def run_whatif_analysis(self):
        """Запускает What-if анализ"""
        if not self.system_model:
            messagebox.showwarning("Предупреждение", "Сначала создайте систему!")
            return
        
        try:
            sims = int(self.whatif_sims_var.get())
            
            self.status_var.set("╔═══ WHAT-IF АНАЛИЗ ═══╗")
            
            # Создаем анализатор What-if
            self.whatif_analyzer = WhatIfAnalyzer(self.system_model)
            self.whatif_analyzer.create_baseline_system()
            
            # Настраиваем параметры
            self._setup_whatif_parameters()
            
            results = {}
            
            if self.whatif_analysis_types['sensitivity'].get():
                sensitivity_results = self.whatif_analyzer.analyze_parameter_sensitivity(
                    list(self.whatif_analyzer.parameter_ranges.values()), num_samples=20
                )
                results['sensitivity'] = sensitivity_results
            
            if self.whatif_analysis_types['monte_carlo'].get():
                mc_results = self.whatif_analyzer.monte_carlo_analysis(num_simulations=sims, simulation_duration=60)
                results['monte_carlo'] = mc_results
            
            # Сохраняем результаты
            self.analysis_results['whatif'] = results
            
            # Обновляем визуализацию
            self._update_whatif_visualization(results)
            
            self.status_var.set("╔═══ WHAT-IF АНАЛИЗ ЗАВЕРШЕН ═══╗")
            messagebox.showinfo("Успех", "What-if анализ завершен!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка What-if анализа: {e}")
    
    def run_full_analysis(self):
        """Запускает полный анализ системы"""
        if not self.system_model:
            messagebox.showwarning("Предупреждение", "Сначала создайте систему!")
            return
        
        try:
            self.status_var.set("╔═══ ПОЛНЫЙ АНАЛИЗ СИСТЕМЫ ═══╗")
            
            # Анализ надежности
            self.run_reliability_analysis()
            
            # Стресс-тестирование
            self.run_stress_tests()
            
            # What-if анализ
            self.run_whatif_analysis()
            
            self.status_var.set("╔═══ ПОЛНЫЙ АНАЛИЗ ЗАВЕРШЕН ═══╗")
            messagebox.showinfo("Успех", "Полный анализ системы завершен!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка полного анализа: {e}")
    
    def export_analysis_results(self):
        """Экспортирует результаты анализа"""
        if not self.analysis_results:
            messagebox.showwarning("Предупреждение", "Нет результатов для экспорта!")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Сохранить результаты анализа"
            )
            
            if filename:
                self.status_var.set("╔═══ ЭКСПОРТ РЕЗУЛЬТАТОВ ═══╗")
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Система
                    if self.system_model:
                        nodes_df, links_df = self.system_model.export_to_dataframe()
                        nodes_df.to_excel(writer, sheet_name='Узлы', index=False)
                        links_df.to_excel(writer, sheet_name='Каналы', index=False)
                    
                    # Результаты надежности
                    if 'reliability' in self.analysis_results:
                        reliability_data = self.analysis_results['reliability']
                        if 'report' in reliability_data:
                            reliability_data['report'].to_excel(writer, sheet_name='Надежность', index=False)
                    
                    # Результаты стресс-тестирования
                    if 'stress_test' in self.analysis_results:
                        stress_results = self.analysis_results['stress_test']
                        if stress_results:
                            report_data = []
                            for result in stress_results:
                                report_data.append({
                                    'scenario': result.scenario_name,
                                    'success': result.success,
                                    'failure_points': len(result.failure_points),
                                    'performance_degradation': result.performance_degradation
                                })
                            df = pd.DataFrame(report_data)
                            df.to_excel(writer, sheet_name='Стресс-тесты', index=False)
                
                self.status_var.set("╔═══ ЭКСПОРТ ЗАВЕРШЕН ═══╗")
                messagebox.showinfo("Успех", f"Результаты экспортированы в {filename}")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {e}")
    
    def _setup_reliability_parameters(self):
        """Настраивает параметры надежности"""
        if self.system_model is None or self.reliability_analyzer is None:
            return
        
        failure_rates = {}
        repair_rates = {}
        
        for node_id in self.system_model.nodes:
            failure_rates[node_id] = np.random.uniform(1e-5, 1e-3)
            repair_rates[node_id] = np.random.uniform(0.1, 1.0)
        
        for (source, target), link in self.system_model.links.items():
            link_id = f"{source}_{target}"
            failure_rates[link_id] = np.random.uniform(1e-6, 1e-4)
            repair_rates[link_id] = np.random.uniform(0.5, 2.0)
        
        self.reliability_analyzer.set_failure_rates(failure_rates)
        self.reliability_analyzer.set_repair_rates(repair_rates)
    
    def _setup_whatif_parameters(self):
        """Настраивает параметры What-if анализа"""
        if self.system_model is None or self.whatif_analyzer is None:
            return
        
        parameter_ranges = []
        
        for node_id, node in self.system_model.nodes.items():
            parameter_ranges.append(
                ParameterRange(
                    param_type=ParameterType.NODE_CAPACITY,
                    component_id=node_id,
                    min_value=node.capacity * 0.5,
                    max_value=node.capacity * 2.0,
                    default_value=node.capacity
                )
            )
        
        for (source, target), link in self.system_model.links.items():
            link_id = f"{source}_{target}"
            parameter_ranges.append(
                ParameterRange(
                    param_type=ParameterType.LINK_BANDWIDTH,
                    component_id=link_id,
                    min_value=link.bandwidth * 0.5,
                    max_value=link.bandwidth * 2.0,
                    default_value=link.bandwidth
                )
            )
        
        self.whatif_analyzer.set_parameter_ranges(parameter_ranges)
    
    def _update_network_visualization(self):
        """Обновляет визуализацию сети"""
        if not self.system_model:
            return
        
        # Переключаемся на вкладку сети
        self.viz_notebook.select(1)  # Вкладка "СЕТЬ"
        
        # Здесь можно добавить код для обновления визуализации сети
        # с использованием данных из self.system_model
    
    def _update_reliability_visualization(self, reliability_results, mc_results):
        """Обновляет визуализацию надежности"""
        # Переключаемся на вкладку надежности
        self.viz_notebook.select(3)  # Вкладка "НАДЕЖНОСТЬ"
        
        # Очищаем оси
        self.reliability_ax.clear()
        self.mttf_ax.clear()
        self.monte_carlo_ax.clear()
        self.fault_tree_ax.clear()
        
        # График надежности компонентов
        if reliability_results:
            components = list(reliability_results.keys())
            values = list(reliability_results.values())
            
            self.reliability_ax.bar(components[:5], values[:5], 
                                  color=BLOOD_ANGELS_COLORS['primary_red'], alpha=0.7)
            self.reliability_ax.set_title("НАДЕЖНОСТЬ КОМПОНЕНТОВ")
            self.reliability_ax.set_ylabel("Надежность")
        
        # График Монте-Карло
        if mc_results and 'throughput_samples' in mc_results:
            throughput_stats = mc_results['throughput_samples']
            self.monte_carlo_ax.bar(['Mean', 'Std', 'Min', 'Max'], 
                                  [throughput_stats['mean'], throughput_stats['std'], 
                                   throughput_stats['min'], throughput_stats['max']],
                                  color=BLOOD_ANGELS_COLORS['primary_gold'], alpha=0.7)
            self.monte_carlo_ax.set_title("АНАЛИЗ МОНТЕ-КАРЛО")
        
        # Перерисовка
        self.reliability_canvas.draw()
    
    def _update_stress_test_visualization(self, results):
        """Обновляет визуализацию стресс-тестов"""
        # Переключаемся на вкладку стресс-тестов
        self.viz_notebook.select(4)  # Вкладка "СТРЕСС-ТЕСТЫ"
        
        # Очищаем оси
        self.stress_results_ax.clear()
        self.degradation_ax.clear()
        self.failure_points_ax.clear()
        self.recovery_ax.clear()
        
        if results:
            # График результатов
            scenarios = [result.scenario_name for result in results]
            success_rates = [1 if result.success else 0 for result in results]
            
            self.stress_results_ax.bar(scenarios, success_rates, 
                                     color=BLOOD_ANGELS_COLORS['success'], alpha=0.7)
            self.stress_results_ax.set_title("РЕЗУЛЬТАТЫ СТРЕСС-ТЕСТОВ")
            self.stress_results_ax.set_ylabel("Успех (0/1)")
            
            # График деградации
            degradations = [result.performance_degradation for result in results]
            self.degradation_ax.bar(scenarios, degradations, 
                                  color=BLOOD_ANGELS_COLORS['warning'], alpha=0.7)
            self.degradation_ax.set_title("ДЕГРАДАЦИЯ ПРОИЗВОДИТЕЛЬНОСТИ")
            self.degradation_ax.set_ylabel("Деградация")
        
        # Перерисовка
        self.stress_canvas.draw()
    
    def _update_whatif_visualization(self, results):
        """Обновляет визуализацию What-if анализа"""
        # Переключаемся на вкладку What-if
        self.viz_notebook.select(5)  # Вкладка "WHAT-IF"
        
        # Очищаем оси
        self.sensitivity_ax.clear()
        self.whatif_monte_carlo_ax.clear()
        self.scenarios_ax.clear()
        self.optimization_ax.clear()
        
        # График чувствительности
        if 'sensitivity' in results:
            sensitivity_data = results['sensitivity']
            params = list(sensitivity_data.keys())
            means = [np.mean(values) if values else 0 for values in sensitivity_data.values()]
            
            self.sensitivity_ax.bar(params[:5], means[:5], 
                                  color=BLOOD_ANGELS_COLORS['info'], alpha=0.7)
            self.sensitivity_ax.set_title("ЧУВСТВИТЕЛЬНОСТЬ ПАРАМЕТРОВ")
            self.sensitivity_ax.set_ylabel("Среднее значение")
        
        # График Монте-Карло
        if 'monte_carlo' in results and 'throughput_samples' in results['monte_carlo']:
            mc_stats = results['monte_carlo']['throughput_samples']
            self.whatif_monte_carlo_ax.bar(['Mean', 'Std', 'Min', 'Max'], 
                                         [mc_stats['mean'], mc_stats['std'], 
                                          mc_stats['min'], mc_stats['max']],
                                         color=BLOOD_ANGELS_COLORS['primary_gold'], alpha=0.7)
            self.whatif_monte_carlo_ax.set_title("ЧТО-ЕСЛИ МОНТЕ-КАРЛО")
        
        # Перерисовка
        self.whatif_canvas.draw()


class ICSAnalyzer:
    """Основной класс ИКС Анализатора для CLI режима"""
    
    def __init__(self):
        self.system_model = None
        self.reliability_analyzer = None
        self.simulator = None
        self.stress_tester = None
        self.whatif_analyzer = None
        self.results = {}
    
    def create_sample_system(self) -> SystemModel:
        """Создать пример системы для анализа"""
        print("Создание примерной ИКС...")
        self.system_model = create_sample_network()
        
        print(f"Система создана: {self.system_model.name}")
        print(f"Узлов: {len(self.system_model.nodes)}")
        print(f"Каналов: {len(self.system_model.links)}")
        
        return self.system_model
    
    def create_custom_system(self, num_nodes: int = 10, connection_prob: float = 0.3) -> SystemModel:
        """Создать пользовательскую систему"""
        print(f"Создание пользовательской ИКС ({num_nodes} узлов, вероятность соединения {connection_prob})...")
        
        self.system_model = SystemModel("Пользовательская ИКС")
        self.system_model.generate_random_network(num_nodes, connection_prob)
        
        print(f"Система создана: {self.system_model.name}")
        print(f"Узлов: {len(self.system_model.nodes)}")
        print(f"Каналов: {len(self.system_model.links)}")
        
        return self.system_model
    
    def analyze_reliability(self, duration_hours: float = 8760) -> Dict:
        """Анализ надежности системы"""
        if not self.system_model:
            raise ValueError("Сначала создайте систему")
        
        print(f"\n=== Анализ надежности (на {duration_hours} часов) ===")
        
        # Создаем анализатор надежности
        self.reliability_analyzer = ReliabilityAnalyzer(self.system_model)
        
        # Устанавливаем частоты отказов и восстановления
        self._setup_reliability_parameters()
        
        # Рассчитываем надежность системы
        reliability_results = self.reliability_analyzer.calculate_system_reliability(duration_hours)
        
        # Анализ связности сети
        connectivity_reliability = self.reliability_analyzer.calculate_network_connectivity_reliability()
        
        # Анализ Монте-Карло
        print("Проведение анализа Монте-Карло...")
        mc_results = self.reliability_analyzer.monte_carlo_reliability_analysis(1000)
        
        # Генерируем отчет
        report = self.reliability_analyzer.generate_reliability_report()
        
        self.results['reliability'] = {
            'component_reliability': reliability_results,
            'connectivity_reliability': connectivity_reliability,
            'monte_carlo': mc_results,
            'report': report
        }
        
        print(f"Надежность системы: {reliability_results.get('system_overall', 0):.4f}")
        print(f"Надежность связности: {connectivity_reliability:.4f}")
        print(f"Надежность (Монте-Карло): {mc_results.get('system_reliability', 0):.4f}")
        print(f"Среднее время работы: {mc_results.get('average_uptime', 0):.1f} часов в год")
        
        return self.results['reliability']
    
    def run_simulation(self, duration: float = 300) -> Dict:
        """Запуск имитационного моделирования"""
        if not self.system_model:
            raise ValueError("Сначала создайте систему")
        
        print(f"\n=== Имитационное моделирование ({duration} секунд) ===")
        
        # Создаем симулятор
        self.simulator = NetworkSimulator(self.system_model, duration)
        
        # Запускаем симуляцию
        print("Запуск симуляции...")
        self.simulator.run_simulation()
        
        # Получаем результаты
        simulation_results = self.simulator.get_simulation_results()
        
        # Экспортируем данные
        events_df = self.simulator.export_events_to_dataframe()
        metrics_df = self.simulator.export_metrics_to_dataframe()
        
        self.results['simulation'] = {
            'metrics': simulation_results['metrics'],
            'events': simulation_results['events'],
            'events_dataframe': events_df,
            'metrics_dataframe': metrics_df
        }
        
        metrics = simulation_results['metrics']
        print(f"Всего запросов: {metrics.get('total_requests', 0)}")
        print(f"Успешных запросов: {metrics.get('successful_requests', 0)}")
        print(f"Успешность: {metrics.get('success_rate', 0):.3f}")
        print(f"Среднее время отклика: {metrics.get('average_response_time', 0):.3f} сек")
        print(f"Пропускная способность: {metrics.get('network_throughput', 0):.2f} Мбит/сек")
        
        return self.results['simulation']
    
    def run_stress_tests(self, duration: float = 300) -> Dict:
        """Запуск стресс-тестирования"""
        if not self.system_model:
            raise ValueError("Сначала создайте систему")
        
        print(f"\n=== Стресс-тестирование ({duration} секунд) ===")
        
        # Создаем стресс-тестер
        self.stress_tester = StressTester(self.system_model)
        
        # Запускаем все стресс-тесты
        stress_results = self.stress_tester.run_all_stress_tests(duration)
        
        # Генерируем отчет
        report = self.stress_tester.generate_stress_test_report()
        
        self.results['stress_test'] = {
            'results': stress_results,
            'report': report
        }
        
        print(f"Выполнено {len(stress_results)} стресс-тестов")
        successful_tests = sum(1 for result in stress_results if result.success)
        print(f"Успешных тестов: {successful_tests}/{len(stress_results)}")
        
        return self.results['stress_test']
    
    def run_whatif_analysis(self, scenarios: Optional[List[Dict]] = None) -> Dict:
        """Запуск What-if анализа"""
        if not self.system_model:
            raise ValueError("Сначала создайте систему")
        
        print(f"\n=== What-if анализ ===")
        
        # Создаем анализатор What-if
        self.whatif_analyzer = WhatIfAnalyzer(self.system_model)
        self.whatif_analyzer.create_baseline_system()
        
        # Устанавливаем диапазоны параметров
        self._setup_whatif_parameters()
        
        whatif_results = {}
        
        # Анализ чувствительности
        print("Анализ чувствительности параметров...")
        sensitivity_results = self.whatif_analyzer.analyze_parameter_sensitivity(
            list(self.whatif_analyzer.parameter_ranges.values()), num_samples=20
        )
        whatif_results['sensitivity'] = sensitivity_results
        
        # Анализ Монте-Карло
        print("Анализ методом Монте-Карло...")
        mc_results = self.whatif_analyzer.monte_carlo_analysis(num_simulations=100, simulation_duration=60)
        whatif_results['monte_carlo'] = mc_results
        
        # Анализ отдельных сценариев
        if scenarios:
            print("Анализ пользовательских сценариев...")
            scenario_results = self._analyze_custom_scenarios(scenarios)
            whatif_results['scenarios'] = scenario_results
        
        # Генерируем отчет
        report = self.whatif_analyzer.generate_whatif_report()
        whatif_results['report'] = report
        
        self.results['whatif'] = whatif_results
        
        print("What-if анализ завершен")
        
        return self.results['whatif']
    
    def _setup_reliability_parameters(self):
        """Настройка параметров надежности"""
        if self.system_model is None or self.reliability_analyzer is None:
            return
        
        # Частоты отказов (отказов в час)
        failure_rates = {}
        for node_id in self.system_model.nodes:
            failure_rates[node_id] = np.random.uniform(1e-5, 1e-3)
        
        for (source, target), link in self.system_model.links.items():
            link_id = f"{source}_{target}"
            failure_rates[link_id] = np.random.uniform(1e-6, 1e-4)
        
        # Частоты восстановления (восстановлений в час)
        repair_rates = {}
        for node_id in self.system_model.nodes:
            repair_rates[node_id] = np.random.uniform(0.1, 1.0)  # 1-10 часов на восстановление
        
        for (source, target), link in self.system_model.links.items():
            link_id = f"{source}_{target}"
            repair_rates[link_id] = np.random.uniform(0.5, 2.0)  # 0.5-2 часа на восстановление
        
        self.reliability_analyzer.set_failure_rates(failure_rates)
        self.reliability_analyzer.set_repair_rates(repair_rates)
    
    def _setup_whatif_parameters(self):
        """Настройка параметров What-if анализа"""
        if self.system_model is None or self.whatif_analyzer is None:
            return
        
        parameter_ranges = []
        
        # Диапазоны для узлов
        for node_id, node in self.system_model.nodes.items():
            parameter_ranges.append(
                ParameterRange(
                    param_type=ParameterType.NODE_CAPACITY,
                    component_id=node_id,
                    min_value=node.capacity * 0.5,
                    max_value=node.capacity * 2.0,
                    default_value=node.capacity
                )
            )
        
        # Диапазоны для каналов
        for (source, target), link in self.system_model.links.items():
            link_id = f"{source}_{target}"
            parameter_ranges.append(
                ParameterRange(
                    param_type=ParameterType.LINK_BANDWIDTH,
                    component_id=link_id,
                    min_value=link.bandwidth * 0.5,
                    max_value=link.bandwidth * 2.0,
                    default_value=link.bandwidth
                )
            )
        
        self.whatif_analyzer.set_parameter_ranges(parameter_ranges)
    
    def _analyze_custom_scenarios(self, scenarios: List[Dict]) -> List:
        """Анализ пользовательских сценариев"""
        if self.whatif_analyzer is None:
            return []
        
        from src.whatif import WhatIfScenario
        
        whatif_scenarios = []
        for scenario in scenarios:
            whatif_scenario = WhatIfScenario(
                name=scenario.get('name', 'Пользовательский сценарий'),
                description=scenario.get('description', ''),
                parameter_changes=scenario.get('parameter_changes', {}),
                expected_impact=scenario.get('expected_impact', '')
            )
            whatif_scenarios.append(whatif_scenario)
        
        return self.whatif_analyzer.scenario_analysis(whatif_scenarios)
    
    def export_results(self, filename: str = "ics_analysis_results.xlsx"):
        """Экспорт результатов в Excel"""
        if not self.results:
            print("Нет результатов для экспорта")
            return
        
        print(f"Экспорт результатов в {filename}...")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Общие метрики системы
            if self.system_model:
                nodes_df, links_df = self.system_model.export_to_dataframe()
                nodes_df.to_excel(writer, sheet_name='Узлы', index=False)
                links_df.to_excel(writer, sheet_name='Каналы', index=False)
            
            # Результаты надежности
            if 'reliability' in self.results:
                reliability_data = self.results['reliability']
                if 'report' in reliability_data:
                    reliability_data['report'].to_excel(writer, sheet_name='Надежность', index=False)
            
            # Результаты симуляции
            if 'simulation' in self.results:
                simulation_data = self.results['simulation']
                if 'events_dataframe' in simulation_data and not simulation_data['events_dataframe'].empty:
                    simulation_data['events_dataframe'].to_excel(writer, sheet_name='События', index=False)
                if 'metrics_dataframe' in simulation_data and not simulation_data['metrics_dataframe'].empty:
                    simulation_data['metrics_dataframe'].to_excel(writer, sheet_name='Метрики', index=False)
            
            # Результаты стресс-тестирования
            if 'stress_test' in self.results:
                stress_data = self.results['stress_test']
                if 'report' in stress_data and not stress_data['report'].empty:
                    stress_data['report'].to_excel(writer, sheet_name='Стресс-тесты', index=False)
            
            # Результаты What-if анализа
            if 'whatif' in self.results:
                whatif_data = self.results['whatif']
                if 'report' in whatif_data and not whatif_data['report'].empty:
                    whatif_data['report'].to_excel(writer, sheet_name='What-if', index=False)
        
        print(f"Результаты экспортированы в {filename}")
    
    def print_summary(self):
        """Вывести краткое резюме анализа"""
        print("\n" + "="*60)
        print("           РЕЗЮМЕ АНАЛИЗА ИКС")
        print("="*60)
        
        if not self.results:
            print("Анализ не проводился")
            return
        
        # Информация о системе
        if self.system_model:
            print(f"Система: {self.system_model.name}")
            print(f"Узлов: {len(self.system_model.nodes)}")
            print(f"Каналов: {len(self.system_model.links)}")
        
        # Результаты надежности
        if 'reliability' in self.results:
            reliability = self.results['reliability']
            print(f"\nНадежность:")
            print(f"  Общая надежность: {reliability['component_reliability'].get('system_overall', 0):.4f}")
            print(f"  Надежность связности: {reliability['connectivity_reliability']:.4f}")
        
        # Результаты симуляции
        if 'simulation' in self.results:
            simulation = self.results['simulation']['metrics']
            print(f"\nСимуляция:")
            print(f"  Успешность: {simulation.get('success_rate', 0):.3f}")
            print(f"  Пропускная способность: {simulation.get('network_throughput', 0):.2f} Мбит/сек")
            print(f"  Время отклика: {simulation.get('average_response_time', 0):.3f} сек")
        
        # Результаты стресс-тестирования
        if 'stress_test' in self.results:
            stress_results = self.results['stress_test']['results']
            successful_tests = sum(1 for result in stress_results if result.success)
            print(f"\nСтресс-тестирование:")
            print(f"  Успешных тестов: {successful_tests}/{len(stress_results)}")
        
        print("="*60)


def main():
    """Главная функция запуска приложения"""
    import argparse
    import sys
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        # Проверяем специальный аргумент для GUI
        if sys.argv[1] in ['critics', 'gui', '-gui', '--gui']:
            return run_gui_mode()
        # CLI режим
        return run_cli_mode()
    else:
        # GUI режим по умолчанию
        return run_gui_mode()


def run_cli_mode():
    """Запуск в режиме командной строки"""
    import argparse
    parser = argparse.ArgumentParser(
        description="ИКС Анализатор Системы - Анализ информационно-коммуникационных систем",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

1. Полный анализ примерной системы:
   python main.py --full-analysis

2. Создание пользовательской системы и анализ надежности:
   python main.py --custom-system --nodes 15 --connection-prob 0.4 --reliability

3. Только симуляция:
   python main.py --simulation --duration 600

4. Стресс-тестирование:
   python main.py --stress-tests --duration 300

5. What-if анализ:
   python main.py --whatif-analysis
        """
    )
    
    # Основные опции
    parser.add_argument('--full-analysis', action='store_true',
                       help='Выполнить полный анализ системы')
    parser.add_argument('--custom-system', action='store_true',
                       help='Создать пользовательскую систему')
    parser.add_argument('--nodes', type=int, default=10,
                       help='Количество узлов для пользовательской системы (по умолчанию: 10)')
    parser.add_argument('--connection-prob', type=float, default=0.3,
                       help='Вероятность соединения для пользовательской системы (по умолчанию: 0.3)')
    
    # Отдельные виды анализа
    parser.add_argument('--reliability', action='store_true',
                       help='Анализ надежности')
    parser.add_argument('--simulation', action='store_true',
                       help='Имитационное моделирование')
    parser.add_argument('--stress-tests', action='store_true',
                       help='Стресс-тестирование')
    parser.add_argument('--whatif-analysis', action='store_true',
                       help='What-if анализ')
    
    # Параметры анализа
    parser.add_argument('--duration', type=float, default=300,
                       help='Длительность симуляции в секундах (по умолчанию: 300)')
    parser.add_argument('--reliability-hours', type=float, default=8760,
                       help='Время для анализа надежности в часах (по умолчанию: 8760)')
    
    # Экспорт результатов
    parser.add_argument('--export', type=str, default='ics_analysis_results.xlsx',
                       help='Имя файла для экспорта результатов (по умолчанию: ics_analysis_results.xlsx)')
    
    args = parser.parse_args()
    
    # Создаем анализатор
    analyzer = ICSAnalyzer()
    
    try:
        # Создаем систему
        if args.custom_system:
            analyzer.create_custom_system(args.nodes, args.connection_prob)
        else:
            analyzer.create_sample_system()
        
        # Выполняем анализ
        if args.full_analysis:
            print("\n=== ПОЛНЫЙ АНАЛИЗ СИСТЕМЫ ===")
            analyzer.analyze_reliability(args.reliability_hours)
            analyzer.run_simulation(args.duration)
            analyzer.run_stress_tests(args.duration)
            analyzer.run_whatif_analysis()
        else:
            # Отдельные виды анализа
            if args.reliability:
                analyzer.analyze_reliability(args.reliability_hours)
            
            if args.simulation:
                analyzer.run_simulation(args.duration)
            
            if args.stress_tests:
                analyzer.run_stress_tests(args.duration)
            
            if args.whatif_analysis:
                analyzer.run_whatif_analysis()
        
        # Экспортируем результаты
        analyzer.export_results(args.export)
        
        # Выводим резюме
        analyzer.print_summary()
        
    except Exception as e:
        print(f"Ошибка при выполнении анализа: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def run_gui_mode():
    """Запуск в режиме графического интерфейса"""
    print("=== ИКС АНАЛИЗАТОР СИСТЕМЫ ===")
    print("Система мониторинга и анализа информационно-коммуникационных сетей")
    print("в неблагоприятных условиях с использованием передовых технологий")
    print("и современного интерфейса для профессионального анализа")
    print()
    print("Цветовая схема:")
    print("• Темно-красный (#8B0000) - основной цвет интерфейса")
    print("• Кримсон (#DC143C) - вторичный красный")
    print("• Золотой (#DAA520) - акцентный цвет")
    print("• Черный (#1C1C1C) - базовый фон")
    print()
    print("Особенности интерфейса:")
    print("• Современная эстетика с ASCII-рамками")
    print("• Темная цветовая схема для снижения усталости глаз")
    print("• Высококонтрастные элементы управления")
    print("• Стилизованные графики и визуализации")
    print()
    
    # Создание главного окна
    root = tk.Tk()
    
    # Загрузка конфигурации
    config_path = 'config.json'
    if os.path.exists(config_path):
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        # Базовая конфигурация по умолчанию
        config = {
            "simulation": {"time_steps": 1000, "dt": 0.1, "random_seed": 42},
            "network": {"nodes": 10, "connections": 0.3, "bandwidth": 1000, "latency": 10, "reliability": 0.95},
            "adverse_conditions": {"noise_level": 0.1, "interference_probability": 0.05, "failure_rate": 0.02}
        }
    
    # Создание главного окна приложения с пагинацией
    app = NewMainWindow(root, config)
    
    # Центрирование окна на экране
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Запуск главного цикла
    print("=== СИСТЕМА ИНИЦИАЛИЗИРОВАНА ===")
    print("Интерфейс готов к работе")
    print("Запуск графического интерфейса")
    print()
    
    root.mainloop()
    
    print("=== СИСТЕМА ЗАВЕРШИЛА РАБОТУ ===")
    print("Благодарим за использование")
    print("ИКС Анализатора Системы")
    
    return 0


if __name__ == "__main__":
    main()
