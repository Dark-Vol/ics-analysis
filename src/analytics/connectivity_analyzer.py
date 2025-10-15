#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор связности и устойчивости ИКС
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

class ConnectivityMetric(Enum):
    """Метрики связности"""
    BASIC_CONNECTIVITY = "basic_connectivity"
    NODE_CONNECTIVITY = "node_connectivity"
    EDGE_CONNECTIVITY = "edge_connectivity"
    ROBUSTNESS = "robustness"
    REDUNDANCY = "redundancy"
    CRITICAL_NODES = "critical_nodes"
    CRITICAL_LINKS = "critical_links"

@dataclass
class ConnectivityReport:
    """Отчет по связности сети"""
    is_connected: bool
    num_components: int
    connectivity_coefficient: float
    node_connectivity: int
    edge_connectivity: int
    robustness_score: float
    redundancy_score: float
    critical_nodes: List[str]
    critical_links: List[Tuple[str, str]]
    component_analysis: Dict[str, Dict]
    failure_impact_analysis: Dict[str, float]

class ConnectivityAnalyzer:
    """Анализатор связности и устойчивости сети"""
    
    def __init__(self):
        self.graph = None
        self.node_data = {}
        self.link_data = {}
    
    def analyze_network(self, system_model) -> ConnectivityReport:
        """Провести полный анализ связности сети"""
        self.graph = system_model.graph.copy()
        self.node_data = system_model.nodes.copy()
        self.link_data = system_model.links.copy()
        
        # Базовая связность
        is_connected = nx.is_connected(self.graph)
        num_components = nx.number_connected_components(self.graph)
        connectivity_coefficient = self._calculate_connectivity_coefficient()
        
        # Метрики связности
        node_connectivity = nx.node_connectivity(self.graph) if len(self.graph.nodes()) > 1 else 0
        edge_connectivity = nx.edge_connectivity(self.graph) if len(self.graph.nodes()) > 1 else 0
        
        # Оценка устойчивости
        robustness_score = self._calculate_robustness_score()
        redundancy_score = self._calculate_redundancy_score()
        
        # Критические элементы
        critical_nodes = self._find_critical_nodes()
        critical_links = self._find_critical_links()
        
        # Анализ компонентов
        component_analysis = self._analyze_components()
        
        # Анализ влияния отказов
        failure_impact_analysis = self._analyze_failure_impacts()
        
        return ConnectivityReport(
            is_connected=is_connected,
            num_components=num_components,
            connectivity_coefficient=connectivity_coefficient,
            node_connectivity=node_connectivity,
            edge_connectivity=edge_connectivity,
            robustness_score=robustness_score,
            redundancy_score=redundancy_score,
            critical_nodes=critical_nodes,
            critical_links=critical_links,
            component_analysis=component_analysis,
            failure_impact_analysis=failure_impact_analysis
        )
    
    def _calculate_connectivity_coefficient(self) -> float:
        """Рассчитать коэффициент связности"""
        if not self.graph.nodes():
            return 0.0
        
        n = len(self.graph.nodes())
        if n <= 1:
            return 1.0
        
        # Количество достижимых пар узлов
        reachable_pairs = 0
        total_pairs = n * (n - 1)
        
        for source in self.graph.nodes():
            for target in self.graph.nodes():
                if source != target and nx.has_path(self.graph, source, target):
                    reachable_pairs += 1
        
        return reachable_pairs / total_pairs if total_pairs > 0 else 0.0
    
    def _calculate_robustness_score(self) -> float:
        """Рассчитать оценку устойчивости сети"""
        if not self.graph.nodes():
            return 0.0
        
        # Устойчивость к случайным отказам узлов
        random_failure_robustness = self._test_random_node_failures()
        
        # Устойчивость к целевым атакам
        targeted_attack_robustness = self._test_targeted_node_attacks()
        
        # Устойчивость к отказам связей
        link_failure_robustness = self._test_link_failures()
        
        # Общая оценка устойчивости
        robustness_score = (random_failure_robustness + 
                          targeted_attack_robustness + 
                          link_failure_robustness) / 3
        
        return robustness_score
    
    def _test_random_node_failures(self, num_tests: int = 100) -> float:
        """Тестировать устойчивость к случайным отказам узлов"""
        if len(self.graph.nodes()) <= 1:
            return 1.0
        
        original_graph = self.graph.copy()
        robustness_scores = []
        
        for _ in range(num_tests):
            test_graph = original_graph.copy()
            
            # Случайно удаляем 10% узлов
            nodes_to_remove = list(np.random.choice(
                list(test_graph.nodes()), 
                size=max(1, len(test_graph.nodes()) // 10),
                replace=False
            ))
            
            test_graph.remove_nodes_from(nodes_to_remove)
            
            # Рассчитываем связность после удаления
            if len(test_graph.nodes()) > 0:
                connectivity = nx.number_connected_components(test_graph)
                largest_component = max(nx.connected_components(test_graph), key=len)
                robustness = len(largest_component) / len(original_graph.nodes())
                robustness_scores.append(robustness)
        
        return np.mean(robustness_scores) if robustness_scores else 0.0
    
    def _test_targeted_node_attacks(self) -> float:
        """Тестировать устойчивость к целевым атакам на важные узлы"""
        if len(self.graph.nodes()) <= 1:
            return 1.0
        
        original_graph = self.graph.copy()
        
        # Находим узлы с высокой центральностью
        centrality = nx.betweenness_centrality(original_graph)
        high_centrality_nodes = sorted(centrality.keys(), 
                                     key=lambda x: centrality[x], 
                                     reverse=True)[:max(1, len(centrality) // 5)]
        
        test_graph = original_graph.copy()
        test_graph.remove_nodes_from(high_centrality_nodes)
        
        if len(test_graph.nodes()) > 0:
            largest_component = max(nx.connected_components(test_graph), key=len)
            robustness = len(largest_component) / len(original_graph.nodes())
        else:
            robustness = 0.0
        
        return robustness
    
    def _test_link_failures(self, num_tests: int = 50) -> float:
        """Тестировать устойчивость к отказам связей"""
        if len(self.graph.edges()) <= 1:
            return 1.0
        
        original_graph = self.graph.copy()
        robustness_scores = []
        
        for _ in range(num_tests):
            test_graph = original_graph.copy()
            
            # Случайно удаляем 20% связей
            edges_to_remove = list(np.random.choice(
                list(test_graph.edges()),
                size=max(1, len(test_graph.edges()) // 5),
                replace=False
            ))
            
            test_graph.remove_edges_from(edges_to_remove)
            
            # Рассчитываем связность после удаления связей
            if len(test_graph.nodes()) > 0:
                connectivity = nx.number_connected_components(test_graph)
                largest_component = max(nx.connected_components(test_graph), key=len)
                robustness = len(largest_component) / len(original_graph.nodes())
                robustness_scores.append(robustness)
        
        return np.mean(robustness_scores) if robustness_scores else 0.0
    
    def _calculate_redundancy_score(self) -> float:
        """Рассчитать оценку избыточности сети"""
        if not self.graph.nodes():
            return 0.0
        
        # Избыточность путей между узлами
        path_redundancy = self._calculate_path_redundancy()
        
        # Избыточность связей
        link_redundancy = self._calculate_link_redundancy()
        
        # Избыточность узлов
        node_redundancy = self._calculate_node_redundancy()
        
        redundancy_score = (path_redundancy + link_redundancy + node_redundancy) / 3
        
        return redundancy_score
    
    def _calculate_path_redundancy(self) -> float:
        """Рассчитать избыточность путей"""
        if len(self.graph.nodes()) < 2:
            return 0.0
        
        total_redundancy = 0.0
        path_pairs = 0
        
        for source in self.graph.nodes():
            for target in self.graph.nodes():
                if source != target:
                    try:
                        # Количество кратчайших путей
                        num_shortest_paths = len(list(nx.all_shortest_paths(self.graph, source, target)))
                        # Количество всех простых путей
                        num_all_paths = len(list(nx.all_simple_paths(self.graph, source, target)))
                        
                        if num_all_paths > 0:
                            redundancy = (num_all_paths - num_shortest_paths) / num_all_paths
                            total_redundancy += redundancy
                            path_pairs += 1
                    except:
                        continue
        
        return total_redundancy / path_pairs if path_pairs > 0 else 0.0
    
    def _calculate_link_redundancy(self) -> float:
        """Рассчитать избыточность связей"""
        if not self.graph.edges():
            return 0.0
        
        # Связи, которые не являются мостами
        bridges = list(nx.bridges(self.graph))
        non_bridge_edges = [edge for edge in self.graph.edges() if edge not in bridges]
        
        return len(non_bridge_edges) / len(self.graph.edges()) if self.graph.edges() else 0.0
    
    def _calculate_node_redundancy(self) -> float:
        """Рассчитать избыточность узлов"""
        if len(self.graph.nodes()) < 2:
            return 0.0
        
        # Узлы, которые не являются точками сочленения
        articulation_points = set(nx.articulation_points(self.graph))
        non_articulation_nodes = [node for node in self.graph.nodes() if node not in articulation_points]
        
        return len(non_articulation_nodes) / len(self.graph.nodes())
    
    def _find_critical_nodes(self, threshold: float = 0.8) -> List[str]:
        """Найти критические узлы"""
        if not self.graph.nodes():
            return []
        
        critical_nodes = []
        
        for node in self.graph.nodes():
            # Тестируем удаление узла
            test_graph = self.graph.copy()
            test_graph.remove_node(node)
            
            # Рассчитываем влияние на связность
            if len(test_graph.nodes()) > 0:
                original_connectivity = self._calculate_connectivity_coefficient()
                new_connectivity = self._calculate_connectivity_coefficient_for_graph(test_graph)
                impact = (original_connectivity - new_connectivity) / original_connectivity if original_connectivity > 0 else 0
                
                if impact > threshold:
                    critical_nodes.append(node)
        
        return critical_nodes
    
    def _find_critical_links(self, threshold: float = 0.5) -> List[Tuple[str, str]]:
        """Найти критические связи"""
        if not self.graph.edges():
            return []
        
        critical_links = []
        
        for edge in self.graph.edges():
            # Тестируем удаление связи
            test_graph = self.graph.copy()
            test_graph.remove_edge(*edge)
            
            # Рассчитываем влияние на связность
            original_connectivity = self._calculate_connectivity_coefficient()
            new_connectivity = self._calculate_connectivity_coefficient_for_graph(test_graph)
            impact = (original_connectivity - new_connectivity) / original_connectivity if original_connectivity > 0 else 0
            
            if impact > threshold:
                critical_links.append(edge)
        
        return critical_links
    
    def _calculate_connectivity_coefficient_for_graph(self, graph: nx.Graph) -> float:
        """Рассчитать коэффициент связности для заданного графа"""
        if not graph.nodes():
            return 0.0
        
        n = len(graph.nodes())
        if n <= 1:
            return 1.0
        
        reachable_pairs = 0
        total_pairs = n * (n - 1)
        
        for source in graph.nodes():
            for target in graph.nodes():
                if source != target and nx.has_path(graph, source, target):
                    reachable_pairs += 1
        
        return reachable_pairs / total_pairs if total_pairs > 0 else 0.0
    
    def _analyze_components(self) -> Dict[str, Dict]:
        """Анализировать компоненты связности"""
        components = list(nx.connected_components(self.graph))
        component_analysis = {}
        
        for i, component in enumerate(components):
            subgraph = self.graph.subgraph(component)
            
            component_analysis[f"component_{i}"] = {
                "size": len(component),
                "density": nx.density(subgraph),
                "diameter": nx.diameter(subgraph) if len(component) > 1 else 0,
                "average_path_length": nx.average_shortest_path_length(subgraph) if len(component) > 1 else 0,
                "clustering_coefficient": nx.average_clustering(subgraph),
                "nodes": list(component)
            }
        
        return component_analysis
    
    def _analyze_failure_impacts(self) -> Dict[str, float]:
        """Анализировать влияние различных типов отказов"""
        failure_impacts = {}
        
        # Влияние отказа каждого узла
        for node in self.graph.nodes():
            test_graph = self.graph.copy()
            test_graph.remove_node(node)
            
            original_connectivity = self._calculate_connectivity_coefficient()
            new_connectivity = self._calculate_connectivity_coefficient_for_graph(test_graph)
            
            failure_impacts[f"node_{node}_failure"] = (
                original_connectivity - new_connectivity
            ) / original_connectivity if original_connectivity > 0 else 0
        
        # Влияние отказа каждой связи
        for edge in self.graph.edges():
            test_graph = self.graph.copy()
            test_graph.remove_edge(*edge)
            
            original_connectivity = self._calculate_connectivity_coefficient()
            new_connectivity = self._calculate_connectivity_coefficient_for_graph(test_graph)
            
            failure_impacts[f"link_{edge[0]}_{edge[1]}_failure"] = (
                original_connectivity - new_connectivity
            ) / original_connectivity if original_connectivity > 0 else 0
        
        return failure_impacts
    
    def get_connectivity_recommendations(self, report: ConnectivityReport) -> List[str]:
        """Получить рекомендации по улучшению связности"""
        recommendations = []
        
        if not report.is_connected:
            recommendations.append("Сеть несвязна. Необходимо добавить связи между компонентами.")
        
        if report.num_components > 1:
            recommendations.append(f"Сеть состоит из {report.num_components} компонентов. Рекомендуется увеличить связность.")
        
        if report.node_connectivity < 2:
            recommendations.append("Низкая узловая связность. Добавьте резервные пути между узлами.")
        
        if report.edge_connectivity < 2:
            recommendations.append("Низкая реберная связность. Добавьте резервные связи.")
        
        if report.robustness_score < 0.7:
            recommendations.append("Низкая устойчивость к отказам. Увеличьте избыточность сети.")
        
        if report.redundancy_score < 0.5:
            recommendations.append("Недостаточная избыточность. Добавьте альтернативные пути и связи.")
        
        if len(report.critical_nodes) > 0:
            recommendations.append(f"Найдены критические узлы: {', '.join(report.critical_nodes)}. Защитите их или добавьте резервирование.")
        
        if len(report.critical_links) > 0:
            recommendations.append(f"Найдены критические связи: {report.critical_links}. Добавьте резервные каналы.")
        
        if not recommendations:
            recommendations.append("Сеть имеет хорошую связность и устойчивость.")
        
        return recommendations

