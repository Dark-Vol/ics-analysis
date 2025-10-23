#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенный анализатор надежности ИКС с функциями:
- Критерий Бирнбаума
- Теория вероятностей
- Тест Дарбина-Уотсона
- Оценка хрупкости системы
- Моделирование внешних воздействий
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.stattools import durbin_watson
from typing import Dict, List, Tuple, Optional, Union
import random
import itertools
from dataclasses import dataclass
import warnings

# Константы
CRITICAL_NODE_THRESHOLD = 3  # Минимальное количество узлов для функционирования системы


@dataclass
class SystemState:
    """Состояние системы"""
    node_states: Dict[str, bool]  # True - работает, False - отказал
    system_reliability: float
    connectivity_status: bool


class AdvancedReliabilityAnalyzer:
    """Расширенный анализатор надежности ИКС"""
    
    def __init__(self):
        self.probabilities = {}
        self.structure_matrix = []
        self.network_graph = None
        self.critical_threshold = CRITICAL_NODE_THRESHOLD
    
    def calculate_birnbaum_criterion(self, probabilities: Dict[str, float], 
                                   structure_matrix: List[List[int]]) -> Dict[str, float]:
        """
        Рассчитывает коэффициенты значимости Бирнбаума для каждого узла системы.
        
        Args:
            probabilities: Словарь с вероятностями безотказной работы узлов
            structure_matrix: Матрица связности системы
            
        Returns:
            Словарь с коэффициентами значимости каждого узла
        """
        self.probabilities = probabilities
        self.structure_matrix = structure_matrix
        
        # Получаем список узлов
        nodes = list(probabilities.keys())
        birnbaum_coefficients = {}
        
        # Для каждого узла рассчитываем коэффициент Бирнбаума
        for node in nodes:
            # Рассчитываем надежность системы при работе узла
            reliability_with_node = self._calculate_system_reliability_with_node_state(node, True)
            
            # Рассчитываем надежность системы при отказе узла
            reliability_without_node = self._calculate_system_reliability_with_node_state(node, False)
            
            # Коэффициент Бирнбаума = разность надежностей
            birnbaum_coefficients[node] = reliability_with_node - reliability_without_node
        
        return birnbaum_coefficients
    
    def _calculate_system_reliability_with_node_state(self, target_node: str, node_working: bool) -> float:
        """Рассчитывает надежность системы при заданном состоянии узла"""
        # Создаем копию вероятностей с измененным состоянием целевого узла
        modified_probs = self.probabilities.copy()
        modified_probs[target_node] = 1.0 if node_working else 0.0
        
        # Рассчитываем надежность системы
        return self.system_reliability(modified_probs, self._get_connections_from_matrix())
    
    def system_reliability(self, probabilities: Dict[str, float], 
                          connections: Dict[str, List[str]]) -> float:
        """
        Вычисляет общую вероятность безотказной работы системы на основе структуры и вероятностей узлов.
        
        Args:
            probabilities: Словарь с вероятностями безотказной работы узлов
            connections: Словарь связей между узлами
            
        Returns:
            Общая вероятность безотказной работы системы
        """
        nodes = list(probabilities.keys())
        
        # Если система пустая
        if not nodes:
            return 0.0
        
        # Если только один узел
        if len(nodes) == 1:
            return probabilities[nodes[0]]
        
        # Используем метод включения-исключения для расчета надежности системы
        total_reliability = 0.0
        
        # Генерируем все возможные состояния системы
        for state_vector in itertools.product([0, 1], repeat=len(nodes)):
            state_prob = 1.0
            working_nodes = []
            
            # Рассчитываем вероятность данного состояния
            for i, node_state in enumerate(state_vector):
                node = nodes[i]
                if node_state == 1:  # Узел работает
                    state_prob *= probabilities[node]
                    working_nodes.append(node)
                else:  # Узел отказал
                    state_prob *= (1 - probabilities[node])
            
            # Проверяем, является ли система работоспособной в данном состоянии
            if self._is_system_working(working_nodes, connections):
                total_reliability += state_prob
        
        return total_reliability
    
    def _is_system_working(self, working_nodes: List[str], connections: Dict[str, List[str]]) -> bool:
        """Проверяет, является ли система работоспособной при заданном наборе работающих узлов"""
        if not working_nodes:
            return False
        
        # Проверяем связность системы
        return self._is_connected(working_nodes, connections)
    
    def _is_connected(self, nodes: List[str], connections: Dict[str, List[str]]) -> bool:
        """Проверяет связность подмножества узлов"""
        if len(nodes) <= 1:
            return True
        
        # Используем алгоритм поиска в глубину для проверки связности
        visited = set()
        stack = [nodes[0]]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            
            visited.add(current)
            
            # Добавляем соседние узлы, которые работают
            if current in connections:
                for neighbor in connections[current]:
                    if neighbor in nodes and neighbor not in visited:
                        stack.append(neighbor)
        
        # Система связна, если все узлы достижимы
        return len(visited) == len(nodes)
    
    def calculate_probability_distribution(self, probabilities: Dict[str, float]) -> Dict[str, float]:
        """
        Вычисляет распределение вероятностей возможных состояний системы.
        
        Args:
            probabilities: Словарь с вероятностями безотказной работы узлов
            
        Returns:
            Словарь с вероятностями различных состояний системы
        """
        nodes = list(probabilities.keys())
        state_probabilities = {}
        
        # Генерируем все возможные состояния системы
        for state_vector in itertools.product([0, 1], repeat=len(nodes)):
            state_prob = 1.0
            state_description = []
            
            # Рассчитываем вероятность данного состояния
            for i, node_state in enumerate(state_vector):
                node = nodes[i]
                if node_state == 1:  # Узел работает
                    state_prob *= probabilities[node]
                    state_description.append(f"{node}:работает")
                else:  # Узел отказал
                    state_prob *= (1 - probabilities[node])
                    state_description.append(f"{node}:отказал")
            
            state_key = " | ".join(state_description)
            state_probabilities[state_key] = state_prob
        
        return state_probabilities
    
    def calculate_node_failure_probabilities(self, probabilities: Dict[str, float]) -> Dict[str, float]:
        """
        Вычисляет вероятности отказа отдельных узлов.
        
        Args:
            probabilities: Словарь с вероятностями безотказной работы узлов
            
        Returns:
            Словарь с вероятностями отказа каждого узла
        """
        failure_probabilities = {}
        
        for node, reliability in probabilities.items():
            failure_probabilities[node] = 1 - reliability
        
        return failure_probabilities
    
    def durbin_watson_test(self, residuals: List[float]) -> Tuple[float, str]:
        """
        Проверяет наличие автокорреляции остатков по критерию Дарбина–Уотсона.
        
        Args:
            residuals: Список остатков регрессии
            
        Returns:
            Кортеж (значение статистики, текстовая интерпретация результата)
        """
        if len(residuals) < 3:
            return 0.0, "Недостаточно данных для проведения теста"
        
        # Рассчитываем статистику Дарбина-Уотсона
        try:
            dw_statistic = durbin_watson(residuals)
        except Exception as e:
            warnings.warn(f"Ошибка при расчете статистики Дарбина-Уотсона: {e}")
            return 0.0, "Ошибка при расчете статистики"
        
        # Интерпретация результата
        n = len(residuals)
        
        # Критические значения для теста Дарбина-Уотсона (приблизительные)
        if n <= 15:
            d_lower = 0.95
            d_upper = 1.54
        elif n <= 20:
            d_lower = 1.00
            d_upper = 1.68
        elif n <= 25:
            d_lower = 1.05
            d_upper = 1.66
        elif n <= 30:
            d_lower = 1.08
            d_upper = 1.65
        else:
            d_lower = 1.10
            d_upper = 1.64
        
        # Интерпретация
        if dw_statistic < d_lower:
            interpretation = "Положительная автокорреляция остатков (отклоняем H0)"
        elif dw_statistic > (4 - d_lower):
            interpretation = "Отрицательная автокорреляция остатков (отклоняем H0)"
        elif d_lower <= dw_statistic <= d_upper:
            interpretation = "Зона неопределенности (нельзя сделать вывод)"
        elif d_upper < dw_statistic < (4 - d_upper):
            interpretation = "Автокорреляция отсутствует (принимаем H0)"
        else:
            interpretation = "Зона неопределенности (нельзя сделать вывод)"
        
        return dw_statistic, interpretation
    
    def remove_nodes(self, network: Dict[str, any], nodes_to_remove: List[str]) -> Dict[str, any]:
        """
        Удаляет указанные узлы из сети и возвращает обновлённую структуру.
        
        Args:
            network: Словарь с описанием сети
            nodes_to_remove: Список узлов для удаления
            
        Returns:
            Обновлённая структура сети
        """
        updated_network = network.copy()
        
        # Удаляем узлы из списка узлов
        if 'nodes' in updated_network:
            updated_network['nodes'] = [
                node for node in updated_network['nodes'] 
                if node.get('id') not in nodes_to_remove
            ]
        
        # Удаляем связи, связанные с удаляемыми узлами
        if 'connections' in updated_network:
            updated_connections = {}
            for node, neighbors in updated_network['connections'].items():
                if node not in nodes_to_remove:
                    updated_connections[node] = [
                        neighbor for neighbor in neighbors 
                        if neighbor not in nodes_to_remove
                    ]
            updated_network['connections'] = updated_connections
        
        # Удаляем связи из списка связей
        if 'links' in updated_network:
            updated_network['links'] = [
                link for link in updated_network['links']
                if (link.get('source') not in nodes_to_remove and 
                    link.get('target') not in nodes_to_remove)
            ]
        
        return updated_network
    
    def check_critical_threshold(self, network: Dict[str, any]) -> Tuple[bool, str]:
        """
        Проверяет, не достигнут ли критический порог системы.
        
        Args:
            network: Словарь с описанием сети
            
        Returns:
            Кортеж (достигнут_ли_порог, сообщение)
        """
        # Подсчитываем количество узлов
        node_count = 0
        
        if 'nodes' in network:
            node_count = len(network['nodes'])
        elif 'connections' in network:
            node_count = len(network['connections'])
        
        if node_count < self.critical_threshold:
            message = f"ВНИМАНИЕ: Достигнут критический порог! Количество узлов ({node_count}) меньше минимального ({self.critical_threshold})"
            return True, message
        else:
            message = f"Система стабильна. Количество узлов: {node_count} (минимум: {self.critical_threshold})"
            return False, message
    
    def simulate_external_events(self, network: Dict[str, any]) -> Dict[str, any]:
        """
        Моделирует внешние воздействия на узлы:
        - хакерские атаки
        - отключение питания
        - сбои оборудования
        
        Args:
            network: Словарь с описанием сети
            
        Returns:
            Обновлённая структура сети с вероятностями отказов
        """
        updated_network = network.copy()
        
        # Получаем список узлов
        nodes = []
        if 'nodes' in updated_network:
            nodes = updated_network['nodes']
        elif 'connections' in updated_network:
            nodes = [{'id': node_id} for node_id in updated_network['connections'].keys()]
        
        # Симулируем различные типы внешних воздействий
        affected_nodes = []
        
        # 1. Хакерская атака (вероятность 0.1)
        if random.random() < 0.1:
            attack_targets = random.sample(nodes, min(2, len(nodes)))
            for node in attack_targets:
                node_id = node.get('id', str(node))
                affected_nodes.append({
                    'node_id': node_id,
                    'event_type': 'hacker_attack',
                    'probability': 0.3,  # 30% вероятность компрометации
                    'description': f'Хакерская атака на узел {node_id}'
                })
        
        # 2. Отключение электроэнергии (вероятность 0.05)
        if random.random() < 0.05:
            power_failure_nodes = random.sample(nodes, min(3, len(nodes)))
            for node in power_failure_nodes:
                node_id = node.get('id', str(node))
                affected_nodes.append({
                    'node_id': node_id,
                    'event_type': 'power_outage',
                    'probability': 0.8,  # 80% вероятность отказа при отключении питания
                    'description': f'Отключение питания узла {node_id}'
                })
        
        # 3. Случайный отказ оборудования (вероятность 0.15)
        if random.random() < 0.15:
            hardware_failure_node = random.choice(nodes)
            node_id = hardware_failure_node.get('id', str(hardware_failure_node))
            affected_nodes.append({
                'node_id': node_id,
                'event_type': 'hardware_failure',
                'probability': 0.2,  # 20% вероятность отказа оборудования
                'description': f'Случайный отказ оборудования узла {node_id}'
            })
        
        # Обновляем вероятности отказов узлов
        if 'node_failure_probabilities' not in updated_network:
            updated_network['node_failure_probabilities'] = {}
        
        for event in affected_nodes:
            node_id = event['node_id']
            if node_id not in updated_network['node_failure_probabilities']:
                updated_network['node_failure_probabilities'][node_id] = 0.0
            
            # Увеличиваем вероятность отказа
            updated_network['node_failure_probabilities'][node_id] += event['probability']
            # Ограничиваем максимальную вероятность отказа
            updated_network['node_failure_probabilities'][node_id] = min(
                updated_network['node_failure_probabilities'][node_id], 0.95
            )
        
        # Добавляем информацию о внешних событиях
        updated_network['external_events'] = affected_nodes
        
        return updated_network
    
    def _get_connections_from_matrix(self) -> Dict[str, List[str]]:
        """Преобразует матрицу связности в словарь связей"""
        connections = {}
        
        if not self.structure_matrix:
            return connections
        
        # Предполагаем, что узлы пронумерованы как строки/столбцы матрицы
        nodes = list(self.probabilities.keys())
        
        for i, row in enumerate(self.structure_matrix):
            if i < len(nodes):
                node = nodes[i]
                connections[node] = []
                
                for j, connection in enumerate(row):
                    if j < len(nodes) and connection == 1 and i != j:
                        connections[node].append(nodes[j])
        
        return connections
    
    def generate_reliability_report(self, probabilities: Dict[str, float], 
                                  structure_matrix: List[List[int]]) -> pd.DataFrame:
        """
        Генерирует подробный отчет по надежности системы.
        
        Args:
            probabilities: Словарь с вероятностями безотказной работы узлов
            structure_matrix: Матрица связности системы
            
        Returns:
            DataFrame с результатами анализа
        """
        # Рассчитываем все метрики
        birnbaum_coeffs = self.calculate_birnbaum_criterion(probabilities, structure_matrix)
        failure_probs = self.calculate_node_failure_probabilities(probabilities)
        connections = self._get_connections_from_matrix()
        system_reliability = self.system_reliability(probabilities, connections)
        
        # Создаем отчет
        report_data = []
        
        for node in probabilities.keys():
            report_data.append({
                'node_id': node,
                'reliability': probabilities[node],
                'failure_probability': failure_probs[node],
                'birnbaum_coefficient': birnbaum_coeffs[node],
                'connections_count': len(connections.get(node, [])),
                'criticality_level': self._get_criticality_level(birnbaum_coeffs[node])
            })
        
        # Добавляем общую информацию о системе
        report_data.append({
            'node_id': 'SYSTEM_TOTAL',
            'reliability': system_reliability,
            'failure_probability': 1 - system_reliability,
            'birnbaum_coefficient': sum(birnbaum_coeffs.values()),
            'connections_count': sum(len(neighbors) for neighbors in connections.values()) // 2,
            'criticality_level': 'SYSTEM'
        })
        
        return pd.DataFrame(report_data)
    
    def _get_criticality_level(self, birnbaum_coefficient: float) -> str:
        """Определяет уровень критичности узла на основе коэффициента Бирнбаума"""
        if birnbaum_coefficient >= 0.5:
            return 'КРИТИЧЕСКИЙ'
        elif birnbaum_coefficient >= 0.2:
            return 'ВЫСОКИЙ'
        elif birnbaum_coefficient >= 0.1:
            return 'СРЕДНИЙ'
        else:
            return 'НИЗКИЙ'


