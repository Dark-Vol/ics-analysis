#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Рендерер графиков для визуализации
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Any, Optional

class ChartRenderer:
    """Рендерер для создания различных типов графиков"""
    
    def __init__(self):
        # Настройка стиля
        plt.style.use('default')
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    def render_line_chart(self, data: Dict[str, List[float]], 
                         title: str = "График", xlabel: str = "X", 
                         ylabel: str = "Y") -> plt.Figure:
        """Создает линейный график"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for i, (label, values) in enumerate(data.items()):
            x = list(range(len(values)))
            ax.plot(x, values, label=label, color=self.colors[i % len(self.colors)], 
                   linewidth=2, marker='o', markersize=4)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def render_bar_chart(self, data: Dict[str, float], 
                        title: str = "Столбчатая диаграмма", 
                        xlabel: str = "Категории", 
                        ylabel: str = "Значения") -> plt.Figure:
        """Создает столбчатую диаграмму"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        categories = list(data.keys())
        values = list(data.values())
        
        bars = ax.bar(categories, values, color=self.colors[:len(categories)])
        
        # Добавление значений на столбцы
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{value:.2f}', ha='center', va='bottom')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def render_pie_chart(self, data: Dict[str, float], 
                        title: str = "Круговая диаграмма") -> plt.Figure:
        """Создает круговую диаграмму"""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels = list(data.keys())
        sizes = list(data.values())
        colors = self.colors[:len(labels)]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        
        # Настройка текста
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        return fig
    
    def render_heatmap(self, data: np.ndarray, 
                      row_labels: List[str], 
                      col_labels: List[str],
                      title: str = "Тепловая карта") -> plt.Figure:
        """Создает тепловую карту"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
        
        # Настройка осей
        ax.set_xticks(range(len(col_labels)))
        ax.set_yticks(range(len(row_labels)))
        ax.set_xticklabels(col_labels)
        ax.set_yticklabels(row_labels)
        
        # Добавление значений в ячейки
        for i in range(len(row_labels)):
            for j in range(len(col_labels)):
                text = ax.text(j, i, f'{data[i, j]:.2f}',
                             ha="center", va="center", color="black")
        
        # Цветовая шкала
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Значение')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def render_histogram(self, data: List[float], 
                        bins: int = 30, 
                        title: str = "Гистограмма",
                        xlabel: str = "Значения",
                        ylabel: str = "Частота") -> plt.Figure:
        """Создает гистограмму"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        n, bins_edges, patches = ax.hist(data, bins=bins, alpha=0.7, 
                                        color=self.colors[0], edgecolor='black')
        
        # Добавление статистических линий
        mean_val = np.mean(data)
        median_val = np.median(data)
        
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                  label=f'Среднее: {mean_val:.2f}')
        ax.axvline(median_val, color='green', linestyle='--', linewidth=2, 
                  label=f'Медиана: {median_val:.2f}')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def render_scatter_plot(self, x_data: List[float], y_data: List[float],
                           title: str = "Диаграмма рассеяния",
                           xlabel: str = "X",
                           ylabel: str = "Y",
                           color_by: Optional[List[float]] = None) -> plt.Figure:
        """Создает диаграмму рассеяния"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if color_by is not None:
            scatter = ax.scatter(x_data, y_data, c=color_by, cmap='viridis', alpha=0.6)
            plt.colorbar(scatter, ax=ax, label='Цветовая метка')
        else:
            ax.scatter(x_data, y_data, alpha=0.6, color=self.colors[0])
        
        # Линия тренда
        if len(x_data) > 1:
            z = np.polyfit(x_data, y_data, 1)
            p = np.poly1d(z)
            ax.plot(x_data, p(x_data), "r--", alpha=0.8, linewidth=2)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def render_box_plot(self, data: Dict[str, List[float]], 
                       title: str = "Диаграмма размаха") -> plt.Figure:
        """Создает диаграмму размаха (box plot)"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        box_data = list(data.values())
        box_labels = list(data.keys())
        
        bp = ax.boxplot(box_data, labels=box_labels, patch_artist=True)
        
        # Цветовая раскраска
        for patch, color in zip(bp['boxes'], self.colors[:len(box_data)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylabel('Значения')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig








