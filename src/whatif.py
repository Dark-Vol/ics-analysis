#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль многофакторного анализа (What-if анализ) ИКС
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
from scipy.optimize import minimize, differential_evolution
from scipy.stats import norm, uniform
import itertools
from .system_model import SystemModel
from .simulation import NetworkSimulator
from .reliability import ReliabilityAnalyzer


class ParameterType(Enum):
    """Типы параметров для анализа"""
    NODE_CAPACITY = "node_capacity"
    LINK_BANDWIDTH = "link_bandwidth"
    FAILURE_RATE = "failure_rate"
    TRAFFIC_LOAD = "traffic_load"
    NETWORK_TOPOLOGY = "network_topology"


@dataclass
class ParameterRange:
    """Диапазон параметра для анализа"""
    param_type: ParameterType
    component_id: str
    min_value: float
    max_value: float
    default_value: float
    step_size: float = 0.1


@dataclass
class WhatIfScenario:
    """Сценарий What-if анализа"""
    name: str
    description: str
    parameter_changes: Dict[str, float]  # component_id -> new_value
    expected_impact: str = ""


@dataclass
class WhatIfResult:
    """Результат What-if анализа"""
    scenario_name: str
    baseline_metrics: Dict
    modified_metrics: Dict
    impact_metrics: Dict
    confidence_interval: Tuple[float, float]
    recommendations: List[str]


