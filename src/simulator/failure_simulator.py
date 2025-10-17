#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Симулятор отказов для ИКС
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class FailureType(Enum):
    """Типы отказов"""
    NODE_FAILURE = "node_failure"
    LINK_FAILURE = "link_failure"
    SOFTWARE_FAILURE = "software_failure"
    HARDWARE_FAILURE = "hardware_failure"
    POWER_FAILURE = "power_failure"

@dataclass
class FailureEvent:
    """Событие отказа"""
    type: FailureType
    node_id: Optional[int] = None
    link_source: Optional[int] = None
    link_target: Optional[int] = None
    severity: float = 1.0  # 0-1, где 1 - полный отказ
    duration: float = 0.0  # 0 - постоянный отказ
    start_time: float = 0.0

class FailureSimulator:
    """Симулятор отказов узлов и связей"""
    
    def __init__(self, network):
        self.network = network
        self.active_failures = []
        self.failure_history = []
        self.current_time = 0.0
        
        # Параметры отказов
        self.node_failure_rate = 0.01  # вероятность отказа узла в секунду
        self.link_failure_rate = 0.02  # вероятность отказа связи в секунду
        self.repair_rate = 0.05  # вероятность восстановления в секунду
    
    def simulate_failures(self, dt: float) -> List[FailureEvent]:
        """Симулирует отказы"""
        new_failures = []
        
        # Симуляция отказов узлов
        for node in self.network.nodes:
            if np.random.random() < self.node_failure_rate * dt:
                failure = self._create_node_failure(node.id)
                if failure:
                    new_failures.append(failure)
                    self.active_failures.append(failure)
        
        # Симуляция отказов связей
        for link in self.network.links[:]:  # копия для безопасного удаления
            if np.random.random() < self.link_failure_rate * dt:
                failure = self._create_link_failure(link.source, link.target)
                if failure:
                    new_failures.append(failure)
                    self.active_failures.append(failure)
        
        # Симуляция восстановления
        self._simulate_repairs(dt)
        
        # Обновление времени
        self.current_time += dt
        
        return new_failures
    
    def _create_node_failure(self, node_id: int) -> Optional[FailureEvent]:
        """Создает отказ узла"""
        # Проверяем, что узел еще не отказал
        for failure in self.active_failures:
            if (failure.type == FailureType.NODE_FAILURE and 
                failure.node_id == node_id):
                return None
        
        severity = np.random.uniform(0.5, 1.0)
        duration = np.random.uniform(0, 60)  # 0-60 секунд (0 = постоянный отказ)
        
        failure = FailureEvent(
            type=FailureType.NODE_FAILURE,
            node_id=node_id,
            severity=severity,
            duration=duration,
            start_time=self.current_time
        )
        
        # Применение отказа к сети
        if severity >= 0.8:
            self.network.apply_failure(node_id)
        
        return failure
    
    def _create_link_failure(self, source: int, target: int) -> Optional[FailureEvent]:
        """Создает отказ связи"""
        # Проверяем, что связь еще не отказала
        for failure in self.active_failures:
            if (failure.type == FailureType.LINK_FAILURE and
                ((failure.link_source == source and failure.link_target == target) or
                 (failure.link_source == target and failure.link_target == source))):
                return None
        
        severity = np.random.uniform(0.5, 1.0)
        duration = np.random.uniform(0, 30)  # 0-30 секунд
        
        failure = FailureEvent(
            type=FailureType.LINK_FAILURE,
            link_source=source,
            link_target=target,
            severity=severity,
            duration=duration,
            start_time=self.current_time
        )
        
        # Применение отказа к сети
        if severity >= 0.8:
            self.network.apply_link_failure(source, target)
        
        return failure
    
    def _simulate_repairs(self, dt: float):
        """Симулирует восстановление после отказов"""
        repaired_failures = []
        
        for failure in self.active_failures:
            # Проверяем, истекло ли время отказа
            if failure.duration > 0 and self.current_time >= failure.start_time + failure.duration:
                repaired_failures.append(failure)
            # Случайное восстановление
            elif np.random.random() < self.repair_rate * dt:
                repaired_failures.append(failure)
        
        # Восстановление отказов
        for failure in repaired_failures:
            self._repair_failure(failure)
            self.active_failures.remove(failure)
            self.failure_history.append(failure)
    
    def _repair_failure(self, failure: FailureEvent):
        """Восстанавливает отказавший элемент"""
        if failure.type == FailureType.NODE_FAILURE:
            # Поиск узла в исходной топологии (упрощенная модель)
            for node in self.network.nodes:
                if node.id == failure.node_id:
                    self.network.restore_node(node)
                    break
        
        elif failure.type == FailureType.LINK_FAILURE:
            # Поиск связи в исходной топологии (упрощенная модель)
            for link in self.network.links:
                if ((link.source == failure.link_source and link.target == failure.link_target) or
                    (link.source == failure.link_target and link.target == failure.link_source)):
                    self.network.restore_link(link)
                    break
    
    def get_failure_statistics(self) -> Dict[str, any]:
        """Возвращает статистику отказов"""
        node_failures = len([f for f in self.failure_history if f.type == FailureType.NODE_FAILURE])
        link_failures = len([f for f in self.failure_history if f.type == FailureType.LINK_FAILURE])
        
        total_failures = node_failures + link_failures
        failure_rate = total_failures / max(self.current_time, 1) if self.current_time > 0 else 0
        
        return {
            'active_failures': len(self.active_failures),
            'total_failures': len(self.failure_history),
            'node_failures': node_failures,
            'link_failures': link_failures,
            'failure_rate': failure_rate,
            'current_time': self.current_time
        }
    
    def get_network_reliability(self) -> float:
        """Вычисляет надежность сети"""
        if not self.network.nodes:
            return 0.0
        
        # Упрощенная модель надежности
        node_reliabilities = [node.reliability for node in self.network.nodes]
        link_reliabilities = [link.reliability for link in self.network.links]
        
        # Учет активных отказов
        for failure in self.active_failures:
            if failure.type == FailureType.NODE_FAILURE:
                # Снижение надежности узла
                for node in self.network.nodes:
                    if node.id == failure.node_id:
                        node.reliability *= (1 - failure.severity)
            elif failure.type == FailureType.LINK_FAILURE:
                # Снижение надежности связи
                for link in self.network.links:
                    if ((link.source == failure.link_source and link.target == failure.link_target) or
                        (link.source == failure.link_target and link.target == failure.link_source)):
                        link.reliability *= (1 - failure.severity)
        
        # Надежность сети = произведение надежностей элементов
        network_reliability = np.prod(node_reliabilities) * np.prod(link_reliabilities)
        
        return network_reliability










