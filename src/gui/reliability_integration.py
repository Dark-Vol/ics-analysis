#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция расширенного анализа надежности в основное приложение
Адаптер для интеграции PyQt5 панели в tkinter приложение
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from typing import Dict, List, Optional, Tuple

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
    from PyQt5.QtCore import QTimer
    from PyQt5.QtGui import QWindow
    from PyQt5.QtWidgets import QWidget
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt5 не установлен. Расширенный анализ надежности недоступен.")


class ReliabilityAnalysisDialog:
    """Диалог расширенного анализа надежности"""
    
    def __init__(self, parent, network_data=None, probabilities=None):
        self.parent = parent
        self.network_data = network_data
        self.probabilities = probabilities
        self.dialog = None
        self.qt_app = None
        
    def show(self):
        """Показывает диалог анализа надежности"""
        if not PYQT_AVAILABLE:
            messagebox.showwarning(
                "Предупреждение", 
                "PyQt5 не установлен. Расширенный анализ надежности недоступен.\n"
                "Установите PyQt5 для использования этой функции."
            )
            return
        
        try:
            # Создаем QApplication если его еще нет
            if not QApplication.instance():
                self.qt_app = QApplication(sys.argv)
            else:
                self.qt_app = QApplication.instance()
            
            # Импортируем панель анализа
            from src.gui.advanced_reliability_panel import AdvancedReliabilityPanel, create_sample_network_with_states
            
            # Создаем диалог
            self.dialog = tk.Toplevel(self.parent)
            self.dialog.title("Расширенный анализ надежности ИКС")
            self.dialog.geometry("1200x800")
            self.dialog.resizable(True, True)
            
            # Создаем контейнер для PyQt виджета
            container_frame = tk.Frame(self.dialog)
            container_frame.pack(fill=tk.BOTH, expand=True)
            
            # Создаем панель анализа
            self.analysis_panel = AdvancedReliabilityPanel()
            
            # Загружаем данные
            if self.network_data and self.probabilities:
                self.analysis_panel.set_network_data(self.network_data, self.probabilities)
            else:
                # Используем пример данных
                network, probabilities, node_states = create_sample_network_with_states()
                self.analysis_panel.set_network_data(network, probabilities)
            
            # Встраиваем PyQt виджет в tkinter
            self._embed_pyqt_widget(container_frame)
            
            # Запускаем начальный анализ
            self.analysis_panel.run_analysis()
            
            # Обработчик закрытия
            self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать диалог анализа надежности: {str(e)}")
    
    def _embed_pyqt_widget(self, parent_frame):
        """Встраивает PyQt виджет в tkinter контейнер"""
        try:
            # Получаем window ID tkinter виджета
            win_id = parent_frame.winfo_id()
            
            # Создаем QWindow для встраивания
            qwindow = QWindow.fromWinId(win_id)
            
            # Создаем контейнер виджет
            container = QWidget.createWindowContainer(qwindow)
            
            # Размещаем панель анализа в контейнере
            layout = QVBoxLayout()
            layout.addWidget(self.analysis_panel)
            container.setLayout(layout)
            
            # Показываем контейнер
            container.show()
            
        except Exception as e:
            print(f"Ошибка при встраивании PyQt виджета: {e}")
            # Альтернативный способ - показываем в отдельном окне
            self._show_separate_window()
    
    def _show_separate_window(self):
        """Показывает панель анализа в отдельном окне"""
        try:
            self.analysis_panel.show()
        except Exception as e:
            print(f"Ошибка при показе отдельного окна: {e}")
    
    def _on_close(self):
        """Обработчик закрытия диалога"""
        if self.dialog:
            self.dialog.destroy()