class WhatIfAnalyzer:
    """Анализатор What-if сценариев"""
    
    def __init__(self, system_model: SystemModel):
        self.system_model = system_model
        self.baseline_system = None
        self.parameter_ranges = {}
        self.analysis_results = []
        self.monte_carlo_results = {}
    
    def set_parameter_ranges(self, parameter_ranges: List[ParameterRange]):
        """Установить диапазоны параметров для анализа"""
        self.parameter_ranges = {
            f"{param.param_type.value}_{param.component_id}": param
            for param in parameter_ranges
        }
    
    def create_baseline_system(self) -> SystemModel:
        """Создать базовую систему для сравнения"""
        self.baseline_system = SystemModel(f"{self.system_model.name}_baseline")
        
        # Копируем все узлы и каналы
        for node_id, node in self.system_model.nodes.items():
            self.baseline_system.add_node(node)
        
        for (source, target), link in self.system_model.links.items():
            self.baseline_system.add_link(link)
        
        return self.baseline_system
    
    def analyze_single_parameter_change(self, component_id: str, 
                                      parameter_type: ParameterType,
                                      new_value: float, 
                                      simulation_duration: float = 300) -> WhatIfResult:
        """Анализ изменения одного параметра"""
        scenario_name = f"Изменение {parameter_type.value} для {component_id}"
        
        # Создаем модифицированную систему
        modified_system = self._create_modified_system(component_id, parameter_type, new_value)
        
        # Запускаем симуляцию базовой системы
        baseline_simulator = NetworkSimulator(self.baseline_system or self.system_model, simulation_duration)
        baseline_simulator.run_simulation()
        baseline_metrics = baseline_simulator.get_simulation_results()['metrics']
        
        # Запускаем симуляцию модифицированной системы
        modified_simulator = NetworkSimulator(modified_system, simulation_duration)
        modified_simulator.run_simulation()
        modified_metrics = modified_simulator.get_simulation_results()['metrics']
        
        # Рассчитываем влияние
        impact_metrics = self._calculate_impact_metrics(baseline_metrics, modified_metrics)
        
        # Генерируем рекомендации
        recommendations = self._generate_recommendations(impact_metrics, parameter_type, component_id)
        
        # Рассчитываем доверительный интервал (упрощенный)
        confidence_interval = self._calculate_confidence_interval(modified_metrics)
        
        result = WhatIfResult(
            scenario_name=scenario_name,
            baseline_metrics=baseline_metrics,
            modified_metrics=modified_metrics,
            impact_metrics=impact_metrics,
            confidence_interval=confidence_interval,
            recommendations=recommendations
        )
        
        self.analysis_results.append(result)
        return result
    
    def analyze_parameter_sensitivity(self, parameter_ranges: List[ParameterRange],
                                    num_samples: int = 50) -> Dict[str, List[float]]:
        """Анализ чувствительности параметров"""
        sensitivity_results = {}
        
        for param_range in parameter_ranges:
            param_key = f"{param_range.param_type.value}_{param_range.component_id}"
            sensitivity_results[param_key] = []
            
            # Генерируем случайные значения в диапазоне
            values = np.random.uniform(
                param_range.min_value, 
                param_range.max_value, 
                num_samples
            )
            
            for value in values:
                # Создаем модифицированную систему
                modified_system = self._create_modified_system(
                    param_range.component_id, 
                    param_range.param_type, 
                    value
                )
                
                # Быстрая симуляция для оценки производительности
                simulator = NetworkSimulator(modified_system, 60)  # 1 минута
                simulator.run_simulation()
                
                metrics = simulator.get_simulation_results()['metrics']
                throughput = metrics.get('network_throughput', 0)
                
                sensitivity_results[param_key].append(throughput)
        
        return sensitivity_results
    
    def monte_carlo_analysis(self, num_simulations: int = 1000,
                           simulation_duration: float = 300) -> Dict[str, float]:
        """Анализ методом Монте-Карло"""
        print(f"Запуск анализа Монте-Карло ({num_simulations} симуляций)...")
        
        results = {
            'throughput_samples': [],
            'response_time_samples': [],
            'success_rate_samples': [],
            'reliability_samples': []
        }
        
        for i in range(num_simulations):
            if i % 100 == 0:
                print(f"Прогресс: {i}/{num_simulations}")
            
            # Создаем случайную модификацию системы
            modified_system = self._create_random_system_modification()
            
            # Запускаем симуляцию
            simulator = NetworkSimulator(modified_system, simulation_duration)
            simulator.run_simulation()
            
            metrics = simulator.get_simulation_results()['metrics']
            
            # Собираем образцы
            results['throughput_samples'].append(metrics.get('network_throughput', 0))
            results['response_time_samples'].append(metrics.get('average_response_time', 0))
            results['success_rate_samples'].append(metrics.get('success_rate', 0))
            
            # Рассчитываем надежность
            reliability_analyzer = ReliabilityAnalyzer(modified_system)
            reliability_results = reliability_analyzer.calculate_system_reliability()
            results['reliability_samples'].append(reliability_results.get('system_overall', 0))
        
        # Статистический анализ
        monte_carlo_stats = {}
        for metric, samples in results.items():
            if samples:
                monte_carlo_stats[metric] = {
                    'mean': np.mean(samples),
                    'std': np.std(samples),
                    'min': np.min(samples),
                    'max': np.max(samples),
                    'percentile_5': np.percentile(samples, 5),
                    'percentile_95': np.percentile(samples, 95)
                }
        
        self.monte_carlo_results = monte_carlo_stats
        return monte_carlo_stats
    
    def optimization_analysis(self, objective_function: str = "maximize_throughput",
                            constraints: Dict = None) -> Dict:
        """Анализ оптимизации системы"""
        if not constraints:
            constraints = {
                'max_cost': 10000,  # Максимальная стоимость
                'min_reliability': 0.95,  # Минимальная надежность
                'max_response_time': 1.0  # Максимальное время отклика
            }
        
        print(f"Запуск анализа оптимизации: {objective_function}")
        
        # Определяем целевую функцию
        if objective_function == "maximize_throughput":
            def objective(x):
                # x - вектор параметров системы
                modified_system = self._create_system_from_vector(x)
                simulator = NetworkSimulator(modified_system, 60)
                simulator.run_simulation()
                metrics = simulator.get_simulation_results()['metrics']
                return -metrics.get('network_throughput', 0)  # Минимизируем отрицательную пропускную способность
        
        elif objective_function == "minimize_response_time":
            def objective(x):
                modified_system = self._create_system_from_vector(x)
                simulator = NetworkSimulator(modified_system, 60)
                simulator.run_simulation()
                metrics = simulator.get_simulation_results()['metrics']
                return metrics.get('average_response_time', 10)
        
        else:
            raise ValueError(f"Неизвестная целевая функция: {objective_function}")
        
        # Определяем ограничения
        def constraint_reliability(x):
            modified_system = self._create_system_from_vector(x)
            reliability_analyzer = ReliabilityAnalyzer(modified_system)
            reliability_results = reliability_analyzer.calculate_system_reliability()
            return reliability_results.get('system_overall', 0) - constraints['min_reliability']
        
        def constraint_cost(x):
            # Упрощенная модель стоимости
            cost = np.sum(x) * 100  # Стоимость пропорциональна параметрам
            return constraints['max_cost'] - cost
        
        # Границы параметров
        bounds = []
        for param_range in self.parameter_ranges.values():
            bounds.append((param_range.min_value, param_range.max_value))
        
        # Оптимизация
        try:
            result = minimize(
                objective,
                x0=[param.default_value for param in self.parameter_ranges.values()],
                bounds=bounds,
                constraints=[
                    {'type': 'ineq', 'fun': constraint_reliability},
                    {'type': 'ineq', 'fun': constraint_cost}
                ],
                method='SLSQP'
            )
            
            return {
                'success': result.success,
                'optimal_parameters': result.x,
                'optimal_value': result.fun,
                'iterations': result.nit,
                'message': result.message
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'optimal_parameters': None,
                'optimal_value': None
            }
    
    def scenario_analysis(self, scenarios: List[WhatIfScenario],
                         simulation_duration: float = 300) -> List[WhatIfResult]:
        """Анализ множественных сценариев"""
        results = []
        
        for scenario in scenarios:
            print(f"Анализ сценария: {scenario.name}")
            
            # Создаем модифицированную систему
            modified_system = self._apply_scenario_changes(scenario)
            
            # Базовые метрики
            baseline_simulator = NetworkSimulator(self.baseline_system or self.system_model, simulation_duration)
            baseline_simulator.run_simulation()
            baseline_metrics = baseline_simulator.get_simulation_results()['metrics']
            
            # Модифицированные метрики
            modified_simulator = NetworkSimulator(modified_system, simulation_duration)
            modified_simulator.run_simulation()
            modified_metrics = modified_simulator.get_simulation_results()['metrics']
            
            # Анализ влияния
            impact_metrics = self._calculate_impact_metrics(baseline_metrics, modified_metrics)
            recommendations = self._generate_scenario_recommendations(scenario, impact_metrics)
            confidence_interval = self._calculate_confidence_interval(modified_metrics)
            
            result = WhatIfResult(
                scenario_name=scenario.name,
                baseline_metrics=baseline_metrics,
                modified_metrics=modified_metrics,
                impact_metrics=impact_metrics,
                confidence_interval=confidence_interval,
                recommendations=recommendations
            )
            
            results.append(result)
            self.analysis_results.append(result)
        
        return results
    
    def _create_modified_system(self, component_id: str, parameter_type: ParameterType, 
                              new_value: float) -> SystemModel:
        """Создать модифицированную систему"""
        modified_system = SystemModel(f"{self.system_model.name}_modified")
        
        # Копируем базовую систему
        for node_id, node in self.system_model.nodes.items():
            modified_system.add_node(node)
        
        for (source, target), link in self.system_model.links.items():
            modified_system.add_link(link)
        
        # Применяем изменения
        if parameter_type == ParameterType.NODE_CAPACITY:
            if component_id in modified_system.nodes:
                modified_system.nodes[component_id].capacity = new_value
        
        elif parameter_type == ParameterType.LINK_BANDWIDTH:
            # Ищем канал по компоненту
            for (source, target), link in modified_system.links.items():
                if f"{source}_{target}" == component_id:
                    link.bandwidth = new_value
                    break
        
        elif parameter_type == ParameterType.FAILURE_RATE:
            # Модифицируем надежность узлов/каналов
            if component_id in modified_system.nodes:
                modified_system.nodes[component_id].reliability = 1 - new_value
        
        return modified_system
    
    def _create_random_system_modification(self) -> SystemModel:
        """Создать случайную модификацию системы"""
        modified_system = SystemModel(f"{self.system_model.name}_random")
        
        # Копируем базовую систему
        for node_id, node in self.system_model.nodes.items():
            modified_system.add_node(node)
        
        for (source, target), link in self.system_model.links.items():
            modified_system.add_link(link)
        
        # Случайные модификации
        for node_id, node in modified_system.nodes.items():
            # Случайное изменение пропускной способности
            node.capacity *= random.uniform(0.8, 1.2)
            # Случайное изменение надежности
            node.reliability = max(0.8, min(0.99, node.reliability + random.uniform(-0.05, 0.05)))
        
        for (source, target), link in modified_system.links.items():
            # Случайное изменение пропускной способности канала
            link.bandwidth *= random.uniform(0.9, 1.1)
            # Случайное изменение надежности канала
            link.reliability = max(0.9, min(0.99, link.reliability + random.uniform(-0.02, 0.02)))
        
        return modified_system
    
    def _create_system_from_vector(self, x: np.ndarray) -> SystemModel:
        """Создать систему из вектора параметров"""
        modified_system = SystemModel(f"{self.system_model.name}_optimized")
        
        # Копируем базовую систему
        for node_id, node in self.system_model.nodes.items():
            modified_system.add_node(node)
        
        for (source, target), link in self.system_model.links.items():
            modified_system.add_link(link)
        
        # Применяем параметры из вектора
        param_keys = list(self.parameter_ranges.keys())
        for i, param_key in enumerate(param_keys):
            if i < len(x):
                param_range = self.parameter_ranges[param_key]
                param_type = param_range.param_type
                component_id = param_range.component_id
                
                if param_type == ParameterType.NODE_CAPACITY:
                    if component_id in modified_system.nodes:
                        modified_system.nodes[component_id].capacity = x[i]
        
        return modified_system
    
    def _apply_scenario_changes(self, scenario: WhatIfScenario) -> SystemModel:
        """Применить изменения сценария к системе"""
        modified_system = SystemModel(f"{self.system_model.name}_scenario")
        
        # Копируем базовую систему
        for node_id, node in self.system_model.nodes.items():
            modified_system.add_node(node)
        
        for (source, target), link in self.system_model.links.items():
            modified_system.add_link(link)
        
        # Применяем изменения сценария
        for component_id, new_value in scenario.parameter_changes.items():
            # Определяем тип компонента и применяем изменение
            if component_id in modified_system.nodes:
                # Это узел - изменяем пропускную способность
                modified_system.nodes[component_id].capacity = new_value
            else:
                # Это канал - ищем по ID
                for (source, target), link in modified_system.links.items():
                    if f"{source}_{target}" == component_id:
                        link.bandwidth = new_value
                        break
        
        return modified_system
    
    def _calculate_impact_metrics(self, baseline: Dict, modified: Dict) -> Dict:
        """Рассчитать метрики влияния"""
        impact = {}
        
        for metric in ['network_throughput', 'average_response_time', 'success_rate']:
            baseline_val = baseline.get(metric, 0)
            modified_val = modified.get(metric, 0)
            
            if baseline_val != 0:
                if metric == 'average_response_time':
                    # Для времени отклика меньше - лучше
                    impact[f"{metric}_change"] = (baseline_val - modified_val) / baseline_val
                else:
                    # Для остальных метрик больше - лучше
                    impact[f"{metric}_change"] = (modified_val - baseline_val) / baseline_val
            else:
                impact[f"{metric}_change"] = 0
        
        return impact
    
    def _calculate_confidence_interval(self, metrics: Dict, confidence: float = 0.95) -> Tuple[float, float]:
        """Рассчитать доверительный интервал (упрощенный)"""
        throughput = metrics.get('network_throughput', 0)
        std_error = throughput * 0.1  # 10% стандартная ошибка
        
        alpha = 1 - confidence
        z_score = 1.96  # Для 95% доверительного интервала
        
        lower_bound = throughput - z_score * std_error
        upper_bound = throughput + z_score * std_error
        
        return (lower_bound, upper_bound)
    
    def _generate_recommendations(self, impact_metrics: Dict, 
                                parameter_type: ParameterType, 
                                component_id: str) -> List[str]:
        """Генерировать рекомендации на основе анализа"""
        recommendations = []
        
        throughput_change = impact_metrics.get('network_throughput_change', 0)
        response_time_change = impact_metrics.get('average_response_time_change', 0)
        success_rate_change = impact_metrics.get('success_rate_change', 0)
        
        if throughput_change > 0.1:
            recommendations.append(f"Рекомендуется увеличить {parameter_type.value} для {component_id}")
        elif throughput_change < -0.1:
            recommendations.append(f"Рассмотреть уменьшение {parameter_type.value} для {component_id}")
        
        if response_time_change > 0.1:
            recommendations.append(f"Улучшение времени отклика при изменении {parameter_type.value} для {component_id}")
        
        if success_rate_change < -0.05:
            recommendations.append(f"Внимание: снижение успешности при изменении {parameter_type.value} для {component_id}")
        
        if not recommendations:
            recommendations.append("Изменение параметра не оказывает значительного влияния на систему")
        
        return recommendations
    
    def _generate_scenario_recommendations(self, scenario: WhatIfScenario, 
                                         impact_metrics: Dict) -> List[str]:
        """Генерировать рекомендации для сценария"""
        recommendations = []
        
        if scenario.expected_impact:
            recommendations.append(f"Ожидаемое влияние: {scenario.expected_impact}")
        
        # Анализ метрик влияния
        throughput_change = impact_metrics.get('network_throughput_change', 0)
        if abs(throughput_change) > 0.05:
            recommendations.append(f"Значительное изменение пропускной способности: {throughput_change:.1%}")
        
        return recommendations
    
    def generate_whatif_report(self) -> pd.DataFrame:
        """Сгенерировать отчет по What-if анализу"""
        if not self.analysis_results:
            return pd.DataFrame()
        
        report_data = []
        for result in self.analysis_results:
            report_data.append({
                'scenario': result.scenario_name,
                'baseline_throughput': result.baseline_metrics.get('network_throughput', 0),
                'modified_throughput': result.modified_metrics.get('network_throughput', 0),
                'throughput_change': result.impact_metrics.get('network_throughput_change', 0),
                'baseline_response_time': result.baseline_metrics.get('average_response_time', 0),
                'modified_response_time': result.modified_metrics.get('average_response_time', 0),
                'response_time_change': result.impact_metrics.get('average_response_time_change', 0),
                'confidence_lower': result.confidence_interval[0],
                'confidence_upper': result.confidence_interval[1],
                'recommendations_count': len(result.recommendations)
            })
        
        return pd.DataFrame(report_data)


