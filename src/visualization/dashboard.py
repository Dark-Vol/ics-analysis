#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дашборд для визуализации данных ИКС
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional
from .plot_generator import PlotGenerator
from .chart_renderer import ChartRenderer

class Dashboard:
    """Дашборд для комплексной визуализации данных"""
    
    def __init__(self):
        self.plot_generator = PlotGenerator()
        self.chart_renderer = ChartRenderer()
    
    def create_performance_dashboard(self, metrics_history: List,
                                   network_metrics: Dict[str, Any],
                                   adverse_conditions: Dict[str, Any],
                                   traffic_analysis: Dict[str, Any]) -> plt.Figure:
        """Создает комплексный дашборд производительности"""
        fig = plt.figure(figsize=(20, 16))
        
        # Создание сетки подграфиков
        gs = fig.add_gridspec(4, 5, hspace=0.3, wspace=0.3)
        
        # 1. График пропускной способности (верхний левый)
        ax1 = fig.add_subplot(gs[0, :2])
        self._plot_throughput(ax1, metrics_history)
        
        # 2. График задержки (верхний центр)
        ax2 = fig.add_subplot(gs[0, 2:4])
        self._plot_latency(ax2, metrics_history)
        
        # 3. Индикатор качества (верхний правый)
        ax3 = fig.add_subplot(gs[0, 4])
        self._plot_quality_indicator(ax3, metrics_history)
        
        # 4. График надежности и доступности (второй ряд, левая половина)
        ax4 = fig.add_subplot(gs[1, :2])
        self._plot_reliability_availability(ax4, metrics_history)
        
        # 5. Состояние сети (второй ряд, правая половина)
        ax5 = fig.add_subplot(gs[1, 2:])
        self._plot_network_status(ax5, network_metrics)
        
        # 6. Неблагоприятные условия (третий ряд, левая половина)
        ax6 = fig.add_subplot(gs[2, :2])
        self._plot_adverse_conditions(ax6, adverse_conditions)
        
        # 7. Анализ трафика (третий ряд, правая половина)
        ax7 = fig.add_subplot(gs[2, 2:])
        self._plot_traffic_analysis(ax7, traffic_analysis)
        
        # 8. Статистика производительности (четвертый ряд, левая половина)
        ax8 = fig.add_subplot(gs[3, :2])
        self._plot_performance_stats(ax8, metrics_history)
        
        # 9. Рекомендации (четвертый ряд, правая половина)
        ax9 = fig.add_subplot(gs[3, 2:])
        self._plot_recommendations(ax9, metrics_history, network_metrics)
        
        plt.suptitle('Дашборд анализа ИКС в неблагоприятных условиях', 
                    fontsize=16, fontweight='bold')
        
        return fig
    
    def _plot_throughput(self, ax, metrics_history):
        """График пропускной способности"""
        if not metrics_history:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Пропускная способность', fontweight='bold')
            return
        
        timestamps = [m.timestamp for m in metrics_history]
        throughput = [m.throughput for m in metrics_history]
        
        ax.plot(timestamps, throughput, 'b-', linewidth=2, label='Пропускная способность')
        ax.fill_between(timestamps, throughput, alpha=0.3, color='blue')
        
        # Средняя линия
        mean_throughput = np.mean(throughput)
        ax.axhline(y=mean_throughput, color='red', linestyle='--', 
                  label=f'Среднее: {mean_throughput:.1f} Мбит/с')
        
        ax.set_title('Пропускная способность', fontweight='bold')
        ax.set_ylabel('Мбит/с')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_latency(self, ax, metrics_history):
        """График задержки"""
        if not metrics_history:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Задержка', fontweight='bold')
            return
        
        timestamps = [m.timestamp for m in metrics_history]
        latency = [m.latency for m in metrics_history]
        
        ax.plot(timestamps, latency, 'r-', linewidth=2, label='Задержка')
        ax.fill_between(timestamps, latency, alpha=0.3, color='red')
        
        # Средняя линия
        mean_latency = np.mean(latency)
        ax.axhline(y=mean_latency, color='blue', linestyle='--', 
                  label=f'Среднее: {mean_latency:.1f} мс')
        
        ax.set_title('Задержка', fontweight='bold')
        ax.set_ylabel('мс')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_quality_indicator(self, ax, metrics_history):
        """Индикатор качества"""
        if not metrics_history:
            quality_score = 0
        else:
            # Упрощенный расчет качества
            latest = metrics_history[-1]
            quality_score = (latest.reliability * 0.4 + latest.availability * 0.4 + 
                           (1 - latest.packet_loss) * 0.2)
        
        # Цветовая индикация
        if quality_score >= 0.8:
            color = 'green'
            status = 'Отлично'
        elif quality_score >= 0.6:
            color = 'yellow'
            status = 'Хорошо'
        elif quality_score >= 0.4:
            color = 'orange'
            status = 'Удовлетворительно'
        else:
            color = 'red'
            status = 'Плохо'
        
        # Создание кругового индикатора
        theta = np.linspace(0, 2*np.pi, 100)
        radius = 1
        x = radius * np.cos(theta)
        y = radius * np.sin(theta)
        
        ax.fill_between(x, y, alpha=0.3, color=color)
        ax.plot(x, y, 'k-', linewidth=2)
        
        # Заливка в зависимости от качества
        fill_angle = 2 * np.pi * quality_score
        fill_theta = np.linspace(0, fill_angle, 100)
        fill_x = radius * np.cos(fill_theta)
        fill_y = radius * np.sin(fill_theta)
        ax.fill_between(fill_x, fill_y, alpha=0.7, color=color)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.set_title(f'Качество\n{status}', fontweight='bold')
        ax.text(0, 0, f'{quality_score:.2f}', ha='center', va='center', 
               fontsize=16, fontweight='bold')
        ax.axis('off')
    
    def _plot_reliability_availability(self, ax, metrics_history):
        """График надежности и доступности"""
        if not metrics_history:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Надежность и доступность', fontweight='bold')
            return
        
        timestamps = [m.timestamp for m in metrics_history]
        reliability = [m.reliability for m in metrics_history]
        availability = [m.availability for m in metrics_history]
        
        ax.plot(timestamps, reliability, 'g-', linewidth=2, label='Надежность')
        ax.plot(timestamps, availability, 'm-', linewidth=2, label='Доступность')
        
        ax.set_title('Надежность и доступность', fontweight='bold')
        ax.set_ylabel('Значение')
        ax.set_ylim(0, 1)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_network_status(self, ax, network_metrics):
        """Состояние сети"""
        if not network_metrics:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Состояние сети', fontweight='bold')
            return
        
        # Данные для отображения
        categories = ['Узлы', 'Связи', 'Активные узлы']
        values = [
            network_metrics.get('nodes_count', 0),
            network_metrics.get('links_count', 0),
            network_metrics.get('active_nodes', 0)
        ]
        
        bars = ax.bar(categories, values, color=['blue', 'green', 'orange'], alpha=0.7)
        
        # Добавление значений на столбцы
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   str(int(value)), ha='center', va='bottom')
        
        ax.set_title('Состояние сети', fontweight='bold')
        ax.set_ylabel('Количество')
    
    def _plot_adverse_conditions(self, ax, adverse_conditions):
        """Неблагоприятные условия"""
        if not adverse_conditions:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Неблагоприятные условия', fontweight='bold')
            return
        
        conditions = list(adverse_conditions.keys())
        counts = list(adverse_conditions.values())
        
        bars = ax.bar(conditions, counts, color='red', alpha=0.7)
        
        # Добавление значений на столбцы
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   str(count), ha='center', va='bottom')
        
        ax.set_title('Неблагоприятные условия', fontweight='bold')
        ax.set_ylabel('Количество')
        ax.tick_params(axis='x', rotation=45)
    
    def _plot_traffic_analysis(self, ax, traffic_analysis):
        """Анализ трафика"""
        if not traffic_analysis:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Анализ трафика', fontweight='bold')
            return
        
        # Круговая диаграмма успешных/неуспешных потоков
        labels = ['Успешные', 'Неуспешные']
        sizes = [
            traffic_analysis.get('successful_flows', 0),
            traffic_analysis.get('failed_flows', 0)
        ]
        
        if sum(sizes) == 0:
            sizes = [1, 0]  # избегаем деления на ноль
        
        colors = ['green', 'red']
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Анализ трафика', fontweight='bold')
    
    def _plot_performance_stats(self, ax, metrics_history):
        """Статистика производительности"""
        if not metrics_history:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Статистика производительности', fontweight='bold')
            return
        
        # Создание box plot для основных метрик
        throughput = [m.throughput for m in metrics_history]
        latency = [m.latency for m in metrics_history]
        
        data = [throughput, latency]
        labels = ['Пропускная способность', 'Задержка']
        
        bp = ax.boxplot(data, labels=labels, patch_artist=True)
        
        colors = ['lightblue', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title('Статистика производительности', fontweight='bold')
        ax.set_ylabel('Значения')
        ax.grid(True, alpha=0.3)
    
    def _plot_recommendations(self, ax, metrics_history, network_metrics):
        """Рекомендации"""
        recommendations = []
        
        if metrics_history:
            latest = metrics_history[-1]
            
            if latest.throughput < 100:
                recommendations.append("Низкая пропускная способность")
            if latest.latency > 100:
                recommendations.append("Высокая задержка")
            if latest.reliability < 0.95:
                recommendations.append("Низкая надежность")
            if latest.availability < 0.99:
                recommendations.append("Низкая доступность")
        
        if network_metrics:
            if network_metrics.get('active_nodes', 0) < network_metrics.get('nodes_count', 1):
                recommendations.append("Есть неактивные узлы")
        
        if not recommendations:
            recommendations = ["Система работает в норме"]
        
        # Отображение рекомендаций
        y_pos = np.arange(len(recommendations))
        colors = ['red' if 'Низкая' in rec or 'Высокая' in rec or 'Есть' in rec else 'green' 
                 for rec in recommendations]
        
        bars = ax.barh(y_pos, [1] * len(recommendations), color=colors, alpha=0.7)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(recommendations)
        ax.set_xlim(0, 1)
        ax.set_title('Рекомендации', fontweight='bold')
        ax.set_xlabel('Статус')
        
        # Скрытие оси X
        ax.set_xticks([])





