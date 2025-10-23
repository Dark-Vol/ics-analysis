#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационный скрипт для расширенного анализа надежности ИКС
с визуализацией и GUI интеграцией
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QMenuBar, QAction
from PyQt5.QtCore import Qt

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gui.advanced_reliability_panel import (
    AdvancedReliabilityPanel,
    create_sample_network_with_states,
    FragilityAnalysisModule,
    ExternalThreatsModule,
    NetworkVisualizationWidget,
    BirnbaumVisualizationWidget,
    ACFVisualizationWidget
)


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Расширенный анализ надежности ИКС")
        self.setGeometry(100, 100, 1200, 800)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем панель анализа
        self.analysis_panel = AdvancedReliabilityPanel()
        
        # Загружаем пример данных
        network, probabilities, node_states = create_sample_network_with_states()
        self.analysis_panel.set_network_data(network, probabilities)
        
        # Размещаем панель
        layout = QVBoxLayout()
        layout.addWidget(self.analysis_panel)
        central_widget.setLayout(layout)
        
        # Создаем меню
        self.create_menu()
        
        # Запускаем начальный анализ
        self.analysis_panel.run_analysis()
    
    def create_menu(self):
        """Создает меню приложения"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')
        
        new_action = QAction('Новый анализ', self)
        new_action.triggered.connect(self.new_analysis)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Анализ"
        analysis_menu = menubar.addMenu('Анализ')
        
        birnbaum_action = QAction('Критерий Бирнбаума', self)
        birnbaum_action.triggered.connect(self.run_birnbaum_analysis)
        analysis_menu.addAction(birnbaum_action)
        
        fragility_action = QAction('Анализ хрупкости', self)
        fragility_action.triggered.connect(self.run_fragility_analysis)
        analysis_menu.addAction(fragility_action)
        
        threats_action = QAction('Внешние угрозы', self)
        threats_action.triggered.connect(self.run_threats_analysis)
        analysis_menu.addAction(threats_action)
        
        # Меню "Визуализация"
        viz_menu = menubar.addMenu('Визуализация')
        
        network_action = QAction('Топология сети', self)
        network_action.triggered.connect(self.show_network_topology)
        viz_menu.addAction(network_action)
        
        birnbaum_viz_action = QAction('График Бирнбаума', self)
        birnbaum_viz_action.triggered.connect(self.show_birnbaum_chart)
        viz_menu.addAction(birnbaum_viz_action)
        
        acf_action = QAction('Автокорреляция', self)
        acf_action.triggered.connect(self.show_acf_chart)
        viz_menu.addAction(acf_action)
    
    def new_analysis(self):
        """Создает новый анализ"""
        self.analysis_panel.clear_results()
        self.analysis_panel.run_analysis()
    
    def run_birnbaum_analysis(self):
        """Запускает анализ по критерию Бирнбаума"""
        self.analysis_panel.tab_widget.setCurrentIndex(0)  # Вкладка анализа
        self.analysis_panel.run_analysis()
    
    def run_fragility_analysis(self):
        """Запускает анализ хрупкости"""
        self.analysis_panel.tab_widget.setCurrentIndex(2)  # Вкладка хрупкости
    
    def run_threats_analysis(self):
        """Запускает анализ внешних угроз"""
        self.analysis_panel.tab_widget.setCurrentIndex(3)  # Вкладка угроз
    
    def show_network_topology(self):
        """Показывает топологию сети"""
        self.analysis_panel.tab_widget.setCurrentIndex(1)  # Вкладка визуализации
    
    def show_birnbaum_chart(self):
        """Показывает график Бирнбаума"""
        self.analysis_panel.tab_widget.setCurrentIndex(1)  # Вкладка визуализации
    
    def show_acf_chart(self):
        """Показывает график автокорреляции"""
        self.analysis_panel.tab_widget.setCurrentIndex(1)  # Вкладка визуализации


def demonstrate_console_analysis():
    """Демонстрация анализа в консольном режиме"""
    print("=" * 80)
    print("ДЕМОНСТРАЦИЯ РАСШИРЕННОГО АНАЛИЗА НАДЕЖНОСТИ ИКС")
    print("=" * 80)
    
    # Создаем пример сети
    network, probabilities, node_states = create_sample_network_with_states()
    
    print("\n1. Инициализация тестовой сети:")
    print(f"   Узлы: {list(probabilities.keys())}")
    print(f"   Вероятности безотказной работы: {probabilities}")
    
    # Демонстрация модуля хрупкости
    print("\n2. Анализ хрупкости системы:")
    print("-" * 50)
    
    fragility_module = FragilityAnalysisModule()
    removal_order = ['switch1', 'switch2', 'router1', 'router2', 'server1']
    
    states = fragility_module.remove_nodes_step_by_step(
        network, probabilities, removal_order
    )
    
    for i, state in enumerate(states):
        print(f"Шаг {i+1}:")
        print(f"  Количество узлов: {len(state.node_states)}")
        print(f"  Надежность системы: {state.system_reliability:.6f}")
        print(f"  Связность: {'Да' if state.connectivity_status else 'Нет'}")
        
        if state.critical_threshold_reached:
            print("  ⚠️ КРИТИЧЕСКИЙ ПОРОГ ДОСТИГНУТ!")
            print("  Система перестает функционировать.")
            break
        print()
    
    # Демонстрация внешних угроз
    print("\n3. Моделирование внешних угроз:")
    print("-" * 50)
    
    threats_module = ExternalThreatsModule()
    
    # Симулируем несколько раундов угроз
    for round_num in range(1, 4):
        print(f"Раунд {round_num}:")
        
        updated_probs, events = threats_module.simulate_threats(network, probabilities)
        
        if events:
            print("  Произошедшие события:")
            for event in events:
                print(f"    - {event['description']}")
                print(f"      Тип: {event['type']}")
                print(f"      Воздействие: {event['impact']:.2f}")
        else:
            print("  Внешние события не произошли")
        
        print("  Обновленные вероятности:")
        for node, prob in updated_probs.items():
            original_prob = probabilities[node]
            change = prob - original_prob
            print(f"    {node}: {prob:.4f} ({change:+.4f})")
        print()
    
    # Демонстрация визуализации
    print("\n4. Создание графиков:")
    print("-" * 50)
    
    # Создаем график коэффициентов Бирнбаума
    try:
        from src.analytics.advanced_reliability_analyzer import AdvancedReliabilityAnalyzer
        
        analyzer = AdvancedReliabilityAnalyzer()
        structure_matrix = [
            [0, 1, 1, 0, 0, 0, 1],  # server1
            [1, 0, 0, 1, 0, 0, 1],  # server2
            [1, 0, 0, 1, 1, 0, 0],  # router1
            [0, 1, 1, 0, 0, 1, 0],  # router2
            [0, 0, 1, 0, 0, 1, 0],  # switch1
            [0, 0, 0, 1, 1, 0, 0],  # switch2
            [1, 1, 0, 0, 0, 0, 0]   # firewall
        ]
        
        birnbaum_coeffs = analyzer.calculate_birnbaum_criterion(probabilities, structure_matrix)
        
        print("Коэффициенты значимости Бирнбаума:")
        for node, coeff in sorted(birnbaum_coeffs.items(), key=lambda x: x[1], reverse=True):
            if coeff >= 0.5:
                criticality = "КРИТИЧЕСКИЙ"
            elif coeff >= 0.2:
                criticality = "ВЫСОКИЙ"
            elif coeff >= 0.1:
                criticality = "СРЕДНИЙ"
            else:
                criticality = "НИЗКИЙ"
            
            print(f"  {node:12s}: {coeff:8.4f} ({criticality})")
        
        # Создаем график
        plt.figure(figsize=(10, 6))
        nodes = list(birnbaum_coeffs.keys())
        values = list(birnbaum_coeffs.values())
        
        colors = []
        for value in values:
            if value >= 0.5:
                colors.append('#8B0000')  # Темно-красный
            elif value >= 0.2:
                colors.append('#DC143C')  # Красный
            elif value >= 0.1:
                colors.append('#FFD700')  # Золотой
            else:
                colors.append('#2E8B57')  # Зеленый
        
        bars = plt.bar(range(len(nodes)), values, color=colors, alpha=0.8)
        plt.xlabel('Узлы системы')
        plt.ylabel('Коэффициент значимости Бирнбаума')
        plt.title('Коэффициенты значимости Бирнбаума')
        plt.xticks(range(len(nodes)), nodes, rotation=45)
        
        # Добавляем значения на столбцы
        for i, (bar, value) in enumerate(zip(bars, values)):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom')
        
        # Добавляем линии критичности
        plt.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='Критический (≥0.5)')
        plt.axhline(y=0.2, color='orange', linestyle='--', alpha=0.7, label='Высокий (≥0.2)')
        plt.axhline(y=0.1, color='yellow', linestyle='--', alpha=0.7, label='Средний (≥0.1)')
        
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Сохраняем график
        plt.savefig('birnbaum_coefficients.png', dpi=300, bbox_inches='tight')
        print(f"\nГрафик сохранен как 'birnbaum_coefficients.png'")
        
    except Exception as e:
        print(f"Ошибка при создании графика: {e}")
    
    print("\n" + "=" * 80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)


def main():
    """Основная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == '--console':
        # Консольный режим
        demonstrate_console_analysis()
    else:
        # GUI режим
        app = QApplication(sys.argv)
        
        # Создаем главное окно
        window = MainWindow()
        window.show()
        
        # Запускаем приложение
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
