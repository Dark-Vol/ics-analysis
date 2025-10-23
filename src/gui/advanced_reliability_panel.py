#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенный анализатор надежности ИКС с визуализацией и GUI интеграцией
Включает:
- Критерий Бирнбаума с визуализацией
- Теория вероятностей
- Тест Дарбина-Уотсона с графиком ACF
- Модуль Fragility Analysis
- Визуализация топологии сети
- Учет внешних угроз
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import networkx as nx
from scipy import stats
from statsmodels.stats.stattools import durbin_watson
from statsmodels.graphics.tsaplots import plot_acf
from typing import Dict, List, Tuple, Optional, Union
import random
import itertools
from dataclasses import dataclass
import warnings
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QTableWidget, QTableWidgetItem, QTabWidget,
                             QTextEdit, QSlider, QSpinBox, QCheckBox, QGroupBox,
                             QProgressBar, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

# Константы
CRITICAL_NODE_THRESHOLD = 3  # Минимальное количество узлов для функционирования системы

# Цвета для визуализации состояний узлов
NODE_COLORS = {
    'working': '#2E8B57',      # Зеленый - работает
    'attacked': '#DC143C',     # Красный - атакован
    'failed': '#696969',       # Серый - отказал
    'disconnected': '#FF8C00', # Оранжевый - отключен
    'critical': '#8B0000'      # Темно-красный - критический
}


@dataclass
class NodeState:
    """Состояние узла"""
    id: str
    is_working: bool = True
    is_attacked: bool = False
    is_failed: bool = False
    is_disconnected: bool = False
    reliability: float = 0.95
    failure_probability: float = 0.05
    birnbaum_coefficient: float = 0.0


@dataclass
class SystemState:
    """Состояние системы"""
    node_states: Dict[str, NodeState]
    system_reliability: float
    connectivity_status: bool
    critical_threshold_reached: bool = False


class FragilityAnalysisModule:
    """Модуль анализа хрупкости системы"""
    
    def __init__(self, critical_threshold: int = CRITICAL_NODE_THRESHOLD):
        self.critical_threshold = critical_threshold
        self.removal_history = []
        self.current_state = None
    
    def remove_nodes_step_by_step(self, network: Dict, probabilities: Dict[str, float], 
                                 removal_order: List[str]) -> List[SystemState]:
        """
        Пошаговое удаление узлов с анализом влияния на систему.
        
        Args:
            network: Структура сети
            probabilities: Вероятности безотказной работы узлов
            removal_order: Порядок удаления узлов
            
        Returns:
            Список состояний системы после каждого удаления
        """
        states = []
        current_network = network.copy()
        current_probs = probabilities.copy()
        
        for node_to_remove in removal_order:
            if node_to_remove not in current_probs:
                continue
            
            # Удаляем узел
            current_network = self._remove_node_from_network(current_network, node_to_remove)
            del current_probs[node_to_remove]
            
            # Создаем состояние системы
            state = self._create_system_state(current_network, current_probs)
            states.append(state)
            
            # Проверяем критический порог
            if len(current_probs) < self.critical_threshold:
                state.critical_threshold_reached = True
                break
        
        return states
    
    def _remove_node_from_network(self, network: Dict, node_id: str) -> Dict:
        """Удаляет узел из сети"""
        updated_network = network.copy()
        
        # Удаляем узел из списка узлов
        if 'nodes' in updated_network:
            updated_network['nodes'] = [
                node for node in updated_network['nodes'] 
                if node.get('id') != node_id
            ]
        
        # Удаляем связи с узлом
        if 'connections' in updated_network:
            updated_connections = {}
            for node, neighbors in updated_network['connections'].items():
                if node != node_id:
                    updated_connections[node] = [
                        neighbor for neighbor in neighbors 
                        if neighbor != node_id
                    ]
            updated_network['connections'] = updated_connections
        
        return updated_network
    
    def _create_system_state(self, network: Dict, probabilities: Dict[str, float]) -> SystemState:
        """Создает состояние системы"""
        node_states = {}
        
        for node_id, prob in probabilities.items():
            node_states[node_id] = NodeState(
                id=node_id,
                reliability=prob,
                failure_probability=1 - prob
            )
        
        # Рассчитываем общую надежность системы
        system_reliability = np.prod(list(probabilities.values())) if probabilities else 0.0
        
        # Проверяем связность
        connectivity_status = len(probabilities) >= self.critical_threshold
        
        return SystemState(
            node_states=node_states,
            system_reliability=system_reliability,
            connectivity_status=connectivity_status,
            critical_threshold_reached=len(probabilities) < self.critical_threshold
        )


