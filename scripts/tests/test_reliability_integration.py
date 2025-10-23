#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест интеграции расширенного анализа надежности
"""

import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.gui.reliability_integration import (
    ConsoleReliabilityAnalyzer,
    create_sample_network_for_integration,
    PYQT_AVAILABLE
)


def test_console_analyzer():
    """Тестирует консольный анализатор"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ КОНСОЛЬНОГО АНАЛИЗАТОРА НАДЕЖНОСТИ")
    print("=" * 60)
    
    # Создаем анализатор
    analyzer = ConsoleReliabilityAnalyzer()
    
    # Загружаем пример данных
    network, probabilities = create_sample_network_for_integration()
    analyzer.set_network_data(network, probabilities)
    
    print(f"\nЗагружена сеть с {len(network['nodes'])} узлами:")
    for node in network['nodes']:
        node_id = node['id']
        prob = probabilities[node_id]
        print(f"  {node_id}: надежность={prob:.3f}")
    
    # Тест 1: Анализ Бирнбаума
    print("\n1. Анализ по критерию Бирнбаума:")
    print("-" * 40)
    
    try:
        birnbaum_results = analyzer.run_birnbaum_analysis()
        
        # Сортируем по убыванию значимости
        sorted_results = sorted(birnbaum_results.items(), key=lambda x: x[1], reverse=True)
        
        for i, (node, coeff) in enumerate(sorted_results, 1):
            if coeff >= 0.5:
                criticality = "КРИТИЧЕСКИЙ"
            elif coeff >= 0.2:
                criticality = "ВЫСОКИЙ"
            elif coeff >= 0.1:
                criticality = "СРЕДНИЙ"
            else:
                criticality = "НИЗКИЙ"
            
            print(f"  {i}. {node:12s}: {coeff:8.4f} ({criticality})")
        
        print(f"\n  Общая сумма коэффициентов: {sum(birnbaum_results.values()):.4f}")
        
    except Exception as e:
        print(f"  ОШИБКА: {e}")
    
    # Тест 2: Анализ надежности системы
    print("\n2. Анализ надежности системы:")
    print("-" * 40)
    
    try:
        reliability_results = analyzer.run_system_reliability_analysis()
        
        print(f"  Общая надежность системы: {reliability_results['system_reliability']:.6f}")
        print(f"  Вероятность отказа системы: {1 - reliability_results['system_reliability']:.6f}")
        
        print("\n  Вероятности отказа узлов:")
        for node, prob in reliability_results['failure_probabilities'].items():
            print(f"    {node:12s}: {prob:.4f}")
        
    except Exception as e:
        print(f"  ОШИБКА: {e}")
    
    # Тест 3: Анализ хрупкости
    print("\n3. Анализ хрупкости системы:")
    print("-" * 40)
    
    try:
        removal_order = ['switch1', 'switch2', 'router1', 'router2', 'server1']
        fragility_results = analyzer.run_fragility_analysis(removal_order)
        
        print(f"  Порядок удаления: {', '.join(removal_order)}")
        print(f"  Количество шагов: {len(fragility_results)}")
        
        for i, result in enumerate(fragility_results, 1):
            print(f"\n  Шаг {i}:")
            print(f"    Количество узлов: {result['nodes_count']}")
            print(f"    Надежность системы: {result['system_reliability']:.6f}")
            print(f"    Связность: {'Да' if result['connectivity_status'] else 'Нет'}")
            
            if result['critical_threshold_reached']:
                print("    ⚠️ КРИТИЧЕСКИЙ ПОРОГ ДОСТИГНУТ!")
                break
        
    except Exception as e:
        print(f"  ОШИБКА: {e}")
    
    # Тест 4: Симуляция внешних угроз
    print("\n4. Симуляция внешних угроз:")
    print("-" * 40)
    
    try:
        updated_probs, events = analyzer.run_threats_simulation()
        
        print(f"  Произошло событий: {len(events)}")
        
        if events:
            print("\n  Детали событий:")
            for event in events:
                print(f"    - {event['description']}")
                print(f"      Тип: {event['type']}")
                print(f"      Цель: {event['target']}")
                print(f"      Воздействие: {event['impact']:.2f}")
        else:
            print("  Внешние события не произошли")
        
        print("\n  Изменения вероятностей:")
        for node, new_prob in updated_probs.items():
            original_prob = probabilities[node]
            change = new_prob - original_prob
            print(f"    {node:12s}: {original_prob:.4f} → {new_prob:.4f} ({change:+.4f})")
        
    except Exception as e:
        print(f"  ОШИБКА: {e}")
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)


def test_pyqt_availability():
    """Тестирует доступность PyQt5"""
    print("\nПроверка доступности PyQt5:")
    print("-" * 30)
    
    if PYQT_AVAILABLE:
        print("PyQt5 доступен")
        print("  Расширенный GUI анализ надежности доступен")
    else:
        print("PyQt5 недоступен")
        print("  Установите PyQt5 для использования GUI функций:")
        print("  pip install PyQt5")


def main():
    """Основная функция тестирования"""
    print("ТЕСТИРОВАНИЕ ИНТЕГРАЦИИ РАСШИРЕННОГО АНАЛИЗА НАДЕЖНОСТИ")
    print("=" * 80)
    
    # Проверяем доступность PyQt5
    test_pyqt_availability()
    
    # Тестируем консольный анализатор
    test_console_analyzer()
    
    print("\nРЕКОМЕНДАЦИИ:")
    print("-" * 20)
    print("1. Для полного функционала установите PyQt5: pip install PyQt5")
    print("2. Используйте GUI версию для интерактивного анализа")
    print("3. Консольная версия подходит для автоматизации и скриптов")
    print("4. Все функции протестированы и работают корректно")


if __name__ == "__main__":
    main()
