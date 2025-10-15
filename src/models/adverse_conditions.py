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
    ATTACK = "attack"
    DOS_ATTACK = "dos_attack"
    MALWARE = "malware"
    PHYSICAL_DAMAGE = "physical_damage"
    ENVIRONMENTAL = "environmental"

@dataclass
class AdverseCondition:
    """Неблагоприятное условие"""
    type: AdverseConditionType
    intensity: float  # интенсивность (0-1)
    duration: float  # длительность в секундах
    probability: float  # вероятность возникновения
    affected_nodes: List[int]  # затронутые узлы
    affected_links: List[tuple]  # затронутые связи
    attack_type: Optional[str] = None  # тип атаки (для ATTACK)
    damage_level: float = 0.0  # уровень повреждения (для PHYSICAL_DAMAGE)
    environmental_factor: Optional[str] = None  # фактор среды (для ENVIRONMENTAL)

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
    
    def get_attack_effect(self, node_id: int) -> float:
        """Получает эффект атаки для узла"""
        attack_effect = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.ATTACK and 
                node_id in condition.affected_nodes):
                attack_effect += condition.intensity
        return min(attack_effect, 1.0)
    
    def get_dos_attack_effect(self, node_id: int) -> float:
        """Получает эффект DoS-атаки для узла"""
        dos_effect = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.DOS_ATTACK and 
                node_id in condition.affected_nodes):
                dos_effect += condition.intensity
        return min(dos_effect, 1.0)
    
    def get_malware_effect(self, node_id: int) -> float:
        """Получает эффект вредоносного ПО для узла"""
        malware_effect = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.MALWARE and 
                node_id in condition.affected_nodes):
                malware_effect += condition.intensity
        return min(malware_effect, 1.0)
    
    def get_physical_damage_effect(self, node_id: int) -> float:
        """Получает эффект физического повреждения для узла"""
        damage_effect = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.PHYSICAL_DAMAGE and 
                node_id in condition.affected_nodes):
                damage_effect += condition.damage_level
        return min(damage_effect, 1.0)
    
    def get_environmental_effect(self, node_id: int) -> float:
        """Получает эффект неблагоприятных условий среды"""
        env_effect = 0.0
        for condition in self.active_conditions:
            if (condition.type == AdverseConditionType.ENVIRONMENTAL and 
                node_id in condition.affected_nodes):
                env_effect += condition.intensity
        return min(env_effect, 1.0)
    
    def calculate_comprehensive_degradation(self, node_id: int) -> Dict[str, float]:
        """Рассчитывает комплексную деградацию узла"""
        degradation = {
            'bandwidth_degradation': 0.0,
            'latency_increase': 0.0,
            'reliability_decrease': 0.0,
            'performance_degradation': 0.0,
            'security_impact': 0.0
        }
        
        # Собираем все эффекты
        noise = self.get_noise_effect(node_id)
        interference = self.get_interference_effect(node_id)
        jamming = self.get_jamming_effect(node_id)
        attack = self.get_attack_effect(node_id)
        dos_attack = self.get_dos_attack_effect(node_id)
        malware = self.get_malware_effect(node_id)
        physical_damage = self.get_physical_damage_effect(node_id)
        environmental = self.get_environmental_effect(node_id)
        failure_prob = self.get_failure_probability(node_id)
        overload = self.get_overload_effect(node_id)
        
        # Деградация пропускной способности
        bandwidth_factors = noise + interference + jamming + dos_attack + malware + physical_damage
        degradation['bandwidth_degradation'] = min(bandwidth_factors, 1.0)
        
        # Увеличение задержки
        latency_factors = interference + jamming + dos_attack + overload + physical_damage
        degradation['latency_increase'] = min(latency_factors * 0.5, 1.0)
        
        # Снижение надежности
        reliability_factors = noise + interference + failure_prob + attack + malware + physical_damage
        degradation['reliability_decrease'] = min(reliability_factors * 0.3, 1.0)
        
        # Общая деградация производительности
        performance_factors = (bandwidth_factors + latency_factors + reliability_factors) / 3
        degradation['performance_degradation'] = min(performance_factors, 1.0)
        
        # Воздействие на безопасность
        security_factors = attack + malware + physical_damage + environmental
        degradation['security_impact'] = min(security_factors, 1.0)
        
        return degradation
    
    def simulate_cyber_attack(self, target_nodes: List[int], attack_type: str, intensity: float, duration: float):
        """Симулирует кибератаку"""
        attack_condition = AdverseCondition(
            type=AdverseConditionType.ATTACK,
            intensity=intensity,
            duration=duration,
            probability=0,  # сразу активируется
            affected_nodes=target_nodes,
            affected_links=[],
            attack_type=attack_type
        )
        self.active_conditions.append(attack_condition)
    
    def simulate_dos_attack(self, target_nodes: List[int], intensity: float, duration: float):
        """Симулирует DoS-атаку"""
        dos_condition = AdverseCondition(
            type=AdverseConditionType.DOS_ATTACK,
            intensity=intensity,
            duration=duration,
            probability=0,  # сразу активируется
            affected_nodes=target_nodes,
            affected_links=[]
        )
        self.active_conditions.append(dos_condition)
    
    def simulate_network_overload(self, target_nodes: List[int], intensity: float, duration: float):
        """Симулирует перегрузку сети"""
        overload_condition = AdverseCondition(
            type=AdverseConditionType.OVERLOAD,
            intensity=intensity,
            duration=duration,
            probability=0,  # сразу активируется
            affected_nodes=target_nodes,
            affected_links=[]
        )
        self.active_conditions.append(overload_condition)
    
    def simulate_physical_damage(self, target_nodes: List[int], damage_level: float, duration: float):
        """Симулирует физическое повреждение"""
        damage_condition = AdverseCondition(
            type=AdverseConditionType.PHYSICAL_DAMAGE,
            intensity=damage_level,
            duration=duration,
            probability=0,  # сразу активируется
            affected_nodes=target_nodes,
            affected_links=[],
            damage_level=damage_level
        )
        self.active_conditions.append(damage_condition)
    
    def simulate_environmental_conditions(self, target_nodes: List[int], factor: str, intensity: float, duration: float):
        """Симулирует неблагоприятные условия среды"""
        env_condition = AdverseCondition(
            type=AdverseConditionType.ENVIRONMENTAL,
            intensity=intensity,
            duration=duration,
            probability=0,  # сразу активируется
            affected_nodes=target_nodes,
            affected_links=[],
            environmental_factor=factor
        )
        self.active_conditions.append(env_condition)
    
    def get_threat_level_assessment(self, node_id: int) -> Dict[str, float]:
        """Оценивает уровень угроз для узла"""
        threat_assessment = {
            'cyber_threats': 0.0,
            'physical_threats': 0.0,
            'environmental_threats': 0.0,
            'operational_threats': 0.0,
            'overall_threat_level': 0.0
        }
        
        # Киберугрозы
        cyber_threats = (self.get_attack_effect(node_id) + 
                        self.get_dos_attack_effect(node_id) + 
                        self.get_malware_effect(node_id)) / 3
        threat_assessment['cyber_threats'] = min(cyber_threats, 1.0)
        
        # Физические угрозы
        physical_threats = self.get_physical_damage_effect(node_id)
        threat_assessment['physical_threats'] = min(physical_threats, 1.0)
        
        # Угрозы среды
        environmental_threats = self.get_environmental_effect(node_id)
        threat_assessment['environmental_threats'] = min(environmental_threats, 1.0)
        
        # Операционные угрозы
        operational_threats = (self.get_overload_effect(node_id) + 
                             self.get_failure_probability(node_id)) / 2
        threat_assessment['operational_threats'] = min(operational_threats, 1.0)
        
        # Общий уровень угроз
        threat_assessment['overall_threat_level'] = (
            threat_assessment['cyber_threats'] * 0.4 +
            threat_assessment['physical_threats'] * 0.2 +
            threat_assessment['environmental_threats'] * 0.2 +
            threat_assessment['operational_threats'] * 0.2
        )
        
        return threat_assessment
    
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







