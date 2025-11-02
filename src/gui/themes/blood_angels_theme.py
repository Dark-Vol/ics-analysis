#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тема Кровавых Ангелов для GUI приложения
Цветовая схема в стиле Warhammer 40,000 Blood Angels
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

class BloodAngelsTheme:
    """Тема Кровавых Ангелов с военной эстетикой"""
    
    # Основная цветовая палитра
    COLORS = {
        # Основные цвета
        'primary_red': '#8B0000',      # Темно-красный (основной)
        'secondary_red': '#DC143C',    # Кримсон (вторичный)
        'accent_red': '#FF4500',       # Оранжево-красный (акцент)
        'blood_red': '#B22222',        # Кроваво-красный
        
        # Золотые цвета
        'primary_gold': '#DAA520',     # Золотой (основной)
        'secondary_gold': '#FFD700',   # Золотой (яркий)
        'accent_gold': '#FFA500',      # Оранжевое золото
        'dark_gold': '#B8860B',        # Темное золото
        
        # Черные и серые тона
        'primary_black': '#1C1C1C',    # Основной черный
        'secondary_black': '#2F2F2F',  # Вторичный черный
        'dark_gray': '#404040',        # Темно-серый
        'medium_gray': '#696969',      # Средне-серый
        'light_gray': '#A9A9A9',       # Светло-серый
        
        # Специальные цвета
        'warning': '#FF6B6B',          # Цвет предупреждения
        'success': '#4ECDC4',          # Цвет успеха
        'info': '#45B7D1',             # Цвет информации
        'danger': '#FF4757',           # Цвет опасности
        
        # Фоновые цвета
        'bg_primary': '#1C1C1C',       # Основной фон
        'bg_secondary': '#2F2F2F',     # Вторичный фон
        'bg_panel': '#404040',         # Фон панелей
        'bg_card': '#4A4A4A',          # Фон карточек
        
        # Текстовые цвета
        'text_primary': '#FFFFFF',     # Основной текст
        'text_secondary': '#DAA520',   # Вторичный текст (золотой)
        'text_muted': '#A9A9A9',       # Приглушенный текст
        'text_warning': '#FFD700',     # Текст предупреждения
    }
    
    # Шрифты
    FONTS = {
        'title': ('Arial', 16, 'bold'),
        'subtitle': ('Arial', 12, 'bold'),
        'body': ('Arial', 10),
        'small': ('Arial', 8),
        'monospace': ('Consolas', 9),
        'military': ('Courier New', 10, 'bold'),
    }
    
    @classmethod
    def configure_styles(cls, root):
        """Настраивает стили для tkinter виджетов"""
        style = ttk.Style()
        
        # Настройка темы
        style.theme_use('clam')
        
        # Стиль для Frame
        style.configure('BloodAngels.TFrame',
                       background=cls.COLORS['bg_secondary'],
                       relief='raised',
                       borderwidth=2)
        
        # Стиль для Label
        style.configure('BloodAngels.TLabel',
                       background=cls.COLORS['bg_secondary'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['body'])
        
        # Стиль для заголовков
        style.configure('BloodAngels.Title.TLabel',
                       background=cls.COLORS['bg_secondary'],
                       foreground=cls.COLORS['text_secondary'],
                       font=cls.FONTS['title'])
        
        # Стиль для кнопок
        style.configure('BloodAngels.TButton',
                       background=cls.COLORS['primary_red'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['body'],
                       borderwidth=2,
                       relief='raised')
        
        style.map('BloodAngels.TButton',
                 background=[('active', cls.COLORS['secondary_red']),
                           ('pressed', cls.COLORS['blood_red'])],
                 relief=[('pressed', 'sunken'),
                        ('active', 'raised')])
        
        # Стиль для специальных кнопок
        style.configure('BloodAngels.Gold.TButton',
                       background=cls.COLORS['primary_gold'],
                       foreground=cls.COLORS['primary_black'],
                       font=cls.FONTS['body'],
                       borderwidth=2,
                       relief='raised')
        
        style.map('BloodAngels.Gold.TButton',
                 background=[('active', cls.COLORS['secondary_gold']),
                           ('pressed', cls.COLORS['dark_gold'])],
                 relief=[('pressed', 'sunken'),
                        ('active', 'raised')])
        
        # Стиль для Entry
        style.configure('BloodAngels.TEntry',
                       fieldbackground=cls.COLORS['bg_panel'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=2,
                       insertcolor=cls.COLORS['text_primary'])
        
        # Стиль для Notebook
        style.configure('BloodAngels.TNotebook',
                       background=cls.COLORS['bg_secondary'],
                       borderwidth=2)
        
        style.configure('BloodAngels.TNotebook.Tab',
                       background=cls.COLORS['bg_panel'],
                       foreground=cls.COLORS['text_primary'],
                       padding=[20, 10],
                       font=cls.FONTS['body'])
        
        style.map('BloodAngels.TNotebook.Tab',
                 background=[('selected', cls.COLORS['primary_red']),
                           ('active', cls.COLORS['secondary_red'])],
                 foreground=[('selected', cls.COLORS['text_primary']),
                           ('active', cls.COLORS['text_primary'])])
        
        # Стиль для Progressbar
        style.configure('BloodAngels.Horizontal.TProgressbar',
                       background=cls.COLORS['primary_gold'],
                       troughcolor=cls.COLORS['bg_panel'],
                       borderwidth=2,
                       lightcolor=cls.COLORS['primary_gold'],
                       darkcolor=cls.COLORS['primary_gold'])
        
        # Стиль для Treeview
        style.configure('BloodAngels.Treeview',
                       background=cls.COLORS['bg_panel'],
                       foreground=cls.COLORS['text_primary'],
                       fieldbackground=cls.COLORS['bg_panel'],
                       borderwidth=2)
        
        style.configure('BloodAngels.Treeview.Heading',
                       background=cls.COLORS['primary_red'],
                       foreground=cls.COLORS['text_primary'],
                       font=cls.FONTS['body'])
        
        # Стиль для Scale
        style.configure('BloodAngels.Horizontal.TScale',
                       background=cls.COLORS['bg_secondary'],
                       troughcolor=cls.COLORS['bg_panel'],
                       borderwidth=2,
                       sliderlength=20)
        
        # Стиль для Spinbox
        style.configure('BloodAngels.TSpinbox',
                       fieldbackground=cls.COLORS['bg_panel'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=2,
                       arrowcolor=cls.COLORS['text_primary'])
        
        # Стиль для Checkbutton
        style.configure('BloodAngels.TCheckbutton',
                       background=cls.COLORS['bg_secondary'],
                       foreground=cls.COLORS['text_primary'],
                       focuscolor='none')
        
        # Стиль для Radiobutton
        style.configure('BloodAngels.TRadiobutton',
                       background=cls.COLORS['bg_secondary'],
                       foreground=cls.COLORS['text_primary'],
                       focuscolor='none')
        
        # Стиль для Combobox
        style.configure('BloodAngels.TCombobox',
                       fieldbackground=cls.COLORS['bg_panel'],
                       foreground=cls.COLORS['text_primary'],
                       borderwidth=2,
                       arrowcolor=cls.COLORS['text_primary'])
        
        # Стиль для LabelFrame
        style.configure('BloodAngels.TLabelframe',
                       background=cls.COLORS['bg_secondary'],
                       borderwidth=2,
                       relief='raised')
        
        style.configure('BloodAngels.TLabelframe.Label',
                       background=cls.COLORS['bg_secondary'],
                       foreground=cls.COLORS['text_secondary'],
                       font=cls.FONTS['subtitle'])
    
    @classmethod
    def configure_matplotlib_style(cls):
        """Настраивает стиль для matplotlib графиков"""
        plt.style.use('dark_background')
        
        # Настройка цветовой схемы
        blood_angels_colors = [
            cls.COLORS['primary_red'],
            cls.COLORS['secondary_red'],
            cls.COLORS['primary_gold'],
            cls.COLORS['secondary_gold'],
            cls.COLORS['accent_red'],
            cls.COLORS['blood_red']
        ]
        
        # Создание кастомной цветовой схемы
        cmap = LinearSegmentedColormap.from_list('BloodAngels', blood_angels_colors)
        # Регистрация цветовой схемы (пропускаем, если не поддерживается)
        try:
            from matplotlib.cm import register_cmap
            register_cmap('BloodAngels', cmap)
        except (AttributeError, ImportError):
            # Если регистрация не поддерживается, просто пропускаем
            pass
        
        # Настройка параметров matplotlib
        plt.rcParams.update({
            'figure.facecolor': cls.COLORS['bg_primary'],
            'axes.facecolor': cls.COLORS['bg_panel'],
            'axes.edgecolor': cls.COLORS['primary_gold'],
            'axes.labelcolor': cls.COLORS['text_primary'],
            'text.color': cls.COLORS['text_primary'],
            'xtick.color': cls.COLORS['text_primary'],
            'ytick.color': cls.COLORS['text_primary'],
            'grid.color': cls.COLORS['medium_gray'],
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
    
    @classmethod
    def create_gradient_background(cls, widget, color1, color2, direction='vertical'):
        """Создает градиентный фон для виджета"""
        # Это базовая реализация, можно расширить для создания реальных градиентов
        widget.configure(bg=color1)
    
    @classmethod
    def get_status_color(cls, status):
        """Возвращает цвет в зависимости от статуса"""
        status_colors = {
            'excellent': cls.COLORS['success'],
            'good': cls.COLORS['primary_gold'],
            'warning': cls.COLORS['warning'],
            'critical': cls.COLORS['danger'],
            'error': cls.COLORS['danger'],
            'normal': cls.COLORS['text_primary']
        }
        return status_colors.get(status.lower(), cls.COLORS['text_primary'])
    
    @classmethod
    def create_military_frame(cls, parent, title="", relief='raised', borderwidth=2):
        """Создает фрейм в военном стиле"""
        frame = tk.Frame(parent, 
                        bg=cls.COLORS['bg_panel'],
                        relief=relief,
                        borderwidth=borderwidth,
                        highlightbackground=cls.COLORS['primary_gold'],
                        highlightthickness=1)
        
        if title:
            title_frame = tk.Frame(frame, bg=cls.COLORS['primary_red'], height=30)
            title_frame.pack(fill=tk.X, padx=2, pady=2)
            title_frame.pack_propagate(False)
            
            title_label = tk.Label(title_frame, 
                                  text=title,
                                  bg=cls.COLORS['primary_red'],
                                  fg=cls.COLORS['text_primary'],
                                  font=cls.FONTS['subtitle'])
            title_label.pack(expand=True)
        
        return frame
    
    @classmethod
    def create_status_indicator(cls, parent, text, status='normal', size=(100, 30)):
        """Создает индикатор статуса в военном стиле"""
        frame = tk.Frame(parent, 
                        bg=cls.COLORS['bg_panel'],
                        relief='raised',
                        borderwidth=2,
                        width=size[0],
                        height=size[1])
        frame.pack_propagate(False)
        
        # Индикаторная полоса
        indicator = tk.Frame(frame, 
                           bg=cls.get_status_color(status),
                           width=5)
        indicator.pack(side=tk.LEFT, fill=tk.Y, padx=2, pady=2)
        
        # Текст
        label = tk.Label(frame,
                        text=text,
                        bg=cls.COLORS['bg_panel'],
                        fg=cls.COLORS['text_primary'],
                        font=cls.FONTS['small'])
        label.pack(expand=True)
        
        return frame, label
    
    @classmethod
    def create_metric_display(cls, parent, label_text, value_text="0.000", unit="", 
                            status='normal', width=150):
        """Создает отображение метрики в военном стиле"""
        frame = cls.create_military_frame(parent, width=width)
        
        # Заголовок метрики
        label = tk.Label(frame,
                        text=label_text,
                        bg=cls.COLORS['bg_panel'],
                        fg=cls.COLORS['text_secondary'],
                        font=cls.FONTS['small'])
        label.pack(pady=(5, 0))
        
        # Значение метрики
        value_label = tk.Label(frame,
                              text=f"{value_text} {unit}",
                              bg=cls.COLORS['bg_panel'],
                              fg=cls.get_status_color(status),
                              font=cls.FONTS['body'])
        value_label.pack()
        
        # Индикаторная полоса
        indicator = tk.Frame(frame,
                           bg=cls.get_status_color(status),
                           height=3)
        indicator.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        return frame, value_label
    
    @classmethod
    def create_control_panel(cls, parent, title="КОНТРОЛЬНЫЙ ПАНЕЛЬ"):
        """Создает панель управления в военном стиле"""
        frame = cls.create_military_frame(parent, title=title)
        
        # Заголовок в военном стиле
        header_frame = tk.Frame(frame, bg=cls.COLORS['primary_red'], height=40)
        header_frame.pack(fill=tk.X, padx=2, pady=2)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text=f"╔═══ {title} ═══╗",
                               bg=cls.COLORS['primary_red'],
                               fg=cls.COLORS['text_primary'],
                               font=cls.FONTS['military'])
        header_label.pack(expand=True)
        
        return frame
    
    @classmethod
    def add_border_effect(cls, widget, color=None):
        """Добавляет эффект рамки к виджету"""
        if color is None:
            color = cls.COLORS['primary_gold']
        
        widget.configure(highlightbackground=color,
                        highlightthickness=1)
        return widget
