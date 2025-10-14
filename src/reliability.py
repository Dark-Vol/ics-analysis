#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль анализа надежности и отказоустойчивости ИКС
"""

import numpy as np
import pandas as pd
import sympy as sp
from sympy.stats import *
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import networkx as nx
from .system_model import SystemModel, Node, Link


class FailureType(Enum):
    """Типы отказов"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    POWER = "power"
    HUMAN = "human"
    ENVIRONMENTAL = "environmental"


@dataclass
class FailureEvent:
    """Событие отказа"""
    id: str
    failure_type: FailureType
    probability: float
    description: str
    affected_components: List[str]
    impact_level: int  # 1-5, где 5 - критический


class FaultTree:
    """Дерево отказов (Fault Tree Analysis)"""
    
    def __init__(self, name: str):
        self.name = name
        self.events = {}
        self.gates = {}  # Логические вентили
        self.top_event = None
    
    def add_event(self, event: FailureEvent):
        """Добавить событие отказа"""
        self.events[event.id] = event
    
    def add_gate(self, gate_id: str, gate_type: str, inputs: List[str]):
        """Добавить логический вентиль"""
        self.gates[gate_id] = {
            'type': gate_type,  # 'AND', 'OR', 'NOT'
            'inputs': inputs
        }
    
    def calculate_top_event_probability(self) -> float:
        """Рассчитать вероятность топ-события"""
        if not self.top_event:
            return 0.0
        
        return self._calculate_gate_probability(self.top_event)
    
    def _calculate_gate_probability(self, gate_id: str) -> float:
        """Рассчитать вероятность для логического вентиля"""
        if gate_id in self.events:
            return self.events[gate_id].probability
        
        if gate_id not in self.gates:
            return 0.0
        
        gate = self.gates[gate_id]
        input_probs = [self._calculate_gate_probability(input_id) 
                      for input_id in gate['inputs']]
        
        if gate['type'] == 'AND':
            return np.prod(input_probs)
        elif gate['type'] == 'OR':
            return 1 - np.prod([1 - p for p in input_probs])
        elif gate['type'] == 'NOT':
            return 1 - input_probs[0] if input_probs else 0.0
        
        return 0.0


