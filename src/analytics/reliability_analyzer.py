#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор надежности ИКС
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ReliabilityMetrics:
    """Метрики надежности"""
    mttf: float  # Mean Time To Failure - среднее время до отказа
    mttr: float  # Mean Time To Repair - среднее время восстановления
    availability: float  # доступность
    reliability: float  # надежность
    failure_rate: float  # интенсивность отказов

class ReliabilityAnalyzer:
    """Анализатор надежности сети"""
    
    def __init__(self):
        self.failure_events = []
        self.repair_events = []
    
    def analyze_reliability(self, network_metrics: Dict, failure_events: List) -> ReliabilityMetrics:
        """Анализирует надежность сети"""
        # Расчет MTTF (среднее время до отказа)
        mttf = self._calculate_mttf(failure_events)
        
        # Расчет MTTR (среднее время восстановления)
        mttr = self._calculate_mttr(failure_events)
        
        # Расчет доступности
        availability = self._calculate_availability(network_metrics)
        
        # Расчет надежности
        reliability = self._calculate_reliability(network_metrics)
        
        # Расчет интенсивности отказов
        failure_rate = self._calculate_failure_rate(failure_events)
        
        return ReliabilityMetrics(
            mttf=mttf,
            mttr=mttr,
            availability=availability,
            reliability=reliability,
            failure_rate=failure_rate
        )
    
    def _calculate_mttf(self, failure_events: List) -> float:
        """Вычисляет среднее время до отказа"""
        if not failure_events:
            return float('inf')
        
        # Группировка отказов по элементам
        element_failures = {}
        
        for event in failure_events:
            if event['type'] == 'node_failure':
                element_id = f"node_{event['node_id']}"
            elif event['type'] == 'link_failure':
                element_id = f"link_{event['source']}_{event['target']}"
            else:
                continue
            
            if element_id not in element_failures:
                element_failures[element_id] = []
            
            element_failures[element_id].append(event['timestamp'])
        
        # Расчет времени между отказами для каждого элемента
        times_to_failure = []
        
        for element_id, timestamps in element_failures.items():
            if len(timestamps) > 1:
                timestamps.sort()
                for i in range(1, len(timestamps)):
                    time_to_failure = timestamps[i] - timestamps[i-1]
                    times_to_failure.append(time_to_failure)
        
        return np.mean(times_to_failure) if times_to_failure else float('inf')
    
    def _calculate_mttr(self, failure_events: List) -> float:
        """Вычисляет среднее время восстановления"""
        # Упрощенная модель - предполагаем, что восстановление происходит мгновенно
        # В реальной системе здесь был бы анализ событий восстановления
        return 10.0  # секунды
    
    def _calculate_availability(self, network_metrics: Dict) -> float:
        """Вычисляет доступность сети"""
        active_nodes = network_metrics.get('active_nodes', 0)
        total_nodes = network_metrics.get('total_nodes', 1)
        
        if total_nodes == 0:
            return 0.0
        
        return active_nodes / total_nodes
    
    def _calculate_reliability(self, network_metrics: Dict) -> float:
        """Вычисляет надежность сети"""
        # Получение надежностей узлов и связей
        node_reliabilities = network_metrics.get('node_reliabilities', [])
        link_reliabilities = network_metrics.get('link_reliabilities', [])
        
        if not node_reliabilities and not link_reliabilities:
            return 1.0
        
        # Надежность сети = произведение надежностей элементов
        network_reliability = 1.0
        
        for reliability in node_reliabilities:
            network_reliability *= reliability
        
        for reliability in link_reliabilities:
            network_reliability *= reliability
        
        return network_reliability
    
    def _calculate_failure_rate(self, failure_events: List) -> float:
        """Вычисляет интенсивность отказов"""
        if not failure_events:
            return 0.0
        
        # Группировка по времени
        time_intervals = {}
        for event in failure_events:
            time_bucket = int(event['timestamp'] // 10)  # 10-секундные интервалы
            if time_bucket not in time_intervals:
                time_intervals[time_bucket] = 0
            time_intervals[time_bucket] += 1
        
        # Расчет средней интенсивности отказов
        total_failures = len(failure_events)
        total_time = max(time_intervals.keys()) * 10 if time_intervals else 1
        
        return total_failures / total_time if total_time > 0 else 0.0





