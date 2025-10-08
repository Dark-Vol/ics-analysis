#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализатор производительности ИКС
"""

import numpy as np
import statistics
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from ..models.performance_metrics import MetricsSnapshot

@dataclass
class PerformanceAnalysis:
    """Результат анализа производительности"""
    metric_name: str
    mean_value: float
    std_value: float
    min_value: float
    max_value: float
    median_value: float
    q25_value: float
    q75_value: float
    trend: str  # "increasing", "decreasing", "stable"
    anomalies: List[Tuple[float, float]]  # (timestamp, value)
    recommendations: List[str]

class PerformanceAnalyzer:
    """Анализатор производительности сети"""
    
    def __init__(self):
        self.analysis_history = []
    
    def analyze_metrics(self, metrics_history: List[MetricsSnapshot]) -> Dict[str, PerformanceAnalysis]:
        """Анализирует метрики производительности"""
        if not metrics_history:
            return {}
        
        analyses = {}
        
        # Анализ каждой метрики
        metric_names = ['throughput', 'latency', 'reliability', 'availability', 
                       'packet_loss', 'jitter', 'energy_efficiency']
        
        for metric_name in metric_names:
            values = []
            timestamps = []
            
            for snapshot in metrics_history:
                value = getattr(snapshot, metric_name)
                if value is not None:
                    values.append(value)
                    timestamps.append(snapshot.timestamp)
            
            if values:
                analysis = self._analyze_single_metric(metric_name, values, timestamps)
                analyses[metric_name] = analysis
        
        return analyses
    
    def _analyze_single_metric(self, metric_name: str, values: List[float], 
                              timestamps: List[float]) -> PerformanceAnalysis:
        """Анализирует одну метрику"""
        # Основная статистика
        mean_value = statistics.mean(values)
        std_value = statistics.stdev(values) if len(values) > 1 else 0.0
        min_value = min(values)
        max_value = max(values)
        median_value = statistics.median(values)
        q25_value = np.percentile(values, 25)
        q75_value = np.percentile(values, 75)
        
        # Анализ тренда
        trend = self._analyze_trend(values, timestamps)
        
        # Поиск аномалий
        anomalies = self._find_anomalies(values, timestamps)
        
        # Генерация рекомендаций
        recommendations = self._generate_recommendations(metric_name, mean_value, std_value, 
                                                       min_value, max_value, trend, anomalies)
        
        return PerformanceAnalysis(
            metric_name=metric_name,
            mean_value=mean_value,
            std_value=std_value,
            min_value=min_value,
            max_value=max_value,
            median_value=median_value,
            q25_value=q25_value,
            q75_value=q75_value,
            trend=trend,
            anomalies=anomalies,
            recommendations=recommendations
        )
    
    def _analyze_trend(self, values: List[float], timestamps: List[float]) -> str:
        """Анализирует тренд метрики"""
        if len(values) < 3:
            return "stable"
        
        # Простая линейная регрессия
        x = np.array(timestamps)
        y = np.array(values)
        
        # Нормализация времени
        x_norm = (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else x
        
        # Расчет коэффициента наклона
        n = len(x_norm)
        slope = (n * np.sum(x_norm * y) - np.sum(x_norm) * np.sum(y)) / \
                (n * np.sum(x_norm**2) - np.sum(x_norm)**2)
        
        # Определение тренда
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _find_anomalies(self, values: List[float], timestamps: List[float]) -> List[Tuple[float, float]]:
        """Находит аномалии в данных"""
        if len(values) < 3:
            return []
        
        anomalies = []
        mean_value = statistics.mean(values)
        std_value = statistics.stdev(values)
        
        # Использование правила 3-сигма для обнаружения аномалий
        threshold = 3 * std_value
        
        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            if abs(value - mean_value) > threshold:
                anomalies.append((timestamp, value))
        
        return anomalies
    
    def _generate_recommendations(self, metric_name: str, mean_value: float, 
                                 std_value: float, min_value: float, max_value: float,
                                 trend: str, anomalies: List[Tuple[float, float]]) -> List[str]:
        """Генерирует рекомендации по улучшению"""
        recommendations = []
        
        if metric_name == 'throughput':
            if mean_value < 100:  # Мбит/с
                recommendations.append("Пропускная способность низкая. Рассмотрите увеличение пропускной способности каналов.")
            if std_value / mean_value > 0.3:  # Коэффициент вариации > 30%
                recommendations.append("Высокая вариативность пропускной способности. Проверьте стабильность соединений.")
            if trend == "decreasing":
                recommendations.append("Наблюдается снижение пропускной способности. Проверьте нагрузку на сеть.")
        
        elif metric_name == 'latency':
            if mean_value > 100:  # мс
                recommendations.append("Высокая задержка. Оптимизируйте маршрутизацию или увеличьте пропускную способность.")
            if std_value > 50:  # мс
                recommendations.append("Высокая вариативность задержки. Проверьте качество соединений.")
            if trend == "increasing":
                recommendations.append("Задержка увеличивается. Возможно перегрузка сети.")
        
        elif metric_name == 'reliability':
            if mean_value < 0.95:
                recommendations.append("Надежность ниже рекомендуемого уровня. Улучшите резервирование.")
            if trend == "decreasing":
                recommendations.append("Надежность снижается. Проверьте состояние оборудования.")
        
        elif metric_name == 'availability':
            if mean_value < 0.99:
                recommendations.append("Доступность ниже SLA. Улучшите резервирование и мониторинг.")
            if trend == "decreasing":
                recommendations.append("Доступность снижается. Проверьте систему мониторинга.")
        
        elif metric_name == 'packet_loss':
            if mean_value > 0.01:  # 1%
                recommendations.append("Высокая потеря пакетов. Проверьте качество соединений.")
            if trend == "increasing":
                recommendations.append("Потеря пакетов увеличивается. Возможны проблемы с оборудованием.")
        
        elif metric_name == 'jitter':
            if mean_value > 20:  # мс
                recommendations.append("Высокий джиттер. Оптимизируйте буферизацию.")
            if trend == "increasing":
                recommendations.append("Джиттер увеличивается. Проверьте стабильность соединений.")
        
        # Общие рекомендации при наличии аномалий
        if len(anomalies) > len(values) * 0.1:  # Более 10% аномалий
            recommendations.append("Обнаружено много аномалий. Проведите диагностику сети.")
        
        return recommendations
    
    def compare_performance(self, baseline_analysis: Dict[str, PerformanceAnalysis],
                           current_analysis: Dict[str, PerformanceAnalysis]) -> Dict[str, Dict[str, float]]:
        """Сравнивает производительность с базовым уровнем"""
        comparison = {}
        
        for metric_name in baseline_analysis:
            if metric_name in current_analysis:
                baseline = baseline_analysis[metric_name]
                current = current_analysis[metric_name]
                
                comparison[metric_name] = {
                    'mean_change': (current.mean_value - baseline.mean_value) / baseline.mean_value * 100,
                    'std_change': (current.std_value - baseline.std_value) / baseline.std_value * 100 if baseline.std_value > 0 else 0,
                    'min_change': (current.min_value - baseline.min_value) / baseline.min_value * 100 if baseline.min_value > 0 else 0,
                    'max_change': (current.max_value - baseline.max_value) / baseline.max_value * 100 if baseline.max_value > 0 else 0
                }
        
        return comparison
    
    def generate_performance_report(self, analyses: Dict[str, PerformanceAnalysis]) -> str:
        """Генерирует отчет о производительности"""
        report = "ОТЧЕТ О ПРОИЗВОДИТЕЛЬНОСТИ СЕТИ\n"
        report += "=" * 50 + "\n\n"
        
        for metric_name, analysis in analyses.items():
            report += f"{metric_name.upper()}:\n"
            report += f"  Среднее значение: {analysis.mean_value:.3f}\n"
            report += f"  Стд. отклонение: {analysis.std_value:.3f}\n"
            report += f"  Минимум: {analysis.min_value:.3f}\n"
            report += f"  Максимум: {analysis.max_value:.3f}\n"
            report += f"  Медиана: {analysis.median_value:.3f}\n"
            report += f"  Тренд: {analysis.trend}\n"
            report += f"  Аномалий: {len(analysis.anomalies)}\n"
            
            if analysis.recommendations:
                report += "  Рекомендации:\n"
                for rec in analysis.recommendations:
                    report += f"    - {rec}\n"
            
            report += "\n"
        
        return report