class ReliabilityAnalyzer:
    """Анализатор надежности ИКС"""
    
    def __init__(self, system_model: SystemModel):
        self.system_model = system_model
        self.failure_rates = {}
        self.repair_rates = {}
        self.availability_data = {}
    
    def calculate_component_reliability(self, component_id: str, 
                                      time_hours: float = 8760) -> float:
        """Рассчитать надежность компонента"""
        # Используем экспоненциальное распределение
        if component_id in self.failure_rates:
            failure_rate = self.failure_rates[component_id]
            return np.exp(-failure_rate * time_hours)
        
        # Если нет данных о частоте отказов, используем базовую надежность
        if component_id in self.system_model.nodes:
            return self.system_model.nodes[component_id].reliability
        elif any(component_id in link for link in self.system_model.links):
            # Для каналов берем среднюю надежность
            return 0.95
        
        return 0.9  # Значение по умолчанию
    
    def calculate_system_reliability(self, time_hours: float = 8760) -> Dict[str, float]:
        """Рассчитать надежность системы"""
        results = {}
        
        # Надежность узлов
        for node_id in self.system_model.nodes:
            results[f"node_{node_id}"] = self.calculate_component_reliability(node_id, time_hours)
        
        # Надежность каналов
        for (source, target), link in self.system_model.links.items():
            link_id = f"{source}_{target}"
            results[f"link_{link_id}"] = self.calculate_component_reliability(link_id, time_hours)
        
        # Надежность системы в целом (минимальная надежность среди всех компонентов)
        results['system_overall'] = min(results.values()) if results else 0.0
        
        return results
    
    def calculate_availability(self, component_id: str) -> float:
        """Рассчитать доступность компонента"""
        if component_id in self.availability_data:
            return self.availability_data[component_id]
        
        # Формула доступности: MTTF / (MTTF + MTTR)
        # Где MTTF - среднее время до отказа, MTTR - среднее время восстановления
        
        if component_id in self.failure_rates and component_id in self.repair_rates:
            mttf = 1.0 / self.failure_rates[component_id]
            mttr = 1.0 / self.repair_rates[component_id]
            return mttf / (mttf + mttr)
        
        # Значения по умолчанию
        if component_id in self.system_model.nodes:
            node = self.system_model.nodes[component_id]
            if node.node_type.value == 'server':
                return 0.999  # 99.9% для серверов
            elif node.node_type.value == 'router':
                return 0.995  # 99.5% для маршрутизаторов
            else:
                return 0.99   # 99% для остальных
        
        return 0.95  # Для каналов связи
    
    def calculate_network_connectivity_reliability(self) -> float:
        """Рассчитать надежность связности сети"""
        if not self.system_model.graph.nodes():
            return 0.0
        
        # Используем алгоритм для расчета надежности связности
        # Упрощенная модель: вероятность того, что сеть остается связной
        
        node_probs = {}
        for node_id in self.system_model.nodes:
            node_probs[node_id] = self.calculate_availability(node_id)
        
        edge_probs = {}
        for (source, target), link in self.system_model.links.items():
            edge_probs[(source, target)] = self.calculate_availability(f"{source}_{target}")
        
        # Простая оценка: произведение вероятностей всех компонентов
        # В реальности это более сложный расчет
        all_probs = list(node_probs.values()) + list(edge_probs.values())
        return np.prod(all_probs) if all_probs else 0.0
    
    def monte_carlo_reliability_analysis(self, num_simulations: int = 10000) -> Dict[str, float]:
        """Анализ надежности методом Монте-Карло"""
        results = {
            'system_available_count': 0,
            'component_failures': {},
            'average_uptime': 0.0
        }
        
        for _ in range(num_simulations):
            # Симулируем отказы компонентов
            failed_components = []
            
            # Проверяем узлы
            for node_id in self.system_model.nodes:
                availability = self.calculate_availability(node_id)
                if np.random.random() > availability:
                    failed_components.append(node_id)
                    if node_id not in results['component_failures']:
                        results['component_failures'][node_id] = 0
                    results['component_failures'][node_id] += 1
            
            # Проверяем каналы
            for (source, target), link in self.system_model.links.items():
                link_id = f"{source}_{target}"
                availability = self.calculate_availability(link_id)
                if np.random.random() > availability:
                    failed_components.append(link_id)
                    if link_id not in results['component_failures']:
                        results['component_failures'][link_id] = 0
                    results['component_failures'][link_id] += 1
            
            # Проверяем связность сети
            if self._is_system_connected_after_failures(failed_components):
                results['system_available_count'] += 1
        
        results['system_reliability'] = results['system_available_count'] / num_simulations
        results['average_uptime'] = results['system_reliability'] * 8760  # часов в году
        
        return results
    
    def _is_system_connected_after_failures(self, failed_components: List[str]) -> bool:
        """Проверить связность системы после отказов"""
        # Создаем копию графа
        test_graph = self.system_model.graph.copy()
        
        # Удаляем отказавшие узлы
        for component in failed_components:
            if component in test_graph.nodes:
                test_graph.remove_node(component)
            else:
                # Это канал связи
                parts = component.split('_')
                if len(parts) == 2:
                    source, target = parts
                    if test_graph.has_edge(source, target):
                        test_graph.remove_edge(source, target)
        
        # Проверяем связность
        return nx.is_connected(test_graph)
    
    def create_fault_tree(self, top_event: str) -> FaultTree:
        """Создать дерево отказов для системы"""
        fault_tree = FaultTree(f"FTA_{self.system_model.name}")
        
        # Добавляем события отказов для всех компонентов
        for node_id in self.system_model.nodes:
            failure_event = FailureEvent(
                id=f"node_failure_{node_id}",
                failure_type=FailureType.HARDWARE,
                probability=1 - self.calculate_availability(node_id),
                description=f"Отказ узла {node_id}",
                affected_components=[node_id],
                impact_level=3
            )
            fault_tree.add_event(failure_event)
        
        for (source, target), link in self.system_model.links.items():
            link_id = f"{source}_{target}"
            failure_event = FailureEvent(
                id=f"link_failure_{link_id}",
                failure_type=FailureType.NETWORK,
                probability=1 - self.calculate_availability(link_id),
                description=f"Отказ канала {source}-{target}",
                affected_components=[source, target],
                impact_level=2
            )
            fault_tree.add_event(failure_event)
        
        # Добавляем логические вентили (упрощенная модель)
        if len(self.system_model.nodes) > 1:
            # OR вентиль для любого отказа узла
            node_failures = [f"node_failure_{node_id}" for node_id in self.system_model.nodes]
            fault_tree.add_gate("any_node_failure", "OR", node_failures)
            
            # OR вентиль для любого отказа канала
            link_failures = [f"link_failure_{source}_{target}" 
                           for (source, target) in self.system_model.links.keys()]
            if link_failures:
                fault_tree.add_gate("any_link_failure", "OR", link_failures)
        
        fault_tree.top_event = top_event
        return fault_tree
    
    def calculate_mttf_mttr(self, component_id: str) -> Tuple[float, float]:
        """Рассчитать MTTF и MTTR для компонента"""
        if component_id in self.failure_rates and component_id in self.repair_rates:
            mttf = 1.0 / self.failure_rates[component_id]  # часов
            mttr = 1.0 / self.repair_rates[component_id]   # часов
        else:
            # Значения по умолчанию в зависимости от типа компонента
            if component_id in self.system_model.nodes:
                node = self.system_model.nodes[component_id]
                if node.node_type.value == 'server':
                    mttf = 8760  # 1 год
                    mttr = 4     # 4 часа
                elif node.node_type.value == 'router':
                    mttf = 4380  # 6 месяцев
                    mttr = 2     # 2 часа
                else:
                    mttf = 2190  # 3 месяца
                    mttr = 1     # 1 час
            else:
                # Для каналов связи
                mttf = 4380  # 6 месяцев
                mttr = 1     # 1 час
        
        return mttf, mttr
    
    def generate_reliability_report(self) -> pd.DataFrame:
        """Сгенерировать отчет по надежности"""
        report_data = []
        
        # Анализ узлов
        for node_id, node in self.system_model.nodes.items():
            mttf, mttr = self.calculate_mttf_mttr(node_id)
            availability = self.calculate_availability(node_id)
            reliability = self.calculate_component_reliability(node_id)
            
            report_data.append({
                'component_type': 'node',
                'component_id': node_id,
                'component_subtype': node.node_type.value,
                'reliability': reliability,
                'availability': availability,
                'mttf_hours': mttf,
                'mttr_hours': mttr,
                'cpu_load': node.cpu_load,
                'memory_usage': node.memory_usage
            })
        
        # Анализ каналов
        for (source, target), link in self.system_model.links.items():
            link_id = f"{source}_{target}"
            mttf, mttr = self.calculate_mttf_mttr(link_id)
            availability = self.calculate_availability(link_id)
            reliability = self.calculate_component_reliability(link_id)
            
            report_data.append({
                'component_type': 'link',
                'component_id': link_id,
                'component_subtype': link.link_type.value,
                'reliability': reliability,
                'availability': availability,
                'mttf_hours': mttf,
                'mttr_hours': mttr,
                'bandwidth': link.bandwidth,
                'latency': link.latency,
                'utilization': link.utilization
            })
        
        return pd.DataFrame(report_data)
    
    def set_failure_rates(self, failure_rates: Dict[str, float]):
        """Установить частоты отказов для компонентов"""
        self.failure_rates.update(failure_rates)
    
    def set_repair_rates(self, repair_rates: Dict[str, float]):
        """Установить частоты восстановления для компонентов"""
        self.repair_rates.update(repair_rates)