def create_sample_network() -> Tuple[Dict[str, float], List[List[int]], Dict[str, any]]:
    """
    Создает пример сети для демонстрации функций анализа надежности.
    
    Returns:
        Кортеж (вероятности, матрица_связности, структура_сети)
    """
    # Вероятности безотказной работы узлов
    probabilities = {
        'server1': 0.99,
        'server2': 0.98,
        'router1': 0.95,
        'router2': 0.96,
        'switch1': 0.97,
        'switch2': 0.94,
        'firewall': 0.92
    }
    
    # Матрица связности (7x7)
    structure_matrix = [
        [0, 1, 1, 0, 0, 0, 1],  # server1
        [1, 0, 0, 1, 0, 0, 1],  # server2
        [1, 0, 0, 1, 1, 0, 0],  # router1
        [0, 1, 1, 0, 0, 1, 0],  # router2
        [0, 0, 1, 0, 0, 1, 0],  # switch1
        [0, 0, 0, 1, 1, 0, 0],  # switch2
        [1, 1, 0, 0, 0, 0, 0]   # firewall
    ]
    
    # Структура сети
    network_structure = {
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
        },
        'links': [
            {'source': 'server1', 'target': 'server2', 'bandwidth': 1000},
            {'source': 'server1', 'target': 'router1', 'bandwidth': 100},
            {'source': 'server1', 'target': 'firewall', 'bandwidth': 100},
            {'source': 'server2', 'target': 'router2', 'bandwidth': 100},
            {'source': 'server2', 'target': 'firewall', 'bandwidth': 100},
            {'source': 'router1', 'target': 'router2', 'bandwidth': 50},
            {'source': 'router1', 'target': 'switch1', 'bandwidth': 50},
            {'source': 'router2', 'target': 'switch2', 'bandwidth': 50},
            {'source': 'switch1', 'target': 'switch2', 'bandwidth': 25}
        ]
    }
    
    return probabilities, structure_matrix, network_structure


