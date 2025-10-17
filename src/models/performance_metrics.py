#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Метрики производительности для анализа ИКС
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
import statistics

@dataclass
class MetricsSnapshot:
    """Снимок метрик в определенный момент времени"""
    timestamp: float
    throughput: float  # Мбит/с
    latency: float  # мс
    reliability: float  # 0-1
    availability: float  # 0-1
    packet_loss: float  # 0-1
    jitter: float  # мс
    energy_efficiency: float  # Мбит/с/Вт

class PerformanceMetrics:
    """Класс для расчета и хранения метрик производительности"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history = deque(maxlen=history_size)
        self.current_metrics = MetricsSnapshot(0, 0, 0, 0, 0, 0, 0, 0)
        
        # Статистика
        self.total_packets_sent = 0
        self.total_packets_received = 0
        self.total_bytes_transferred = 0
        self.total_energy_consumed = 0
        
        # Временные метрики
        self.connection_uptime = 0.0
        self.last_update_time = 0.0
        
    def update_metrics(self, timestamp: float, network_state: Dict):
        """Обновляет метрики на основе текущего состояния сети"""
        self.last_update_time = timestamp
        
        # Расчет пропускной способности
        throughput = self._calculate_throughput(network_state)
        
        # Расчет задержки
        latency = self._calculate_latency(network_state)
        
        # Расчет надежности
        reliability = self._calculate_reliability(network_state)
        
        # Расчет доступности
        availability = self._calculate_availability(network_state)
        
        # Расчет потери пакетов
        packet_loss = self._calculate_packet_loss(network_state)
        
        # Расчет джиттера
        jitter = self._calculate_jitter(network_state)
        
        # Расчет энергетической эффективности
        energy_efficiency = self._calculate_energy_efficiency(network_state)
        
        # Создание снимка метрик
        self.current_metrics = MetricsSnapshot(
            timestamp=timestamp,
            throughput=throughput,
            latency=latency,
            reliability=reliability,
            availability=availability,
            packet_loss=packet_loss,
            jitter=jitter,
            energy_efficiency=energy_efficiency
        )
        
        # Добавление в историю
        self.metrics_history.append(self.current_metrics)
    
    def _calculate_throughput(self, network_state: Dict) -> float:
        """Вычисляет пропускную способность"""
        if 'active_connections' not in network_state:
            return 0.0
        
        total_throughput = 0.0
        for connection in network_state['active_connections']:
            bandwidth = connection.get('bandwidth', 0)
            utilization = connection.get('utilization', 0.5)
            total_throughput += bandwidth * utilization
        
        return total_throughput
    
    def _calculate_latency(self, network_state: Dict) -> float:
        """Вычисляет среднюю задержку"""
        if 'latencies' not in network_state or not network_state['latencies']:
            return 0.0
        
        latencies = network_state['latencies']
        return statistics.mean(latencies) if latencies else 0.0
    
    def _calculate_reliability(self, network_state: Dict) -> float:
        """Вычисляет надежность сети"""
        if 'node_reliabilities' not in network_state:
            return 1.0
        
        reliabilities = network_state['node_reliabilities']
        if not reliabilities:
            return 1.0
        
        # Надежность сети = произведение надежностей узлов
        return np.prod(reliabilities)
    
    def _calculate_availability(self, network_state: Dict) -> float:
        """Вычисляет доступность сети"""
        if 'active_nodes' not in network_state or 'total_nodes' not in network_state:
            return 1.0
        
        active_nodes = network_state['active_nodes']
        total_nodes = network_state['total_nodes']
        
        if total_nodes == 0:
            return 0.0
        
        return active_nodes / total_nodes
    
    def _calculate_packet_loss(self, network_state: Dict) -> float:
        """Вычисляет потерю пакетов"""
        if 'packets_sent' not in network_state or 'packets_received' not in network_state:
            return 0.0
        
        packets_sent = network_state['packets_sent']
        packets_received = network_state['packets_received']
        
        if packets_sent == 0:
            return 0.0
        
        return (packets_sent - packets_received) / packets_sent
    
    def _calculate_jitter(self, network_state: Dict) -> float:
        """Вычисляет джиттер (вариацию задержки)"""
        if 'latencies' not in network_state or len(network_state['latencies']) < 2:
            return 0.0
        
        latencies = network_state['latencies']
        return statistics.stdev(latencies) if len(latencies) > 1 else 0.0
    
    def _calculate_energy_efficiency(self, network_state: Dict) -> float:
        """Вычисляет энергетическую эффективность"""
        if 'energy_consumed' not in network_state or 'data_transferred' not in network_state:
            return 0.0
        
        energy_consumed = network_state['energy_consumed']
        data_transferred = network_state['data_transferred']
        
        if energy_consumed == 0:
            return 0.0
        
        return data_transferred / energy_consumed
    
    def get_average_metrics(self, time_window: Optional[float] = None) -> Dict[str, float]:
        """Получает средние метрики за временное окно"""
        if not self.metrics_history:
            return {}
        
        # Фильтрация по временному окну
        if time_window:
            cutoff_time = self.last_update_time - time_window
            filtered_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
        else:
            filtered_metrics = list(self.metrics_history)
        
        if not filtered_metrics:
            return {}
        
        return {
            'throughput': statistics.mean([m.throughput for m in filtered_metrics]),
            'latency': statistics.mean([m.latency for m in filtered_metrics]),
            'reliability': statistics.mean([m.reliability for m in filtered_metrics]),
            'availability': statistics.mean([m.availability for m in filtered_metrics]),
            'packet_loss': statistics.mean([m.packet_loss for m in filtered_metrics]),
            'jitter': statistics.mean([m.jitter for m in filtered_metrics]),
            'energy_efficiency': statistics.mean([m.energy_efficiency for m in filtered_metrics])
        }
    
    def get_metric_statistics(self, metric_name: str, time_window: Optional[float] = None) -> Dict[str, float]:
        """Получает статистику для конкретной метрики"""
        if not self.metrics_history:
            return {}
        
        # Фильтрация по временному окну
        if time_window:
            cutoff_time = self.last_update_time - time_window
            filtered_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
        else:
            filtered_metrics = list(self.metrics_history)
        
        if not filtered_metrics:
            return {}
        
        # Получение значений метрики
        values = [getattr(m, metric_name) for m in filtered_metrics if hasattr(m, metric_name)]
        
        if not values:
            return {}
        
        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0.0,
            'min': min(values),
            'max': max(values),
            'q25': np.percentile(values, 25),
            'q75': np.percentile(values, 75)
        }
    
    def get_quality_score(self) -> float:
        """Вычисляет общий показатель качества сети"""
        if not self.metrics_history:
            return 0.0
        
        latest = self.metrics_history[-1]
        
        # Нормализованные веса для метрик
        weights = {
            'throughput': 0.2,
            'latency': 0.2,
            'reliability': 0.25,
            'availability': 0.25,
            'packet_loss': 0.05,
            'jitter': 0.05
        }
        
        # Нормализация метрик (чем больше, тем лучше)
        throughput_score = min(latest.throughput / 1000, 1.0)  # нормализация к 1 Гбит/с
        latency_score = max(0, 1 - latest.latency / 100)  # нормализация к 100 мс
        reliability_score = latest.reliability
        availability_score = latest.availability
        packet_loss_score = max(0, 1 - latest.packet_loss)
        jitter_score = max(0, 1 - latest.jitter / 50)  # нормализация к 50 мс
        
        # Взвешенная сумма
        quality_score = (
            weights['throughput'] * throughput_score +
            weights['latency'] * latency_score +
            weights['reliability'] * reliability_score +
            weights['availability'] * availability_score +
            weights['packet_loss'] * packet_loss_score +
            weights['jitter'] * jitter_score
        )
        
        return quality_score
    
    def reset_metrics(self):
        """Сбрасывает все метрики"""
        self.metrics_history.clear()
        self.current_metrics = MetricsSnapshot(0, 0, 0, 0, 0, 0, 0, 0)
        self.total_packets_sent = 0
        self.total_packets_received = 0
        self.total_bytes_transferred = 0
        self.total_energy_consumed = 0
        self.connection_uptime = 0.0
        self.last_update_time = 0.0










