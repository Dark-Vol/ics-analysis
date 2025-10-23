#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Панель отображения метрик в стиле Кровавых Ангелов
"""

import tkinter as tk
from tkinter import ttk
from ..models.performance_metrics import MetricsSnapshot
from .themes.blood_angels_theme import BloodAngelsTheme

class MetricsPanel:
    """Панель отображения метрик производительности в стиле Кровавых Ангелов"""
    
    def __init__(self, parent):
        self.parent = parent
        self.theme = BloodAngelsTheme()
        
        # Создание фрейма в военном стиле
        self.frame = self.theme.create_military_frame(parent.root, 
                                                   title="ПАНЕЛЬ МЕТРИК")
        
        # Текущие метрики
        self.current_metrics = None
        
        # Создание виджетов
        self._create_widgets()
    
    def _create_widgets(self):
        """Создает виджеты панели в военном стиле"""
        # Создание notebook для вкладок в стиле Кровавых Ангелов
        self.notebook = ttk.Notebook(self.frame, style='BloodAngels.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка "Текущие метрики"
        self.current_frame = ttk.Frame(self.notebook, style='BloodAngels.TFrame')
        self.notebook.add(self.current_frame, text="╔═══ ПОТОЧНІ ═══╗")
        self._create_current_metrics_tab()
        
        # Вкладка "Статистика"
        self.stats_frame = ttk.Frame(self.notebook, style='BloodAngels.TFrame')
        self.notebook.add(self.stats_frame, text="╔═══ СТАТИСТИКА ═══╗")
        self._create_stats_tab()
        
        # Вкладка "Качество"
        self.quality_frame = ttk.Frame(self.notebook, style='BloodAngels.TFrame')
        self.notebook.add(self.quality_frame, text="╔═══ ЯКІСТЬ ═══╗")
        self._create_quality_tab()
    
    def _create_current_metrics_tab(self):
        """Создает вкладку текущих метрик"""
        # Пропускная способность
        self._create_metric_row(self.current_frame, 0, "Пропускная способность:", "throughput", "Мбит/с")
        
        # Задержка
        self._create_metric_row(self.current_frame, 1, "Задержка:", "latency", "мс")
        
        # Надежность
        self._create_metric_row(self.current_frame, 2, "Надежность:", "reliability", "")
        
        # Доступность
        self._create_metric_row(self.current_frame, 3, "Доступность:", "availability", "")
        
        # Потеря пакетов
        self._create_metric_row(self.current_frame, 4, "Потеря пакетов:", "packet_loss", "%")
        
        # Джиттер
        self._create_metric_row(self.current_frame, 5, "Джиттер:", "jitter", "мс")
        
        # Энергетическая эффективность
        self._create_metric_row(self.current_frame, 6, "Энергоэффективность:", "energy_efficiency", "Мбит/с/Вт")
    
    def _create_stats_tab(self):
        """Создает вкладку статистики"""
        # Создание текстового виджета для статистики
        self.stats_text = tk.Text(self.stats_frame, height=15, width=30, wrap=tk.WORD)
        self.stats_scrollbar = ttk.Scrollbar(self.stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=self.stats_scrollbar.set)
        
        # Размещение виджетов
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stats_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопка обновления статистики
        update_button = ttk.Button(self.stats_frame, text="Оновити статистику", 
                                  command=self._update_statistics)
        update_button.pack(side=tk.BOTTOM, pady=5)
    
    def _create_quality_tab(self):
        """Создает вкладку качества"""
        # Показатель качества
        quality_label = ttk.Label(self.quality_frame, text="Загальний показник якості:", 
                                 font=("Arial", 10, "bold"))
        quality_label.pack(side=tk.TOP, pady=10)
        
        self.quality_var = tk.StringVar(value="0.000")
        quality_value_label = ttk.Label(self.quality_frame, textvariable=self.quality_var, 
                                       font=("Arial", 16, "bold"), foreground="blue")
        quality_value_label.pack(side=tk.TOP, pady=5)
        
        # Прогресс-бар качества
        self.quality_progress = ttk.Progressbar(self.quality_frame, length=200, mode='determinate')
        self.quality_progress.pack(side=tk.TOP, pady=10)
        
        # Описание качества
        self.quality_description = ttk.Label(self.quality_frame, text="Якість не оцінена", 
                                            wraplength=200, justify=tk.CENTER)
        self.quality_description.pack(side=tk.TOP, pady=10)
        
        # Кнопка расчета качества
        calculate_button = ttk.Button(self.quality_frame, text="Розрахувати якість", 
                                     command=self._calculate_quality)
        calculate_button.pack(side=tk.BOTTOM, pady=10)
    
    def _create_metric_row(self, parent, row, label_text, metric_name, unit):
        """Создает строку метрики"""
        # Метка названия
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        
        # Значение метрики
        var = tk.StringVar(value="0.000")
        setattr(self, f"{metric_name}_var", var)
        
        value_label = ttk.Label(parent, textvariable=var, font=("Arial", 9, "bold"))
        value_label.grid(row=row, column=1, sticky=tk.E, padx=5, pady=2)
        
        # Единицы измерения
        if unit:
            unit_label = ttk.Label(parent, text=unit, font=("Arial", 8))
            unit_label.grid(row=row, column=2, sticky=tk.W, padx=(0, 5), pady=2)
    
    def update_metrics(self, metrics: MetricsSnapshot):
        """Обновляет отображаемые метрики"""
        self.current_metrics = metrics
        
        # Обновление значений
        self.throughput_var.set(f"{metrics.throughput:.2f}")
        self.latency_var.set(f"{metrics.latency:.2f}")
        self.reliability_var.set(f"{metrics.reliability:.3f}")
        self.availability_var.set(f"{metrics.availability:.3f}")
        self.packet_loss_var.set(f"{metrics.packet_loss * 100:.2f}")
        self.jitter_var.set(f"{metrics.jitter:.2f}")
        self.energy_efficiency_var.set(f"{metrics.energy_efficiency:.2f}")
        
        # Обновление статистики
        self._update_statistics()
        
        # Обновление качества
        self._calculate_quality()
    
    def _update_statistics(self):
        """Обновляет статистику"""
        if not hasattr(self.parent, 'simulator') or not self.parent.simulator:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "Нет данных для статистики")
            return
        
        # Получение статистики
        stats = self.parent.simulator.performance_metrics.get_metric_statistics('throughput')
        
        if not stats:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "Недостаточно данных для статистики")
            return
        
        # Форматирование статистики
        stats_text = f"""СТАТИСТИКА ПРОПУСКНОЙ СПОСОБНОСТИ