class ExternalThreatsModule:
    """Модуль моделирования внешних угроз"""
    
    def __init__(self):
        self.threat_probabilities = {
            'hacker_attack': 0.1,      # 10% вероятность атаки
            'power_outage': 0.05,       # 5% вероятность отключения питания
            'communication_failure': 0.15  # 15% вероятность сбоя связи
        }
        
        self.threat_impact = {
            'hacker_attack': 0.3,       # 30% вероятность компрометации
            'power_outage': 0.8,        # 80% вероятность отказа при отключении
            'communication_failure': 0.2  # 20% вероятность отказа связи
        }
    
    def simulate_threats(self, network: Dict, probabilities: Dict[str, float]) -> Tuple[Dict, List[Dict]]:
        """
        Симулирует внешние угрозы и их влияние на систему.
        
        Args:
            network: Структура сети
            probabilities: Вероятности безотказной работы узлов
            
        Returns:
            Кортеж (обновленные_вероятности, список_событий)
        """
        updated_probs = probabilities.copy()
        events = []
        
        nodes = list(probabilities.keys())
        
        # Хакерская атака
        if random.random() < self.threat_probabilities['hacker_attack']:
            target_nodes = random.sample(nodes, min(2, len(nodes)))
            for node in target_nodes:
                if random.random() < self.threat_impact['hacker_attack']:
                    updated_probs[node] *= 0.3  # Снижаем надежность
                    events.append({
                        'type': 'hacker_attack',
                        'target': node,
                        'impact': self.threat_impact['hacker_attack'],
                        'description': f'Хакерская атака на узел {node}'
                    })
        
        # Отключение питания
        if random.random() < self.threat_probabilities['power_outage']:
            affected_nodes = random.sample(nodes, min(3, len(nodes)))
            for node in affected_nodes:
                if random.random() < self.threat_impact['power_outage']:
                    updated_probs[node] = 0.0  # Полный отказ
                    events.append({
                        'type': 'power_outage',
                        'target': node,
                        'impact': self.threat_impact['power_outage'],
                        'description': f'Отключение питания узла {node}'
                    })
        
        # Сбой коммуникации
        if random.random() < self.threat_probabilities['communication_failure']:
            target_node = random.choice(nodes)
            if random.random() < self.threat_impact['communication_failure']:
                updated_probs[target_node] *= 0.5  # Снижаем надежность связи
                events.append({
                    'type': 'communication_failure',
                    'target': target_node,
                    'impact': self.threat_impact['communication_failure'],
                    'description': f'Сбой коммуникации узла {target_node}'
                })
        
        return updated_probs, events


