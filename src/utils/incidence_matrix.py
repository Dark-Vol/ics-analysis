#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Утиліти для роботи з матрицею інцидентності мережі
"""

import numpy as np
import json
import pickle
from typing import Dict, List, Tuple, Optional
import os


class IncidenceMatrixManager:
    """Менеджер для роботи з матрицею інцидентності"""
    
    def __init__(self, matrix_file: str = "matrix.db"):
        self.matrix_file = matrix_file
        self.matrix = None
        self.node_mapping = {}  # Мапінг імен вузлів до індексів
    
    def create_matrix_from_network(self, network_dict: Dict[str, List[str]]) -> np.ndarray:
        """
        Створює матрицю інцидентності з словника мережі
        
        Args:
            network_dict: Словник мережі у форматі {'a': ['b', 'c'], 'b': ['c'], 'c': []}
        
        Returns:
            Матриця інцидентності як numpy array
        """
        # Отримуємо всі унікальні вузли
        all_nodes = set()
        for node, connections in network_dict.items():
            all_nodes.add(node)
            all_nodes.update(connections)
        
        all_nodes = sorted(list(all_nodes))
        n = len(all_nodes)
        
        # Створюємо мапінг вузлів до індексів
        self.node_mapping = {node: i for i, node in enumerate(all_nodes)}
        
        # Створюємо матрицю інцидентності
        matrix = np.zeros((n, n), dtype=int)
        
        # Заповнюємо матрицю
        for from_node, connections in network_dict.items():
            from_idx = self.node_mapping[from_node]
            for to_node in connections:
                to_idx = self.node_mapping[to_node]
                matrix[from_idx][to_idx] = 1
        
        self.matrix = matrix
        return matrix
    
    def save_matrix(self, file_format: str = 'db') -> bool:
        """
        Зберігає матрицю інцидентності у файл
        
        Args:
            file_format: Формат файлу ('db', 'json', 'pickle')
        
        Returns:
            True якщо збереження успішне
        """
        if self.matrix is None:
            return False
        
        try:
            if file_format == 'db':
                # Використовуємо pickle для .db файлу
                with open(self.matrix_file, 'wb') as f:
                    pickle.dump({
                        'matrix': self.matrix,
                        'node_mapping': self.node_mapping
                    }, f)
            elif file_format == 'json':
                # Конвертуємо numpy array в список для JSON
                json_file = self.matrix_file.replace('.db', '.json')
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'matrix': self.matrix.tolist(),
                        'node_mapping': self.node_mapping
                    }, f, ensure_ascii=False, indent=2)
            elif file_format == 'pickle':
                pickle_file = self.matrix_file.replace('.db', '.pkl')
                with open(pickle_file, 'wb') as f:
                    pickle.dump({
                        'matrix': self.matrix,
                        'node_mapping': self.node_mapping
                    }, f)
            
            return True
        except Exception as e:
            print(f"Помилка збереження матриці: {e}")
            return False
    
    def load_matrix(self, file_format: str = 'db') -> bool:
        """
        Завантажує матрицю інцидентності з файлу
        
        Args:
            file_format: Формат файлу ('db', 'json', 'pickle')
        
        Returns:
            True якщо завантаження успішне
        """
        try:
            if file_format == 'db':
                if not os.path.exists(self.matrix_file):
                    return False
                with open(self.matrix_file, 'rb') as f:
                    data = pickle.load(f)
            elif file_format == 'json':
                json_file = self.matrix_file.replace('.db', '.json')
                if not os.path.exists(json_file):
                    return False
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['matrix'] = np.array(data['matrix'])
            elif file_format == 'pickle':
                pickle_file = self.matrix_file.replace('.db', '.pkl')
                if not os.path.exists(pickle_file):
                    return False
                with open(pickle_file, 'rb') as f:
                    data = pickle.load(f)
            
            self.matrix = data['matrix']
            self.node_mapping = data['node_mapping']
            return True
        except Exception as e:
            print(f"Помилка завантаження матриці: {e}")
            return False
    
    def get_network_from_matrix(self) -> Dict[str, List[str]]:
        """
        Конвертує матрицю інцидентності назад у словник мережі
        
        Returns:
            Словник мережі
        """
        if self.matrix is None:
            return {}
        
        # Створюємо зворотний мапінг
        reverse_mapping = {i: node for node, i in self.node_mapping.items()}
        
        network_dict = {}
        n = self.matrix.shape[0]
        
        for i in range(n):
            from_node = reverse_mapping[i]
            connections = []
            for j in range(n):
                if self.matrix[i][j] == 1:
                    to_node = reverse_mapping[j]
                    connections.append(to_node)
            network_dict[from_node] = connections
        
        return network_dict
    
    def get_matrix_info(self) -> Dict:
        """
        Повертає інформацію про матрицю
        
        Returns:
            Словник з інформацією про матрицю
        """
        if self.matrix is None:
            return {}
        
        return {
            'size': self.matrix.shape,
            'total_edges': int(np.sum(self.matrix)),
            'node_count': self.matrix.shape[0],
            'node_mapping': self.node_mapping,
            'matrix': self.matrix.tolist()
        }
    
    def calculate_connectivity_metrics(self) -> Dict[str, float]:
        """
        Обчислює метрики зв'язності на основі матриці
        
        Returns:
            Словник з метриками зв'язності
        """
        if self.matrix is None:
            return {}
        
        n = self.matrix.shape[0]
        
        # Кількість ребер
        total_edges = int(np.sum(self.matrix))
        
        # Максимальна кількість можливих ребер (для орієнтованого графа)
        max_possible_edges = n * n
        
        # Щільність мережі
        density = total_edges / max_possible_edges if max_possible_edges > 0 else 0
        
        # Середня ступінь вузлів
        out_degrees = np.sum(self.matrix, axis=1)
        in_degrees = np.sum(self.matrix, axis=0)
        avg_out_degree = np.mean(out_degrees)
        avg_in_degree = np.mean(in_degrees)
        
        return {
            'total_edges': total_edges,
            'density': density,
            'avg_out_degree': float(avg_out_degree),
            'avg_in_degree': float(avg_in_degree),
            'max_out_degree': int(np.max(out_degrees)),
            'max_in_degree': int(np.max(in_degrees))
        }



