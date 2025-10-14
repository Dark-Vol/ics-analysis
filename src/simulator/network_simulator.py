#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной симулятор сети ИКС
"""

import numpy as np
import threading
import time
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass

from ..models.network_model import NetworkModel
from ..models.adverse_conditions import AdverseConditions, AdverseCondition, AdverseConditionType
from ..models.performance_metrics import PerformanceMetrics, MetricsSnapshot

@dataclass
class SimulationConfig:
    """Конфигурация симуляции"""
    duration: float = 100.0  # секунды
    time_step: float = 0.1  # секунды
    random_seed: int = 42
    enable_traffic: bool = True
    enable_failures: bool = True
    enable_adverse_conditions: bool = True

class NetworkSimulator:
    """Основной класс симулятора сети"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.network = None
        self.adverse_conditions = AdverseConditions()
        self.performance_metrics = PerformanceMetrics()
        
        # Состояние симуляции
        self.is_running = False
        self.is_paused = False
        self.current_time = 0.0
        self.simulation_thread = None
        
        # Обратные вызовы
        self.update_callbacks = []
        self.finish_callbacks = []
        
        # Данные симуляции
        self.traffic_data = []
        self.failure_events = []
        self.network_state_history = []
        
        # Установка seed для воспроизводимости
        np.random.seed(config.random_seed)
    
    def initialize_network(self, nodes: int = 10, connection_probability: float = 0.3):
        """Инициализирует сеть"""
        self.network = NetworkModel(nodes, connection_probability)
        self.adverse_conditions.clear_conditions()
        self.performance_metrics.reset_metrics()
        self.current_time = 0.0
        self.traffic_data.clear()
        self.failure_events.clear()
        self.network_state_history.clear()
    
    def add_adverse_condition(self, condition: AdverseCondition):
        """Добавляет неблагоприятное условие"""
        self.adverse_conditions.add_condition(condition)
    
    def add_update_callback(self, callback: Callable):
        """Добавляет callback для обновления"""
        self.update_callbacks.append(callback)
    
    def add_finish_callback(self, callback: Callable):
        """Добавляет callback для завершения"""
        self.finish_callbacks.append(callback)
    
    def start_simulation(self):
        """Запускает симуляцию"""
        if self.is_running:
            return
        
        if not self.network:
            raise ValueError("Сеть не инициализирована")
        
        self.is_running = True
        self.is_paused = False
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def pause_simulation(self):
        """Приостанавливает симуляцию"""
        self.is_paused = True
    
    def resume_simulation(self):
        """Возобновляет симуляцию"""
        self.is_paused = False
    
    def stop_simulation(self):
        """Останавливает симуляцию"""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=1.0)
    
    def _simulation_loop(self):
        """Основной цикл симуляции"""
        start_time = time.time()
        
        while self.is_running and self.current_time < self.config.duration:
            if self.is_paused:
                time.sleep(0.01)
                continue
            
            # Обновление неблагоприятных условий
            if self.config.enable_adverse_conditions:
                self.adverse_conditions.update(self.config.time_step)
            
            # Симуляция трафика
            if self.config.enable_traffic:
                self._simulate_traffic()
            
            # Симуляция отказов
            if self.config.enable_failures:
                self._simulate_failures()
            
            # Обновление метрик
            self._update_metrics()
            
            # Сохранение состояния
            self._save_network_state()
            
            # Вызов callbacks
            self._notify_update()
            
            # Обновление времени
            self.current_time += self.config.time_step
            
            # Контроль скорости симуляции
            elapsed_real_time = time.time() - start_time
            target_time = self.current_time
            if elapsed_real_time < target_time:
                time.sleep(target_time - elapsed_real_time)
    
        # Завершение симуляции
        self.is_running = False
        self._notify_finish()
    
    def _simulate_traffic(self):
        """Симулирует сетевой трафик"""
        if not self.network:
            return
        
        # Генерация трафика между случайными узлами
        if np.random.random() < 0.1:  # 10% вероятность генерации трафика
            available_nodes = [node.id for node in self.network.nodes]
            if len(available_nodes) >= 2:
                source = np.random.choice(available_nodes)
                target = np.random.choice([n for n in available_nodes if n != source])
                
                # Поиск пути
                path = self.network.calculate_shortest_path(source, target)
                if path:
                    path_metrics = self.network.calculate_path_metrics(path)
                    
                    # Применение неблагоприятных условий
                    degraded_metrics = self._apply_adverse_conditions_to_path(path_metrics, path)
                    
                    # Сохранение данных трафика
                    traffic_event = {
                        'timestamp': self.current_time,
                        'source': source,
                        'target': target,
                        'path': path,
                        'original_metrics': path_metrics,
                        'degraded_metrics': degraded_metrics
                    }
                    self.traffic_data.append(traffic_event)
    
    def _simulate_failures(self):
        """Симулирует отказы узлов и связей"""
        if not self.network:
            return
        
        # Отказы узлов
        for node in self.network.nodes:
            failure_prob = self.adverse_conditions.get_failure_probability(node.id)
            if np.random.random() < failure_prob * self.config.time_step:
                self.network.apply_failure(node.id)
                self.failure_events.append({
                    'timestamp': self.current_time,
                    'type': 'node_failure',
                    'node_id': node.id
                })
        
        # Отказы связей
        for link in self.network.links[:]:  # копия списка для безопасного удаления
            # Упрощенная модель отказа связи
            failure_prob = 0.01 * self.config.time_step  # 1% вероятность в секунду
            if np.random.random() < failure_prob:
                self.network.apply_link_failure(link.source, link.target)
                self.failure_events.append({
                    'timestamp': self.current_time,
                    'type': 'link_failure',
                    'source': link.source,
                    'target': link.target
                })
    
    def _apply_adverse_conditions_to_path(self, path_metrics: Dict, path: List[int]) -> Dict:
        """Применяет неблагоприятные условия к пути"""
        degraded_metrics = path_metrics.copy()
        
        # Деградация пропускной способности
        for node_id in path:
            noise_effect = self.adverse_conditions.get_noise_effect(node_id)
            interference_effect = self.adverse_conditions.get_interference_effect(node_id)
            jamming_effect = self.adverse_conditions.get_jamming_effect(node_id)
            
            degraded_bandwidth = self.adverse_conditions.calculate_degraded_bandwidth(
                path_metrics['bandwidth'], noise_effect, interference_effect, jamming_effect
            )
            degraded_metrics['bandwidth'] = min(degraded_metrics['bandwidth'], degraded_bandwidth)
        
        # Деградация задержки
        for i in range(len(path) - 1):
            link = (path[i], path[i + 1])
            fading_effect = self.adverse_conditions.get_fading_effect(link)
            multipath_effect = self.adverse_conditions.get_multipath_effect(link)
            overload_effect = self.adverse_conditions.get_overload_effect(path[i])
            
            degraded_latency = self.adverse_conditions.calculate_degraded_latency(
                path_metrics['latency'], fading_effect, multipath_effect, overload_effect
            )
            degraded_metrics['latency'] += degraded_latency - path_metrics['latency']
        
        # Деградация надежности
        total_noise = sum(self.adverse_conditions.get_noise_effect(node_id) for node_id in path)
        total_interference = sum(self.adverse_conditions.get_interference_effect(node_id) for node_id in path)
        total_failure_prob = sum(self.adverse_conditions.get_failure_probability(node_id) for node_id in path)
        
        degraded_reliability = self.adverse_conditions.calculate_degraded_reliability(
            path_metrics['reliability'], total_noise, total_interference, total_failure_prob
        )
        degraded_metrics['reliability'] = degraded_reliability
        
        return degraded_metrics
    
    def _update_metrics(self):
        """Обновляет метрики производительности"""
        if not self.network:
            return
        
        # Подготовка состояния сети
        network_state = self._get_current_network_state()
        
        # Обновление метрик
        self.performance_metrics.update_metrics(self.current_time, network_state)
    
    def _get_current_network_state(self) -> Dict:
        """Получает текущее состояние сети"""
        if not self.network:
            return {}
        
        # Подсчет активных соединений
        active_connections = []
        total_bandwidth = 0
        
        for link in self.network.links:
            bandwidth = link.bandwidth
            utilization = np.random.uniform(0.3, 0.8)  # случайная утилизация
            total_bandwidth += bandwidth * utilization
            
            active_connections.append({
                'bandwidth': bandwidth,
                'utilization': utilization,
                'source': link.source,
                'target': link.target
            })
        
        # Расчет задержек
        latencies = [link.latency for link in self.network.links]
        
        # Надежности узлов
        node_reliabilities = [node.reliability for node in self.network.nodes]
        
        # Статистика узлов
        active_nodes = len(self.network.nodes)
        total_nodes = len(self.network.nodes) + len([e for e in self.failure_events if e['type'] == 'node_failure'])
        
        return {
            'active_connections': active_connections,
            'latencies': latencies,
            'node_reliabilities': node_reliabilities,
            'active_nodes': active_nodes,
            'total_nodes': total_nodes,
            'packets_sent': len(self.traffic_data),
            'packets_received': len([t for t in self.traffic_data if t['degraded_metrics']['reliability'] > 0.5]),
            'data_transferred': total_bandwidth * self.config.time_step,
            'energy_consumed': active_nodes * 10 * self.config.time_step  # упрощенная модель
        }
    
    def _save_network_state(self):
        """Сохраняет текущее состояние сети"""
        state = {
            'timestamp': self.current_time,
            'nodes': len(self.network.nodes) if self.network else 0,
            'links': len(self.network.links) if self.network else 0,
            'active_conditions': len(self.adverse_conditions.active_conditions),
            'metrics': self.performance_metrics.current_metrics
        }
        self.network_state_history.append(state)
    
    def _notify_update(self):
        """Уведомляет об обновлении"""
        for callback in self.update_callbacks:
            try:
                callback(self.current_time, self.performance_metrics.current_metrics)
            except Exception as e:
                print(f"Ошибка в callback обновления: {e}")
    
    def _notify_finish(self):
        """Уведомляет о завершении"""
        for callback in self.finish_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Ошибка в callback завершения: {e}")
    
    def get_simulation_results(self) -> Dict[str, Any]:
        """Получает результаты симуляции"""
        return {
            'duration': self.current_time,
            'traffic_events': len(self.traffic_data),
            'failure_events': len(self.failure_events),
            'network_metrics': self.performance_metrics.get_average_metrics(),
            'quality_score': self.performance_metrics.get_quality_score(),
            'adverse_conditions_summary': self.adverse_conditions.get_active_conditions_summary(),
            'network_topology': self.network.get_network_metrics() if self.network else {}
        }
    
    def get_metrics_history(self) -> List[MetricsSnapshot]:
        """Получает историю метрик"""
        return list(self.performance_metrics.metrics_history)
    
    def get_traffic_data(self) -> List[Dict]:
        """Получает данные трафика"""
        return self.traffic_data.copy()
    
    def get_failure_events(self) -> List[Dict]:
        """Получает события отказов"""
        return self.failure_events.copy()





