#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модели неблагоприятных условий для ИКС
"""

import numpy as np
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum

class AdverseConditionType(Enum):
    """Типы неблагоприятных условий"""
    NOISE = "noise"
    INTERFERENCE = "interference"
    JAMMING = "jamming"
    FADING = "fading"
    MULTIPATH = "multipath"
    FAILURE = "failure"
    OVERLOAD = "overload"

@dataclass
class AdverseCondition:
    """Неблагоприятное условие"""
    type: AdverseConditionType
    intensity: float  # интенсивность (0-1)
    duration: float  # длительность в секундах
    probability: float  # вероятность возникновения
    affected_nodes: List[int]  # затронутые узлы
    affected_links: List[tuple]  # затронутые связи

class AdverseConditions:
    """Класс для моделирования неблагоприятных условий"""
    
    def __init__(self):
        self.conditions = []
        self.active_conditions = []
        self.time = 0.0
    
    def add_condition(self, condition: AdverseCondition):
        """Добавляет неблагоприятное условие"""
        self.conditions.append(condition)
    
    def update(self, dt: float):
        """Обновляет состояние неблагоприятных условий"""
        self.time += dt
        
        # Проверяем возникновение новых условий
        for condition in self.conditions:
            if np.random.random() < condition.probability * dt:
                self._activate_condition(condition)
        
        # Обновляем активные условия
        self.active_conditions = [
            cond for cond in self.active_conditions 
            if cond.duration > 0
        ]
        
        # Уменьшаем длительность активных условий
        for condition in self.active_conditions:
            condition.duration -= dt
    
    def _activate_condition(self, condition: AdverseCondition):
        """Активирует неблагоприятное условие"""
        active_condition = AdverseCondition(
            type=condition.type,
            intensity=condition.intensity,
            duration=condition.duration,
            probability=0,  # уже активировано
            affected_nodes=condition.affected_nodes.copy(),
            affected_links=condition.affected_links.copy()
        )
        self.active_conditions.append(active_condition)
    
    def get_noise_effect(self, node_id: int) -> float:
        """Получает эффект шума для узла"""
        noise_level = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.NOISE and 
                node_id in condition.affected_nodes):
                noise_level += condition.intensity
        return min(noise_level, 1.0)
    
    def get_interference_effect(self, node_id: int) -> float:
        """Получает эффект помех для узла"""
        interference = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.INTERFERENCE and 
                node_id in condition.affected_nodes):
                interference += condition.intensity
        return min(interference, 1.0)
    
    def get_jamming_effect(self, node_id: int) -> float:
        """Получает эффект глушения для узла"""
        jamming = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.JAMMING and 
                node_id in condition.affected_nodes):
                jamming += condition.intensity
        return min(jamming, 1.0)
    
    def get_fading_effect(self, link: tuple) -> float:
        """Получает эффект замирания для связи"""
        fading = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.FADING and 
                link in condition.affected_links):
                fading += condition.intensity
        return min(fading, 1.0)
    
    def get_multipath_effect(self, link: tuple) -> float:
        """Получает эффект многолучевости для связи"""
        multipath = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.MULTIPATH and 
                link in condition.affected_links):
                multipath += condition.intensity
        return min(multipath, 1.0)
    
    def get_failure_probability(self, node_id: int) -> float:
        """Получает вероятность отказа узла"""
        failure_prob = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.FAILURE and 
                node_id in condition.affected_nodes):
                failure_prob += condition.intensity
        return min(failure_prob, 1.0)
    
    def get_overload_effect(self, node_id: int) -> float:
        """Получает эффект перегрузки для узла"""
        overload = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.OVERLOAD and 
                node_id in condition.affected_nodes):
                overload += condition.intensity
        return min(overload, 1.0)
    
    def calculate_degraded_bandwidth(self, original_bandwidth: float, 
                                   noise_effect: float, interference_effect: float,
                                   jamming_effect: float) -> float:
        """Вычисляет деградированную пропускную способность"""
        degradation = noise_effect + interference_effect + jamming_effect
        return original_bandwidth * (1 - degradation)
    
    def calculate_degraded_latency(self, original_latency: float,
                                 fading_effect: float, multipath_effect: float,
                                 overload_effect: float) -> float:
        """Вычисляет деградированную задержку"""
        latency_increase = fading_effect * 0.5 + multipath_effect * 0.3 + overload_effect * 0.2
        return original_latency * (1 + latency_increase)
    
    def calculate_degraded_reliability(self, original_reliability: float,
                                     noise_effect: float, interference_effect: float,
                                     failure_prob: float) -> float:
        """Вычисляет деградированную надежность"""
        reliability_decrease = (noise_effect * 0.3 + 
                              interference_effect * 0.4 + 
                              failure_prob * 0.3)
        return max(0.0, original_reliability - reliability_decrease)
    
    def get_active_conditions_summary(self) -> Dict[str, int]:
        """Получает сводку активных условий"""
        summary = {}
        for condition_type in AdverseConditionType:
            summary[condition_type.value] = len([
                cond for cond in self.active_conditions 
                if cond.type == condition_type
            ])
        return summary
    
    def clear_conditions(self):
        """Очищает все условия"""
        self.conditions.clear()
        self.active_conditions.clear()
        self.time = 0.0





