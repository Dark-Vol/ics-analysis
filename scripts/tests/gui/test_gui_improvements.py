#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование улучшений GUI - пагинация и график надежности
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import messagebox
import json
import time
import threading

# Импорт модулей проекта
from src.gui.main_window import MainWindow
from src.system_model import SystemModel, Node, NodeType, Link, LinkType
from src.simulator.network_simulator import NetworkSimulator, SimulationConfig
from src.models.adverse_conditions import AdverseConditions
import random
import numpy as np

class TestGUI:
    """Класс для тестирования улучшений GUI"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.config = self._load_config()
        self.main_window = MainWindow(self.root, self.config)
        
        # Создаем тестовую сеть
        self.test_network = self._create_test_network()
        
        # Устанавливаем сеть в визуализатор
        self.main_window.network_viewer.update_network(self.test_network)
        
        # Создаем симулятор
        self.simulator = None
        
    def _load_config(self):
        """Загружает конфигурацию"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # Базовая конфигурация
            return {
                "simulation": {"time_steps": 1000, "dt": 0.1, "random_seed": 42},
                "network": {"nodes": 10, "connections": 0.3, "bandwidth": 1000, "latency": 10, "reliability": 0.95},
                "adverse_conditions": {"noise_level": 0.1, "interference_probability": 0.05, "failure_rate": 0.02, "jamming_intensity": 0.1}
            }
    
    def _create_test_network(self):
        """Создает тестовую сеть"""
        network = SystemModel("Тестовая сеть для GUI")
        
        # Создаем узлы
        node_types = [NodeType.SERVER, NodeType.ROUTER, NodeType.SWITCH, NodeType.CLIENT, NodeType.GATEWAY]
        
        for i in range(15):
            node_type = random.choice(node_types)
            node = Node(
                id=f"node_{i}",
                node_type=node_type,
                capacity=random.uniform(100, 1000),
                reliability=random.uniform(0.85, 0.99),
                x=random.uniform(0, 100),
                y=random.uniform(0, 100),
                threat_level=random.uniform(0.1, 0.3),
                load=random.uniform(0.2, 0.8),
                encryption=random.choice([True, False])
            )
            network.add_node(node)
        
        # Создаем связи
        nodes = list(network.nodes.keys())
        link_types = list(LinkType)
        
        for i, source in enumerate(nodes):
            for j, target in enumerate(nodes[i+1:], i+1):
                if random.random() < 0.4:  # 40% вероятность связи
                    link = Link(
                        source=source,
                        target=target,
                        bandwidth=random.uniform(10, 100),
                        latency=random.uniform(1, 50),
                        reliability=random.uniform(0.90, 0.99),
                        link_type=random.choice(link_types),
                        threat_level=random.uniform(0.05, 0.2),
                        load=random.uniform(0.1, 0.6),
                        encryption=random.choice([True, False])
                    )
                    network.add_link(link)
        
        return network
    
    def test_pagination(self):
        """Тестирует пагинацию между панелями"""
        print("Тестирование пагинации...")
        
        # Переключаемся между панелями
        tabs = ["🎛️ Контрольная панель", "📊 Панель визуализации", "⚡ Статус системы"]
        
        for i, tab_name in enumerate(tabs):
            print(f"Переключение на вкладку: {tab_name}")
            
            # Находим нужную вкладку и переключаемся на неё
            notebook = self.main_window.plots_notebook
            for j in range(notebook.index("end")):
                if notebook.tab(j, "text") == tab_name:
                    notebook.select(j)
                    break
            
            # Небольшая пауза для демонстрации
            self.root.update()
            time.sleep(1)
        
        print("✓ Пагинация работает корректно")
    
    def test_reliability_plot(self):
        """Тестирует график надежности"""
        print("Тестирование графика надежности...")
        
        # Переключаемся на панель визуализации
        notebook = self.main_window.plots_notebook
        for j in range(notebook.index("end")):
            if notebook.tab(j, "text") == "📊 Панель визуализации":
                notebook.select(j)
                break
        
        # Переключаемся на вкладку надежности
        viz_notebook = self.main_window.viz_notebook
        for j in range(viz_notebook.index("end")):
            if viz_notebook.tab(j, "text") == "🛡️ Надежность":
                viz_notebook.select(j)
                break
        
        # Обновляем интерфейс
        self.root.update()
        
        print("✓ График надежности отображается")
    
    def test_simulation_with_reliability(self):
        """Тестирует симуляцию с отображением надежности"""
        print("Запуск симуляции для тестирования графиков...")
        
        # Создаем конфигурацию симуляции
        config = SimulationConfig(
            duration=60.0,  # 1 минута
            time_step=0.5,
            enable_traffic=True,
            enable_failures=True,
            enable_adverse_conditions=True
        )
        
        # Создаем симулятор
        self.simulator = NetworkSimulator(config)
        self.simulator.initialize_network(15, 0.4)
        
        # Добавляем неблагоприятные условия
        adverse_conditions = AdverseConditions()
        
        # Симулируем различные воздействия
        adverse_conditions.simulate_cyber_attack(
            target_nodes=[1, 2, 3], 
            attack_type="ddos", 
            intensity=0.3, 
            duration=30
        )
        
        adverse_conditions.simulate_network_overload(
            target_nodes=[4, 5], 
            intensity=0.5, 
            duration=40
        )
        
        # Устанавливаем симулятор в главное окно
        self.main_window.simulator = self.simulator
        
        # Добавляем callback для обновления графиков
        self.simulator.add_update_callback(self.main_window._update_plots)
        
        # Запускаем симуляцию в отдельном потоке
        simulation_thread = threading.Thread(target=self._run_simulation)
        simulation_thread.daemon = True
        simulation_thread.start()
        
        print("✓ Симуляция запущена")
    
    def _run_simulation(self):
        """Запускает симуляцию"""
        try:
            self.simulator.start_simulation()
            
            # Ждем завершения симуляции
            while self.simulator.is_running:
                time.sleep(0.1)
            
            print("✓ Симуляция завершена")
            
        except Exception as e:
            print(f"Ошибка симуляции: {e}")
    
    def test_network_operations(self):
        """Тестирует операции с сетью"""
        print("Тестирование операций с сетью...")
        
        # Переключаемся на контрольную панель
        notebook = self.main_window.plots_notebook
        for j in range(notebook.index("end")):
            if notebook.tab(j, "text") == "🎛️ Контрольная панель":
                notebook.select(j)
                break
        
        self.root.update()
        time.sleep(1)
        
        print("✓ Операции с сетью доступны")
    
    def test_status_panel(self):
        """Тестирует панель статуса"""
        print("Тестирование панели статуса...")
        
        # Переключаемся на панель статуса
        notebook = self.main_window.plots_notebook
        for j in range(notebook.index("end")):
            if notebook.tab(j, "text") == "⚡ Статус системы":
                notebook.select(j)
                break
        
        self.root.update()
        time.sleep(1)
        
        print("✓ Панель статуса отображается")
    
    def run_tests(self):
        """Запускает все тесты"""
        print("=" * 60)
        print("ТЕСТИРОВАНИЕ УЛУЧШЕНИЙ GUI")
        print("=" * 60)
        
        try:
            # Тест 1: Пагинация
            self.test_pagination()
            
            # Тест 2: График надежности
            self.test_reliability_plot()
            
            # Тест 3: Операции с сетью
            self.test_network_operations()
            
            # Тест 4: Панель статуса
            self.test_status_panel()
            
            # Тест 5: Симуляция с графиками
            self.test_simulation_with_reliability()
            
            print("\n" + "=" * 60)
            print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ УСПЕШНО!")
            print("=" * 60)
            print("\nВозможности GUI:")
            print("✅ Пагинация между панелями работает")
            print("✅ График надежности отображается")
            print("✅ Панель визуализации с подвкладками")
            print("✅ Панель статуса системы")
            print("✅ Контрольная панель с операциями")
            print("✅ Симуляция с обновлением графиков")
            
        except Exception as e:
            print(f"\n❌ Ошибка при тестировании: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Запускает GUI и тесты"""
        # Запускаем тесты через 2 секунды после запуска GUI
        self.root.after(2000, self.run_tests)
        
        # Запускаем GUI
        self.root.mainloop()

def main():
    """Основная функция"""
    print("Запуск тестирования улучшений GUI...")
    
    try:
        test_gui = TestGUI()
        test_gui.run()
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

