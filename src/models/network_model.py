#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модель сети для анализа ИКС
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class NetworkNode:
    """Узел сети"""
    id: int
    x: float
    y: float
    capacity: float  # пропускная способность
    reliability: float  # надежность
    processing_delay: float  # задержка обработки

@dataclass
class NetworkLink:
    """Связь в сети"""
    source: int
    target: int
    bandwidth: float  # пропускная способность
    latency: float  # задержка
    reliability: float  # надежность
    distance: float  # расстояние

class NetworkModel:
    """Модель информационно-коммуникационной сети"""
    
    def __init__(self, nodes: int = 10, connection_probability: float = 0.3):
        self.nodes = []
        self.links = []
        self.graph = nx.Graph()
        self._create_network(nodes, connection_probability)
    
    def _create_network(self, nodes: int, connection_probability: float):
        """Создает сеть с заданными параметрами"""
        # Создание узлов
        for i in range(nodes):
            node = NetworkNode(
                id=i,
                x=np.random.uniform(0, 100),
                y=np.random.uniform(0, 100),
                capacity=np.random.uniform(100, 1000),  # Мбит/с
                reliability=np.random.uniform(0.9, 0.99),
                processing_delay=np.random.uniform(1, 10)  # мс
            )
            self.nodes.append(node)
            self.graph.add_node(i, **node.__dict__)
        
        # Создание связей
        for i in range(nodes):
            for j in range(i + 1, nodes):
                if np.random.random() < connection_probability:
                    distance = np.sqrt(
                        (self.nodes[i].x - self.nodes[j].x)**2 + 
                        (self.nodes[i].y - self.nodes[j].y)**2
                    )
                    
                    link = NetworkLink(
                        source=i,
                        target=j,
                        bandwidth=np.random.uniform(10, 100),  # Мбит/с
                        latency=distance * 0.1 + np.random.uniform(1, 5),  # мс
                        reliability=np.random.uniform(0.85, 0.98),
                        distance=distance
                    )
                    
                    self.links.append(link)
                    self.graph.add_edge(i, j, **link.__dict__)
    
    def get_node(self, node_id: int) -> Optional[NetworkNode]:
        """Получает узел по ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_link(self, source: int, target: int) -> Optional[NetworkLink]:
        """Получает связь между узлами"""
        for link in self.links:
            if (link.source == source and link.target == target) or \
               (link.source == target and link.target == source):
                return link
        return None
    
    def get_neighbors(self, node_id: int) -> List[int]:
        """Получает соседние узлы"""
        return list(self.graph.neighbors(node_id))
    
    def calculate_shortest_path(self, source: int, target: int) -> List[int]:
        """Вычисляет кратчайший путь между узлами"""
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return []
    
    def calculate_path_metrics(self, path: List[int]) -> Dict[str, float]:
        """Вычисляет метрики пути"""
        if len(path) < 2:
            return {"latency": 0, "reliability": 1, "bandwidth": float('inf')}
        
        total_latency = 0
        total_reliability = 1
        min_bandwidth = float('inf')
        
        for i in range(len(path) - 1):
            link = self.get_link(path[i], path[i + 1])
            if link:
                total_latency += link.latency
                total_reliability *= link.reliability
                min_bandwidth = min(min_bandwidth, link.bandwidth)
            
            # Добавляем задержку обработки узла
            node = self.get_node(path[i + 1])
            if node:
                total_latency += node.processing_delay
        
        return {
            "latency": total_latency,
            "reliability": total_reliability,
            "bandwidth": min_bandwidth
        }
    
    def get_network_metrics(self) -> Dict[str, float]:
        """Вычисляет общие метрики сети"""
        if not self.graph.nodes():
            return {}
        
        return {
            "nodes_count": len(self.nodes),
            "links_count": len(self.links),
            "density": nx.density(self.graph),
            "average_clustering": nx.average_clustering(self.graph),
            "diameter": nx.diameter(self.graph) if nx.is_connected(self.graph) else 0,
            "average_path_length": nx.average_shortest_path_length(self.graph) if nx.is_connected(self.graph) else 0
        }
    
    def apply_failure(self, node_id: int):
        """Применяет отказ узла"""
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
            self.nodes = [node for node in self.nodes if node.id != node_id]
            self.links = [link for link in self.links if link.source != node_id and link.target != node_id]
    
    def apply_link_failure(self, source: int, target: int):
        """Применяет отказ связи"""
        if self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)
            self.links = [link for link in self.links if not 
                         ((link.source == source and link.target == target) or
                          (link.source == target and link.target == source))]
    
    def restore_node(self, node: NetworkNode):
        """Восстанавливает узел"""
        if not self.graph.has_node(node.id):
            self.nodes.append(node)
            self.graph.add_node(node.id, **node.__dict__)
    
    def restore_link(self, link: NetworkLink):
        """Восстанавливает связь"""
        if not self.graph.has_edge(link.source, link.target):
            self.links.append(link)
            self.graph.add_edge(link.source, link.target, **link.__dict__)