class ConsoleReliabilityAnalyzer:
    """Консольный анализатор надежности для использования без GUI"""
    
    def __init__(self):
        self.network_data = None
        self.probabilities = None
    
    def set_network_data(self, network_data: Dict, probabilities: Dict[str, float]):
        """Устанавливает данные сети"""
        self.network_data = network_data
        self.probabilities = probabilities
    
    def run_birnbaum_analysis(self) -> Dict[str, float]:
        """Запускает анализ по критерию Бирнбаума"""
        if not self.network_data or not self.probabilities:
            raise ValueError("Данные сети не установлены")
        
        try:
            from src.analytics.advanced_reliability_analyzer import AdvancedReliabilityAnalyzer
            
            analyzer = AdvancedReliabilityAnalyzer()
            structure_matrix = self._create_structure_matrix()
            
            return analyzer.calculate_birnbaum_criterion(self.probabilities, structure_matrix)
            
        except Exception as e:
            raise RuntimeError(f"Ошибка при анализе Бирнбаума: {str(e)}")
    
    def run_system_reliability_analysis(self) -> Dict[str, float]:
        """Запускает анализ надежности системы"""
        if not self.network_data or not self.probabilities:
            raise ValueError("Данные сети не установлены")
        
        try:
            from src.analytics.advanced_reliability_analyzer import AdvancedReliabilityAnalyzer
            
            analyzer = AdvancedReliabilityAnalyzer()
            connections = self._get_connections_from_network()
            
            system_reliability = analyzer.system_reliability(self.probabilities, connections)
            failure_probs = analyzer.calculate_node_failure_probabilities(self.probabilities)
            
            return {
                'system_reliability': system_reliability,
                'failure_probabilities': failure_probs
            }
            
        except Exception as e:
            raise RuntimeError(f"Ошибка при анализе надежности системы: {str(e)}")
    
    def run_fragility_analysis(self, removal_order: List[str]) -> List[Dict]:
        """Запускает анализ хрупкости системы"""
        if not self.network_data or not self.probabilities:
            raise ValueError("Данные сети не установлены")
        
        try:
            from src.gui.advanced_reliability_panel import FragilityAnalysisModule
            
            fragility_module = FragilityAnalysisModule()
            states = fragility_module.remove_nodes_step_by_step(
                self.network_data, self.probabilities, removal_order
            )
            
            # Преобразуем состояния в словари для удобства
            results = []
            for state in states:
                results.append({
                    'nodes_count': len(state.node_states),
                    'system_reliability': state.system_reliability,
                    'connectivity_status': state.connectivity_status,
                    'critical_threshold_reached': state.critical_threshold_reached
                })
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Ошибка при анализе хрупкости: {str(e)}")
    
    def run_threats_simulation(self) -> Tuple[Dict[str, float], List[Dict]]:
        """Запускает симуляцию внешних угроз"""
        if not self.network_data or not self.probabilities:
            raise ValueError("Данные сети не установлены")
        
        try:
            from src.gui.advanced_reliability_panel import ExternalThreatsModule
            
            threats_module = ExternalThreatsModule()
            updated_probs, events = threats_module.simulate_threats(
                self.network_data, self.probabilities
            )
            
            return updated_probs, events
            
        except Exception as e:
            raise RuntimeError(f"Ошибка при симуляции угроз: {str(e)}")
    
    def _create_structure_matrix(self) -> List[List[int]]:
        """Создает матрицу связности из структуры сети"""
        if not self.network_data or 'connections' not in self.network_data:
            return []
        
        nodes = list(self.probabilities.keys())
        n = len(nodes)
        matrix = [[0] * n for _ in range(n)]
        
        # Заполняем матрицу на основе связей
        for i, node1 in enumerate(nodes):
            if node1 in self.network_data['connections']:
                for node2 in self.network_data['connections'][node1]:
                    if node2 in nodes:
                        j = nodes.index(node2)
                        matrix[i][j] = 1
                        matrix[j][i] = 1  # Симметричная матрица
        
        return matrix
    
    def _get_connections_from_network(self) -> Dict[str, List[str]]:
        """Получает связи из структуры сети"""
        if not self.network_data or 'connections' not in self.network_data:
            return {}
        
        return self.network_data['connections']


def create_sample_network_for_integration() -> Tuple[Dict, Dict[str, float]]:
    """Создает пример сети для интеграции"""
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
    
    probabilities = {
        'server1': 0.99,
        'server2': 0.98,
        'router1': 0.95,
        'router2': 0.96,
        'switch1': 0.97,
        'switch2': 0.94,
        'firewall': 0.92
    }
    
    return network, probabilities