class NetworkVisualizationWidget(QWidget):
    """Виджет для визуализации топологии сети"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.network_graph = None
        self.node_states = {}
    
    def draw_network(self, network: Dict, node_states: Dict[str, NodeState] = None):
        """Отрисовывает сеть с цветовой индикацией состояний узлов"""
        self.ax.clear()
        
        if not network or 'nodes' not in network:
            self.ax.text(0.5, 0.5, 'Нет данных для отображения', 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Создаем граф
        G = nx.Graph()
        
        # Добавляем узлы
        for node in network['nodes']:
            node_id = node.get('id', str(node))
            G.add_node(node_id)
        
        # Добавляем связи
        if 'connections' in network:
            for node, neighbors in network['connections'].items():
                for neighbor in neighbors:
                    if G.has_node(node) and G.has_node(neighbor):
                        G.add_edge(node, neighbor)
        
        # Определяем позиции узлов
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Определяем цвета узлов
        node_colors = []
        for node in G.nodes():
            if node_states and node in node_states:
                state = node_states[node]
                if state.is_failed or state.is_disconnected:
                    node_colors.append(NODE_COLORS['failed'])
                elif state.is_attacked:
                    node_colors.append(NODE_COLORS['attacked'])
                else:
                    node_colors.append(NODE_COLORS['working'])
            else:
                node_colors.append(NODE_COLORS['working'])
        
        # Отрисовываем граф
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=1000, alpha=0.8)
        nx.draw_networkx_edges(G, pos, alpha=0.5, width=2)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Добавляем легенду
        legend_elements = [
            patches.Patch(color=NODE_COLORS['working'], label='Работает'),
            patches.Patch(color=NODE_COLORS['attacked'], label='Атакован'),
            patches.Patch(color=NODE_COLORS['failed'], label='Отказал'),
            patches.Patch(color=NODE_COLORS['disconnected'], label='Отключен')
        ]
        self.ax.legend(handles=legend_elements, loc='upper right')
        
        self.ax.set_title('Топология сети', fontsize=14, fontweight='bold')
        self.ax.axis('off')
        
        self.canvas.draw()
    
    def update_node_states(self, node_states: Dict[str, NodeState]):
        """Обновляет состояния узлов"""
        self.node_states = node_states


class ACFVisualizationWidget(QWidget):
    """Виджет для визуализации автокорреляции"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_acf(self, residuals: List[float], title: str = "Автокорреляционная функция"):
        """Строит график автокорреляционной функции"""
        self.figure.clear()
        
        ax = self.figure.add_subplot(111)
        
        # Используем statsmodels для построения ACF
        try:
            from statsmodels.tsa.stattools import acf
            from statsmodels.graphics.tsaplots import plot_acf
            
            # Строим ACF график
            plot_acf(residuals, ax=ax, lags=20, alpha=0.05)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('Лаг')
            ax.set_ylabel('Автокорреляция')
            
        except ImportError:
            # Альтернативная реализация без statsmodels
            ax.text(0.5, 0.5, 'Не удалось построить ACF график\n(требуется statsmodels)', 
                   ha='center', va='center', transform=ax.transAxes)
        
        self.figure.tight_layout()
        self.canvas.draw()