def create_sample_whatif_analysis() -> Tuple[SystemModel, WhatIfAnalyzer]:
    """Создать пример What-if анализа"""
    from .system_model import create_sample_network
    
    # Создаем тестовую систему
    system = create_sample_network()
    
    # Создаем анализатор
    analyzer = WhatIfAnalyzer(system)
    
    # Создаем базовую систему
    analyzer.create_baseline_system()
    
    # Устанавливаем диапазоны параметров
    parameter_ranges = [
        ParameterRange(
            param_type=ParameterType.NODE_CAPACITY,
            component_id="server1",
            min_value=500,
            max_value=2000,
            default_value=1000
        ),
        ParameterRange(
            param_type=ParameterType.LINK_BANDWIDTH,
            component_id="server1_router1",
            min_value=50,
            max_value=200,
            default_value=100
        ),
        ParameterRange(
            param_type=ParameterType.FAILURE_RATE,
            component_id="server1",
            min_value=0.001,
            max_value=0.01,
            default_value=0.005
        )
    ]
    
    analyzer.set_parameter_ranges(parameter_ranges)
    
    return system, analyzer


if __name__ == "__main__":
    # Тестирование модуля
    system, analyzer = create_sample_whatif_analysis()
    
    print("=== What-if анализ ИКС ===")
    print(f"Система: {system.name}")
    print(f"Узлов: {len(system.nodes)}, Каналов: {len(system.links)}")
    
    # Анализ изменения одного параметра
    print("\n=== Анализ изменения параметра ===")
    result = analyzer.analyze_single_parameter_change(
        "server1", ParameterType.NODE_CAPACITY, 1500, simulation_duration=60
    )
    
    print(f"Сценарий: {result.scenario_name}")
    print(f"Изменение пропускной способности: {result.impact_metrics.get('network_throughput_change', 0):.1%}")
    print(f"Изменение времени отклика: {result.impact_metrics.get('average_response_time_change', 0):.1%}")
    print(f"Рекомендации: {len(result.recommendations)}")
    
    # Анализ чувствительности
    print("\n=== Анализ чувствительности ===")
    sensitivity_results = analyzer.analyze_parameter_sensitivity(
        analyzer.parameter_ranges.values(), num_samples=10
    )
    
    for param, samples in sensitivity_results.items():
        if samples:
            print(f"{param}: среднее = {np.mean(samples):.2f}, std = {np.std(samples):.2f}")
    
    # Анализ Монте-Карло
    print("\n=== Анализ Монте-Карло ===")
    mc_results = analyzer.monte_carlo_analysis(num_simulations=50, simulation_duration=30)
    
    if 'throughput_samples' in mc_results:
        throughput_stats = mc_results['throughput_samples']
        print(f"Пропускная способность: {throughput_stats['mean']:.2f} ± {throughput_stats['std']:.2f}")
        print(f"Диапазон: {throughput_stats['min']:.2f} - {throughput_stats['max']:.2f}")
    
    # Генерация отчета
    report = analyzer.generate_whatif_report()
    if not report.empty:
        print(f"\nОтчет по What-if анализу ({len(report)} сценариев):")
        print(report[['scenario', 'throughput_change', 'response_time_change']].head())