def integrate_with_main_window(main_window):
    """Интегрирует расширенный анализ надежности с главным окном"""
    
    def show_advanced_reliability_analysis():
        """Показывает диалог расширенного анализа надежности"""
        try:
            # Получаем данные текущей сети из главного окна
            network_data = None
            probabilities = None
            
            # Попытка получить данные из симулятора
            if hasattr(main_window, 'simulator') and main_window.simulator:
                # Преобразуем данные симулятора в нужный формат
                network_data, probabilities = _extract_network_from_simulator(main_window.simulator)
            
            # Если данных нет, используем пример
            if not network_data or not probabilities:
                network_data, probabilities = create_sample_network_for_integration()
            
            # Создаем и показываем диалог
            dialog = ReliabilityAnalysisDialog(main_window.root, network_data, probabilities)
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть анализ надежности: {str(e)}")
    
    def _extract_network_from_simulator(simulator):
        """Извлекает данные сети из симулятора"""
        try:
            # Здесь нужно адаптировать под конкретную структуру симулятора
            # Это примерная реализация
            network = {
                'nodes': [],
                'connections': {}
            }
            
            probabilities = {}
            
            # Извлекаем узлы и их вероятности
            if hasattr(simulator, 'nodes'):
                for node in simulator.nodes:
                    node_id = str(node.id) if hasattr(node, 'id') else str(node)
                    network['nodes'].append({'id': node_id, 'type': 'node'})
                    probabilities[node_id] = getattr(node, 'reliability', 0.95)
            
            return network, probabilities
            
        except Exception as e:
            print(f"Ошибка при извлечении данных сети: {e}")
            return None, None
    
    # Добавляем функцию в главное окно
    main_window.show_advanced_reliability_analysis = show_advanced_reliability_analysis
    
    # Добавляем пункт меню
    if hasattr(main_window, '_create_menu'):
        original_create_menu = main_window._create_menu
        
        def enhanced_create_menu():
            original_create_menu()
            
            # Добавляем пункт в меню "Анализ"
            analysis_menu = None
            for child in main_window.root.winfo_children():
                if isinstance(child, tk.Menu):
                    # Ищем меню "Анализ"
                    try:
                        analysis_menu = child.nametowidget('analysis')
                    except:
                        pass
            
            if analysis_menu:
                analysis_menu.add_separator()
                analysis_menu.add_command(
                    label="Расширенный анализ надежности",
                    command=show_advanced_reliability_analysis
                )
        
        main_window._create_menu = enhanced_create_menu


if __name__ == "__main__":
    # Тестирование интеграции
    print("Тестирование интеграции расширенного анализа надежности...")
    
    # Создаем консольный анализатор
    analyzer = ConsoleReliabilityAnalyzer()
    
    # Загружаем пример данных
    network, probabilities = create_sample_network_for_integration()
    analyzer.set_network_data(network, probabilities)
    
    try:
        # Тестируем анализ Бирнбаума
        print("\n1. Тестирование анализа Бирнбаума:")
        birnbaum_results = analyzer.run_birnbaum_analysis()
        for node, coeff in birnbaum_results.items():
            print(f"  {node}: {coeff:.4f}")
        
        # Тестируем анализ надежности системы
        print("\n2. Тестирование анализа надежности системы:")
        reliability_results = analyzer.run_system_reliability_analysis()
        print(f"  Надежность системы: {reliability_results['system_reliability']:.6f}")
        
        # Тестируем анализ хрупкости
        print("\n3. Тестирование анализа хрупкости:")
        removal_order = ['switch1', 'switch2', 'router1']
        fragility_results = analyzer.run_fragility_analysis(removal_order)
        for i, result in enumerate(fragility_results):
            print(f"  Шаг {i+1}: узлов={result['nodes_count']}, надежность={result['system_reliability']:.6f}")
        
        # Тестируем симуляцию угроз
        print("\n4. Тестирование симуляции угроз:")
        updated_probs, events = analyzer.run_threats_simulation()
        print(f"  Произошло событий: {len(events)}")
        for event in events:
            print(f"    - {event['description']}")
        
        print("\nВсе тесты прошли успешно!")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
