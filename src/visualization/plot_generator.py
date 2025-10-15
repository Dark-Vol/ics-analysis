#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор графиков для анализа ИКС
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
from ..models.performance_metrics import MetricsSnapshot

class PlotGenerator:
    """Генератор графиков для визуализации данных"""
    
    def __init__(self):
        # Настройка стиля matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Русская локализация
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'Arial']
        
    def create_metrics_timeline(self, metrics_history: List[MetricsSnapshot], 
                               metrics: List[str] = None) -> plt.Figure:
        """Создает график метрик во времени"""
        if not metrics_history:
            return self._create_empty_figure("Нет данных для отображения")
        
        if metrics is None:
            metrics = ['throughput', 'latency', 'reliability', 'availability']
        
        # Подготовка данных
        timestamps = [m.timestamp for m in metrics_history]
        
        # Создание подграфиков
        n_metrics = len(metrics)
        fig, axes = plt.subplots(n_metrics, 1, figsize=(12, 3 * n_metrics))
        
        if n_metrics == 1:
            axes = [axes]
        
        # Настройка подграфиков
        for i, metric in enumerate(metrics):
            values = [getattr(m, metric) for m in metrics_history]
            
            axes[i].plot(timestamps, values, linewidth=2, alpha=0.8)
            axes[i].set_title(self._get_metric_title(metric), fontsize=12, fontweight='bold')
            axes[i].set_xlabel('Время (с)')
            axes[i].set_ylabel(self._get_metric_unit(metric))
            axes[i].grid(True, alpha=0.3)
            
            # Добавление статистики
            mean_val = np.mean(values)
            axes[i].axhline(y=mean_val, color='red', linestyle='--', alpha=0.7, 
                           label=f'Среднее: {mean_val:.2f}')
            axes[i].legend()
        
        plt.tight_layout()
        return fig
    
    def create_distribution_plot(self, metrics_history: List[MetricsSnapshot], 
                                metric: str) -> plt.Figure:
        """Создает график распределения метрики"""
        if not metrics_history:
            return self._create_empty_figure("Нет данных для отображения")
        
        values = [getattr(m, metric) for m in metrics_history if hasattr(m, metric)]
        
        if not values:
            return self._create_empty_figure(f"Нет данных для метрики {metric}")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Гистограмма
        ax1.hist(values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title(f'Распределение {self._get_metric_title(metric)}', fontweight='bold')
        ax1.set_xlabel(self._get_metric_unit(metric))
        ax1.set_ylabel('Частота')
        ax1.grid(True, alpha=0.3)
        
        # Добавление статистических линий
        mean_val = np.mean(values)
        median_val = np.median(values)
        ax1.axvline(mean_val, color='red', linestyle='--', label=f'Среднее: {mean_val:.2f}')
        ax1.axvline(median_val, color='green', linestyle='--', label=f'Медиана: {median_val:.2f}')
        ax1.legend()
        
        # Box plot
        ax2.boxplot(values, patch_artist=True, 
                   boxprops=dict(facecolor='lightblue', alpha=0.7))
        ax2.set_title(f'Box Plot {self._get_metric_title(metric)}', fontweight='bold')
        ax2.set_ylabel(self._get_metric_unit(metric))
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_correlation_matrix(self, metrics_history: List[MetricsSnapshot]) -> plt.Figure:
        """Создает матрицу корреляций между метриками"""
        if not metrics_history:
            return self._create_empty_figure("Нет данных для отображения")
        
        # Подготовка данных
        metrics = ['throughput', 'latency', 'reliability', 'availability', 'packet_loss', 'jitter']
        data = {}
        
        for metric in metrics:
            values = [getattr(m, metric) for m in metrics_history if hasattr(m, metric)]
            if values:
                data[metric] = values
        
        if len(data) < 2:
            return self._create_empty_figure("Недостаточно данных для корреляционного анализа")
        
        # Создание DataFrame
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Расчет корреляций
        correlation_matrix = df.corr()
        
        # Создание heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='coolwarm', 
                   center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        
        ax.set_title('Матрица корреляций метрик производительности', fontsize=14, fontweight='bold')
        
        # Русские названия метрик
        metric_names = {
            'throughput': 'Пропускная способность',
            'latency': 'Задержка',
            'reliability': 'Надежность',
            'availability': 'Доступность',
            'packet_loss': 'Потеря пакетов',
            'jitter': 'Джиттер'
        }
        
        ax.set_xticklabels([metric_names.get(m, m) for m in correlation_matrix.columns], rotation=45)
        ax.set_yticklabels([metric_names.get(m, m) for m in correlation_matrix.columns], rotation=0)
        
        plt.tight_layout()
        return fig
    
    def create_network_analysis_plot(self, network_metrics: Dict[str, Any]) -> plt.Figure:
        """Создает график анализа сети"""
        if not network_metrics:
            return self._create_empty_figure("Нет данных о сети")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # График связности
        connectivity_metrics = ['nodes_count', 'links_count', 'density']
        connectivity_values = [network_metrics.get(m, 0) for m in connectivity_metrics]
        connectivity_labels = ['Узлы', 'Связи', 'Плотность']
        
        axes[0, 0].bar(connectivity_labels, connectivity_values, color=['blue', 'green', 'orange'])
        axes[0, 0].set_title('Характеристики связности', fontweight='bold')
        axes[0, 0].set_ylabel('Количество')
        
        # График качества соединений
        quality_metrics = ['average_clustering', 'diameter', 'average_path_length']
        quality_values = [network_metrics.get(m, 0) for m in quality_metrics]
        quality_labels = ['Кластеризация', 'Диаметр', 'Средний путь']
        
        axes[0, 1].bar(quality_labels, quality_values, color=['purple', 'red', 'brown'])
        axes[0, 1].set_title('Качество соединений', fontweight='bold')
        axes[0, 1].set_ylabel('Значение')
        
        # Круговая диаграмма состояния сети
        states = ['Активные узлы', 'Неактивные узлы', 'Отказавшие связи']
        active_nodes = network_metrics.get('nodes_count', 0)
        total_nodes = network_metrics.get('total_nodes', active_nodes)
        inactive_nodes = total_nodes - active_nodes
        failed_links = network_metrics.get('failed_links', 0)
        
        state_values = [active_nodes, inactive_nodes, failed_links]
        state_colors = ['green', 'red', 'orange']
        
        axes[1, 0].pie(state_values, labels=states, colors=state_colors, autopct='%1.1f%%')
        axes[1, 0].set_title('Состояние сети', fontweight='bold')
        
        # График эффективности
        efficiency_metrics = ['throughput_efficiency', 'latency_efficiency', 'reliability_efficiency']
        efficiency_values = [network_metrics.get(m, 0) for m in efficiency_metrics]
        efficiency_labels = ['Пропускная способность', 'Задержка', 'Надежность']
        
        axes[1, 1].bar(efficiency_labels, efficiency_values, color=['cyan', 'magenta', 'yellow'])
        axes[1, 1].set_title('Эффективность сети', fontweight='bold')
        axes[1, 1].set_ylabel('Эффективность (%)')
        axes[1, 1].set_ylim(0, 100)
        
        plt.tight_layout()
        return fig
    
    def create_adverse_conditions_plot(self, adverse_conditions_data: Dict[str, Any]) -> plt.Figure:
        """Создает график неблагоприятных условий"""
        if not adverse_conditions_data:
            return self._create_empty_figure("Нет данных о неблагоприятных условиях")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # График типов условий
        condition_types = list(adverse_conditions_data.keys())
        condition_counts = list(adverse_conditions_data.values())
        
        axes[0, 0].bar(condition_types, condition_counts, color='red', alpha=0.7)
        axes[0, 0].set_title('Активные неблагоприятные условия', fontweight='bold')
        axes[0, 0].set_ylabel('Количество')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # График интенсивности условий
        intensities = [0.1, 0.2, 0.3, 0.4, 0.5]  # Примерные значения
        intensity_counts = [5, 3, 2, 1, 1]  # Примерные данные
        
        axes[0, 1].bar(intensities, intensity_counts, color='orange', alpha=0.7)
        axes[0, 1].set_title('Распределение интенсивности', fontweight='bold')
        axes[0, 1].set_xlabel('Интенсивность')
        axes[0, 1].set_ylabel('Количество')
        
        # График влияния на производительность
        metrics = ['Пропускная способность', 'Задержка', 'Надежность']
        impact_values = [0.8, 0.6, 0.9]  # Примерные значения влияния
        
        axes[1, 0].bar(metrics, impact_values, color='purple', alpha=0.7)
        axes[1, 0].set_title('Влияние на производительность', fontweight='bold')
        axes[1, 0].set_ylabel('Коэффициент влияния')
        axes[1, 0].set_ylim(0, 1)
        
        # Временная диаграмма условий
        time_points = np.linspace(0, 100, 50)
        noise_level = 0.1 + 0.05 * np.sin(time_points / 10)
        interference_level = 0.05 + 0.03 * np.cos(time_points / 15)
        
        axes[1, 1].plot(time_points, noise_level, label='Шум', linewidth=2)
        axes[1, 1].plot(time_points, interference_level, label='Помехи', linewidth=2)
        axes[1, 1].set_title('Динамика неблагоприятных условий', fontweight='bold')
        axes[1, 1].set_xlabel('Время (с)')
        axes[1, 1].set_ylabel('Интенсивность')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_performance_dashboard(self, metrics_history: List[MetricsSnapshot],
                                   network_metrics: Dict[str, Any],
                                   adverse_conditions: Dict[str, Any]) -> plt.Figure:
        """Создает дашборд производительности"""
        fig = plt.figure(figsize=(16, 12))
        
        # Создание сетки подграфиков
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # График пропускной способности
        ax1 = fig.add_subplot(gs[0, :2])
        if metrics_history:
            timestamps = [m.timestamp for m in metrics_history]
            throughput = [m.throughput for m in metrics_history]
            ax1.plot(timestamps, throughput, 'b-', linewidth=2, label='Пропускная способность')
            ax1.set_title('Пропускная способность во времени', fontweight='bold')
            ax1.set_ylabel('Мбит/с')
            ax1.grid(True, alpha=0.3)
            ax1.legend()
        
        # График задержки
        ax2 = fig.add_subplot(gs[0, 2:4])  # Исправлено: ограничиваем до 4 колонок
        if metrics_history:
            latency = [m.latency for m in metrics_history]
            ax2.plot(timestamps, latency, 'r-', linewidth=2, label='Задержка')
            ax2.set_title('Задержка во времени', fontweight='bold')
            ax2.set_ylabel('мс')
            ax2.grid(True, alpha=0.3)
            ax2.legend()
        
        # График надежности и доступности
        ax3 = fig.add_subplot(gs[1, :2])
        if metrics_history:
            reliability = [m.reliability for m in metrics_history]
            availability = [m.availability for m in metrics_history]
            ax3.plot(timestamps, reliability, 'g-', linewidth=2, label='Надежность')
            ax3.plot(timestamps, availability, 'm-', linewidth=2, label='Доступность')
            ax3.set_title('Надежность и доступность', fontweight='bold')
            ax3.set_ylabel('Значение')
            ax3.set_ylim(0, 1)
            ax3.grid(True, alpha=0.3)
            ax3.legend()
        
        # Состояние сети
        ax4 = fig.add_subplot(gs[1, 2:])
        if network_metrics:
            states = ['Узлы', 'Связи', 'Активные']
            values = [
                network_metrics.get('nodes_count', 0),
                network_metrics.get('links_count', 0),
                network_metrics.get('active_nodes', 0)
            ]
            ax4.bar(states, values, color=['blue', 'green', 'orange'])
            ax4.set_title('Состояние сети', fontweight='bold')
            ax4.set_ylabel('Количество')
        
        # Неблагоприятные условия
        ax5 = fig.add_subplot(gs[2, :2])
        if adverse_conditions:
            conditions = list(adverse_conditions.keys())
            counts = list(adverse_conditions.values())
            ax5.bar(conditions, counts, color='red', alpha=0.7)
            ax5.set_title('Неблагоприятные условия', fontweight='bold')
            ax5.set_ylabel('Количество')
            ax5.tick_params(axis='x', rotation=45)
        
        # Общий показатель качества
        ax6 = fig.add_subplot(gs[2, 2:])
        if metrics_history:
            quality_scores = []
            for m in metrics_history:
                # Упрощенный расчет качества
                quality = (m.reliability * 0.4 + m.availability * 0.4 + 
                          (1 - m.packet_loss) * 0.2)
                quality_scores.append(quality)
            
            ax6.plot(timestamps, quality_scores, 'purple', linewidth=3, label='Качество сети')
            ax6.set_title('Общий показатель качества', fontweight='bold')
            ax6.set_ylabel('Качество')
            ax6.set_xlabel('Время (с)')
            ax6.set_ylim(0, 1)
            ax6.grid(True, alpha=0.3)
            ax6.legend()
        
        return fig
    
    def _get_metric_title(self, metric: str) -> str:
        """Возвращает русское название метрики"""
        titles = {
            'throughput': 'Пропускная способность',
            'latency': 'Задержка',
            'reliability': 'Надежность',
            'availability': 'Доступность',
            'packet_loss': 'Потеря пакетов',
            'jitter': 'Джиттер',
            'energy_efficiency': 'Энергетическая эффективность'
        }
        return titles.get(metric, metric)
    
    def _get_metric_unit(self, metric: str) -> str:
        """Возвращает единицы измерения метрики"""
        units = {
            'throughput': 'Мбит/с',
            'latency': 'мс',
            'reliability': 'Безразмерная',
            'availability': 'Безразмерная',
            'packet_loss': '%',
            'jitter': 'мс',
            'energy_efficiency': 'Мбит/с/Вт'
        }
        return units.get(metric, '')
    
    def _create_empty_figure(self, message: str) -> plt.Figure:
        """Создает пустой график с сообщением"""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=16, 
                transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return fig