def create_sample_reliability_analysis() -> Tuple[SystemModel, ReliabilityAnalyzer]:
    """Создать пример анализа надежности"""
    # Создаем тестовую систему
    system = SystemModel("Тестовая система для анализа надежности")
    
    # Добавляем узлы
    nodes = [
        Node("server1", "server", 1000, 0.99),
        Node("server2", "server", 800, 0.98),
        Node("router1", "router", 500, 0.95),
        Node("switch1", "switch", 300, 0.97),
    ]
    
    for node in nodes:
        system.add_node(node)
    
    # Добавляем каналы
    links = [
        Link("server1", "router1", 100, 5, 0.98, "fiber"),
        Link("server2", "router1", 80, 6, 0.97, "fiber"),
        Link("router1", "switch1", 50, 2, 0.99, "ethernet"),
    ]
    
    for link in links:
        system.add_link(link)
    
    # Создаем анализатор надежности
    analyzer = ReliabilityAnalyzer(system)
    
    # Устанавливаем частоты отказов (отказов в час)
    failure_rates = {
        "server1": 1e-4,  # 1 отказ на 10000 часов
        "server2": 1.2e-4,
        "router1": 2e-4,
        "switch1": 1.5e-4,
        "server1_router1": 1e-5,
        "server2_router1": 1.2e-5,
        "router1_switch1": 8e-6,
    }
    
    # Устанавливаем частоты восстановления (восстановлений в час)
    repair_rates = {
        "server1": 0.25,  # 4 часа на восстановление
        "server2": 0.25,
        "router1": 0.5,   # 2 часа на восстановление
        "switch1": 0.5,
        "server1_router1": 1.0,   # 1 час на восстановление
        "server2_router1": 1.0,
        "router1_switch1": 1.0,
    }
    
    analyzer.set_failure_rates(failure_rates)
    analyzer.set_repair_rates(repair_rates)
    
    return system, analyzer


if __name__ == "__main__":
    # Тестирование модуля
    system, analyzer = create_sample_reliability_analysis()
    
    print("=== Анализ надежности ИКС ===")
    print(f"Система: {system.name}")
    print(f"Узлов: {len(system.nodes)}, Каналов: {len(system.links)}")
    
    # Расчет надежности системы
    reliability_results = analyzer.calculate_system_reliability()
    print(f"\nНадежность системы: {reliability_results['system_overall']:.4f}")
    
    # Расчет доступности
    connectivity_reliability = analyzer.calculate_network_connectivity_reliability()
    print(f"Надежность связности: {connectivity_reliability:.4f}")
    
    # Анализ Монте-Карло
    print("\nАнализ Монте-Карло (1000 симуляций):")
    mc_results = analyzer.monte_carlo_reliability_analysis(1000)
    print(f"Надежность системы: {mc_results['system_reliability']:.4f}")
    print(f"Среднее время работы: {mc_results['average_uptime']:.1f} часов в год")
    
    # Отчет по надежности
    report = analyzer.generate_reliability_report()
    print(f"\nОтчет по надежности ({len(report)} компонентов):")
    print(report[['component_type', 'component_id', 'reliability', 'availability']].head())
