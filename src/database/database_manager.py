#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер базы данных для сохранения и загрузки сетей
"""

import json
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import os
from ..models.network_model import NetworkModel, NetworkNode, NetworkLink

class DatabaseManager:
    """Менеджер базы данных для работы с сетевыми конфигурациями"""
    
    def __init__(self, db_path: str = "networks.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Инициализирует базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Создание таблицы для сетей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS networks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                analysis_time INTEGER DEFAULT 300,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                network_data TEXT NOT NULL
            )
        ''')
        
        # Создание таблицы для узлов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network_id INTEGER NOT NULL,
                node_id INTEGER NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                capacity REAL NOT NULL,
                reliability REAL NOT NULL,
                processing_delay REAL NOT NULL,
                FOREIGN KEY (network_id) REFERENCES networks (id),
                UNIQUE(network_id, node_id)
            )
        ''')
        
        # Создание таблицы для связей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS network_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network_id INTEGER NOT NULL,
                source INTEGER NOT NULL,
                target INTEGER NOT NULL,
                bandwidth REAL NOT NULL,
                latency REAL NOT NULL,
                reliability REAL NOT NULL,
                distance REAL NOT NULL,
                FOREIGN KEY (network_id) REFERENCES networks (id)
            )
        ''')
        
        # Миграция: добавление поля analysis_time если его нет
        try:
            # Проверяем, существует ли поле analysis_time
            cursor.execute("PRAGMA table_info(networks)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'analysis_time' not in column_names:
                # Добавляем поле без DEFAULT (SQLite не поддерживает DEFAULT в ALTER TABLE)
                cursor.execute("ALTER TABLE networks ADD COLUMN analysis_time INTEGER")
                
                # Устанавливаем значение по умолчанию для существующих записей
                cursor.execute("UPDATE networks SET analysis_time = 300 WHERE analysis_time IS NULL")
                
                conn.commit()
                print("[INFO] Добавлено поле analysis_time в таблицу networks")
            else:
                print("[INFO] Поле analysis_time уже существует")
                
        except sqlite3.OperationalError as e:
            print(f"[WARNING] Ошибка при добавлении поля analysis_time: {e}")
        
        conn.commit()
        conn.close()
    
    def save_network(self, network: NetworkModel, name: str, description: str = "", analysis_time: int = 300) -> int:
        """Сохраняет сеть в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Проверяем, существует ли сеть с таким именем
            cursor.execute("SELECT id FROM networks WHERE name = ?", (name,))
            existing = cursor.fetchone()
            
            if existing:
                # Обновляем существующую сеть
                network_id = existing[0]
                cursor.execute('''
                    UPDATE networks 
                    SET description = ?, analysis_time = ?, updated_at = CURRENT_TIMESTAMP, network_data = ?
                    WHERE id = ?
                ''', (description, analysis_time, json.dumps(self._serialize_network(network)), network_id))
                
                # Удаляем старые узлы и связи
                cursor.execute("DELETE FROM network_nodes WHERE network_id = ?", (network_id,))
                cursor.execute("DELETE FROM network_links WHERE network_id = ?", (network_id,))
            else:
                # Создаем новую сеть
                cursor.execute('''
                    INSERT INTO networks (name, description, analysis_time, network_data)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, analysis_time, json.dumps(self._serialize_network(network))))
                network_id = cursor.lastrowid
            
            # Сохраняем узлы
            for node in network.nodes:
                cursor.execute('''
                    INSERT INTO network_nodes 
                    (network_id, node_id, x, y, capacity, reliability, processing_delay)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (network_id, node.id, node.x, node.y, node.capacity, 
                      node.reliability, node.processing_delay))
            
            # Сохраняем связи
            for link in network.links:
                cursor.execute('''
                    INSERT INTO network_links 
                    (network_id, source, target, bandwidth, latency, reliability, distance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (network_id, link.source, link.target, link.bandwidth,
                      link.latency, link.reliability, link.distance))
            
            conn.commit()
            return network_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def load_network(self, network_id: int) -> Optional[NetworkModel]:
        """Загружает сеть из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Загружаем основную информацию о сети
            cursor.execute("SELECT network_data FROM networks WHERE id = ?", (network_id,))
            result = cursor.fetchone()
            
            if not result:
                return None
            
            # Загружаем узлы
            cursor.execute('''
                SELECT node_id, x, y, capacity, reliability, processing_delay
                FROM network_nodes WHERE network_id = ? ORDER BY node_id
            ''', (network_id,))
            
            nodes_data = cursor.fetchall()
            nodes = []
            for node_data in nodes_data:
                node = NetworkNode(
                    id=node_data[0],
                    x=node_data[1],
                    y=node_data[2],
                    capacity=node_data[3],
                    reliability=node_data[4],
                    processing_delay=node_data[5]
                )
                nodes.append(node)
            
            # Загружаем связи
            cursor.execute('''
                SELECT source, target, bandwidth, latency, reliability, distance
                FROM network_links WHERE network_id = ? ORDER BY source, target
            ''', (network_id,))
            
            links_data = cursor.fetchall()
            links = []
            for link_data in links_data:
                link = NetworkLink(
                    source=link_data[0],
                    target=link_data[1],
                    bandwidth=link_data[2],
                    latency=link_data[3],
                    reliability=link_data[4],
                    distance=link_data[5]
                )
                links.append(link)
            
            # Создаем объект NetworkModel
            network = NetworkModel.__new__(NetworkModel)
            network.nodes = nodes
            network.links = links
            network.graph = self._rebuild_graph(nodes, links)
            
            return network
            
        except Exception as e:
            raise e
        finally:
            conn.close()
    
    def load_network_by_name(self, name: str) -> Optional[NetworkModel]:
        """Загружает сеть по имени"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id FROM networks WHERE name = ?", (name,))
            result = cursor.fetchone()
            
            if result:
                return self.load_network(result[0])
            return None
            
        finally:
            conn.close()
    
    def get_all_networks(self) -> List[Dict[str, Any]]:
        """Получает список всех сохраненных сетей"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, name, description, analysis_time, created_at, updated_at
                FROM networks ORDER BY updated_at DESC
            ''')
            
            networks = []
            for row in cursor.fetchall():
                networks.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'analysis_time': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                })
            
            return networks
            
        finally:
            conn.close()
    
    def get_network(self, network_id: int) -> Optional[Dict[str, Any]]:
        """Получает данные сети по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, name, description, analysis_time, created_at, updated_at, network_data
                FROM networks 
                WHERE id = ?
            ''', (network_id,))
            
            row = cursor.fetchone()
            if row:
                network_data = json.loads(row[6])  # network_data теперь в позиции 6
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'analysis_time': row[3],
                    'created_at': row[4],
                    'updated_at': row[5],
                    'network_data': network_data
                }
            return None
            
        finally:
            conn.close()
    
    def delete_network(self, network_id: int) -> bool:
        """Удаляет сеть из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM networks WHERE id = ?", (network_id,))
            cursor.execute("DELETE FROM network_nodes WHERE network_id = ?", (network_id,))
            cursor.execute("DELETE FROM network_links WHERE network_id = ?", (network_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_all_networks(self) -> int:
        """Удаляет все сети из базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Сначала получаем количество сетей для возврата
            cursor.execute("SELECT COUNT(*) FROM networks")
            count = cursor.fetchone()[0]
            
            # Удаляем все данные
            cursor.execute("DELETE FROM network_links")
            cursor.execute("DELETE FROM network_nodes")
            cursor.execute("DELETE FROM networks")
            
            conn.commit()
            return count
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _serialize_network(self, network: NetworkModel) -> Dict[str, Any]:
        """Сериализует сеть для сохранения"""
        return {
            'nodes': [asdict(node) for node in network.nodes],
            'links': [asdict(link) for link in network.links],
            'metrics': network.get_network_metrics()
        }
    
    def _rebuild_graph(self, nodes: List[NetworkNode], links: List[NetworkLink]):
        """Восстанавливает граф из узлов и связей"""
        import networkx as nx
        
        graph = nx.Graph()
        
        # Добавляем узлы
        for node in nodes:
            graph.add_node(node.id, **asdict(node))
        
        # Добавляем связи
        for link in links:
            graph.add_edge(link.source, link.target, **asdict(link))
        
        return graph