class BirnbaumVisualizationWidget(QWidget):
    """Виджет для визуализации коэффициентов Бирнбаума"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def plot_birnbaum_coefficients(self, coefficients: Dict[str, float]):
        """Строит график коэффициентов Бирнбаума"""
        self.figure.clear()
        
        ax = self.figure.add_subplot(111)
        
        # Сортируем коэффициенты по убыванию
        sorted_coeffs = sorted(coefficients.items(), key=lambda x: x[1], reverse=True)
        nodes = [item[0] for item in sorted_coeffs]
        values = [item[1] for item in sorted_coeffs]
        
        # Определяем цвета в зависимости от критичности
        colors = []
        for value in values:
            if value >= 0.5:
                colors.append(NODE_COLORS['critical'])
            elif value >= 0.2:
                colors.append(NODE_COLORS['attacked'])
            elif value >= 0.1:
                colors.append('#FFD700')  # Золотой
            else:
                colors.append(NODE_COLORS['working'])
        
        # Строим столбчатую диаграмму
        bars = ax.bar(range(len(nodes)), values, color=colors, alpha=0.8)
        
        # Настраиваем график
        ax.set_xlabel('Узлы системы')
        ax.set_ylabel('Коэффициент значимости Бирнбаума')
        ax.set_title('Коэффициенты значимости Бирнбаума', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(nodes)))
        ax.set_xticklabels(nodes, rotation=45, ha='right')
        
        # Добавляем значения на столбцы
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{value:.3f}', ha='center', va='bottom')
        
        # Добавляем горизонтальные линии для уровней критичности
        ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Критический (≥0.5)')
        ax.axhline(y=0.2, color='orange', linestyle='--', alpha=0.7, label='Высокий (≥0.2)')
        ax.axhline(y=0.1, color='yellow', linestyle='--', alpha=0.7, label='Средний (≥0.1)')
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
        self.canvas.draw()


class AdvancedReliabilityPanel(QWidget):
    """Панель расширенного анализа надежности"""
    
    analysis_completed = pyqtSignal(dict)  # Сигнал о завершении анализа
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Модули анализа
        self.fragility_module = FragilityAnalysisModule()
        self.threats_module = ExternalThreatsModule()
        
        # Данные
        self.current_network = None
        self.current_probabilities = None
        self.current_results = {}
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout()
        
        # Создаем вкладки
        self.tab_widget = QTabWidget()
        
        # Вкладка анализа
        self.analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "Анализ надежности")
        
        # Вкладка визуализации
        self.visualization_tab = self.create_visualization_tab()
        self.tab_widget.addTab(self.visualization_tab, "Визуализация")
        
        # Вкладка хрупкости
        self.fragility_tab = self.create_fragility_tab()
        self.tab_widget.addTab(self.fragility_tab, "Анализ хрупкости")
        
        # Вкладка внешних угроз
        self.threats_tab = self.create_threats_tab()
        self.tab_widget.addTab(self.threats_tab, "Внешние угрозы")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def create_analysis_tab(self) -> QWidget:
        """Создает вкладку анализа"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Кнопки управления
        controls_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("Запустить анализ")
        self.analyze_btn.clicked.connect(self.run_analysis)
        controls_layout.addWidget(self.analyze_btn)
        
        self.clear_btn = QPushButton("Очистить результаты")
        self.clear_btn.clicked.connect(self.clear_results)
        controls_layout.addWidget(self.clear_btn)
        
        layout.addLayout(controls_layout)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "Узел", "Надежность", "Коэфф. Бирнбаума", "Критичность"
        ])
        layout.addWidget(self.results_table)
        
        # Текстовое поле для дополнительной информации
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        layout.addWidget(self.info_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_visualization_tab(self) -> QWidget:
        """Создает вкладку визуализации"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Создаем виджеты визуализации
        self.network_viz = NetworkVisualizationWidget()
        self.birnbaum_viz = BirnbaumVisualizationWidget()
        self.acf_viz = ACFVisualizationWidget()
        
        # Размещаем виджеты в сетке
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.network_viz)
        splitter.addWidget(self.birnbaum_viz)
        
        layout.addWidget(splitter)
        layout.addWidget(self.acf_viz)
        
        widget.setLayout(layout)
        return widget
    
    def create_fragility_tab(self) -> QWidget:
        """Создает вкладку анализа хрупкости"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Настройки анализа хрупкости
        settings_group = QGroupBox("Настройки анализа")
        settings_layout = QVBoxLayout()
        
        # Критический порог
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Критический порог узлов:"))
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(1, 10)
        self.threshold_spinbox.setValue(CRITICAL_NODE_THRESHOLD)
        threshold_layout.addWidget(self.threshold_spinbox)
        threshold_layout.addStretch()
        settings_layout.addLayout(threshold_layout)
        
        # Порядок удаления узлов
        removal_layout = QHBoxLayout()
        removal_layout.addWidget(QLabel("Порядок удаления:"))
        self.removal_order_text = QTextEdit()
        self.removal_order_text.setMaximumHeight(80)
        self.removal_order_text.setPlaceholderText("Введите узлы через запятую (например: switch1, router1, server1)")
        removal_layout.addWidget(self.removal_order_text)
        settings_layout.addLayout(removal_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Кнопки управления
        controls_layout = QHBoxLayout()
        
        self.run_fragility_btn = QPushButton("Запустить анализ хрупкости")
        self.run_fragility_btn.clicked.connect(self.run_fragility_analysis)
        controls_layout.addWidget(self.run_fragility_btn)
        
        self.step_by_step_btn = QPushButton("Пошаговое удаление")
        self.step_by_step_btn.clicked.connect(self.run_step_by_step_removal)
        controls_layout.addWidget(self.step_by_step_btn)
        
        layout.addLayout(controls_layout)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Результаты анализа хрупкости
        self.fragility_results = QTextEdit()
        layout.addWidget(self.fragility_results)
        
        widget.setLayout(layout)
        return widget
    
    def create_threats_tab(self) -> QWidget:
        """Создает вкладку внешних угроз"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Настройки угроз
        threats_group = QGroupBox("Настройки внешних угроз")
        threats_layout = QVBoxLayout()
        
        # Вероятности угроз
        self.hacker_prob_slider = self.create_probability_slider("Хакерская атака", 0.1)
        self.power_prob_slider = self.create_probability_slider("Отключение питания", 0.05)
        self.comm_prob_slider = self.create_probability_slider("Сбой коммуникации", 0.15)
        
        threats_layout.addWidget(self.hacker_prob_slider)
        threats_layout.addWidget(self.power_prob_slider)
        threats_layout.addWidget(self.comm_prob_slider)
        
        threats_group.setLayout(threats_layout)
        layout.addWidget(threats_group)
        
        # Кнопки управления
        controls_layout = QHBoxLayout()
        
        self.simulate_threats_btn = QPushButton("Симулировать угрозы")
        self.simulate_threats_btn.clicked.connect(self.simulate_threats)
        controls_layout.addWidget(self.simulate_threats_btn)
        
        self.reset_threats_btn = QPushButton("Сбросить угрозы")
        self.reset_threats_btn.clicked.connect(self.reset_threats)
        controls_layout.addWidget(self.reset_threats_btn)
        
        layout.addLayout(controls_layout)
        
        # Результаты симуляции угроз
        self.threats_results = QTextEdit()
        layout.addWidget(self.threats_results)
        
        widget.setLayout(layout)
        return widget
    
    def create_probability_slider(self, label_text: str, default_value: float) -> QWidget:
        """Создает слайдер для настройки вероятности"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        label = QLabel(f"{label_text}:")
        layout.addWidget(label)
        
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(default_value * 100))
        layout.addWidget(slider)
        
        value_label = QLabel(f"{default_value:.2f}")
        layout.addWidget(value_label)
        
        # Связываем слайдер с меткой
        def update_label(value):
            prob = value / 100.0
            value_label.setText(f"{prob:.2f}")
        
        slider.valueChanged.connect(update_label)
        
        widget.setLayout(layout)
        return widget
    
    def set_network_data(self, network: Dict, probabilities: Dict[str, float]):
        """Устанавливает данные сети для анализа"""
        self.current_network = network
        self.current_probabilities = probabilities
        
        # Обновляем визуализацию сети
        if hasattr(self, 'network_viz'):
            self.network_viz.draw_network(network)
    
    def run_analysis(self):
        """Запускает полный анализ надежности"""
        if not self.current_network or not self.current_probabilities:
            QMessageBox.warning(self, "Предупреждение", "Нет данных для анализа")
            return
        
        try:
            # Импортируем анализатор
            from src.analytics.advanced_reliability_analyzer import AdvancedReliabilityAnalyzer
            
            analyzer = AdvancedReliabilityAnalyzer()
            
            # Создаем матрицу связности
            structure_matrix = self._create_structure_matrix()
            
            # Рассчитываем коэффициенты Бирнбаума
            birnbaum_coeffs = analyzer.calculate_birnbaum_criterion(
                self.current_probabilities, structure_matrix
            )
            
            # Рассчитываем надежность системы
            connections = analyzer._get_connections_from_matrix()
            system_reliability = analyzer.system_reliability(
                self.current_probabilities, connections
            )
            
            # Сохраняем результаты
            self.current_results = {
                'birnbaum_coefficients': birnbaum_coeffs,
                'system_reliability': system_reliability,
                'probabilities': self.current_probabilities
            }
            
            # Обновляем интерфейс
            self.update_results_table()
            self.update_visualizations()
            
            # Отправляем сигнал о завершении анализа
            self.analysis_completed.emit(self.current_results)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при анализе: {str(e)}")
    
    def _create_structure_matrix(self) -> List[List[int]]:
        """Создает матрицу связности из структуры сети"""
        if not self.current_network or 'connections' not in self.current_network:
            return []
        
        nodes = list(self.current_probabilities.keys())
        n = len(nodes)
        matrix = [[0] * n for _ in range(n)]
        
        # Заполняем матрицу на основе связей
        for i, node1 in enumerate(nodes):
            if node1 in self.current_network['connections']:
                for node2 in self.current_network['connections'][node1]:
                    if node2 in nodes:
                        j = nodes.index(node2)
                        matrix[i][j] = 1
                        matrix[j][i] = 1  # Симметричная матрица
        
        return matrix
    
    def update_results_table(self):
        """Обновляет таблицу результатов"""
        if not self.current_results:
            return
        
        birnbaum_coeffs = self.current_results['birnbaum_coefficients']
        probabilities = self.current_results['probabilities']
        
        self.results_table.setRowCount(len(birnbaum_coeffs))
        
        for i, (node, coeff) in enumerate(birnbaum_coeffs.items()):
            # Узел
            self.results_table.setItem(i, 0, QTableWidgetItem(node))
            
            # Надежность
            reliability = probabilities.get(node, 0.0)
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{reliability:.4f}"))
            
            # Коэффициент Бирнбаума
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{coeff:.4f}"))
            
            # Критичность
            if coeff >= 0.5:
                criticality = "КРИТИЧЕСКИЙ"
            elif coeff >= 0.2:
                criticality = "ВЫСОКИЙ"
            elif coeff >= 0.1:
                criticality = "СРЕДНИЙ"
            else:
                criticality = "НИЗКИЙ"
            
            self.results_table.setItem(i, 3, QTableWidgetItem(criticality))
        
        # Обновляем информацию
        system_reliability = self.current_results['system_reliability']
        self.info_text.setText(f"""
Результаты анализа надежности:
- Общая надежность системы: {system_reliability:.6f}
- Количество проанализированных узлов: {len(birnbaum_coeffs)}
- Критически важных узлов: {len([c for c in birnbaum_coeffs.values() if c >= 0.5])}
- Критический порог системы: {CRITICAL_NODE_THRESHOLD} узлов
        """)
    
    def update_visualizations(self):
        """Обновляет все визуализации"""
        if not self.current_results:
            return
        
        # Обновляем график коэффициентов Бирнбаума
        if hasattr(self, 'birnbaum_viz'):
            self.birnbaum_viz.plot_birnbaum_coefficients(
                self.current_results['birnbaum_coefficients']
            )
        
        # Обновляем визуализацию сети
        if hasattr(self, 'network_viz'):
            self.network_viz.draw_network(self.current_network)
    
    def run_fragility_analysis(self):
        """Запускает анализ хрупкости"""
        if not self.current_network or not self.current_probabilities:
            QMessageBox.warning(self, "Предупреждение", "Нет данных для анализа")
            return
        
        try:
            # Получаем порядок удаления узлов
            removal_text = self.removal_order_text.toPlainText().strip()
            if not removal_text:
                QMessageBox.warning(self, "Предупреждение", "Укажите порядок удаления узлов")
                return
            
            removal_order = [node.strip() for node in removal_text.split(',')]
            
            # Устанавливаем критический порог
            self.fragility_module.critical_threshold = self.threshold_spinbox.value()
            
            # Запускаем анализ
            states = self.fragility_module.remove_nodes_step_by_step(
                self.current_network, self.current_probabilities, removal_order
            )
            
            # Отображаем результаты
            self.display_fragility_results(states)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при анализе хрупкости: {str(e)}")
    
    def display_fragility_results(self, states: List[SystemState]):
        """Отображает результаты анализа хрупкости"""
        results_text = "Результаты анализа хрупкости системы:\n\n"
        
        for i, state in enumerate(states):
            results_text += f"Шаг {i+1}:\n"
            results_text += f"- Количество узлов: {len(state.node_states)}\n"
            results_text += f"- Надежность системы: {state.system_reliability:.6f}\n"
            results_text += f"- Связность: {'Да' if state.connectivity_status else 'Нет'}\n"
            
            if state.critical_threshold_reached:
                results_text += "- ⚠️ КРИТИЧЕСКИЙ ПОРОГ ДОСТИГНУТ!\n"
                results_text += "- Система перестает функционировать.\n"
            
            results_text += "\n"
        
        self.fragility_results.setText(results_text)
    
    def run_step_by_step_removal(self):
        """Запускает пошаговое удаление узлов"""
        # Реализация пошагового удаления с анимацией
        pass
    
    def simulate_threats(self):
        """Симулирует внешние угрозы"""
        if not self.current_network or not self.current_probabilities:
            QMessageBox.warning(self, "Предупреждение", "Нет данных для симуляции")
            return
        
        try:
            # Обновляем вероятности угроз
            self.threats_module.threat_probabilities = {
                'hacker_attack': self.hacker_prob_slider.findChild(QSlider).value() / 100.0,
                'power_outage': self.power_prob_slider.findChild(QSlider).value() / 100.0,
                'communication_failure': self.comm_prob_slider.findChild(QSlider).value() / 100.0
            }
            
            # Симулируем угрозы
            updated_probs, events = self.threats_module.simulate_threats(
                self.current_network, self.current_probabilities
            )
            
            # Отображаем результаты
            self.display_threats_results(events, updated_probs)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при симуляции угроз: {str(e)}")
    
    def display_threats_results(self, events: List[Dict], updated_probs: Dict[str, float]):
        """Отображает результаты симуляции угроз"""
        results_text = "Результаты симуляции внешних угроз:\n\n"
        
        if events:
            results_text += "Произошедшие события:\n"
            for event in events:
                results_text += f"- {event['description']}\n"
                results_text += f"  Тип: {event['type']}\n"
                results_text += f"  Цель: {event['target']}\n"
                results_text += f"  Воздействие: {event['impact']:.2f}\n\n"
        else:
            results_text += "Внешние события не произошли.\n\n"
        
        results_text += "Обновленные вероятности отказов:\n"
        for node, prob in updated_probs.items():
            original_prob = 1 - self.current_probabilities[node]
            change = prob - self.current_probabilities[node]
            results_text += f"- {node}: {prob:.4f} ({change:+.4f})\n"
        
        self.threats_results.setText(results_text)
    
    def reset_threats(self):
        """Сбрасывает результаты симуляции угроз"""
        self.threats_results.clear()
    
    def clear_results(self):
        """Очищает все результаты"""
        self.results_table.setRowCount(0)
        self.info_text.clear()
        self.fragility_results.clear()
        self.threats_results.clear()
        self.current_results = {}


def create_sample_network_with_states() -> Tuple[Dict, Dict[str, float], Dict[str, NodeState]]:
    """
    Создает пример сети с состояниями узлов для демонстрации.
    
    Returns:
        Кортеж (структура_сети, вероятности, состояния_узлов)
    """
    # Структура сети
    network = {
        'nodes': [
            {'id': 'server1', 'type': 'server', 'capacity': 1000},
            {'id': 'server2', 'type': 'server', 'capacity': 800},
            {'id': 'router1', 'type': 'router', 'capacity': 500},
            {'id': 'router2', 'type': 'router', 'capacity': 500},
            {'id': 'switch1', 'type': 'switch', 'capacity': 300},
            {'id': 'switch2', 'type': 'switch', 'capacity': 300},
            {'id': 'firewall', 'type': 'firewall', 'capacity': 200}
        ],
        'connections': {
            'server1': ['server2', 'router1', 'firewall'],
            'server2': ['server1', 'router2', 'firewall'],
            'router1': ['server1', 'router2', 'switch1'],
            'router2': ['server2', 'router1', 'switch2'],
            'switch1': ['router1', 'switch2'],
            'switch2': ['router2', 'switch1'],
            'firewall': ['server1', 'server2']
        }
    }
    
    # Вероятности безотказной работы
    probabilities = {
        'server1': 0.99,
        'server2': 0.98,
        'router1': 0.95,
        'router2': 0.96,
        'switch1': 0.97,
        'switch2': 0.94,
        'firewall': 0.92
    }
    
    # Состояния узлов
    node_states = {}
    for node_id, prob in probabilities.items():
        node_states[node_id] = NodeState(
            id=node_id,
            reliability=prob,
            failure_probability=1 - prob
        )
    
    return network, probabilities, node_states


if __name__ == "__main__":
    # Демонстрация работы модуля
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Создаем панель анализа
    panel = AdvancedReliabilityPanel()
    
    # Загружаем пример данных
    network, probabilities, node_states = create_sample_network_with_states()
    panel.set_network_data(network, probabilities)
    
    # Запускаем анализ
    panel.run_analysis()
    
    # Показываем панель
    panel.show()
    
    sys.exit(app.exec_())