if __name__ == "__main__":
    # Демонстрация работы модуля
    print("=== Расширенный анализ надежности ИКС ===\n")
    
    # Создаем анализатор
    analyzer = AdvancedReliabilityAnalyzer()
    
    # Создаем пример сети
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    print("1. Инициализация тестовой сети:")
    print(f"   Узлы: {list(probabilities.keys())}")
    print(f"   Вероятности безотказной работы: {probabilities}")
    print()
    
    # 2. Расчёт критерия Бирнбаума
    print("2. Расчёт коэффициентов значимости Бирнбаума:")
    birnbaum_coeffs = analyzer.calculate_birnbaum_criterion(probabilities, structure_matrix)
    for node, coeff in birnbaum_coeffs.items():
        print(f"   {node}: {coeff:.4f}")
    print()
    
    # 3. Общая вероятность безотказной работы системы
    connections = analyzer._get_connections_from_matrix()
    system_reliability = analyzer.system_reliability(probabilities, connections)
    print(f"3. Общая вероятность безотказной работы системы: {system_reliability:.4f}")
    
    # Вероятности отказа узлов
    failure_probs = analyzer.calculate_node_failure_probabilities(probabilities)
    print("\n4. Вероятности отказа отдельных узлов:")
    for node, prob in failure_probs.items():
        print(f"   {node}: {prob:.4f}")
    
    # Распределение вероятностей состояний
    state_distribution = analyzer.calculate_probability_distribution(probabilities)
    print(f"\n5. Количество возможных состояний системы: {len(state_distribution)}")
    print("   Примеры состояний:")
    for i, (state, prob) in enumerate(list(state_distribution.items())[:3]):
        print(f"   {i+1}. {state}: {prob:.6f}")
    print()
    
    # 6. Проверка автокорреляции остатков
    print("6. Проверка автокорреляции остатков (тест Дарбина-Уотсона):")
    # Генерируем пример остатков
    np.random.seed(42)
    residuals = np.random.normal(0, 1, 20) + 0.3 * np.random.normal(0, 1, 20)  # с автокорреляцией
    dw_stat, dw_interpretation = analyzer.durbin_watson_test(residuals.tolist())
    print(f"   Статистика Дарбина-Уотсона: {dw_stat:.4f}")
    print(f"   Интерпретация: {dw_interpretation}")
    print()
    
    # 7. Пошаговое удаление узлов
    print("7. Пошаговое удаление узлов:")
    current_network = network_structure.copy()
    nodes_to_test = ['switch1', 'switch2', 'router1']
    
    for node_to_remove in nodes_to_test:
        print(f"   Удаляем узел: {node_to_remove}")
        current_network = analyzer.remove_nodes(current_network, [node_to_remove])
        
        # Проверяем критический порог
        is_critical, message = analyzer.check_critical_threshold(current_network)
        print(f"   {message}")
        
        if is_critical:
            print("   ⚠️  Достигнут критический порог! Останавливаем моделирование.")
            break
        print()
    
    # 8. Имитация внешних событий
    print("8. Имитация внешних воздействий:")
    # Восстанавливаем исходную сеть
    current_network = network_structure.copy()
    
    # Симулируем внешние события несколько раз
    for i in range(3):
        print(f"   Симуляция {i+1}:")
        current_network = analyzer.simulate_external_events(current_network)
        
        if 'external_events' in current_network:
            for event in current_network['external_events']:
                print(f"     - {event['description']} (вероятность: {event['probability']:.2f})")
        
        if 'node_failure_probabilities' in current_network:
            print("     Обновленные вероятности отказов:")
            for node, prob in current_network['node_failure_probabilities'].items():
                print(f"       {node}: {prob:.4f}")
        print()
    
    # 9. Генерация отчета
    print("9. Подробный отчет по надежности:")
    report = analyzer.generate_reliability_report(probabilities, structure_matrix)
    print(report.to_string(index=False))
