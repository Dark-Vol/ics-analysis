#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Реалізація критерію Бірнбаума для оцінки надійності мережі
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
import itertools
from collections import defaultdict


class BirnbaumReliabilityAnalyzer:
    """Аналізатор надійності мережі за критерієм Бірнбаума"""
    
    def __init__(self, network_dict: Dict[str, List[str]], main_node: str = None):
        """
        Ініціалізація аналізатора
        
        Args:
            network_dict: Словник мережі у форматі {'a': ['b', 'c'], 'b': ['c'], 'c': []}
            main_node: Головний вузол мережі
        """
        self.network_dict = network_dict.copy()
        self.main_node = main_node
        self.total_nodes = len(self._get_all_nodes())
        
        # Якщо головний вузол не вказаний, беремо перший
        if self.main_node is None:
            self.main_node = list(network_dict.keys())[0] if network_dict else None
    
    def _get_all_nodes(self) -> Set[str]:
        """Отримує всі вузли мережі"""
        all_nodes = set()
        for node, connections in self.network_dict.items():
            all_nodes.add(node)
            all_nodes.update(connections)
        return all_nodes
    
    def _get_all_edges(self) -> List[Tuple[str, str]]:
        """Отримує всі ребра мережі"""
        edges = []
        for from_node, connections in self.network_dict.items():
            for to_node in connections:
                edges.append((from_node, to_node))
        return edges
    
    def _is_network_connected(self, network: Dict[str, List[str]]) -> bool:
        """
        Перевіряє зв'язність мережі
        
        Args:
            network: Словник мережі для перевірки
        
        Returns:
            True якщо мережа зв'язана
        """
        if not network:
            return False
        
        # Використовуємо BFS для перевірки зв'язності
        start_node = list(network.keys())[0]
        visited = set()
        queue = [start_node]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            
            # Додаємо всіх сусідів
            for neighbor in network.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
            
            # Додаємо вузли, які мають зв'язок з поточним
            for node, connections in network.items():
                if current in connections and node not in visited:
                    queue.append(node)
        
        return len(visited) == len(self._get_all_nodes())
    
    def _remove_edges(self, network: Dict[str, List[str]], edges_to_remove: List[Tuple[str, str]]) -> Dict[str, List[str]]:
        """
        Видаляє вказані ребра з мережі
        
        Args:
            network: Початкова мережа
            edges_to_remove: Список ребер для видалення
        
        Returns:
            Мережа з видаленими ребрами
        """
        new_network = {}
        for node, connections in network.items():
            new_connections = []
            for connection in connections:
                if (node, connection) not in edges_to_remove:
                    new_connections.append(connection)
            new_network[node] = new_connections
        
        return new_network
    
    def calculate_birnbaum_coefficient(self, removed_edges: List[Tuple[str, str]]) -> float:
        """
        Обчислює коефіцієнт надійності за критерієм Бірнбаума
        
        Args:
            removed_edges: Список видалених ребер
        
        Returns:
            Коефіцієнт надійності (0.0 - 1.0)
        """
        if self.total_nodes == 0:
            return 0.0
        
        # Видаляємо ребра
        modified_network = self._remove_edges(self.network_dict, removed_edges)
        
        # Перевіряємо зв'язність
        if not self._is_network_connected(modified_network):
            return 0.0
        
        # Перевіряємо доступність головного вузла
        if self.main_node and not self._is_main_node_accessible(modified_network):
            return 0.0
        
        # Обчислюємо коефіцієнт на основі кількості видалених ребер
        total_edges = len(self._get_all_edges())
        if total_edges == 0:
            return 1.0
        
        # Коефіцієнт Бірнбаума: 1 - (кількість_видалених_ребер / загальна_кількість_ребер)
        birnbaum_coeff = 1.0 - (len(removed_edges) / total_edges)
        
        return max(0.0, birnbaum_coeff)
    
    def _is_main_node_accessible(self, network: Dict[str, List[str]]) -> bool:
        """
        Перевіряє доступність головного вузла
        
        Args:
            network: Мережа для перевірки
        
        Returns:
            True якщо головний вузол доступний
        """
        if not self.main_node:
            return True
        
        # Перевіряємо, чи є головний вузол у мережі
        if self.main_node not in self._get_all_nodes():
            return False
        
        # Перевіряємо зв'язність з головним вузлом
        visited = set()
        queue = [self.main_node]
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            
            visited.add(current)
            
            # Додаємо всіх сусідів
            for neighbor in network.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)
            
            # Додаємо вузли, які мають зв'язок з поточним
            for node, connections in network.items():
                if current in connections and node not in visited:
                    queue.append(node)
        
        # Перевіряємо, чи всі вузли доступні з головного
        return len(visited) == len(self._get_all_nodes())
    
    def analyze_failure_scenarios(self, max_edges_to_remove: int = 3) -> Dict:
        """
        Аналізує сценарії відмов мережі
        
        Args:
            max_edges_to_remove: Максимальна кількість ребер для видалення
        
        Returns:
            Словник з результатами аналізу
        """
        all_edges = self._get_all_edges()
        results = {
            'scenarios': [],
            'summary': {
                'total_scenarios': 0,
                'critical_failures': 0,
                'partial_failures': 0,
                'no_failures': 0
            }
        }
        
        # Аналізуємо всі можливі комбінації видалення ребер
        for num_edges in range(1, min(max_edges_to_remove + 1, len(all_edges) + 1)):
            for edges_combination in itertools.combinations(all_edges, num_edges):
                removed_edges = list(edges_combination)
                birnbaum_coeff = self.calculate_birnbaum_coefficient(removed_edges)
                
                scenario = {
                    'removed_edges': removed_edges,
                    'birnbaum_coefficient': birnbaum_coeff,
                    'failure_type': self._classify_failure(birnbaum_coeff),
                    'edges_count': len(removed_edges)
                }
                
                results['scenarios'].append(scenario)
                results['summary']['total_scenarios'] += 1
                
                # Класифікуємо тип відмови
                if birnbaum_coeff == 0.0:
                    results['summary']['critical_failures'] += 1
                elif birnbaum_coeff < 0.5:
                    results['summary']['partial_failures'] += 1
                else:
                    results['summary']['no_failures'] += 1
        
        return results
    
    def _classify_failure(self, birnbaum_coeff: float) -> str:
        """
        Класифікує тип відмови на основі коефіцієнта Бірнбаума
        
        Args:
            birnbaum_coeff: Коефіцієнт Бірнбаума
        
        Returns:
            Тип відмови
        """
        if birnbaum_coeff == 0.0:
            return "Критична відмова"
        elif birnbaum_coeff < 0.3:
            return "Серйозна деградація"
        elif birnbaum_coeff < 0.7:
            return "Помірна деградація"
        else:
            return "Мінімальний вплив"
    
    def calculate_network_reliability(self, connection_probability: float = 0.8) -> Dict:
        """
        Обчислює загальну надійність мережі
        
        Args:
            connection_probability: Ймовірність роботи кожного ребра
        
        Returns:
            Словник з метриками надійності
        """
        all_edges = self._get_all_edges()
        total_edges = len(all_edges)
        
        if total_edges == 0:
            return {
                'network_reliability': 0.0,
                'expected_failures': 0,
                'reliability_class': 'Невизначена'
            }
        
        # Обчислюємо очікувану кількість відмов
        expected_failures = total_edges * (1 - connection_probability)
        
        # Обчислюємо загальну надійність мережі
        network_reliability = connection_probability ** total_edges
        
        # Класифікуємо надійність
        if network_reliability >= 0.9:
            reliability_class = "Висока надійність"
        elif network_reliability >= 0.7:
            reliability_class = "Помірна надійність"
        elif network_reliability >= 0.5:
            reliability_class = "Низька надійність"
        else:
            reliability_class = "Критично низька надійність"
        
        return {
            'network_reliability': network_reliability,
            'expected_failures': expected_failures,
            'reliability_class': reliability_class,
            'total_edges': total_edges,
            'connection_probability': connection_probability
        }
    
    def generate_reliability_report(self) -> str:
        """
        Генерує звіт про надійність мережі
        
        Returns:
            Текстовий звіт
        """
        report = f"""
=== ЗВІТ ПРО НАДІЙНІСТЬ МЕРЕЖІ ===

Загальна інформація:
- Кількість вузлів: {self.total_nodes}
- Головний вузол: {self.main_node or 'Не вказано'}
- Загальна кількість ребер: {len(self._get_all_edges())}

Аналіз сценаріїв відмов:
"""
        
        # Аналізуємо сценарії відмов
        failure_analysis = self.analyze_failure_scenarios(max_edges_to_remove=3)
        
        report += f"""
- Загальна кількість сценаріїв: {failure_analysis['summary']['total_scenarios']}
- Критичні відмови: {failure_analysis['summary']['critical_failures']}
- Помірні деградації: {failure_analysis['summary']['partial_failures']}
- Мінімальний вплив: {failure_analysis['summary']['no_failures']}
"""
        
        # Обчислюємо загальну надійність
        reliability_metrics = self.calculate_network_reliability()
        
        report += f"""

Метрики надійності:
- Загальна надійність мережі: {reliability_metrics['network_reliability']:.3f}
- Очікувана кількість відмов: {reliability_metrics['expected_failures']:.2f}
- Клас надійності: {reliability_metrics['reliability_class']}
"""
        
        return report

