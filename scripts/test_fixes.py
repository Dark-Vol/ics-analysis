#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование исправлений: пагинация и What-if анализ
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import json
import traceback

def test_pagination():
    """Тестирует пагинацию в GUI"""
    print("Тестирование пагинации...")
    
    try:
        from src.gui.main_window import MainWindow
        
        # Создаем тестовое окно
        root = tk.Tk()
        root.withdraw()  # Скрываем окно для тестирования
        
        # Загружаем конфигурацию
        config_path = 'config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        else:
            config = {
                "simulation": {"time_steps": 1000, "dt": 0.1, "random_seed": 42},
                "network": {"nodes": 10, "connections": 0.3, "bandwidth": 1000, "latency": 10, "reliability": 0.95}
            }
        
        # Создаем главное окно
        main_window = MainWindow(root, config)
        
        # Проверяем наличие пагинации
        if hasattr(main_window, 'plots_notebook'):
            tabs = []
            for i in range(main_window.plots_notebook.index("end")):
                tab_text = main_window.plots_notebook.tab(i, "text")
                tabs.append(tab_text)
            
            print(f"[OK] Найдены вкладки: {tabs}")
            
            # Проверяем наличие всех ожидаемых панелей
            expected_tabs = ["Контрольная панель", "Панель визуализации", "Статус системы"]
            missing_tabs = [tab for tab in expected_tabs if not any(tab in t for t in tabs)]
            
            if missing_tabs:
                print(f"[ERROR] Отсутствуют вкладки: {missing_tabs}")
                return False
            else:
                print("[OK] Все панели пагинации найдены")
                return True
        else:
            print("[ERROR] Пагинация не найдена")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании пагинации: {e}")
        traceback.print_exc()
        return False
    finally:
        try:
            root.destroy()
        except:
            pass

def test_dashboard_fixes():
    """Тестирует исправления в dashboard.py"""
    print("Тестирование исправлений dashboard...")
    
    try:
        from src.visualization.dashboard import Dashboard
        import matplotlib.pyplot as plt
        
        # Создаем dashboard
        dashboard = Dashboard()
        
        # Тестируем создание дашборда с пустыми данными
        fig = dashboard.create_performance_dashboard([], {}, {}, {})
        
        if fig:
            print("[OK] Dashboard создается без ошибок")
            plt.close(fig)
            return True
        else:
            print("[ERROR] Dashboard не создается")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании dashboard: {e}")
        traceback.print_exc()
        return False

def test_plot_generator_fixes():
    """Тестирует исправления в plot_generator.py"""
    print("Тестирование исправлений plot_generator...")
    
    try:
        from src.visualization.plot_generator import PlotGenerator
        import matplotlib.pyplot as plt
        
        # Создаем plot generator
        plot_gen = PlotGenerator()
        
        # Тестируем создание дашборда производительности с пустыми данными
        fig = plot_gen.create_performance_dashboard([], {}, {})
        
        if fig:
            print("[OK] PlotGenerator создается без ошибок")
            plt.close(fig)
            return True
        else:
            print("[ERROR] PlotGenerator не создается")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании plot_generator: {e}")
        traceback.print_exc()
        return False

def test_whatif_analysis():
    """Тестирует What-if анализ"""
    print("Тестирование What-if анализа...")
    
    try:
        from src.whatif import WhatIfAnalyzer, ParameterType, ParameterRange
        from src.system_model import create_sample_network
        
        # Создаем тестовую сеть
        system = create_sample_network()
        
        # Создаем анализатор
        analyzer = WhatIfAnalyzer(system)
        
        # Тестируем базовый анализ
        result = analyzer.analyze_single_parameter_change(
            "node_0", ParameterType.NODE_CAPACITY, 1500.0, simulation_duration=60
        )
        
        if result:
            print("[OK] What-if анализ работает без ошибок")
            print(f"  - Сценарий: {result.scenario_name}")
            print(f"  - Изменение пропускной способности: {result.impact_metrics.get('network_throughput_change', 0):.1%}")
            return True
        else:
            print("[ERROR] What-if анализ не возвращает результат")
            return False
            
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании What-if анализа: {e}")
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ")
    print("=" * 60)
    
    tests = [
        ("Пагинация GUI", test_pagination),
        ("Исправления Dashboard", test_dashboard_fixes),
        ("Исправления PlotGenerator", test_plot_generator_fixes),
        ("What-if анализ", test_whatif_analysis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] Критическая ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] ПРОШЕЛ" if result else "[ERROR] НЕ ПРОШЕЛ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nРезультат: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("[SUCCESS] ВСЕ ИСПРАВЛЕНИЯ РАБОТАЮТ КОРРЕКТНО!")
    else:
        print("[WARNING] НЕКОТОРЫЕ ПРОБЛЕМЫ ТРЕБУЮТ ДОПОЛНИТЕЛЬНОГО ВНИМАНИЯ")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
