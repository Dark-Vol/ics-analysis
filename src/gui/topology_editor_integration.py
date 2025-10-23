#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Интеграция интерактивного редактора топологии в основное приложение
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
from typing import Dict, List, Optional

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class TopologyEditorIntegration:
    """Интеграция редактора топологии с основным приложением"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.topology_editor_window = None
        self.topology_editor = None
    
    def show_topology_editor(self):
        """Показывает редактор топологии"""
        try:
            # Импортируем редактор
            from src.gui.topology_editor import InteractiveNetworkEditor
            
            # Создаем новое окно для редактора
            self.topology_editor_window = tk.Toplevel(self.main_window.root)
            self.topology_editor_window.title("Редактор топологии сети")
            self.topology_editor_window.geometry("1400x900")
            
            # Создаем редактор
            self.topology_editor = InteractiveNetworkEditor(self.topology_editor_window)
            
            # Добавляем кнопку интеграции с основным приложением
            self.add_integration_buttons()
            
            # Обработчик закрытия окна
            self.topology_editor_window.protocol("WM_DELETE_WINDOW", self.on_editor_close)
            
            # Центрируем окно
            self.center_window(self.topology_editor_window)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть редактор топологии: {e}")
    
    def add_integration_buttons(self):
        """Добавляет кнопки интеграции с основным приложением"""
        if not self.topology_editor_window:
            return
        
        # Создаем фрейм для кнопок интеграции
        integration_frame = tk.Frame(self.topology_editor_window)
        integration_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Кнопка "Применить к симулятору"
        apply_btn = tk.Button(integration_frame, text="Применить к симулятору", 
                            command=self.apply_to_simulator, bg="#4CAF50", fg="white")
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка "Загрузить из симулятора"
        load_btn = tk.Button(integration_frame, text="Загрузить из симулятора", 
                           command=self.load_from_simulator, bg="#2196F3", fg="white")
        load_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка "Экспорт для анализа надежности"
        export_btn = tk.Button(integration_frame, text="Экспорт для анализа надежности", 
                             command=self.export_for_reliability_analysis, bg="#FF9800", fg="white")
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка "Закрыть"
        close_btn = tk.Button(integration_frame, text="Закрыть", 
                            command=self.on_editor_close, bg="#F44336", fg="white")
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def apply_to_simulator(self):
        """Применяет топологию к симулятору"""
        if not self.topology_editor:
            messagebox.showwarning("Предупреждение", "Редактор топологии не открыт")
            return
        
        try:
            # Получаем данные сети из редактора
            network_data = self.topology_editor.get_network_data()
            
            # Преобразуем данные в формат симулятора
            simulator_data = self.convert_to_simulator_format(network_data)
            
            # Применяем к симулятору
            if hasattr(self.main_window, 'simulator') and self.main_window.simulator:
                self.update_simulator_topology(simulator_data)
                messagebox.showinfo("Успех", "Топология применена к симулятору")
            else:
                messagebox.showwarning("Предупреждение", "Симулятор не инициализирован")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось применить топологию: {e}")
    
    def load_from_simulator(self):
        """Загружает топологию из симулятора"""
        if not self.topwork_editor:
            messagebox.showwarning("Предупреждение", "Редактор топологии не открыт")
            return
        
        try:
            # Получаем данные из симулятора
            if hasattr(self.main_window, 'simulator') and self.main_window.simulator:
                simulator_data = self.extract_from_simulator()
                
                # Преобразуем в формат редактора
                network_data = self.convert_from_simulator_format(simulator_data)
                
                # Загружаем в редактор
                self.topology_editor.network_data = network_data
                self.topology_editor.update_nodes_list()
                self.topology_editor.update_edges_list()
                self.topology_editor.draw_network()
                
                messagebox.showinfo("Успех", "Топология загружена из симулятора")
            else:
                messagebox.showwarning("Предупреждение", "Симулятор не инициализирован")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить топологию: {e}")
    
    def export_for_reliability_analysis(self):
        """Экспортирует данные для анализа надежности"""
        if not self.topology_editor:
            messagebox.showwarning("Предупреждение", "Редактор топологии не открыт")
            return
        
        try:
            # Получаем данные сети
            network_data = self.topology_editor.get_network_data()
            
            # Создаем вероятности для анализа надежности
            probabilities = {}
            for node_data in network_data['nodes']:
                probabilities[node_data['id']] = node_data.get('reliability', 0.95)
            
            # Создаем структуру для анализа
            analysis_data = {
                'network': network_data,
                'probabilities': probabilities
            }
            
            # Запускаем анализ надежности
            from src.gui.reliability_integration import ReliabilityAnalysisDialog
            
            dialog = ReliabilityAnalysisDialog(self.topology_editor_window, network_data, probabilities)
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def convert_to_simulator_format(self, network_data: Dict) -> Dict:
        """Преобразует данные редактора в формат симулятора"""
        simulator_data = {
            'nodes': [],
            'links': []
        }
        
        # Преобразуем узлы
        for node_data in network_data['nodes']:
            simulator_node = {
                'id': node_data['id'],
                'type': node_data.get('type', 'server'),
                'x': node_data.get('x', 0),
                'y': node_data.get('y', 0),
                'capacity': node_data.get('capacity', 1000),
                'reliability': node_data.get('reliability', 0.95)
            }
            simulator_data['nodes'].append(simulator_node)
        
        # Преобразуем связи
        for from_node, connections in network_data['connections'].items():
            for to_node in connections:
                # Избегаем дублирования
                link_id = f"{from_node}-{to_node}"
                reverse_link_id = f"{to_node}-{from_node}"
                
                if not any(link.get('id') == link_id or link.get('id') == reverse_link_id 
                          for link in simulator_data['links']):
                    
                    # Получаем свойства связи
                    edge_props_key = f"{from_node}-{to_node}"
                    edge_properties = network_data.get('edge_properties', {}).get(edge_props_key, {})
                    
                    simulator_link = {
                        'id': link_id,
                        'source': from_node,
                        'target': to_node,
                        'bandwidth': edge_properties.get('bandwidth', 100),
                        'latency': edge_properties.get('latency', 5.0),
                        'reliability': edge_properties.get('reliability', 0.98)
                    }
                    simulator_data['links'].append(simulator_link)
        
        return simulator_data
    
    def convert_from_simulator_format(self, simulator_data: Dict) -> Dict:
        """Преобразует данные симулятора в формат редактора"""
        network_data = {
            'nodes': [],
            'connections': {},
            'edge_properties': {}
        }
        
        # Преобразуем узлы
        for node_data in simulator_data.get('nodes', []):
            editor_node = {
                'id': node_data['id'],
                'x': node_data.get('x', 0),
                'y': node_data.get('y', 0),
                'type': node_data.get('type', 'server'),
                'capacity': node_data.get('capacity', 1000),
                'reliability': node_data.get('reliability', 0.95)
            }
            network_data['nodes'].append(editor_node)
            network_data['connections'][node_data['id']] = []
        
        # Преобразуем связи
        for link_data in simulator_data.get('links', []):
            source = link_data['source']
            target = link_data['target']
            
            # Добавляем связи в обе стороны
            if source in network_data['connections']:
                network_data['connections'][source].append(target)
            if target in network_data['connections']:
                network_data['connections'][target].append(source)
            
            # Сохраняем свойства связи
            edge_key = f"{source}-{target}"
            network_data['edge_properties'][edge_key] = {
                'bandwidth': link_data.get('bandwidth', 100),
                'latency': link_data.get('latency', 5.0),
                'reliability': link_data.get('reliability', 0.98)
            }
        
        return network_data
    
    def update_simulator_topology(self, simulator_data: Dict):
        """Обновляет топологию симулятора"""
        # Здесь нужно реализовать обновление симулятора
        # Это зависит от конкретной реализации симулятора
        pass
    
    def extract_from_simulator(self) -> Dict:
        """Извлекает данные топологии из симулятора"""
        # Здесь нужно реализовать извлечение данных из симулятора
        # Это зависит от конкретной реализации симулятора
        return {'nodes': [], 'links': []}
    
    def on_editor_close(self):
        """Обработчик закрытия редактора"""
        if self.topology_editor_window:
            self.topology_editor_window.destroy()
            self.topology_editor_window = None
            self.topology_editor = None
    
    def center_window(self, window):
        """Центрирует окно на экране"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')


