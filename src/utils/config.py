#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурация приложения
"""

import json
import os
from typing import Dict, Any

class Config:
    """Класс для управления конфигурацией приложения"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию по умолчанию"""
        return {
            "simulation": {
                "time_steps": 1000,
                "dt": 0.1,
                "random_seed": 42
            },
            "network": {
                "nodes": 10,
                "connections": 0.3,
                "bandwidth": 1000,  # Мбит/с
                "latency": 10,      # мс
                "reliability": 0.95
            },
            "adverse_conditions": {
                "noise_level": 0.1,
                "interference_probability": 0.05,
                "failure_rate": 0.02,
                "jamming_intensity": 0.1
            },
            "visualization": {
                "update_interval": 100,  # мс
                "graph_style": "default",
                "color_scheme": "viridis"
            },
            "analysis": {
                "metrics": ["throughput", "latency", "reliability", "availability"],
                "confidence_level": 0.95
            }
        }
    
    def _load_config(self):
        """Загружает конфигурацию из файла"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """Объединяет конфигурацию из файла с конфигурацией по умолчанию"""
        def merge_dict(base: Dict, update: Dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.config, file_config)
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def get(self, key_path: str, default=None):
        """Получает значение конфигурации по пути (например, 'simulation.time_steps')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Устанавливает значение конфигурации по пути"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Возвращает всю конфигурацию"""
        return self.config.copy()





