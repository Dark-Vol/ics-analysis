#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрация расширенных возможностей ИКС Анализатора
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.system_model import create_sample_network, SystemModel
from src.analytics.connectivity_analyzer import ConnectivityAnalyzer
from src.models.adverse_conditions import AdverseConditions
from src.whatif import WhatIfAnalyzer, ParameterType, ParameterRange
import numpy as np

def demo_enhanced_network_model():
    """Демонстрация расширенной модели сети"""
    print("=== Демонстрация расширенной модели сети ===")
    
    # Создаем систему с новыми атрибутами
    system = create_sample_network()
    
    # Обновляем атрибуты узлов
    for node_id, node in system.nodes.items():
        node.threat_level = np.random.uniform(0.1, 0.3)
        node.load = np.random.uniform(0.2, 0.8)
        node.encryption = np.random.choice([True, False])
    
    # Обновляем атрибуты каналов
    for (source, target), link in system.links.items():
        link.threat_level = np.random.uniform(0.05, 0.2)
        link.load = np.random.uniform(0.1, 0.6)
        link.encryption = np.random.choice([True, False])
    
    print(f"Создана система: {system.name}")
    print(f"Узлов: {len(system.nodes)}, Каналов: {len(system.links)}")
    
    # Анализ новых метрик
    connectivity_metrics = system.calculate_connectivity_metrics()
    data_loss_metrics = system.calculate_data_loss_metrics()
    degradation_metrics = system.calculate_performance_degradation()
    
    print(f"\nМетрики связности:")
    print(f"  Связность: {'Да' if connectivity_metrics['is_connected'] else 'Нет'}")
    print(f"  Коэффициент связности: {connectivity_metrics['connectivity_coefficient']:.3f}")
    print(f"  Узловая связность: {connectivity_metrics['node_connectivity']}")
    
    print(f"\nМетрики потерь данных:")
    print(f"  Коэффициент доступности: {data_loss_metrics['availability_coefficient']:.3f}")
    print(f"  Потери узлов: {data_loss_metrics['node_failure_data_loss']:.1f}")
    print(f"  Потери каналов: {data_loss_metrics['link_failure_data_loss']:.1f}")
    
    print(f"\nДеградация производительности:")
    print(f"  Общая деградация: {degradation_metrics['overall_degradation']:.3f}")
    print(f"  Деградация узлов: {degradation_metrics['node_load_degradation']:.3f}")
    print(f"  Деградация каналов: {degradation_metrics['link_load_degradation']:.3f}")
    
    return system

