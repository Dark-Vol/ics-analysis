#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль имитационного моделирования ИКС с использованием simpy
"""

import simpy
import numpy as np
import pandas as pd
import networkx as nx
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import random
import time
from .system_model import SystemModel, Node, Link


class EventType(Enum):
    """Типы событий в симуляции"""
    TRAFFIC_REQUEST = "traffic_request"
    NODE_FAILURE = "node_failure"
    LINK_FAILURE = "link_failure"
    NODE_RECOVERY = "node_recovery"
    LINK_RECOVERY = "link_recovery"
    NETWORK_CONGESTION = "network_congestion"
    DATA_TRANSFER = "data_transfer"


@dataclass
class SimulationEvent:
    """Событие симуляции"""
    event_type: EventType
    timestamp: float
    source: str
    target: str = ""
    data_size: float = 0.0
    priority: int = 1
    metadata: Dict = None


class NetworkNode:
    """Модель сетевого узла в симуляции"""
    
    def __init__(self, env: simpy.Environment, node: Node, node_id: str):
        self.env = env
        self.node = node
        self.node_id = node_id
        self.cpu_resource = simpy.Resource(env, capacity=1)
        self.memory_resource = simpy.Resource(env, capacity=1)
        self.is_failed = False
        self.queue_length = 0
        self.processed_requests = 0
        self.failed_requests = 0
        self.response_times = []
    
    def process_request(self, request_size: float, priority: int = 1):
        """Обработать запрос"""
        if self.is_failed:
            return False, 0
        
        start_time = self.env.now
        
        try:
            # Запрос ресурсов CPU и памяти
            with self.cpu_resource.request(priority=priority) as cpu_req:
                yield cpu_req
                
                with self.memory_resource.request(priority=priority) as mem_req:
                    yield mem_req
                    
                    # Время обработки зависит от размера запроса и загрузки
                    processing_time = self._calculate_processing_time(request_size)
                    yield self.env.timeout(processing_time)
                    
                    self.processed_requests += 1
                    response_time = self.env.now - start_time
                    self.response_times.append(response_time)
                    
                    return True, response_time
        except:
            self.failed_requests += 1
            return False, 0
    
    def _calculate_processing_time(self, request_size: float) -> float:
        """Рассчитать время обработки запроса"""
        base_time = request_size / self.node.capacity  # секунды на Мбит
        load_factor = 1 + self.node.cpu_load + self.node.memory_usage
        return base_time * load_factor * random.uniform(0.8, 1.2)
    
    def fail(self):
        """Отказ узла"""
        self.is_failed = True
    
    def recover(self):
        """Восстановление узла"""
        self.is_failed = False


class NetworkLink:
    """Модель канала связи в симуляции"""
    
    def __init__(self, env: simpy.Environment, link: Link, link_id: str):
        self.env = env
        self.link = link
        self.link_id = link_id
        self.bandwidth_resource = simpy.Resource(env, capacity=1)
        self.is_failed = False
        self.transferred_data = 0.0
        self.failed_transfers = 0
        self.transfer_times = []
    
    def transfer_data(self, data_size: float, priority: int = 1):
        """Передать данные по каналу"""
        if self.is_failed:
            return False, 0
        
        start_time = self.env.now
        
        try:
            with self.bandwidth_resource.request(priority=priority) as req:
                yield req
                
                # Время передачи зависит от размера данных и пропускной способности
                transfer_time = self._calculate_transfer_time(data_size)
                yield self.env.timeout(transfer_time)
                
                self.transferred_data += data_size
                actual_transfer_time = self.env.now - start_time
                self.transfer_times.append(actual_transfer_time)
                
                return True, actual_transfer_time
        except:
            self.failed_transfers += 1
            return False, 0
    
    def _calculate_transfer_time(self, data_size: float) -> float:
        """Рассчитать время передачи данных"""
        # Учитываем задержку и пропускную способность
        base_time = data_size / self.link.bandwidth  # секунды
        latency_factor = self.link.latency / 1000.0  # преобразуем мс в секунды
        utilization_factor = 1 + self.link.utilization
        
        return base_time * utilization_factor + latency_factor
    
    def fail(self):
        """Отказ канала"""
        self.is_failed = True
    
    def recover(self):
        """Восстановление канала"""
        self.is_failed = False


class NetworkSimulator:
    """Основной класс симулятора сети"""
    
    def __init__(self, system_model: SystemModel, simulation_duration: float = 3600):
        self.system_model = system_model
        self.simulation_duration = simulation_duration
        self.env = simpy.Environment()
        
        # Создаем модели узлов и каналов
        self.network_nodes = {}
        self.network_links = {}
        
        for node_id, node in system_model.nodes.items():
            self.network_nodes[node_id] = NetworkNode(self.env, node, node_id)
        
        for (source, target), link in system_model.links.items():
            link_id = f"{source}_{target}"
            self.network_links[link_id] = NetworkLink(self.env, link, link_id)
        
        # Статистика симуляции
        self.events = []
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'network_throughput': 0.0,
            'node_utilization': {},
            'link_utilization': {}
        }
    
    def add_event(self, event: SimulationEvent):
        """Добавить событие в симуляцию"""
        self.events.append(event)
    
    def run_simulation(self):
        """Запустить симуляцию"""
        # Запускаем процессы
        self.env.process(self._traffic_generator())
        self.env.process(self._failure_generator())
        self.env.process(self._recovery_generator())
        self.env.process(self._metrics_collector())
        
        # Запускаем симуляцию
        self.env.run(until=self.simulation_duration)
        
        # Собираем финальную статистику
        self._collect_final_metrics()
    
    def _traffic_generator(self):
        """Генератор трафика"""
        while True:
            # Генерируем случайный трафик
            source = random.choice(list(self.network_nodes.keys()))
            target = random.choice(list(self.network_nodes.keys()))
            
            if source != target:
                data_size = random.uniform(0.1, 10.0)  # Мбит
                priority = random.randint(1, 5)
                
                # Создаем событие передачи данных
                event = SimulationEvent(
                    event_type=EventType.TRAFFIC_REQUEST,
                    timestamp=self.env.now,
                    source=source,
                    target=target,
                    data_size=data_size,
                    priority=priority
                )
                
                self.env.process(self._handle_traffic_request(event))
            
            # Интервал между запросами (экспоненциальное распределение)
            interval = random.expovariate(1.0)  # 1 запрос в секунду в среднем
            yield self.env.timeout(interval)
    
    def _failure_generator(self):
        """Генератор отказов"""
        while True:
            # Случайные отказы узлов
            if random.random() < 0.001:  # 0.1% вероятность отказа в секунду
                node_id = random.choice(list(self.network_nodes.keys()))
                self.network_nodes[node_id].fail()
                
                event = SimulationEvent(
                    event_type=EventType.NODE_FAILURE,
                    timestamp=self.env.now,
                    source=node_id
                )
                self.add_event(event)
            
            # Случайные отказы каналов
            if random.random() < 0.0005:  # 0.05% вероятность отказа в секунду
                link_id = random.choice(list(self.network_links.keys()))
                self.network_links[link_id].fail()
                
                event = SimulationEvent(
                    event_type=EventType.LINK_FAILURE,
                    timestamp=self.env.now,
                    source=link_id
                )
                self.add_event(event)
            
            yield self.env.timeout(1.0)  # Проверяем каждую секунду
    
    def _recovery_generator(self):
        """Генератор восстановления"""
        while True:
            # Восстановление узлов
            for node_id, node in self.network_nodes.items():
                if node.is_failed and random.random() < 0.01:  # 1% вероятность восстановления
                    node.recover()
                    
                    event = SimulationEvent(
                        event_type=EventType.NODE_RECOVERY,
                        timestamp=self.env.now,
                        source=node_id
                    )
                    self.add_event(event)
            
            # Восстановление каналов
            for link_id, link in self.network_links.items():
                if link.is_failed and random.random() < 0.02:  # 2% вероятность восстановления
                    link.recover()
                    
                    event = SimulationEvent(
                        event_type=EventType.LINK_RECOVERY,
                        timestamp=self.env.now,
                        source=link_id
                    )
                    self.add_event(event)
            
            yield self.env.timeout(10.0)  # Проверяем каждые 10 секунд
    
    def _handle_traffic_request(self, event: SimulationEvent):
        """Обработать запрос трафика"""
        self.metrics['total_requests'] += 1
        
        # Находим путь от источника к цели
        path = self._find_path(event.source, event.target)
        
        if not path:
            self.metrics['failed_requests'] += 1
            return
        
        # Обрабатываем запрос на каждом узле пути
        total_response_time = 0
        
        for node_id in path:
            if node_id in self.network_nodes:
                success, response_time = yield from self.network_nodes[node_id].process_request(
                    event.data_size, event.priority
                )
                
                if not success:
                    self.metrics['failed_requests'] += 1
                    return
                
                total_response_time += response_time
        
        # Передаем данные по каналам
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            link_id = f"{source}_{target}"
            
            if link_id in self.network_links:
                success, transfer_time = yield from self.network_links[link_id].transfer_data(
                    event.data_size, event.priority
                )
                
                if not success:
                    self.metrics['failed_requests'] += 1
                    return
                
                total_response_time += transfer_time
        
        self.metrics['successful_requests'] += 1
    
    def _find_path(self, source: str, target: str) -> List[str]:
        """Найти путь между узлами"""
        try:
            # Используем NetworkX для поиска кратчайшего пути
            path = nx.shortest_path(self.system_model.graph, source, target)
            return path
        except nx.NetworkXNoPath:
            return []
    
    def _metrics_collector(self):
        """Сборщик метрик"""
        while True:
            # Собираем метрики каждые 60 секунд
            self._collect_metrics()
            yield self.env.timeout(60.0)
    
    def _collect_metrics(self):
        """Собрать текущие метрики"""
        # Загрузка узлов
        for node_id, node in self.network_nodes.items():
            self.metrics['node_utilization'][node_id] = {
                'cpu_load': node.node.cpu_load,
                'memory_usage': node.node.memory_usage,
                'queue_length': node.queue_length,
                'processed_requests': node.processed_requests,
                'is_failed': node.is_failed
            }
        
        # Загрузка каналов
        for link_id, link in self.network_links.items():
            self.metrics['link_utilization'][link_id] = {
                'utilization': link.link.utilization,
                'transferred_data': link.transferred_data,
                'is_failed': link.is_failed
            }
    
    def _collect_final_metrics(self):
        """Собрать финальные метрики"""
        # Общие метрики
        if self.metrics['total_requests'] > 0:
            success_rate = self.metrics['successful_requests'] / self.metrics['total_requests']
            self.metrics['success_rate'] = success_rate
        
        # Среднее время отклика
        all_response_times = []
        for node in self.network_nodes.values():
            all_response_times.extend(node.response_times)
        
        if all_response_times:
            self.metrics['average_response_time'] = np.mean(all_response_times)
        
        # Пропускная способность сети
        total_transferred = sum(link.transferred_data for link in self.network_links.values())
        self.metrics['network_throughput'] = total_transferred / self.simulation_duration
    
    def get_simulation_results(self) -> Dict:
        """Получить результаты симуляции"""
        return {
            'metrics': self.metrics,
            'events': self.events,
            'simulation_duration': self.simulation_duration,
            'nodes_count': len(self.network_nodes),
            'links_count': len(self.network_links)
        }
    
    def export_events_to_dataframe(self) -> pd.DataFrame:
        """Экспортировать события в DataFrame"""
        if not self.events:
            return pd.DataFrame()
        
        events_data = []
        for event in self.events:
            events_data.append({
                'timestamp': event.timestamp,
                'event_type': event.event_type.value,
                'source': event.source,
                'target': event.target,
                'data_size': event.data_size,
                'priority': event.priority
            })
        
        return pd.DataFrame(events_data)
    
    def export_metrics_to_dataframe(self) -> pd.DataFrame:
        """Экспортировать метрики в DataFrame"""
        metrics_data = []
        
        # Метрики узлов
        for node_id, node_metrics in self.metrics['node_utilization'].items():
            metrics_data.append({
                'component_type': 'node',
                'component_id': node_id,
                'cpu_load': node_metrics['cpu_load'],
                'memory_usage': node_metrics['memory_usage'],
                'queue_length': node_metrics['queue_length'],
                'processed_requests': node_metrics['processed_requests'],
                'is_failed': node_metrics['is_failed']
            })
        
        # Метрики каналов
        for link_id, link_metrics in self.metrics['link_utilization'].items():
            metrics_data.append({
                'component_type': 'link',
                'component_id': link_id,
                'utilization': link_metrics['utilization'],
                'transferred_data': link_metrics['transferred_data'],
                'is_failed': link_metrics['is_failed']
            })
        
        return pd.DataFrame(metrics_data)


def create_sample_simulation() -> Tuple[SystemModel, NetworkSimulator]:
    """Создать пример симуляции"""
    # Создаем тестовую систему
    system = SystemModel("Тестовая система для симуляции")
    
    # Добавляем узлы
    nodes = [
        Node("server1", "server", 1000, 0.99, 0.3, 0.4),
        Node("server2", "server", 800, 0.98, 0.2, 0.3),
        Node("router1", "router", 500, 0.95, 0.5, 0.6),
        Node("switch1", "switch", 300, 0.97, 0.1, 0.2),
        Node("client1", "client", 100, 0.92, 0.8, 0.7),
        Node("client2", "client", 100, 0.90, 0.6, 0.5),
    ]
    
    for node in nodes:
        system.add_node(node)
    
    # Добавляем каналы
    links = [
        Link("server1", "router1", 100, 5, 0.98, "fiber"),
        Link("server2", "router1", 80, 6, 0.97, "fiber"),
        Link("router1", "switch1", 50, 2, 0.99, "ethernet"),
        Link("switch1", "client1", 10, 1, 0.95, "ethernet"),
        Link("switch1", "client2", 10, 1, 0.94, "ethernet"),
    ]
    
    for link in links:
        system.add_link(link)
    
    # Создаем симулятор
    simulator = NetworkSimulator(system, simulation_duration=300)  # 5 минут
    
    return system, simulator


if __name__ == "__main__":
    # Тестирование модуля
    system, simulator = create_sample_simulation()
    
    print("=== Имитационное моделирование ИКС ===")
    print(f"Система: {system.name}")
    print(f"Узлов: {len(system.nodes)}, Каналов: {len(system.links)}")
    print(f"Длительность симуляции: {simulator.simulation_duration} секунд")
    
    # Запускаем симуляцию
    start_time = time.time()
    simulator.run_simulation()
    simulation_time = time.time() - start_time
    
    print(f"\nСимуляция завершена за {simulation_time:.2f} секунд")
    
    # Получаем результаты
    results = simulator.get_simulation_results()
    metrics = results['metrics']
    
    print(f"\nРезультаты симуляции:")
    print(f"Всего запросов: {metrics['total_requests']}")
    print(f"Успешных запросов: {metrics['successful_requests']}")
    print(f"Неудачных запросов: {metrics['failed_requests']}")
    print(f"Среднее время отклика: {metrics['average_response_time']:.3f} сек")
    print(f"Пропускная способность: {metrics['network_throughput']:.2f} Мбит/сек")
    
    # Экспортируем результаты
    events_df = simulator.export_events_to_dataframe()
    metrics_df = simulator.export_metrics_to_dataframe()
    
    print(f"\nЭкспорт данных:")
    print(f"Событий: {len(events_df)}")
    print(f"Метрик: {len(metrics_df)}")
    
    if not events_df.empty:
        print("\nПервые 5 событий:")
        print(events_df.head())
    
    if not metrics_df.empty:
        print("\nМетрики узлов:")
        node_metrics = metrics_df[metrics_df['component_type'] == 'node']
        print(node_metrics[['component_id', 'cpu_load', 'memory_usage', 'is_failed']].head())
