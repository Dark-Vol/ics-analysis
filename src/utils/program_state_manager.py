#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер состояния программы для управления выполнением
"""

import time
from enum import Enum
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime

class ProgramState(Enum):
    """Состояния программы"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class ActionLog:
    """Запись о действии в программе"""
    timestamp: datetime
    action: str
    details: str = ""
    network_id: Optional[int] = None
    network_name: Optional[str] = None

@dataclass
class ProgramMetrics:
    """Метрики программы"""
    total_networks_created: int = 0
    total_networks_deleted: int = 0
    total_simulations_run: int = 0
    total_runtime_seconds: float = 0.0
    pause_count: int = 0
    last_action_time: Optional[datetime] = None
    current_network_id: Optional[int] = None
    current_network_name: Optional[str] = None

class ProgramStateManager:
    """Менеджер состояния программы"""
    
    def __init__(self):
        self.state = ProgramState.STOPPED
        self.start_time: Optional[datetime] = None
        self.pause_start_time: Optional[datetime] = None
        self.total_pause_time = 0.0
        self.metrics = ProgramMetrics()
        self.action_log: List[ActionLog] = []
        self.state_change_callbacks: List[Callable] = []
        
    def add_state_change_callback(self, callback: Callable):
        """Добавляет callback для изменения состояния"""
        self.state_change_callbacks.append(callback)
    
    def _notify_state_change(self):
        """Уведомляет о изменении состояния"""
        for callback in self.state_change_callbacks:
            try:
                callback(self.state, self.get_status_info())
            except Exception as e:
                print(f"[ERROR] Ошибка в callback изменения состояния: {e}")
    
    def start_program(self):
        """Запускает программу"""
        if self.state == ProgramState.STOPPED:
            self.state = ProgramState.RUNNING
            self.start_time = datetime.now()
            self.total_pause_time = 0.0
            self._log_action("Программа запущена", "Программа успешно запущена")
            self._notify_state_change()
            return True
        return False
    
    def pause_program(self):
        """Приостанавливает программу"""
        if self.state == ProgramState.RUNNING:
            self.state = ProgramState.PAUSED
            self.pause_start_time = datetime.now()
            self.metrics.pause_count += 1
            self._log_action("Программа приостановлена", "Программа временно приостановлена")
            self._notify_state_change()
            return True
        return False
    
    def resume_program(self):
        """Возобновляет выполнение программы"""
        if self.state == ProgramState.PAUSED:
            self.state = ProgramState.RUNNING
            if self.pause_start_time:
                pause_duration = (datetime.now() - self.pause_start_time).total_seconds()
                self.total_pause_time += pause_duration
                self.pause_start_time = None
            self._log_action("Программа возобновлена", "Программа продолжает выполнение")
            self._notify_state_change()
            return True
        return False
    
    def stop_program(self):
        """Останавливает программу"""
        if self.state in [ProgramState.RUNNING, ProgramState.PAUSED]:
            self.state = ProgramState.STOPPED
            
            # Обновляем общее время выполнения
            if self.start_time:
                total_runtime = (datetime.now() - self.start_time).total_seconds()
                self.metrics.total_runtime_seconds = total_runtime - self.total_pause_time
            
            self._log_action("Программа остановлена", "Программа полностью остановлена")
            self._notify_state_change()
            return True
        return False
    
    def log_network_created(self, network_id: int, network_name: str):
        """Логирует создание сети"""
        self.metrics.total_networks_created += 1
        self.metrics.current_network_id = network_id
        self.metrics.current_network_name = network_name
        self.metrics.last_action_time = datetime.now()
        self._log_action("Сеть создана", f"Создана сеть '{network_name}' (ID: {network_id})", network_id, network_name)
    
    def log_network_deleted(self, network_id: int, network_name: str):
        """Логирует удаление сети"""
        self.metrics.total_networks_deleted += 1
        self.metrics.last_action_time = datetime.now()
        self._log_action("Сеть удалена", f"Удалена сеть '{network_name}' (ID: {network_id})", network_id, network_name)
    
    def log_networks_deleted_all(self, count: int):
        """Логирует удаление всех сетей"""
        self.metrics.total_networks_deleted += count
        self.metrics.last_action_time = datetime.now()
        self._log_action("Все сети удалены", f"Удалено {count} сетей")
    
    def log_simulation_started(self, network_id: int, network_name: str):
        """Логирует запуск симуляции"""
        self.metrics.total_simulations_run += 1
        self.metrics.current_network_id = network_id
        self.metrics.current_network_name = network_name
        self.metrics.last_action_time = datetime.now()
        self._log_action("Симуляция запущена", f"Запущена симуляция сети '{network_name}' (ID: {network_id})", network_id, network_name)
    
    def log_simulation_stopped(self, network_id: int, network_name: str):
        """Логирует остановку симуляции"""
        self.metrics.last_action_time = datetime.now()
        self._log_action("Симуляция остановлена", f"Остановлена симуляция сети '{network_name}' (ID: {network_id})", network_id, network_name)
    
    def _log_action(self, action: str, details: str, network_id: Optional[int] = None, network_name: Optional[str] = None):
        """Добавляет запись в журнал действий"""
        log_entry = ActionLog(
            timestamp=datetime.now(),
            action=action,
            details=details,
            network_id=network_id,
            network_name=network_name
        )
        self.action_log.append(log_entry)
        
        # Ограничиваем размер журнала (последние 1000 записей)
        if len(self.action_log) > 1000:
            self.action_log = self.action_log[-1000:]
    
    def get_status_info(self) -> Dict:
        """Возвращает информацию о текущем состоянии"""
        current_time = datetime.now()
        
        # Вычисляем время выполнения
        runtime_seconds = 0.0
        if self.start_time:
            total_time = (current_time - self.start_time).total_seconds()
            runtime_seconds = total_time - self.total_pause_time
        
        return {
            'state': self.state.value,
            'state_display': self._get_state_display_name(),
            'runtime_seconds': runtime_seconds,
            'runtime_display': self._format_duration(runtime_seconds),
            'pause_count': self.metrics.pause_count,
            'total_pause_time': self.total_pause_time,
            'total_pause_time_display': self._format_duration(self.total_pause_time),
            'last_action_time': self.metrics.last_action_time,
            'current_network_id': self.metrics.current_network_id,
            'current_network_name': self.metrics.current_network_name,
            'metrics': {
                'total_networks_created': self.metrics.total_networks_created,
                'total_networks_deleted': self.metrics.total_networks_deleted,
                'total_simulations_run': self.metrics.total_simulations_run,
                'total_runtime_seconds': self.metrics.total_runtime_seconds
            }
        }
    
    def _get_state_display_name(self) -> str:
        """Возвращает отображаемое название состояния"""
        state_names = {
            ProgramState.STOPPED: "Программа остановлена",
            ProgramState.RUNNING: "Программа запущена",
            ProgramState.PAUSED: "Программа на паузе",
            ProgramState.ERROR: "Ошибка программы"
        }
        return state_names.get(self.state, "Неизвестное состояние")
    
    def _format_duration(self, seconds: float) -> str:
        """Форматирует длительность в читаемый вид"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def get_action_log(self, limit: int = 50) -> List[Dict]:
        """Возвращает последние записи журнала действий"""
        recent_logs = self.action_log[-limit:] if limit > 0 else self.action_log
        return [
            {
                'timestamp': log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'action': log.action,
                'details': log.details,
                'network_id': log.network_id,
                'network_name': log.network_name
            }
            for log in recent_logs
        ]
    
    def get_networks_status(self, db_manager) -> Dict:
        """Возвращает статус всех сетей"""
        try:
            all_networks = db_manager.get_all_networks()
            
            # Проверяем, что all_networks является списком
            if not isinstance(all_networks, list):
                print(f"[WARNING] get_all_networks вернул {type(all_networks)} вместо списка")
                all_networks = []
            
            return {
                'total_networks': len(all_networks),
                'networks': [
                    {
                        'id': network.get('id'),
                        'name': network.get('name'),
                        'created_at': network.get('created_at'),
                        'status': 'active'  # Все сети в БД считаются активными
                    }
                    for network in all_networks
                ]
            }
        except Exception as e:
            print(f"[ERROR] Ошибка в get_networks_status: {e}")
            return {
                'total_networks': 0,
                'networks': [],
                'error': str(e)
            }
