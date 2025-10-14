#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль стресс-тестирования и сценарного анализа ИКС
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
import time
from .system_model import SystemModel
from .simulation import NetworkSimulator, SimulationEvent, EventType


class StressTestType(Enum):
    """Типы стресс-тестов"""
    LOAD_INCREASE = "load_increase"
    FAILURE_INJECTION = "failure_injection"
    NETWORK_CONGESTION = "network_congestion"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CASCADE_FAILURE = "cascade_failure"
    RANDOM_STRESS = "random_stress"


@dataclass
class StressTestScenario:
    """Сценарий стресс-тестирования"""
    name: str
    test_type: StressTestType
    duration: float  # секунды
    parameters: Dict  # параметры сценария
    description: str = ""


@dataclass
class StressTestResult:
    """Результат стресс-тестирования"""
    scenario_name: str
    success: bool
    metrics: Dict
    failure_points: List[str]
    recovery_time: float
    performance_degradation: float


class StressTester:
    """Класс для проведения стресс-тестов"""
    
    def __init__(self, system_model: SystemModel):
        self.system_model = system_model
        self.test_results = []
        self.baseline_metrics = {}
    
    def run_baseline_test(self, duration: float = 300) -> Dict:
        """Запустить базовый тест для получения эталонных метрик"""
        print("Запуск базового теста...")
        
        simulator = NetworkSimulator(self.system_model, duration)
        simulator.run_simulation()
        
        self.baseline_metrics = simulator.get_simulation_results()['metrics']
        
        print(f"Базовый тест завершен:")
        print(f"  Успешность: {self.baseline_metrics.get('success_rate', 0):.3f}")
        print(f"  Время отклика: {self.baseline_metrics.get('average_response_time', 0):.3f} сек")
        print(f"  Пропускная способность: {self.baseline_metrics.get('network_throughput', 0):.2f} Мбит/сек")
        
        return self.baseline_metrics
    
    def run_load_increase_test(self, max_load_multiplier: float = 5.0, 
                              duration: float = 300) -> StressTestResult:
        """Тест увеличения нагрузки"""
        scenario = StressTestScenario(
            name="Увеличение нагрузки",
            test_type=StressTestType.LOAD_INCREASE,
            duration=duration,
            parameters={'max_load_multiplier': max_load_multiplier},
            description=f"Постепенное увеличение нагрузки до {max_load_multiplier}x"
        )
        
        print(f"\n=== {scenario.name} ===")
        
        # Создаем симулятор с увеличенной нагрузкой
        simulator = NetworkSimulator(self.system_model, duration)
        
        # Модифицируем генератор трафика для увеличенной нагрузки
        original_traffic_gen = simulator._traffic_generator
        
        def modified_traffic_generator():
            load_factor = 1.0
            max_factor = max_load_multiplier
            increment = (max_factor - 1.0) / (duration / 60.0)  # увеличиваем каждую минуту
            
            while True:
                # Генерируем трафик с текущим коэффициентом нагрузки
                for _ in range(int(load_factor)):
                    source = random.choice(list(simulator.network_nodes.keys()))
                    target = random.choice(list(simulator.network_nodes.keys()))
                    
                    if source != target:
                        data_size = random.uniform(0.1, 10.0) * load_factor
                        priority = random.randint(1, 5)
                        
                        event = SimulationEvent(
                            event_type=EventType.TRAFFIC_REQUEST,
                            timestamp=simulator.env.now,
                            source=source,
                            target=target,
                            data_size=data_size,
                            priority=priority
                        )
                        
                        simulator.env.process(simulator._handle_traffic_request(event))
                
                # Увеличиваем нагрузку
                load_factor = min(load_factor + increment, max_factor)
                
                interval = random.expovariate(1.0 / load_factor)
                yield simulator.env.timeout(interval)
        
        # Заменяем генератор трафика
        simulator._traffic_generator = modified_traffic_generator
        
        # Запускаем тест
        start_time = time.time()
        simulator.run_simulation()
        test_duration = time.time() - start_time
        
        # Анализируем результаты
        results = simulator.get_simulation_results()['metrics']
        success = self._analyze_stress_test_results(results)
        
        failure_points = self._identify_failure_points(simulator)
        recovery_time = self._calculate_recovery_time(simulator)
        performance_degradation = self._calculate_performance_degradation(results)
        
        result = StressTestResult(
            scenario_name=scenario.name,
            success=success,
            metrics=results,
            failure_points=failure_points,
            recovery_time=recovery_time,
            performance_degradation=performance_degradation
        )
        
        self.test_results.append(result)
        return result
    
    def run_failure_injection_test(self, failure_rate: float = 0.3, 
                                  duration: float = 300) -> StressTestResult:
        """Тест инъекции отказов"""
        scenario = StressTestScenario(
            name="Инъекция отказов",
            test_type=StressTestType.FAILURE_INJECTION,
            duration=duration,
            parameters={'failure_rate': failure_rate},
            description=f"Имитация {failure_rate*100:.1f}% отказов компонентов"
        )
        
        print(f"\n=== {scenario.name} ===")
        
        simulator = NetworkSimulator(self.system_model, duration)
        
        # Модифицируем генератор отказов для более агрессивного режима
        def aggressive_failure_generator():
            while True:
                # Отказы узлов
                if random.random() < failure_rate * 0.01:  # Увеличиваем частоту отказов
                    node_id = random.choice(list(simulator.network_nodes.keys()))
                    simulator.network_nodes[node_id].fail()
                    
                    event = SimulationEvent(
                        event_type=EventType.NODE_FAILURE,
                        timestamp=simulator.env.now,
                        source=node_id
                    )
                    simulator.add_event(event)
                
                # Отказы каналов
                if random.random() < failure_rate * 0.005:
                    link_id = random.choice(list(simulator.network_links.keys()))
                    simulator.network_links[link_id].fail()
                    
                    event = SimulationEvent(
                        event_type=EventType.LINK_FAILURE,
                        timestamp=simulator.env.now,
                        source=link_id
                    )
                    simulator.add_event(event)
                
                yield simulator.env.timeout(1.0)
        
        # Заменяем генератор отказов
        simulator._failure_generator = aggressive_failure_generator
        
        # Запускаем тест
        start_time = time.time()
        simulator.run_simulation()
        test_duration = time.time() - start_time
        
        # Анализируем результаты
        results = simulator.get_simulation_results()['metrics']
        success = self._analyze_stress_test_results(results)
        
        failure_points = self._identify_failure_points(simulator)
        recovery_time = self._calculate_recovery_time(simulator)
        performance_degradation = self._calculate_performance_degradation(results)
        
        result = StressTestResult(
            scenario_name=scenario.name,
            success=success,
            metrics=results,
            failure_points=failure_points,
            recovery_time=recovery_time,
            performance_degradation=performance_degradation
        )
        
        self.test_results.append(result)
        return result
    
    def run_cascade_failure_test(self, initial_failure_count: int = 2, 
                                duration: float = 300) -> StressTestResult:
        """Тест каскадных отказов"""
        scenario = StressTestScenario(
            name="Каскадные отказы",
            test_type=StressTestType.CASCADE_FAILURE,
            duration=duration,
            parameters={'initial_failure_count': initial_failure_count},
            description=f"Имитация каскадных отказов начиная с {initial_failure_count} компонентов"
        )
        
        print(f"\n=== {scenario.name} ===")
        
        simulator = NetworkSimulator(self.system_model, duration)
        
        # Специальный генератор каскадных отказов
        def cascade_failure_generator():
            # Начальные отказы
            failed_components = set()
            
            # Отказываем начальные компоненты
            nodes = list(simulator.network_nodes.keys())
            links = list(simulator.network_links.keys())
            
            for _ in range(min(initial_failure_count, len(nodes))):
                node_id = random.choice(nodes)
                simulator.network_nodes[node_id].fail()
                failed_components.add(f"node_{node_id}")
                nodes.remove(node_id)
            
            while True:
                # Каскадные отказы на основе нагрузки
                for node_id, node in simulator.network_nodes.items():
                    if not node.is_failed:
                        # Вероятность отказа увеличивается с нагрузкой
                        failure_prob = node.node.cpu_load * node.node.memory_usage * 0.1
                        if random.random() < failure_prob:
                            node.fail()
                            failed_components.add(f"node_{node_id}")
                
                # Аналогично для каналов
                for link_id, link in simulator.network_links.items():
                    if not link.is_failed:
                        failure_prob = link.link.utilization * 0.05
                        if random.random() < failure_prob:
                            link.fail()
                            failed_components.add(f"link_{link_id}")
                
                yield simulator.env.timeout(10.0)  # Проверяем каждые 10 секунд
        
        # Заменяем генератор отказов
        simulator._failure_generator = cascade_failure_generator
        
        # Запускаем тест
        start_time = time.time()
        simulator.run_simulation()
        test_duration = time.time() - start_time
        
        # Анализируем результаты
        results = simulator.get_simulation_results()['metrics']
        success = self._analyze_stress_test_results(results)
        
        failure_points = self._identify_failure_points(simulator)
        recovery_time = self._calculate_recovery_time(simulator)
        performance_degradation = self._calculate_performance_degradation(results)
        
        result = StressTestResult(
            scenario_name=scenario.name,
            success=success,
            metrics=results,
            failure_points=failure_points,
            recovery_time=recovery_time,
            performance_degradation=performance_degradation
        )
        
        self.test_results.append(result)
        return result
    
    def run_network_congestion_test(self, congestion_factor: float = 3.0, 
                                   duration: float = 300) -> StressTestResult:
        """Тест перегрузки сети"""
        scenario = StressTestScenario(
            name="Перегрузка сети",
            test_type=StressTestType.NETWORK_CONGESTION,
            duration=duration,
            parameters={'congestion_factor': congestion_factor},
            description=f"Имитация перегрузки сети с коэффициентом {congestion_factor}"
        )
        
        print(f"\n=== {scenario.name} ===")
        
        simulator = NetworkSimulator(self.system_model, duration)
        
        # Увеличиваем использование каналов
        for link in simulator.network_links.values():
            link.link.utilization = min(link.link.utilization * congestion_factor, 1.0)
        
        # Увеличиваем загрузку узлов
        for node in simulator.network_nodes.values():
            node.node.cpu_load = min(node.node.cpu_load * congestion_factor, 1.0)
            node.node.memory_usage = min(node.node.memory_usage * congestion_factor, 1.0)
        
        # Запускаем тест
        start_time = time.time()
        simulator.run_simulation()
        test_duration = time.time() - start_time
        
        # Анализируем результаты
        results = simulator.get_simulation_results()['metrics']
        success = self._analyze_stress_test_results(results)
        
        failure_points = self._identify_failure_points(simulator)
        recovery_time = self._calculate_recovery_time(simulator)
        performance_degradation = self._calculate_performance_degradation(results)
        
        result = StressTestResult(
            scenario_name=scenario.name,
            success=success,
            metrics=results,
            failure_points=failure_points,
            recovery_time=recovery_time,
            performance_degradation=performance_degradation
        )
        
        self.test_results.append(result)
        return result
    
    def run_random_stress_test(self, duration: float = 300) -> StressTestResult:
        """Случайный стресс-тест"""
        scenario = StressTestScenario(
            name="Случайный стресс",
            test_type=StressTestType.RANDOM_STRESS,
            duration=duration,
            parameters={},
            description="Случайная комбинация различных стресс-факторов"
        )
        
        print(f"\n=== {scenario.name} ===")
        
        simulator = NetworkSimulator(self.system_model, duration)
        
        # Комбинированный генератор стресса
        def random_stress_generator():
            while True:
                # Случайно выбираем тип стресса
                stress_type = random.choice([
                    'load_spike', 'node_failure', 'link_failure', 
                    'congestion', 'resource_exhaustion'
                ])
                
                if stress_type == 'load_spike':
                    # Спайк нагрузки
                    for _ in range(10):
                        source = random.choice(list(simulator.network_nodes.keys()))
                        target = random.choice(list(simulator.network_nodes.keys()))
                        
                        if source != target:
                            event = SimulationEvent(
                                event_type=EventType.TRAFFIC_REQUEST,
                                timestamp=simulator.env.now,
                                source=source,
                                target=target,
                                data_size=random.uniform(5, 50),
                                priority=random.randint(1, 5)
                            )
                            simulator.env.process(simulator._handle_traffic_request(event))
                
                elif stress_type == 'node_failure':
                    node_id = random.choice(list(simulator.network_nodes.keys()))
                    simulator.network_nodes[node_id].fail()
                
                elif stress_type == 'link_failure':
                    link_id = random.choice(list(simulator.network_links.keys()))
                    simulator.network_links[link_id].fail()
                
                elif stress_type == 'congestion':
                    # Временная перегрузка
                    for link in simulator.network_links.values():
                        link.link.utilization = min(link.link.utilization * 2, 1.0)
                
                elif stress_type == 'resource_exhaustion':
                    # Исчерпание ресурсов
                    for node in simulator.network_nodes.values():
                        node.node.cpu_load = min(node.node.cpu_load * 1.5, 1.0)
                        node.node.memory_usage = min(node.node.memory_usage * 1.5, 1.0)
                
                yield simulator.env.timeout(random.uniform(5, 30))  # Случайный интервал
        
        # Заменяем генераторы
        simulator._failure_generator = random_stress_generator
        
        # Запускаем тест
        start_time = time.time()
        simulator.run_simulation()
        test_duration = time.time() - start_time
        
        # Анализируем результаты
        results = simulator.get_simulation_results()['metrics']
        success = self._analyze_stress_test_results(results)
        
        failure_points = self._identify_failure_points(simulator)
        recovery_time = self._calculate_recovery_time(simulator)
        performance_degradation = self._calculate_performance_degradation(results)
        
        result = StressTestResult(
            scenario_name=scenario.name,
            success=success,
            metrics=results,
            failure_points=failure_points,
            recovery_time=recovery_time,
            performance_degradation=performance_degradation
        )
        
        self.test_results.append(result)
        return result
    
    def _analyze_stress_test_results(self, results: Dict) -> bool:
        """Анализ результатов стресс-теста"""
        if not self.baseline_metrics:
            return True
        
        # Критерии успешности
        success_rate = results.get('success_rate', 0)
        baseline_success_rate = self.baseline_metrics.get('success_rate', 1)
        
        # Считаем тест успешным, если успешность не упала более чем на 50%
        return success_rate >= baseline_success_rate * 0.5
    
    def _identify_failure_points(self, simulator: NetworkSimulator) -> List[str]:
        """Определить точки отказа"""
        failure_points = []
        
        # Анализируем узлы
        for node_id, node in simulator.network_nodes.items():
            if node.is_failed or node.failed_requests > node.processed_requests * 0.5:
                failure_points.append(f"Node {node_id}")
        
        # Анализируем каналы
        for link_id, link in simulator.network_links.items():
            if link.is_failed or link.failed_transfers > link.transferred_data * 0.3:
                failure_points.append(f"Link {link_id}")
        
        return failure_points
    
    def _calculate_recovery_time(self, simulator: NetworkSimulator) -> float:
        """Рассчитать время восстановления"""
        # Упрощенный расчет: среднее время между отказом и восстановлением
        recovery_events = [
            event for event in simulator.events
            if event.event_type in [EventType.NODE_RECOVERY, EventType.LINK_RECOVERY]
        ]
        
        if not recovery_events:
            return 0.0
        
        return np.mean([event.timestamp for event in recovery_events])
    
    def _calculate_performance_degradation(self, results: Dict) -> float:
        """Рассчитать деградацию производительности"""
        if not self.baseline_metrics:
            return 0.0
        
        baseline_throughput = self.baseline_metrics.get('network_throughput', 1)
        current_throughput = results.get('network_throughput', 0)
        
        if baseline_throughput == 0:
            return 1.0
        
        degradation = 1 - (current_throughput / baseline_throughput)
        return max(0, min(1, degradation))
    
    def run_all_stress_tests(self, duration: float = 300) -> List[StressTestResult]:
        """Запустить все стресс-тесты"""
        print("=== Запуск полного набора стресс-тестов ===")
        
        # Сначала базовый тест
        self.run_baseline_test(duration)
        
        # Затем все стресс-тесты
        tests = [
            lambda: self.run_load_increase_test(max_load_multiplier=3.0, duration=duration),
            lambda: self.run_failure_injection_test(failure_rate=0.2, duration=duration),
            lambda: self.run_cascade_failure_test(initial_failure_count=2, duration=duration),
            lambda: self.run_network_congestion_test(congestion_factor=2.5, duration=duration),
            lambda: self.run_random_stress_test(duration=duration)
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                print(f"Тест '{result.scenario_name}': {'УСПЕХ' if result.success else 'НЕУДАЧА'}")
            except Exception as e:
                print(f"Ошибка при выполнении теста: {e}")
        
        return self.test_results
    
    def generate_stress_test_report(self) -> pd.DataFrame:
        """Сгенерировать отчет по стресс-тестам"""
        if not self.test_results:
            return pd.DataFrame()
        
        report_data = []
        for result in self.test_results:
            report_data.append({
                'scenario': result.scenario_name,
                'success': result.success,
                'total_requests': result.metrics.get('total_requests', 0),
                'successful_requests': result.metrics.get('successful_requests', 0),
                'success_rate': result.metrics.get('success_rate', 0),
                'average_response_time': result.metrics.get('average_response_time', 0),
                'network_throughput': result.metrics.get('network_throughput', 0),
                'failure_points_count': len(result.failure_points),
                'recovery_time': result.recovery_time,
                'performance_degradation': result.performance_degradation
            })
        
        return pd.DataFrame(report_data)


def create_sample_stress_test() -> Tuple[SystemModel, StressTester]:
    """Создать пример стресс-тестирования"""
    from .system_model import create_sample_network
    
    # Создаем тестовую систему
    system = create_sample_network()
    
    # Создаем стресс-тестер
    tester = StressTester(system)
    
    return system, tester


if __name__ == "__main__":
    # Тестирование модуля
    system, tester = create_sample_stress_test()
    
    print("=== Стресс-тестирование ИКС ===")
    print(f"Система: {system.name}")
    print(f"Узлов: {len(system.nodes)}, Каналов: {len(system.links)}")
    
    # Запускаем набор стресс-тестов
    results = tester.run_all_stress_tests(duration=60)  # 1 минута на тест
    
    print(f"\n=== Результаты стресс-тестирования ===")
    for result in results:
        print(f"\n{result.scenario_name}:")
        print(f"  Успех: {'Да' if result.success else 'Нет'}")
        print(f"  Успешность: {result.metrics.get('success_rate', 0):.3f}")
        print(f"  Пропускная способность: {result.metrics.get('network_throughput', 0):.2f} Мбит/сек")
        print(f"  Точки отказа: {len(result.failure_points)}")
        print(f"  Деградация производительности: {result.performance_degradation:.1%}")
    
    # Генерируем отчет
    report = tester.generate_stress_test_report()
    if not report.empty:
        print(f"\nОтчет по стресс-тестам:")
        print(report[['scenario', 'success', 'success_rate', 'performance_degradation']])