===============================
Среднее: {stats.get('mean', 0):.2f} Мбит/с
Медиана: {stats.get('median', 0):.2f} Мбит/с
Стд. отклонение: {stats.get('std', 0):.2f} Мбит/с
Минимум: {stats.get('min', 0):.2f} Мбит/с
Максимум: {stats.get('max', 0):.2f} Мбит/с
25-й процентиль: {stats.get('q25', 0):.2f} Мбит/с
75-й процентиль: {stats.get('q75', 0):.2f} Мбит/с

СТАТИСТИКА ЗАДЕРЖКИ
===================
"""
        
        latency_stats = self.parent.simulator.performance_metrics.get_metric_statistics('latency')
        if latency_stats:
            stats_text += f"""Среднее: {latency_stats.get('mean', 0):.2f} мс
Медиана: {latency_stats.get('median', 0):.2f} мс
Стд. отклонение: {latency_stats.get('std', 0):.2f} мс
Минимум: {latency_stats.get('min', 0):.2f} мс
Максимум: {latency_stats.get('max', 0):.2f} мс
"""
        
        stats_text += f"""
СТАТИСТИКА НАДЕЖНОСТИ
====================
"""
        
        reliability_stats = self.parent.simulator.performance_metrics.get_metric_statistics('reliability')
        if reliability_stats:
            stats_text += f"""Среднее: {reliability_stats.get('mean', 0):.3f}
Медиана: {reliability_stats.get('median', 0):.3f}
Стд. отклонение: {reliability_stats.get('std', 0):.3f}
Минимум: {reliability_stats.get('min', 0):.3f}
Максимум: {reliability_stats.get('max', 0):.3f}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
    
    def _calculate_quality(self):
        """Рассчитывает показатель качества"""
        if not hasattr(self.parent, 'simulator') or not self.parent.simulator:
            self.quality_var.set("0.000")
            self.quality_progress['value'] = 0
            self.quality_description.config(text="Якість не оцінена")
            return
        
        # Получение показателя качества
        quality_score = self.parent.simulator.performance_metrics.get_quality_score()
        
        # Обновление отображения
        self.quality_var.set(f"{quality_score:.3f}")
        self.quality_progress['value'] = quality_score * 100
        
        # Описание качества
        if quality_score >= 0.9:
            description = "Отличное качество сети"
            color = "green"
        elif quality_score >= 0.7:
            description = "Хорошее качество сети"
            color = "blue"
        elif quality_score >= 0.5:
            description = "Удовлетворительное качество"
            color = "orange"
        else:
            description = "Плохое качество сети"
            color = "red"
        
        self.quality_description.config(text=description, foreground=color)
    
    def reset_metrics(self):
        """Сбрасывает метрики"""
        self.current_metrics = None
        
        # Сброс значений
        self.throughput_var.set("0.000")
        self.latency_var.set("0.000")
        self.reliability_var.set("0.000")
        self.availability_var.set("0.000")
        self.packet_loss_var.set("0.000")
        self.jitter_var.set("0.000")
        self.energy_efficiency_var.set("0.000")
        
        # Сброс статистики
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, "Статистика недоступна")
        
        # Сброс качества
        self.quality_var.set("0.000")
        self.quality_progress['value'] = 0
        self.quality_description.config(text="Якість не оцінена", foreground="black")

