#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест для проверки работы функций расширенного анализа надежности
"""

import sys
import os
import numpy as np

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analytics.advanced_reliability_analyzer import (
    AdvancedReliabilityAnalyzer, 
    create_sample_network,
    CRITICAL_NODE_THRESHOLD
)


def test_birnbaum_criterion():
    """Тест функции расчета критерия Бирнбаума"""
    print("Тест 1: Расчет критерия Бирнбаума")
    print("-" * 40)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    # Рассчитываем коэффициенты Бирнбаума
    birnbaum_coeffs = analyzer.calculate_birnbaum_criterion(probabilities, structure_matrix)
    
    print("Коэффициенты значимости Бирнбаума:")
    for node, coeff in birnbaum_coeffs.items():
        print(f"  {node}: {coeff:.4f}")
    
    # Проверяем, что все коэффициенты рассчитаны
    assert len(birnbaum_coeffs) == len(probabilities), "Не все коэффициенты рассчитаны"
    
    # Проверяем, что сумма коэффициентов положительна
    total_coeff = sum(birnbaum_coeffs.values())
    assert total_coeff > 0, f"Сумма коэффициентов должна быть положительной, получено: {total_coeff}"
    
    print(f"Общая сумма коэффициентов: {total_coeff:.4f}")
    print("ТЕСТ ПРОЙДЕН УСПЕШНО\n")
    
    return birnbaum_coeffs


def test_system_reliability():
    """Тест функции расчета надежности системы"""
    print("Тест 2: Расчет надежности системы")
    print("-" * 40)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    # Рассчитываем надежность системы
    connections = analyzer._get_connections_from_matrix()
    system_reliability = analyzer.system_reliability(probabilities, connections)
    
    print(f"Надежность системы: {system_reliability:.6f}")
    
    # Проверяем, что надежность в разумных пределах
    assert 0 <= system_reliability <= 1, f"Надежность должна быть от 0 до 1, получено: {system_reliability}"
    
    # Проверяем вероятности отказа узлов
    failure_probs = analyzer.calculate_node_failure_probabilities(probabilities)
    print("Вероятности отказа узлов:")
    for node, prob in failure_probs.items():
        print(f"  {node}: {prob:.4f}")
        assert 0 <= prob <= 1, f"Вероятность отказа должна быть от 0 до 1, получено: {prob}"
    
    print("ТЕСТ ПРОЙДЕН УСПЕШНО\n")
    
    return system_reliability


def test_durbin_watson():
    """Тест функции Дарбина-Уотсона"""
    print("Тест 3: Тест Дарбина-Уотсона")
    print("-" * 40)
    
    analyzer = AdvancedReliabilityAnalyzer()
    
    # Тестируем с остатками без автокорреляции
    np.random.seed(42)
    residuals_no_autocorr = np.random.normal(0, 1, 20)
    
    dw_stat, interpretation = analyzer.durbin_watson_test(residuals_no_autocorr.tolist())
    
    print(f"Статистика Дарбина-Уотсона: {dw_stat:.4f}")
    print(f"Интерпретация: {interpretation}")
    
    # Проверяем, что статистика в разумных пределах
    assert 0 <= dw_stat <= 4, f"Статистика Дарбина-Уотсона должна быть от 0 до 4, получено: {dw_stat}"
    
    print("ТЕСТ ПРОЙДЕН УСПЕШНО\n")
    
    return dw_stat


def test_node_removal():
    """Тест функции удаления узлов"""
    print("Тест 4: Удаление узлов")
    print("-" * 40)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    print(f"Исходное количество узлов: {len(network_structure['nodes'])}")
    
    # Удаляем один узел
    node_to_remove = 'switch1'
    updated_network = analyzer.remove_nodes(network_structure, [node_to_remove])
    
    print(f"Количество узлов после удаления '{node_to_remove}': {len(updated_network['nodes'])}")
    
    # Проверяем, что узел действительно удален
    remaining_node_ids = [node['id'] for node in updated_network['nodes']]
    assert node_to_remove not in remaining_node_ids, f"Узел {node_to_remove} не был удален"
    
    # Проверяем критический порог
    is_critical, message = analyzer.check_critical_threshold(updated_network)
    print(f"Проверка критического порога: {message}")
    
    print("ТЕСТ ПРОЙДЕН УСПЕШНО\n")
    
    return updated_network


def test_external_events():
    """Тест моделирования внешних событий"""
    print("Тест 5: Моделирование внешних событий")
    print("-" * 40)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    # Симулируем внешние события
    updated_network = analyzer.simulate_external_events(network_structure)
    
    print("Результат симуляции внешних событий:")
    
    if 'external_events' in updated_network:
        print(f"Количество произошедших событий: {len(updated_network['external_events'])}")
        for event in updated_network['external_events']:
            print(f"  - {event['description']}")
    else:
        print("Внешние события не произошли")
    
    if 'node_failure_probabilities' in updated_network:
        print("Обновленные вероятности отказов:")
        for node, prob in updated_network['node_failure_probabilities'].items():
            print(f"  {node}: {prob:.4f}")
    
    print("ТЕСТ ПРОЙДЕН УСПЕШНО\n")
    
    return updated_network


def test_comprehensive_report():
    """Тест генерации комплексного отчета"""
    print("Тест 6: Генерация комплексного отчета")
    print("-" * 40)
    
    analyzer = AdvancedReliabilityAnalyzer()
    probabilities, structure_matrix, network_structure = create_sample_network()
    
    # Генерируем отчет
    report = analyzer.generate_reliability_report(probabilities, structure_matrix)
    
    print(f"Размер отчета: {len(report)} строк")
    print("Первые несколько строк отчета:")
    print(report.head().to_string(index=False))
    
    # Проверяем, что отчет содержит все необходимые колонки
    required_columns = ['node_id', 'reliability', 'failure_probability', 'birnbaum_coefficient']
    for col in required_columns:
        assert col in report.columns, f"Отсутствует колонка: {col}"
    
    print("ТЕСТ ПРОЙДЕН УСПЕШНО\n")
    
    return report


def main():
    """Основная функция тестирования"""
    print("ТЕСТИРОВАНИЕ ФУНКЦИЙ РАСШИРЕННОГО АНАЛИЗА НАДЕЖНОСТИ")
    print("=" * 60)
    
    try:
        # Запускаем все тесты
        test_birnbaum_criterion()
        test_system_reliability()
        test_durbin_watson()
        test_node_removal()
        test_external_events()
        test_comprehensive_report()
        
        print("=" * 60)
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        
        print(f"\nКонстанты:")
        print(f"  Критический порог системы: {CRITICAL_NODE_THRESHOLD} узлов")
        
    except Exception as e:
        print(f"\nОШИБКА при тестировании: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