def integrate_topology_editor_with_main_window(main_window):
    """Интегрирует редактор топологии с главным окном"""
    
    # Создаем интеграцию
    integration = TopologyEditorIntegration(main_window)
    
    # Добавляем функцию в главное окно
    main_window.show_topology_editor = integration.show_topology_editor
    
    # Добавляем пункт меню
    if hasattr(main_window, '_create_menu'):
        original_create_menu = main_window._create_menu
        
        def enhanced_create_menu():
            original_create_menu()
            
            # Добавляем пункт в меню "Сеть" или создаем новое меню
            try:
                # Ищем существующее меню "Сеть"
                network_menu = None
                for child in main_window.root.winfo_children():
                    if isinstance(child, tk.Menu):
                        try:
                            network_menu = child.nametowidget('network')
                        except:
                            pass
                
                if network_menu:
                    network_menu.add_separator()
                    network_menu.add_command(
                        label="Редактор топологии",
                        command=integration.show_topology_editor
                    )
                else:
                    # Создаем новое меню "Топология"
                    menubar = main_window.root.nametowidget('!menu')
                    topology_menu = tk.Menu(menubar, tearoff=0)
                    menubar.add_cascade(label="Топология", menu=topology_menu)
                    topology_menu.add_command(
                        label="Редактор топологии",
                        command=integration.show_topology_editor
                    )
                    topology_menu.add_separator()
                    topology_menu.add_command(
                        label="Анализ связности",
                        command=lambda: messagebox.showinfo("Инфо", "Используйте редактор топологии для анализа связности")
                    )
                    
            except Exception as e:
                print(f"Ошибка при добавлении меню: {e}")
        
        main_window._create_menu = enhanced_create_menu
    
    return integration


def create_standalone_topology_editor():
    """Создает автономный редактор топологии"""
    root = tk.Tk()
    root.title("Редактор топологии сети")
    root.geometry("1400x900")
    
    # Создаем редактор
    from src.gui.topology_editor import InteractiveNetworkEditor
    editor = InteractiveNetworkEditor(root)
    
    return root, editor


if __name__ == "__main__":
    # Тестирование автономного редактора
    root, editor = create_standalone_topology_editor()
    root.mainloop()
