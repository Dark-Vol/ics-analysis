#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор трафика для симуляции ИКС
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TrafficFlow:
    """Поток трафика"""
    source: int
    destination: int
    data_rate: float  # Мбит/с
    priority: int  # 1-5 (1 - высший приоритет)
    duration: float  # секунды
    start_time: float
    end_time: float

class TrafficGenerator:
    """Генератор сетевого трафика"""
    
    def __init__(self, network):
        self.network = network
        self.active_flows = []
        self.completed_flows = []
        self.current_time = 0.0
        
        # Статистика
        self.total_packets_sent = 0
        self.total_packets_received = 0
        self.total_bytes_transferred = 0
    
    def generate_traffic(self, dt: float) -> List[TrafficFlow]:
        """Генерирует новый трафик"""
        new_flows = []
        
        # Вероятность генерации нового потока
        flow_probability = 0.1 * dt  # 10% вероятность в секунду
        
        if np.random.random() < flow_probability:
            flow = self._create_random_flow()
            if flow:
                new_flows.append(flow)
                self.active_flows.append(flow)
        
        # Обновление времени
        self.current_time += dt
        
        # Удаление завершенных потоков
        self._cleanup_completed_flows()
        
        return new_flows
    
    def _create_random_flow(self) -> Optional[TrafficFlow]:
        """Создает случайный поток трафика"""
        if len(self.network.nodes) < 2:
            return None
        
        # Выбор случайных узлов
        available_nodes = [node.id for node in self.network.nodes]
        source = np.random.choice(available_nodes)
        destination = np.random.choice([n for n in available_nodes if n != source])
        
        # Проверка наличия пути
        path = self.network.calculate_shortest_path(source, destination)
        if not path:
            return None
        
        # Параметры потока
        data_rate = np.random.uniform(1, 50)  # Мбит/с
        priority = np.random.randint(1, 6)
        duration = np.random.uniform(5, 30)  # секунды
        
        flow = TrafficFlow(
            source=source,
            destination=destination,
            data_rate=data_rate,
            priority=priority,
            duration=duration,
            start_time=self.current_time,
            end_time=self.current_time + duration
        )
        
        return flow
    
    def _cleanup_completed_flows(self):
        """Удаляет завершенные потоки"""
        completed = []
        for flow in self.active_flows:
            if self.current_time >= flow.end_time:
                completed.append(flow)
                self.completed_flows.append(flow)
        
        for flow in completed:
            self.active_flows.remove(flow)
    
    def get_network_load(self) -> Dict[str, float]:
        """Возвращает нагрузку на сеть"""
        total_load = sum(flow.data_rate for flow in self.active_flows)
        max_capacity = sum(link.bandwidth for link in self.network.links)
        
        return {
            'total_load': total_load,
            'max_capacity': max_capacity,
            'utilization': total_load / max_capacity if max_capacity > 0 else 0
        }
    
    def get_traffic_statistics(self) -> Dict[str, int]:
        """Возвращает статистику трафика"""
        return {
            'active_flows': len(self.active_flows),
            'completed_flows': len(self.completed_flows),
            'total_packets_sent': self.total_packets_sent,
            'total_packets_received': self.total_packets_received,
            'total_bytes_transferred': self.total_bytes_transferred
        }