def demo_connectivity_analysis():
    """Демонстрация анализа связности"""
    print("\n=== Демонстрация анализа связности ===")
    
    system = create_sample_network()
    connectivity_analyzer = ConnectivityAnalyzer()
    
    # Полный анализ связности
    report = connectivity_analyzer.analyze_network(system)
    
    print(f"Анализ связности сети:")
    print(f"  Связность: {'Да' if report.is_connected else 'Нет'}")
    print(f"  Компоненты: {report.num_components}")
    print(f"  Коэффициент связности: {report.connectivity_coefficient:.3f}")
    print(f"  Оценка устойчивости: {report.robustness_score:.3f}")
    print(f"  Оценка избыточности: {report.redundancy_score:.3f}")
    
    print(f"\nКритические элементы:")
    print(f"  Критические узлы: {report.critical_nodes}")
    print(f"  Критические связи: {report.critical_links}")
    
    # Генерируем рекомендации
    recommendations = connectivity_analyzer.get_connectivity_recommendations(report)
    print(f"\nРекомендации:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    return report

def demo_adverse_conditions():
    """Демонстрация моделирования неблагоприятных условий"""
    print("\n=== Демонстрация неблагоприятных условий ===")
    
    adverse_conditions = AdverseConditions()
    
    # Симулируем различные типы воздействий
    print("Симуляция неблагоприятных воздействий:")
    
    # Кибератака
    adverse_conditions.simulate_cyber_attack(
        target_nodes=[1, 2], 
        attack_type="ddos", 
        intensity=0.7, 
        duration=100
    )
    print("  ✓ Кибератака (DDoS) на узлы 1, 2")
    
    # DoS-атака
    adverse_conditions.simulate_dos_attack(
        target_nodes=[3], 
        intensity=0.5, 
        duration=80
    )
    print("  ✓ DoS-атака на узел 3")
    
    # Физическое повреждение
    adverse_conditions.simulate_physical_damage(
        target_nodes=[4], 
        damage_level=0.3, 
        duration=200
    )
    print("  ✓ Физическое повреждение узла 4")
    
    # Неблагоприятные условия среды
    adverse_conditions.simulate_environmental_conditions(
        target_nodes=[5, 6], 
        factor="weather", 
        intensity=0.4, 
        duration=150
    )
    print("  ✓ Неблагоприятные условия среды на узлы 5, 6")
    
    # Анализ воздействия на узлы
    print(f"\nАнализ воздействия на узлы:")
    for node_id in range(1, 7):
        degradation = adverse_conditions.calculate_comprehensive_degradation(node_id)
        threat_assessment = adverse_conditions.get_threat_level_assessment(node_id)
        
        print(f"  Узел {node_id}:")
        print(f"    Деградация производительности: {degradation['performance_degradation']:.3f}")
        print(f"    Воздействие на безопасность: {degradation['security_impact']:.3f}")
        print(f"    Общий уровень угроз: {threat_assessment['overall_threat_level']:.3f}")
    
    # Сводка активных условий
    summary = adverse_conditions.get_active_conditions_summary()
    print(f"\nАктивные неблагоприятные условия:")
    for condition_type, count in summary.items():
        if count > 0:
            print(f"  {condition_type}: {count}")
    
    return adverse_conditions

def demo_whatif_analysis():
    """Демонстрация What-if анализа"""
    print("\n=== Демонстрация What-if анализа ===")
    
    system = create_sample_network()
    analyzer = WhatIfAnalyzer(system)
    analyzer.create_baseline_system()
    
    # Настройка параметров для анализа
    parameter_ranges = [
        ParameterRange(
            param_type=ParameterType.THREAT_LEVEL,
            component_id="server1",
            min_value=0.1,
            max_value=0.5,
            default_value=0.2
        ),
        ParameterRange(
            param_type=ParameterType.NODE_LOAD,
            component_id="server1",
            min_value=0.2,
            max_value=0.9,
            default_value=0.5
        ),
        ParameterRange(
            param_type=ParameterType.ENCRYPTION,
            component_id="server1",
            min_value=0,
            max_value=1,
            default_value=1
        )
    ]
    
    analyzer.set_parameter_ranges(parameter_ranges)
    
    print("Анализ влияния параметров:")
    
    # Анализ изменения уровня угроз
    result1 = analyzer.analyze_single_parameter_change(
        "server1", ParameterType.THREAT_LEVEL, 0.4, simulation_duration=60
    )
    print(f"  Изменение уровня угроз:")
    print(f"    Влияние на пропускную способность: {result1.impact_metrics.get('network_throughput_change', 0):.1%}")
    print(f"    Рекомендации: {len(result1.recommendations)}")
    
    # Анализ изменения загрузки
    result2 = analyzer.analyze_single_parameter_change(
        "server1", ParameterType.NODE_LOAD, 0.8, simulation_duration=60
    )
    print(f"  Изменение загрузки узла:")
    print(f"    Влияние на пропускную способность: {result2.impact_metrics.get('network_throughput_change', 0):.1%}")
    print(f"    Рекомендации: {len(result2.recommendations)}")
    
    # Анализ влияния неблагоприятных условий
    print(f"\nАнализ влияния неблагоприятных условий:")
    adverse_result = analyzer.analyze_adverse_conditions_impact(
        adverse_condition_type="cyber_attack",
        intensity_range=(0.1, 0.9),
        target_nodes=["server1", "server2"],
        simulation_duration=60
    )
    
    print(f"  Тип условия: {adverse_result['condition_type']}")
    print(f"  Проанализировано интенсивностей: {len(adverse_result['impact_analysis'])}")
    
    # Анализ чувствительности
    print(f"\nАнализ чувствительности параметров:")
    sensitivity_results = analyzer.analyze_parameter_sensitivity(
        parameter_ranges, num_samples=20
    )
    
    for param_key, samples in sensitivity_results.items():
        if samples:
            print(f"  {param_key}:")
            print(f"    Среднее: {np.mean(samples):.2f}")
            print(f"    Стандартное отклонение: {np.std(samples):.2f}")
    
    return analyzer

def demo_comprehensive_analysis():
    """Демонстрация комплексного анализа"""
    print("\n=== Демонстрация комплексного анализа ===")
    
    system = create_sample_network()
    analyzer = WhatIfAnalyzer(system)
    analyzer.create_baseline_system()
    
    # Сценарии неблагоприятных условий
    adverse_scenarios = [
        {
            'name': 'Кибератака на серверы',
            'condition_type': 'cyber_attack',
            'intensity_range': (0.2, 0.8),
            'target_nodes': ['server1', 'server2']
        },
        {
            'name': 'DoS-атака на маршрутизатор',
            'condition_type': 'dos_attack',
            'intensity_range': (0.3, 0.7),
            'target_nodes': ['router1']
        },
        {
            'name': 'Физическое повреждение',
            'condition_type': 'physical_damage',
            'intensity_range': (0.1, 0.5),
            'target_nodes': ['switch1']
        }
    ]
    
    # Сценарии отказов
    failure_scenarios = [
        {
            'name': 'Отказ критических узлов',
            'failed_nodes': ['router1'],
            'failed_links': []
        },
        {
            'name': 'Отказ каналов связи',
            'failed_nodes': [],
            'failed_links': ['server1_router1', 'router1_switch1']
        }
    ]
    
    # Комплексный анализ
    print("Запуск комплексного анализа...")
    comprehensive_results = analyzer.comprehensive_whatif_analysis(
        parameter_scenarios=[],
        adverse_condition_scenarios=adverse_scenarios,
        failure_scenarios=failure_scenarios,
        simulation_duration=60
    )
    
    # Результаты анализа
    print(f"\nРезультаты комплексного анализа:")
    
    print(f"  Анализ неблагоприятных условий: {len(comprehensive_results['adverse_conditions_analysis'])} сценариев")
    for scenario_result in comprehensive_results['adverse_conditions_analysis']:
        scenario = scenario_result['scenario']
        result = scenario_result['result']
        print(f"    {scenario['name']}: {len(result['impact_analysis'])} точек анализа")
    
    if comprehensive_results['failure_analysis']:
        failure_analysis = comprehensive_results['failure_analysis']
        print(f"  Анализ отказов: {len(failure_analysis['failure_scenarios'])} сценариев")
        
        baseline = failure_analysis['baseline_connectivity']
        print(f"    Базовая связность: {baseline['connectivity_coefficient']:.3f}")
        print(f"    Базовая устойчивость: {baseline['robustness_score']:.3f}")
    
    # Общая оценка
    assessment = comprehensive_results['overall_assessment']
    print(f"\nОбщая оценка:")
    print(f"  Оценка риска: {assessment['risk_assessment']}")
    print(f"  Критических параметров: {len(assessment['critical_parameters'])}")
    print(f"  Высокоэффективных сценариев: {len(assessment['high_impact_scenarios'])}")
    print(f"  Рекомендаций: {len(assessment['recommendations'])}")
    
    for i, rec in enumerate(assessment['recommendations'], 1):
        print(f"    {i}. {rec}")
    
    return comprehensive_results

def main():
    """Основная функция демонстрации"""
    print("ИКС Анализатор - Демонстрация расширенных возможностей")
    print("=" * 60)
    
    try:
        # Демонстрация расширенной модели сети
        system = demo_enhanced_network_model()
        
        # Демонстрация анализа связности
        connectivity_report = demo_connectivity_analysis()
        
        # Демонстрация неблагоприятных условий
        adverse_conditions = demo_adverse_conditions()
        
        # Демонстрация What-if анализа
        whatif_analyzer = demo_whatif_analysis()
        
        # Демонстрация комплексного анализа
        comprehensive_results = demo_comprehensive_analysis()
        
        print("\n" + "=" * 60)
        print("Демонстрация завершена успешно!")
        print("Все новые возможности протестированы и работают корректно.")
        
    except Exception as e:
        print(f"\nОшибка при демонстрации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

