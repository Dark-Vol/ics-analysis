#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль построения модели ИКС в виде графа
"""

import networkx as nx
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import random


class NodeType(Enum):
    """Типы узлов в ИКС"""
    SERVER = "server"
    ROUTER = "router"
    SWITCH = "switch"
    CLIENT = "client"
    GATEWAY = "gateway"
    FIREWALL = "firewall"


class LinkType(Enum):
    """Типы каналов связи"""
    ETHERNET = "ethernet"
    WIFI = "wifi"
    FIBER = "fiber"
    COPPER = "copper"
    WIRELESS = "wireless"


@dataclass
class Node:
    """Узел сети"""
    id: str
    node_type: NodeType
    capacity: float  # Пропускная способность (Мбит/с)
    reliability: float  # Надежность (0-1)
    cpu_load: float = 0.0  # Загрузка CPU (0-1)
    memory_usage: float = 0.0  # Использование памяти (0-1)
    load: float = 0.0  # Общая загрузка узла (0-1)
    threat_level: float = 0.1  # Уровень угрозы/уязвимости (0-1)
    encryption: bool = True  # Наличие криптографической защиты
    x: float = 0.0  # Координата X для визуализации
    y: float = 0.0  # Координата Y для визуализации


@dataclass
class Link:
    """Канал связи"""
    source: str
    target: str
    bandwidth: float  # Пропускная способность (Мбит/с)
    latency: float  # Задержка (мс)
    reliability: float  # Надежность (0-1)
    link_type: LinkType
    utilization: float = 0.0  # Использование канала (0-1)
    load: float = 0.0  # Текущая загрузка канала (0-1)
    encryption: bool = True  # Наличие криптографической защиты
    threat_level: float = 0.1  # Уровень угрозы/уязвимости (0-1)


class SystemModel:
    """Модель ИКС в виде графа"""
    
    def __init__(self, name: str = "ИКС Система"):
        self.name = name
        self.graph = nx.Graph()
        self.nodes: Dict[str, Node] = {}
        self.links: Dict[Tuple[str, str], Link] = {}
        self.metrics = {}
        
    def add_node(self, node: Node):
        """Добавить узел в систему"""
        self.nodes[node.id] = node
        self.graph.add_node(
            node.id,
            node_type=node.node_type.value,
            capacity=node.capacity,
            reliability=node.reliability,
            cpu_load=node.cpu_load,
            memory_usage=node.memory_usage,
            load=node.load,
            threat_level=node.threat_level,
            encryption=node.encryption,
            x=node.x,
            y=node.y
        )
    
    def add_link(self, link: Link):
        """Добавить канал связи"""
        self.links[(link.source, link.target)] = link
        self.graph.add_edge(
            link.source,
            link.target,
            bandwidth=link.bandwidth,
            latency=link.latency,
            reliability=link.reliability,
            link_type=link.link_type.value,
            utilization=link.utilization,
            load=link.load,
            encryption=link.encryption,
            threat_level=link.threat_level
        )
    
    def remove_node(self, node_id: str):
        """Удалить узел из системы"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            self.graph.remove_node(node_id)
            
            # Удаляем связанные каналы
            links_to_remove = []
            for (source, target), link in self.links.items():
                if source == node_id or target == node_id:
                    links_to_remove.append((source, target))
            
            for link_key in links_to_remove:
                del self.links[link_key]
                if self.graph.has_edge(link_key[0], link_key[1]):
                    self.graph.remove_edge(link_key[0], link_key[1])
    
    def remove_link(self, source: str, target: str):
        """Удалить канал связи"""
        if (source, target) in self.links:
            del self.links[(source, target)]
            if self.graph.has_edge(source, target):
                self.graph.remove_edge(source, target)
    
    def generate_random_network(self, num_nodes: int = 10, connection_prob: float = 0.3):
        """Генерировать случайную сеть"""
        # Очищаем текущую сеть
        self.graph.clear()
        self.nodes.clear()
        self.links.clear()
        
        # Генерируем узлы
        node_types = list(NodeType)
        for i in range(num_nodes):
            node_type = random.choice(node_types)
            capacity = random.uniform(100, 1000)  # Мбит/с
            reliability = random.uniform(0.85, 0.99)
            
            node = Node(
                id=f"node_{i}",
                node_type=node_type,
                capacity=capacity,
                reliability=reliability,
                x=random.uniform(0, 100),
                y=random.uniform(0, 100)
            )
            self.add_node(node)
        
        # Генерируем каналы связи
        node_ids = list(self.nodes.keys())
        link_types = list(LinkType)
        
        for i, source in enumerate(node_ids):
            for j, target in enumerate(node_ids[i+1:], i+1):
                if random.random() < connection_prob:
                    bandwidth = random.uniform(10, 100)  # Мбит/с
                    latency = random.uniform(1, 50)  # мс
                    reliability = random.uniform(0.90, 0.99)
                    link_type = random.choice(link_types)
                    
                    link = Link(
                        source=source,
                        target=target,
                        bandwidth=bandwidth,
                        latency=latency,
                        reliability=reliability,
                        link_type=link_type
                    )
                    self.add_link(link)
    
    def calculate_network_metrics(self):
        """Рассчитать метрики сети"""
        if not self.graph.nodes():
            return {}
        
        # Основные метрики
        metrics = {
            'num_nodes': len(self.graph.nodes()),
            'num_edges': len(self.graph.edges()),
            'density': nx.density(self.graph),
            'average_clustering': nx.average_clustering(self.graph),
        }
        
        # Связность
        if nx.is_connected(self.graph):
            metrics['average_path_length'] = nx.average_shortest_path_length(self.graph)
            metrics['diameter'] = nx.diameter(self.graph)
        else:
            # Для несвязных графов считаем по компонентам
            components = list(nx.connected_components(self.graph))
            metrics['num_components'] = len(components)
            metrics['largest_component_size'] = len(max(components, key=len))
        
        # Центральность
        try:
            metrics['betweenness_centrality'] = nx.betweenness_centrality(self.graph)
            metrics['closeness_centrality'] = nx.closeness_centrality(self.graph)
            metrics['degree_centrality'] = nx.degree_centrality(self.graph)
        except:
            pass
        
        # Пропускная способность
        total_bandwidth = sum(link.bandwidth for link in self.links.values())
        avg_reliability = np.mean([node.reliability for node in self.nodes.values()])
        
        metrics['total_bandwidth'] = total_bandwidth
        metrics['average_reliability'] = avg_reliability
        
        self.metrics = metrics
        return metrics
    
    def get_node_load(self, node_id: str) -> Dict[str, float]:
        """Получить загрузку узла"""
        if node_id not in self.nodes:
            return {}
        
        node = self.nodes[node_id]
        
        # Рассчитываем загрузку на основе подключенных каналов
        connected_links = [
            link for link in self.links.values()
            if link.source == node_id or link.target == node_id
        ]
        
        total_bandwidth_used = sum(link.bandwidth * link.utilization for link in connected_links)
        bandwidth_load = min(total_bandwidth_used / node.capacity, 1.0) if node.capacity > 0 else 0
        
        return {
            'cpu_load': node.cpu_load,
            'memory_usage': node.memory_usage,
            'bandwidth_load': bandwidth_load,
            'total_load': (node.cpu_load + node.memory_usage + bandwidth_load) / 3
        }
    
    def update_node_load(self, node_id: str, cpu_load: float = None, 
                        memory_usage: float = None):
        """Обновить загрузку узла"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            if cpu_load is not None:
                node.cpu_load = max(0, min(1, cpu_load))
            if memory_usage is not None:
                node.memory_usage = max(0, min(1, memory_usage))
            
            # Обновляем данные в графе
            self.graph.nodes[node_id]['cpu_load'] = node.cpu_load
            self.graph.nodes[node_id]['memory_usage'] = node.memory_usage
    
    def update_link_utilization(self, source: str, target: str, utilization: float):
        """Обновить использование канала"""
        link_key = (source, target)
        if link_key in self.links:
            link = self.links[link_key]
            link.utilization = max(0, min(1, utilization))
            
            # Обновляем данные в графе
            if self.graph.has_edge(source, target):
                self.graph.edges[source, target]['utilization'] = link.utilization
    
    def simulate_traffic(self, traffic_matrix: Dict[Tuple[str, str], float]):
        """Симулировать трафик между узлами"""
        # Обновляем использование каналов на основе матрицы трафика
        for (source, target), traffic_load in traffic_matrix.items():
            if (source, target) in self.links:
                # Нормализуем трафик относительно пропускной способности канала
                link = self.links[(source, target)]
                utilization = min(traffic_load / link.bandwidth, 1.0)
                self.update_link_utilization(source, target, utilization)
    
    def export_to_dataframe(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Экспортировать модель в DataFrame"""
        # Узлы
        nodes_data = []
        for node_id, node in self.nodes.items():
            nodes_data.append({
                'id': node_id,
                'type': node.node_type.value,
                'capacity': node.capacity,
                'reliability': node.reliability,
                'cpu_load': node.cpu_load,
                'memory_usage': node.memory_usage,
                'x': node.x,
                'y': node.y
            })
        
        nodes_df = pd.DataFrame(nodes_data)
        
        # Каналы
        links_data = []
        for (source, target), link in self.links.items():
            links_data.append({
                'source': source,
                'target': target,
                'bandwidth': link.bandwidth,
                'latency': link.latency,
                'reliability': link.reliability,
                'type': link.link_type.value,
                'utilization': link.utilization
            })
        
        links_df = pd.DataFrame(links_data)
        
        return nodes_df, links_df
    
    def import_from_dataframe(self, nodes_df: pd.DataFrame, links_df: pd.DataFrame):
        """Импортировать модель из DataFrame"""
        # Очищаем текущую модель
        self.graph.clear()
        self.nodes.clear()
        self.links.clear()
        
        # Импортируем узлы
        for _, row in nodes_df.iterrows():
            node = Node(
                id=row['id'],
                node_type=NodeType(row['type']),
                capacity=row['capacity'],
                reliability=row['reliability'],
                cpu_load=row.get('cpu_load', 0.0),
                memory_usage=row.get('memory_usage', 0.0),
                x=row.get('x', 0.0),
                y=row.get('y', 0.0)
            )
            self.add_node(node)
        
        # Импортируем каналы
        for _, row in links_df.iterrows():
            link = Link(
                source=row['source'],
                target=row['target'],
                bandwidth=row['bandwidth'],
                latency=row['latency'],
                reliability=row['reliability'],
                link_type=LinkType(row['type']),
                utilization=row.get('utilization', 0.0)
            )
            self.add_link(link)
    
    def calculate_connectivity_metrics(self) -> Dict[str, float]:
        """Рассчитать метрики связности сети"""
        if not self.graph.nodes():
            return {}
        
        metrics = {}
        
        # Базовая связность
        metrics['is_connected'] = nx.is_connected(self.graph)
        metrics['num_components'] = nx.number_connected_components(self.graph)
        
        if metrics['is_connected']:
            metrics['diameter'] = nx.diameter(self.graph)
            metrics['radius'] = nx.radius(self.graph)
            metrics['average_path_length'] = nx.average_shortest_path_length(self.graph)
            metrics['eccentricity'] = nx.eccentricity(self.graph)
        else:
            # Для несвязных графов анализируем компоненты
            components = list(nx.connected_components(self.graph))
            component_sizes = [len(comp) for comp in components]
            metrics['largest_component_size'] = max(component_sizes)
            metrics['component_size_variance'] = np.var(component_sizes) if component_sizes else 0
        
        # Коэффициент связности
        metrics['connectivity_coefficient'] = self._calculate_connectivity_coefficient()
        
        # Устойчивость к отказам
        metrics['node_connectivity'] = nx.node_connectivity(self.graph) if len(self.graph.nodes()) > 1 else 0
        metrics['edge_connectivity'] = nx.edge_connectivity(self.graph) if len(self.graph.nodes()) > 1 else 0
        
        return metrics
    
    def _calculate_connectivity_coefficient(self) -> float:
        """Рассчитать коэффициент связности сети"""
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
    
    def calculate_data_loss_metrics(self) -> Dict[str, float]:
        """Рассчитать метрики потерь данных"""
        if not self.graph.nodes():
            return {}
        
        metrics = {}
        
        # Потери из-за отказов узлов
        node_failure_loss = 0.0
        for node_id, node in self.nodes.items():
            failure_prob = 1 - node.reliability
            node_failure_loss += failure_prob * node.capacity
        
        metrics['node_failure_data_loss'] = node_failure_loss
        
        # Потери из-за отказов каналов
        link_failure_loss = 0.0
        for (source, target), link in self.links.items():
            failure_prob = 1 - link.reliability
            link_failure_loss += failure_prob * link.bandwidth
        
        metrics['link_failure_data_loss'] = link_failure_loss
        
        # Общие потери данных
        metrics['total_data_loss'] = node_failure_loss + link_failure_loss
        
        # Коэффициент доступности
        total_capacity = sum(node.capacity for node in self.nodes.values())
        total_bandwidth = sum(link.bandwidth for link in self.links.values())
        metrics['availability_coefficient'] = 1 - (metrics['total_data_loss'] / (total_capacity + total_bandwidth)) if (total_capacity + total_bandwidth) > 0 else 1.0
        
        return metrics
    
    def calculate_performance_degradation(self) -> Dict[str, float]:
        """Рассчитать деградацию производительности"""
        if not self.graph.nodes():
            return {}
        
        metrics = {}
        
        # Деградация из-за загрузки узлов
        avg_node_load = np.mean([node.load for node in self.nodes.values()]) if self.nodes else 0
        metrics['node_load_degradation'] = avg_node_load
        
        # Деградация из-за загрузки каналов
        avg_link_load = np.mean([link.load for link in self.links.values()]) if self.links else 0
        metrics['link_load_degradation'] = avg_link_load
        
        # Деградация из-за уровня угроз
        avg_threat_level = np.mean([node.threat_level for node in self.nodes.values()]) if self.nodes else 0
        metrics['threat_degradation'] = avg_threat_level
        
        # Общая деградация производительности
        metrics['overall_degradation'] = (metrics['node_load_degradation'] + 
                                        metrics['link_load_degradation'] + 
                                        metrics['threat_degradation']) / 3
        
        return metrics
    
    def get_network_summary(self) -> str:
        """Получить текстовое описание сети"""
        metrics = self.calculate_network_metrics()
        connectivity = self.calculate_connectivity_metrics()
        data_loss = self.calculate_data_loss_metrics()
        degradation = self.calculate_performance_degradation()
        
        summary = f"""
=== {self.name} ===
Узлы: {metrics.get('num_nodes', 0)}
Каналы: {metrics.get('num_edges', 0)}
Плотность: {metrics.get('density', 0):.3f}
Средняя надежность: {metrics.get('average_reliability', 0):.3f}
Общая пропускная способность: {metrics.get('total_bandwidth', 0):.1f} Мбит/с

=== Связность ===
Связность: {'Да' if connectivity.get('is_connected', False) else 'Нет'}
Компоненты: {connectivity.get('num_components', 0)}
Коэффициент связности: {connectivity.get('connectivity_coefficient', 0):.3f}
Узловая связность: {connectivity.get('node_connectivity', 0)}
Реберная связность: {connectivity.get('edge_connectivity', 0)}

=== Потери данных ===
Коэффициент доступности: {data_loss.get('availability_coefficient', 0):.3f}
Потери узлов: {data_loss.get('node_failure_data_loss', 0):.1f}
Потери каналов: {data_loss.get('link_failure_data_loss', 0):.1f}

=== Деградация производительности ===
Общая деградация: {degradation.get('overall_degradation', 0):.3f}
Деградация узлов: {degradation.get('node_load_degradation', 0):.3f}
Деградация каналов: {degradation.get('link_load_degradation', 0):.3f}
Деградация угроз: {degradation.get('threat_degradation', 0):.3f}
"""
        
        return summary


