#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационный скрипт для расширенного анализа надежности ИКС
Показывает все реализованные функции в действии
"""

import sys
import os
import numpy as np
import pandas as pd
from typing import Dict, List

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analytics.advanced_reliability_analyzer import (
    AdvancedReliabilityAnalyzer, 
    create_sample_network,
    CRITICAL_NODE_THRESHOLD
)


def demonstrate_birnbaum_analysis():
    """Демонстрация анализа по критерию Бирнбаума"""
    print("=" * 60)
    print("АНАЛИЗ ПО КРИТЕРИЮ БИРНБАУМА")
    print("=" * 60)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    # Рассчитываем коэффициенты Бирнбаума
    birnbaum_coeffs = analyzer.calculate_birnbaum_criterion(probabilities, structure_matrix)
    
    print("\nКоэффициенты значимости Бирнбаума:")
    print("-" * 50)
    
    # Сортируем по убыванию значимости
    sorted_coeffs = sorted(birnbaum_coeffs.items(), key=lambda x: x[1], reverse=True)
    
    for i, (node, coeff) in enumerate(sorted_coeffs, 1):
        criticality = analyzer._get_criticality_level(coeff)
        print(f"{i:2d}. {node:12s}: {coeff:8.4f} ({criticality})")
    
    print(f"\nОбщая сумма коэффициентов: {sum(birnbaum_coeffs.values()):.4f}")
    
    return birnbaum_coeffs


def demonstrate_probability_theory():
    """Демонстрация функций теории вероятностей"""
    print("\n" + "=" * 60)
    print("ТЕОРИЯ ВЕРОЯТНОСТЕЙ")
    print("=" * 60)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    # Общая вероятность безотказной работы системы
    connections = analyzer._get_connections_from_matrix()
    system_reliability = analyzer.system_reliability(probabilities, connections)
    
    print(f"\nОбщая вероятность безотказной работы системы: {system_reliability:.6f}")
    
    # Вероятности отказа узлов
    failure_probs = analyzer.calculate_node_failure_probabilities(probabilities)
    
    print("\nВероятности отказа отдельных узлов:")
    print("-" * 50)
    for node, prob in failure_probs.items():
        print(f"{node:12s}: {prob:8.4f}")
    
    # Распределение вероятностей состояний
    state_distribution = analyzer.calculate_probability_distribution(probabilities)
    
    print(f"\nРаспределение вероятностей состояний:")
    print(f"Всего возможных состояний: {len(state_distribution)}")
    
    # Показываем наиболее вероятные состояния
    sorted_states = sorted(state_distribution.items(), key=lambda x: x[1], reverse=True)
    
    print("\nТоп-5 наиболее вероятных состояний:")
    print("-" * 50)
    for i, (state, prob) in enumerate(sorted_states[:5], 1):
        print(f"{i}. {prob:.6f} - {state}")
    
    return {
        'system_reliability': system_reliability,
        'failure_probabilities': failure_probs,
        'state_distribution': state_distribution
    }


def demonstrate_durbin_watson_test():
    """Демонстрация теста Дарбина-Уотсона"""
    print("\n" + "=" * 60)
    print("ТЕСТ ДАРБИНА-УОТСОНА")
    print("=" * 60)
    
    analyzer = AdvancedReliabilityAnalyzer()
    
    # Генерируем различные типы остатков для демонстрации
    np.random.seed(42)
    
    test_cases = [
        ("Остатки без автокорреляции", np.random.normal(0, 1, 25)),
        ("Остатки с положительной автокорреляцией", 
         np.array([0.5 * i + np.random.normal(0, 0.5) for i in range(25)])),
        ("Остатки с отрицательной автокорреляцией",
         np.array([(-1)**i * 0.3 + np.random.normal(0, 1) for i in range(25)]))
    ]
    
    for case_name, residuals in test_cases:
        print(f"\n{case_name}:")
        print("-" * 40)
        
        dw_stat, interpretation = analyzer.durbin_watson_test(residuals.tolist())
        
        print(f"Статистика Дарбина-Уотсона: {dw_stat:.4f}")
        print(f"Интерпретация: {interpretation}")
        
        # Дополнительная статистика
        print(f"Среднее остатков: {np.mean(residuals):.4f}")
        print(f"Стандартное отклонение: {np.std(residuals):.4f}")


def demonstrate_fragility_assessment():
    """Демонстрация оценки хрупкости системы"""
    print("\n" + "=" * 60)
    print("ОЦЕНКА ХРУПКОСТИ СИСТЕМЫ")
    print("=" * 60)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    print(f"Критический порог системы: {CRITICAL_NODE_THRESHOLD} узлов")
    print(f"Исходное количество узлов: {len(network_structure['nodes'])}")
    
    # Рассчитываем исходную надежность системы
    connections = analyzer._get_connections_from_matrix()
    initial_reliability = analyzer.system_reliability(probabilities, connections)
    print(f"Исходная надежность системы: {initial_reliability:.6f}")
    
    # Пошаговое удаление узлов
    print("\nПошаговое удаление узлов:")
    print("-" * 50)
    
    current_network = network_structure.copy()
    current_probabilities = probabilities.copy()
    removal_order = ['switch1', 'switch2', 'router1', 'router2', 'server1']
    
    for i, node_to_remove in enumerate(removal_order, 1):
        print(f"\nШаг {i}: Удаляем узел '{node_to_remove}'")
        
        # Удаляем узел из сети
        current_network = analyzer.remove_nodes(current_network, [node_to_remove])
        
        # Удаляем узел из вероятностей
        if node_to_remove in current_probabilities:
            del current_probabilities[node_to_remove]
        
        # Проверяем критический порог
        is_critical, message = analyzer.check_critical_threshold(current_network)
        print(f"  {message}")
        
        # Рассчитываем новую надежность системы
        if len(current_probabilities) > 0:
            new_connections = analyzer._get_connections_from_matrix()
            new_reliability = analyzer.system_reliability(current_probabilities, new_connections)
            reliability_change = new_reliability - initial_reliability
            
            print(f"  Надежность системы: {new_reliability:.6f}")
            print(f"  Изменение надежности: {reliability_change:+.6f}")
        
        if is_critical:
            print("  ВНИМАНИЕ: ДОСТИГНУТ КРИТИЧЕСКИЙ ПОРОГ!")
            print("  Система перестает функционировать.")
            break


def demonstrate_external_events():
    """Демонстрация моделирования внешних воздействий"""
    print("\n" + "=" * 60)
    print("МОДЕЛИРОВАНИЕ ВНЕШНИХ ВОЗДЕЙСТВИЙ")
    print("=" * 60)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    print("Типы внешних воздействий:")
    print("- Хакерская атака (вероятность: 10%, компрометация: 30%)")
    print("- Отключение электроэнергии (вероятность: 5%, отказ: 80%)")
    print("- Случайный отказ оборудования (вероятность: 15%, отказ: 20%)")
    
    # Исходные вероятности отказов
    initial_failure_probs = analyzer.calculate_node_failure_probabilities(probabilities)
    print(f"\nИсходные вероятности отказов узлов:")
    for node, prob in initial_failure_probs.items():
        print(f"  {node:12s}: {prob:.4f}")
    
    # Симулируем несколько раундов внешних воздействий
    print(f"\nСимуляция внешних воздействий:")
    print("-" * 50)
    
    current_network = network_structure.copy()
    
    for round_num in range(1, 4):
        print(f"\nРаунд {round_num}:")
        
        # Симулируем внешние события
        current_network = analyzer.simulate_external_events(current_network)
        
        # Показываем произошедшие события
        if 'external_events' in current_network and current_network['external_events']:
            print("  Произошедшие события:")
            for event in current_network['external_events']:
                print(f"    - {event['description']}")
                print(f"      Вероятность воздействия: {event['probability']:.2f}")
        else:
            print("  Внешние события не произошли")
        
        # Показываем обновленные вероятности отказов
        if 'node_failure_probabilities' in current_network:
            print("  Обновленные вероятности отказов:")
            for node, prob in current_network['node_failure_probabilities'].items():
                initial_prob = initial_failure_probs.get(node, 0)
                change = prob - initial_prob
                print(f"    {node:12s}: {prob:.4f} ({change:+.4f})")


def generate_comprehensive_report():
    """Генерация комплексного отчета"""
    print("\n" + "=" * 60)
    print("КОМПЛЕКСНЫЙ ОТЧЕТ ПО НАДЕЖНОСТИ")
    print("=" * 60)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    # Генерируем подробный отчет
    report = analyzer.generate_reliability_report(probabilities, structure_matrix)
    
    print("\nДетальный отчет по надежности:")
    print("-" * 80)
    print(report.to_string(index=False, float_format='%.4f'))
    
    # Дополнительная статистика
    print(f"\nСтатистика системы:")
    print(f"  Общее количество узлов: {len(probabilities)}")
    print(f"  Средняя надежность узлов: {np.mean(list(probabilities.values())):.4f}")
    print(f"  Минимальная надежность: {min(probabilities.values()):.4f}")
    print(f"  Максимальная надежность: {max(probabilities.values()):.4f}")
    
    # Анализ критичности
    birnbaum_coeffs = analyzer.calculate_birnbaum_criterion(probabilities, structure_matrix)
    critical_nodes = [node for node, coeff in birnbaum_coeffs.items() 
                     if analyzer._get_criticality_level(coeff) == 'КРИТИЧЕСКИЙ']
    
    print(f"\nКритически важные узлы: {critical_nodes}")
    
    return report


def main():
    """Основная функция демонстрации"""
    print("ДЕМОНСТРАЦИЯ РАСШИРЕННОГО АНАЛИЗА НАДЕЖНОСТИ ИКС")
    print("=" * 80)
    
    try:
        # 1. Анализ по критерию Бирнбаума
        birnbaum_results = demonstrate_birnbaum_analysis()
        
        # 2. Теория вероятностей
        probability_results = demonstrate_probability_theory()
        
        # 3. Тест Дарбина-Уотсона
        demonstrate_durbin_watson_test()
        
        # 4. Оценка хрупкости системы
        demonstrate_fragility_assessment()
        
        # 5. Моделирование внешних воздействий
        demonstrate_external_events()
        
        # 6. Комплексный отчет
        comprehensive_report = generate_comprehensive_report()
        
        print("\n" + "=" * 80)
        print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА УСПЕШНО")
        print("=" * 80)
        
        print("\nСВОДКА РЕЗУЛЬТАТОВ:")
        print(f"  • Проанализировано узлов: {len(birnbaum_results)}")
        print(f"  • Общая надежность системы: {probability_results['system_reliability']:.4f}")
        print(f"  • Критически важных узлов: {len([n for n, c in birnbaum_results.items() if c >= 0.5])}")
        print(f"  • Критический порог системы: {CRITICAL_NODE_THRESHOLD} узлов")
        
    except Exception as e:
        print(f"\nОШИБКА при выполнении демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
