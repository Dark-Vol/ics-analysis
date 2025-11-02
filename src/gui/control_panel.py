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
    
    def __init__(self, parent, frame, config):
        self.parent = parent
        self.frame = frame
        self.config = config
        self.theme = BloodAngelsTheme()
        
        # Создание фрейма в военном стиле (если frame не предоставлен)
        if not self.frame:
            self.frame = self.theme.create_military_frame(parent, 
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
        self.nodes_var = tk.IntVar(value=10)
        self.connection_prob_var = tk.DoubleVar(value=0.3)
        
        # Параметры симуляции
        self.duration_var = tk.DoubleVar(value=100.0)
        self.time_step_var = tk.DoubleVar(value=0.1)
        self.seed_var = tk.IntVar(value=42)
        
        # Флаги
        self.enable_traffic_var = tk.BooleanVar(value=True)
        self.enable_failures_var = tk.BooleanVar(value=True)
        self.enable_adverse_var = tk.BooleanVar(value=True)
        
        # Состояние симуляции
        self.simulation_state = False
    
    def _create_widgets(self):
        """Создает виджеты панели управления в военном стиле"""
        # Панель кнопок управления
        self._create_control_buttons()
        
        # Информационная панель
        self._create_info_panel()
    
    def _create_control_buttons(self):
        """Создает кнопки управления в военном стиле"""
        button_frame = ttk.Frame(self.frame, style='BloodAngels.TFrame')
        button_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Кнопка создания системы
        create_button = ttk.Button(button_frame, text="╔═══ СТВОРИТИ СИСТЕМУ ═══╗", 
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
        
        # Кнопка продолжения
        self.resume_button = ttk.Button(button_frame, text="╔═══ ПРОДОВЖИТИ ═══╗", 
                                       command=self._resume_simulation, 
                                       state=tk.DISABLED,
                                       style='BloodAngels.TButton')
        self.resume_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка остановки
        self.stop_button = ttk.Button(button_frame, text="╔═══ СТОП ═══╗", 
                                    command=self._stop_simulation, 
                                    state=tk.DISABLED,
                                    style='BloodAngels.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Кнопка сброса
        reset_button = ttk.Button(button_frame, text="╔═══ СКИНУТИ ═══╗", 
                                command=self._reset_simulation,
                                style='BloodAngels.TButton')
        reset_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Кнопка генерации отчета
        report_button = ttk.Button(button_frame, text="╔═══ ЗВІТ ═══╗", 
                                  command=self._generate_report,
                                  style='BloodAngels.TButton')
        report_button.pack(side=tk.RIGHT, padx=(5, 0))
    
    def _create_info_panel(self):
        """Создает информационную панель"""
        info_frame = ttk.LabelFrame(self.frame, text="╔═══ ІНФОРМАЦІЯ ═══╗", 
                                   style='BloodAngels.TLabelframe')
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Контейнер с прокруткой
        canvas = tk.Canvas(info_frame, bg=self.theme.COLORS['bg_secondary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='BloodAngels.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Информационные блоки
        info_text = """
╔═══════════════════════════════════╗
║   СИСТЕМА УПРАВЛІННЯ МЕРЕЖАМИ     ║
╚═══════════════════════════════════╝

Для створення або завантаження мережі
використовуйте кнопку "СОЗДАТЬ СЕТЬ"
в головному вікні програми.

═══════════════════════════════════

КНОПКИ УПРАВЛІННЯ:

• СТВОРИТИ СИСТЕМУ
  Генерація нової мережевої системи
  
• ЗАПУСК
  Запуск симуляції мережі
  
• ПАУЗА
  Тимчасова зупинка симуляції
  
• ПРОДОВЖИТИ
  Відновлення симуляції
  
• СТОП
  Повна зупинка симуляції
  
• СКИНУТИ
  Скидання всіх налаштувань
  
• ЗВІТ
  Генерація звіту по аналізу

═══════════════════════════════════

ОСНОВНІ ВОЗМОЖНОСТІ:

1. Створення моделі мережі
   З множинними вузлами та з'єднаннями

2. Симуляція роботи
   З аналізом продуктивності

3. Моніторинг в реальному часі
   Графіки та статистика

4. Аналіз надійності
   Оцінка стійкості системи

5. Стрес-тестування
   Перевірка при навантаженні

6. Генерація звітів
   Детальна документація

═══════════════════════════════════

СТАТУС: Очікування команд
"""
        
        info_label = tk.Label(scrollable_frame, 
                             text=info_text,
                             bg=self.theme.COLORS['bg_secondary'],
                             fg=self.theme.COLORS['text_secondary'],
                             font=self.theme.FONTS['body'],
                             justify=tk.LEFT,
                             anchor=tk.NW,
                             padx=10,
                             pady=10)
        info_label.pack(fill=tk.BOTH, expand=True)
        
        # Привязка прокрутки колесиком мыши и тачпадом
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        # Привязка прокрутки
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Button-4>", _on_mousewheel_linux)
            widget.bind("<Button-5>", _on_mousewheel_linux)
        
        # Привязываем к canvas, scrollable_frame и info_frame
        bind_mousewheel(canvas)
        bind_mousewheel(scrollable_frame)
        bind_mousewheel(info_frame)
        
        # Упаковка canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _load_defaults(self):
        """Загружает значения по умолчанию из конфигурации"""
        self.nodes_var.set(self.config.get('network.nodes', 10))
        self.connection_prob_var.set(self.config.get('network.connections', 0.3))
        self.duration_var.set(self.config.get('simulation.time_steps', 1000) * self.config.get('simulation.dt', 0.1))
        self.time_step_var.set(self.config.get('simulation.dt', 0.1))
        self.seed_var.set(self.config.get('simulation.random_seed', 42))
    
    def _create_system(self):
        """Создает систему"""
        # Открываем диалог создания сети вместо использования несуществующих переменных
        if hasattr(self.parent, '_open_network_dialog'):
            self.parent._open_network_dialog()
        else:
            # Fallback - вызываем метод напрямую
            self.parent.create_system()
    
    def _start_simulation(self):
        """Запускает симуляцию"""
        self.parent.start_simulation()
    
    def _pause_simulation(self):
        """Приостанавливает симуляцию"""
        if hasattr(self.parent, 'pause_simulation'):
            self.parent.pause_simulation()
        elif hasattr(self.parent, 'program_state_manager'):
            self.parent.program_state_manager.pause_program()
            self._update_button_states()
    
    def _resume_simulation(self):
        """Возобновляет симуляцию"""
        if hasattr(self.parent, 'resume_simulation'):
            self.parent.resume_simulation()
        elif hasattr(self.parent, 'program_state_manager'):
            self.parent.program_state_manager.resume_program()
            self._update_button_states()
    
    def _stop_simulation(self):
        """Останавливает симуляцию"""
        if hasattr(self.parent, 'stop_simulation'):
            self.parent.stop_simulation()
        elif hasattr(self.parent, 'program_state_manager'):
            self.parent.program_state_manager.stop_program()
            self._update_button_states()
    
    def _reset_simulation(self):
        """Сбрасывает симуляцию"""
        if hasattr(self.parent, '_reset_simulation'):
            self.parent._reset_simulation()
    
    def _generate_report(self):
        """Генерирует отчет в Word"""
        if hasattr(self.parent, 'generate_report'):
            self.parent.generate_report()
    
    def set_simulation_state(self, is_running):
        """Устанавливает состояние симуляции"""
        self.simulation_state = is_running
        self._update_button_states()
    
    def _update_button_states(self):
        """Обновляет состояния кнопок в зависимости от состояния программы"""
        if not hasattr(self.parent, 'program_state_manager'):
            return
        
        state_manager = self.parent.program_state_manager
        state = state_manager.state.value
        
        if state == 'running':
            # Программа запущена
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        elif state == 'paused':
            # Программа на паузе
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
        elif state == 'stopped':
            # Программа остановлена
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
        else:
            # Неизвестное состояние
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.DISABLED)
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

