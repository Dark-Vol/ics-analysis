#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрація покращеного інтерактивного просмотрщика мережі
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Додаємо шлях до модулів
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from gui.enhanced_interactive_network_viewer import EnhancedInteractiveNetworkViewer
from gui.themes.blood_angels_theme import BloodAngelsTheme
from utils.incidence_matrix import IncidenceMatrixManager
from analytics.birnbaum_reliability import BirnbaumReliabilityAnalyzer


def demo_incidence_matrix():
    """Демонстрація роботи з матрицею інцидентності"""
    print("=== ДЕМОНСТРАЦІЯ МАТРИЦІ ІНЦИДЕНТНОСТІ ===")
    
    # Створюємо тестову мережу
    network_dict = {
        'a': ['b', 'c'],
        'b': ['c', 'd'],
        'c': ['d'],
        'd': []
    }
    
    # Створюємо менеджер матриці
    matrix_manager = IncidenceMatrixManager("demo_matrix.db")
    
    # Створюємо матрицю інцидентності
    matrix = matrix_manager.create_matrix_from_network(network_dict)
    
    print(f"Мережа: {network_dict}")
    print(f"Матриця інцидентності:")
    print(matrix)
    print(f"Мапінг вузлів: {matrix_manager.node_mapping}")
    
    # Обчислюємо метрики зв'язності
    metrics = matrix_manager.calculate_connectivity_metrics()
    print(f"Метрики зв'язності: {metrics}")
    
    # Зберігаємо матрицю
    if matrix_manager.save_matrix():
        print("Матрицю збережено успішно")
    
    print()


def demo_birnbaum_reliability():
    """Демонстрація аналізу надійності за критерієм Бірнбаума"""
    print("=== ДЕМОНСТРАЦІЯ КРИТЕРІЮ БІРНБАУМА ===")
    
    # Створюємо тестову мережу
    network_dict = {
        'node_0': ['node_1', 'node_2'],
        'node_1': ['node_2', 'node_3'],
        'node_2': ['node_3', 'node_4'],
        'node_3': ['node_4'],
        'node_4': []
    }
    
    # Створюємо аналізатор надійності
    analyzer = BirnbaumReliabilityAnalyzer(network_dict, 'node_0')
    
    # Обчислюємо коефіцієнт надійності для різних сценаріїв
    test_scenarios = [
        [('node_0', 'node_1')],  # Видаляємо одне ребро
        [('node_0', 'node_1'), ('node_1', 'node_2')],  # Видаляємо два ребра
        [('node_0', 'node_1'), ('node_0', 'node_2')],  # Видаляємо всі ребра від головного вузла
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        coeff = analyzer.calculate_birnbaum_coefficient(scenario)
        print(f"Сценарій {i}: Видалені ребра {scenario}")
        print(f"  Коефіцієнт Бірнбаума: {coeff:.3f}")
        print(f"  Тип відмови: {analyzer._classify_failure(coeff)}")
        print()
    
    # Генеруємо звіт про надійність
    report = analyzer.generate_reliability_report()
    print("Звіт про надійність:")
    print(report)
    print()


def demo_enhanced_viewer():
    """Демонстрація покращеного просмотрщика"""
    print("=== ДЕМОНСТРАЦІЯ ПОКРАЩЕНОГО ПРОСМОТРЩИКА ===")
    
    # Створюємо головне вікно
    root = tk.Tk()
    root.title("Демонстрація покращеного просмотрщика мережі")
    root.geometry("1200x800")
    
    # Налаштовуємо тему
    theme = BloodAngelsTheme()
    theme.configure_styles(root)
    
    try:
        # Створюємо покращений просмотрщик
        viewer = EnhancedInteractiveNetworkViewer(root)
        
        print("Покращений просмотрщик створено успішно!")
        print("Функції:")
        print("- Покращене відображення зв'язків з плавними анімаціями")
        print("- Force-directed layout для природного позиціювання вузлів")
        print("- Зменшені розміри вузлів для кращого сприйняття")
        print("- Автоматичне збереження мережі в .db форматі")
        print("- Матриця інцидентності")
        print("- Аналіз надійності за критерієм Бірнбаума")
        print("- Ручне створення мережі з ймовірністю з'єднання")
        print()
        print("Натисніть 'Створити випадкову мережу' для тестування")
        
        # Запускаємо головний цикл
        root.mainloop()
        
    except Exception as e:
        print(f"Помилка створення просмотрщика: {e}")
        messagebox.showerror("Помилка", f"Помилка створення просмотрщика: {e}")


def main():
    """Головна функція демонстрації"""
    print("ДЕМОНСТРАЦІЯ ПОКРАЩЕНОГО ІНТЕРАКТИВНОГО ПРОСМОТРЩИКА МЕРЕЖІ")
    print("=" * 60)
    print()
    
    # Демонстрація матриці інцидентності
    demo_incidence_matrix()
    
    # Демонстрація критерію Бірнбаума
    demo_birnbaum_reliability()
    
    # Демонстрація покращеного просмотрщика
    print("Запуск GUI демонстрації...")
    demo_enhanced_viewer()


if __name__ == "__main__":
    main()