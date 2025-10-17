#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки остановки симуляции
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import threading
from src.simulator.network_simulator import NetworkSimulator, SimulationConfig
from src.utils.program_state_manager import ProgramStateManager
from src.system_model import SystemModel, Node, NodeType, Link, LinkType
import random

def test_simulator_stop():
    """Тестирует остановку симулятора"""
    print("=== ТЕСТ ОСТАНОВКИ СИМУЛЯТОРА ===")
    
    try:
        # Создаем конфигурацию симуляции
        config = SimulationConfig(
            duration=60.0,  # 1 минута
            time_step=0.5,
            enable_traffic=True,
            enable_failures=True,
            enable_adverse_conditions=True
        )
        
        # Создаем симулятор
        simulator = NetworkSimulator(config)
        
        # Создаем тестовую сеть
        network = SystemModel("Тестовая сеть")
        
        # Добавляем узлы
        for i in range(5):
            node = Node(
                id=f"node_{i}",
                node_type=NodeType.SERVER,
                capacity=random.uniform(100, 1000),
                reliability=random.uniform(0.85, 0.99),
                x=random.uniform(0, 100),
                y=random.uniform(0, 100),
                threat_level=random.uniform(0.1, 0.3),
                load=random.uniform(0.1, 0.8)
            )
            network.add_node(node)
        
        # Добавляем связи
        nodes = list(network.nodes.keys())
        for i, source in enumerate(nodes):
            for j, target in enumerate(nodes[i+1:], i+1):
                if random.random() < 0.5:  # 50% вероятность связи
                    link = Link(
                        source=source,
                        target=target,
                        bandwidth=random.uniform(10, 100),
                        latency=random.uniform(1, 50),
                        reliability=random.uniform(0.90, 0.99),
                        link_type=LinkType.ETHERNET,
                        threat_level=random.uniform(0.05, 0.2),
                        load=random.uniform(0.1, 0.6)
                    )
                    network.add_link(link)
        
        # Инициализируем симулятор с сетью
        simulator.initialize_network(len(network.nodes), 0.5)
        
        print(f"+ Создана тестовая сеть с {len(network.nodes)} узлами и {len(network.links)} связями")
        print(f"+ Симулятор инициализирован")
        
        # Запускаем симуляцию
        print("+ Запускаем симуляцию...")
        simulator.start_simulation()
        
        # Проверяем, что симуляция запущена
        time.sleep(1)  # Даем время на запуск
        print(f"+ Симуляция запущена: {simulator.is_running}")
        
        # Останавливаем симуляцию
        print("+ Останавливаем симуляцию...")
        simulator.stop_simulation()
        
        # Проверяем, что симуляция остановлена
        time.sleep(1)  # Даем время на остановку
        print(f"+ Симуляция остановлена: {not simulator.is_running}")
        
        if not simulator.is_running:
            print("+ Тест остановки симулятора прошел успешно")
            return True
        else:
            print("- Симулятор не остановился")
            return False
            
    except Exception as e:
        print(f"- Ошибка в тесте симулятора: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_program_state_manager_stop():
    """Тестирует остановку через ProgramStateManager"""
    print("\n=== ТЕСТ PROGRAM_STATE_MANAGER.STOP_PROGRAM ===")
    
    try:
        # Создаем менеджер состояния
        state_manager = ProgramStateManager()
        
        # Проверяем начальное состояние
        print(f"+ Начальное состояние: {state_manager.state.value}")
        
        # Запускаем программу
        success = state_manager.start_program()
        print(f"+ Запуск программы: {success}")
        print(f"+ Состояние после запуска: {state_manager.state.value}")
        
        # Останавливаем программу
        success = state_manager.stop_program()
        print(f"+ Остановка программы: {success}")
        print(f"+ Состояние после остановки: {state_manager.state.value}")
        
        if state_manager.state.value == 'stopped':
            print("+ Тест ProgramStateManager.stop_program прошел успешно")
            return True
        else:
            print("- ProgramStateManager не остановился")
            return False
            
    except Exception as e:
        print(f"- Ошибка в тесте ProgramStateManager: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("ЗАПУСК ТЕСТОВ ОСТАНОВКИ СИМУЛЯЦИИ")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 2
    
    try:
        # Тест 1: Остановка симулятора
        if test_simulator_stop():
            tests_passed += 1
        
        # Тест 2: Остановка через ProgramStateManager
        if test_program_state_manager_stop():
            tests_passed += 1
        
        print("\n" + "=" * 50)
        print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ: {tests_passed}/{total_tests} тестов пройдено")
        
        if tests_passed == total_tests:
            print("ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("Остановка симуляции работает корректно")
            return True
        else:
            print("НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
            return False
        
    except Exception as e:
        print(f"\nОШИБКА В ТЕСТАХ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