def create_sample_network() -> SystemModel:
    """Создать пример сети для тестирования"""
    model = SystemModel("Тестовая ИКС")
    
    # Добавляем узлы
    nodes = [
        Node("server1", NodeType.SERVER, 1000, 0.99, 0.3, 0.4),
        Node("server2", NodeType.SERVER, 800, 0.98, 0.2, 0.3),
        Node("router1", NodeType.ROUTER, 500, 0.95, 0.5, 0.6),
        Node("switch1", NodeType.SWITCH, 300, 0.97, 0.1, 0.2),
        Node("client1", NodeType.CLIENT, 100, 0.92, 0.8, 0.7),
        Node("client2", NodeType.CLIENT, 100, 0.90, 0.6, 0.5),
    ]
    
    for node in nodes:
        model.add_node(node)
    
    # Добавляем каналы
    links = [
        Link("server1", "router1", 100, 5, 0.98, LinkType.FIBER),
        Link("server2", "router1", 80, 6, 0.97, LinkType.FIBER),
        Link("router1", "switch1", 50, 2, 0.99, LinkType.ETHERNET),
        Link("switch1", "client1", 10, 1, 0.95, LinkType.ETHERNET),
        Link("switch1", "client2", 10, 1, 0.94, LinkType.ETHERNET),
    ]
    
    for link in links:
        model.add_link(link)
    
    return model


if __name__ == "__main__":
    # Тестирование модуля
    model = create_sample_network()
    print(model.get_network_summary())
    
    # Тестирование метрик
    metrics = model.calculate_network_metrics()
    print("\nМетрики сети:")
    for key, value in metrics.items():
        if isinstance(value, dict):
            print(f"{key}: {len(value)} элементов")
        else:
            print(f"{key}: {value}")
    
    # Тестирование экспорта
    nodes_df, links_df = model.export_to_dataframe()
    print(f"\nЭкспорт: {len(nodes_df)} узлов, {len(links_df)} каналов")
