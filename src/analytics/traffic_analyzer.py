#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор трафика ИКС
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TrafficAnalysis:
    """Результат анализа трафика"""
    total_flows: int
    successful_flows: int
    failed_flows: int
    average_flow_duration: float
    average_data_rate: float
    network_utilization: float
    congestion_level: float

class TrafficAnalyzer:
    """Анализатор сетевого трафика"""
    
    def __init__(self):
        self.flow_data = []
    
    def analyze_traffic(self, traffic_data: List[Dict], network_metrics: Dict) -> TrafficAnalysis:
        """Анализирует трафик сети"""
        if not traffic_data:
            return TrafficAnalysis(0, 0, 0, 0, 0, 0, 0)
        
        # Подсчет потоков
        total_flows = len(traffic_data)
        successful_flows = len([f for f in traffic_data if f['degraded_metrics']['reliability'] > 0.5])
        failed_flows = total_flows - successful_flows
        
        # Анализ длительности потоков (упрощенная модель)
        flow_durations = [30.0] * total_flows  # предполагаем среднюю длительность 30 секунд
        average_flow_duration = np.mean(flow_durations)
        
        # Анализ скорости передачи данных
        data_rates = [f['degraded_metrics']['bandwidth'] for f in traffic_data]
        average_data_rate = np.mean(data_rates) if data_rates else 0
        
        # Утилизация сети
        network_utilization = self._calculate_network_utilization(traffic_data, network_metrics)
        
        # Уровень перегрузки
        congestion_level = self._calculate_congestion_level(traffic_data, network_metrics)
        
        return TrafficAnalysis(
            total_flows=total_flows,
            successful_flows=successful_flows,
            failed_flows=failed_flows,
            average_flow_duration=average_flow_duration,
            average_data_rate=average_data_rate,
            network_utilization=network_utilization,
            congestion_level=congestion_level
        )
    
    def _calculate_network_utilization(self, traffic_data: List[Dict], network_metrics: Dict) -> float:
        """Вычисляет утилизацию сети"""
        if not traffic_data or not network_metrics:
            return 0.0
        
        # Общая пропускная способность сети
        total_capacity = sum(link['bandwidth'] for link in network_metrics.get('active_connections', []))
        
        # Используемая пропускная способность
        used_capacity = sum(f['degraded_metrics']['bandwidth'] for f in traffic_data)
        
        if total_capacity == 0:
            return 0.0
        
        return min(used_capacity / total_capacity, 1.0)
    
    def _calculate_congestion_level(self, traffic_data: List[Dict], network_metrics: Dict) -> float:
        """Вычисляет уровень перегрузки сети"""
        if not traffic_data:
            return 0.0
        
        # Анализ потери пакетов
        packet_losses = [1 - f['degraded_metrics']['reliability'] for f in traffic_data]
        average_packet_loss = np.mean(packet_losses)
        
        # Анализ задержек
        latencies = [f['degraded_metrics']['latency'] for f in traffic_data]
        average_latency = np.mean(latencies) if latencies else 0
        
        # Уровень перегрузки на основе потери пакетов и задержки
        congestion_from_loss = min(average_packet_loss * 10, 1.0)  # нормализация
        congestion_from_latency = min(average_latency / 100, 1.0)  # нормализация к 100 мс
        
        return (congestion_from_loss + congestion_from_latency) / 2








