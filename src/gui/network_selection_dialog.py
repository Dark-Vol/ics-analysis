#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диалог для выбора сохраненной сети
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict
from ..database.database_manager import DatabaseManager
from ..gui.themes.blood_angels_theme import BloodAngelsTheme

class NetworkSelectionDialog:
    """Диалог для выбора сохраненной сети"""
    
    def __init__(self, parent, db_manager: DatabaseManager, main_window=None):
        self.parent = parent
        self.db_manager = db_manager
        self.main_window = main_window
        self.result = None
        self.theme = BloodAngelsTheme()
        
        # Создание диалогового окна
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Выбор сети")
        self.dialog.geometry("600x400")
        self.dialog.resizable(True, True)
        
        # Делаем диалог модальным
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Центрирование диалога
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Применяем военную тему
        self._apply_military_theme()
        
        # Создание виджетов
        self._create_widgets()
        
        # Загрузка списка сетей
        self._load_networks()
    
    def _apply_military_theme(self):
        """Применяет военную тему к диалогу"""
        self.dialog.configure(bg=self.theme.COLORS['bg_primary'])
        
        # Стили для ttk виджетов
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка стилей
        style.configure('Military.TFrame', background=self.theme.COLORS['bg_secondary'])
        style.configure('Military.TLabel', 
                       background=self.theme.COLORS['bg_secondary'],
                       foreground=self.theme.COLORS['text_primary'],
                       font=self.theme.FONTS['title'])
        style.configure('Military.Treeview',
                       background=self.theme.COLORS['bg_secondary'],
                       foreground=self.theme.COLORS['text_primary'],
                       fieldbackground=self.theme.COLORS['bg_secondary'])
        style.configure('Military.TButton',
                       background=self.theme.COLORS['primary_gold'],
                       foreground=self.theme.COLORS['text_primary'])
    
    def _create_widgets(self):
        """Создает виджеты диалога"""
        # Главный фрейм
        main_frame = ttk.Frame(self.dialog, style='Military.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="ВЫБОР СОХРАНЕННОЙ СЕТИ",
                               style='Military.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Фрейм для списка сетей
        list_frame = ttk.Frame(main_frame, style='Military.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Заголовки колонок
        headers = ['ID', 'Название', 'Узлов', 'Связей', 'Дата создания']
        
        # Создание Treeview
        self.networks_tree = ttk.Treeview(list_frame, columns=headers, show='headings', style='Military.Treeview')
        
        # Настройка колонок
        for header in headers:
            self.networks_tree.heading(header, text=header)
            if header == 'Название':
                self.networks_tree.column(header, width=200, minwidth=150)
            elif header == 'Дата создания':
                self.networks_tree.column(header, width=150, minwidth=120)
            else:
                self.networks_tree.column(header, width=80, minwidth=60)
        
        # Скроллбар для списка
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.networks_tree.yview)
        self.networks_tree.configure(yscrollcommand=scrollbar.set)
        
        # Упаковка списка и скроллбара
        self.networks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Привязка события двойного клика
        self.networks_tree.bind('<Double-1>', self._on_double_click)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame, style='Military.TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Кнопка "Загрузить"
        self.load_button = ttk.Button(button_frame, 
                                     text="ЗАГРУЗИТЬ",
                                     command=self._load_selected_network,
                                     style='Military.TButton')
        self.load_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопка "Удалить"
        self.delete_button = ttk.Button(button_frame, 
                                       text="УДАЛИТЬ",
                                       command=self._delete_selected_network,
                                       style='Military.TButton')
        self.delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопка "Удалить все"
        self.delete_all_button = ttk.Button(button_frame, 
                                           text="УДАЛИТЬ ВСЕ",
                                           command=self._delete_all_networks,
                                           style='Military.TButton')
        self.delete_all_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Кнопка "Отмена"
        self.cancel_button = ttk.Button(button_frame, 
                                       text="ОТМЕНА",
                                       command=self._cancel,
                                       style='Military.TButton')
        self.cancel_button.pack(side=tk.RIGHT)
        
        # Привязка событий клавиатуры
        self.dialog.bind('<Return>', lambda e: self._load_selected_network())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _load_networks(self):
        """Загружает список сохраненных сетей"""
        try:
            # Очищаем список
            for item in self.networks_tree.get_children():
                self.networks_tree.delete(item)
            
            # Получаем список сетей из базы данных
            networks = self.db_manager.get_all_networks()
            
            if not networks:
                # Добавляем сообщение, если сетей нет
                self.networks_tree.insert('', 'end', values=('', 'Сохраненных сетей не найдено', '', '', ''))
                self.load_button.configure(state='disabled')
                self.delete_button.configure(state='disabled')
                return
            
            # Заполняем список
            for network in networks:
                self.networks_tree.insert('', 'end', values=(
                    network.get('id', ''),
                    network.get('name', 'Без названия'),
                    network.get('node_count', 0),
                    network.get('link_count', 0),
                    network.get('created_at', 'Неизвестно')
                ))
            
            # Активируем кнопки
            self.load_button.configure(state='normal')
            self.delete_button.configure(state='normal')
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список сетей: {str(e)}")
            self.load_button.configure(state='disabled')
            self.delete_button.configure(state='disabled')
    
    def _load_selected_network(self):
        """Загружает выбранную сеть"""
        selection = self.networks_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сеть для загрузки")
            return
        
        item = self.networks_tree.item(selection[0])
        network_id = item['values'][0]
        network_name = item['values'][1]
        
        if not network_id:
            messagebox.showwarning("Предупреждение", "Не удалось определить ID сети")
            return
        
        try:
            # Загружаем данные сети из базы данных
            network_data = self.db_manager.get_network(network_id)
            
            if network_data:
                # Получаем время анализа из данных сети
                analysis_time = network_data.get('analysis_time', 300)
                
                self.result = {
                    'action': 'load',
                    'network_id': network_id,
                    'network_name': network_name,
                    'network_data': network_data,
                    'analysis_time': analysis_time
                }
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить данные сети")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке сети: {str(e)}")
    
    def _delete_selected_network(self):
        """Удаляет выбранную сеть"""
        selection = self.networks_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сеть для удаления")
            return
        
        item = self.networks_tree.item(selection[0])
        network_id = item['values'][0]
        network_name = item['values'][1]
        
        if not network_id:
            messagebox.showwarning("Предупреждение", "Не удалось определить ID сети")
            return
        
        # Подтверждение удаления
        result = messagebox.askyesno("Подтверждение", 
                                   f"Вы уверены, что хотите удалить сеть '{network_name}'?")
        
        if result:
            try:
                # Удаляем сеть из базы данных
                success = self.db_manager.delete_network(network_id)
                
                if success:
                    # Логируем удаление сети
                    if self.main_window and hasattr(self.main_window, 'program_state_manager'):
                        self.main_window.program_state_manager.log_network_deleted(network_id, network_name)
                    
                    messagebox.showinfo("Успех", f"Сеть '{network_name}' удалена")
                    # Обновляем список
                    self._load_networks()
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить сеть")
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении сети: {str(e)}")
    
    def _delete_all_networks(self):
        """Удаляет все сети"""
        try:
            # Получаем количество сетей
            networks = self.db_manager.get_all_networks()
            if not networks:
                messagebox.showinfo("Информация", "Нет сетей для удаления")
                return
            
            # Подтверждение удаления
            result = messagebox.askyesno("Подтверждение", 
                                       f"Вы уверены, что хотите удалить ВСЕ {len(networks)} сетей?\n\nЭто действие нельзя отменить!")
            
            if result:
                try:
                    # Удаляем все сети
                    deleted_count = self.db_manager.delete_all_networks()
                    
                    # Логируем удаление всех сетей
                    if self.main_window and hasattr(self.main_window, 'program_state_manager'):
                        self.main_window.program_state_manager.log_networks_deleted_all(deleted_count)
                    
                    messagebox.showinfo("Успех", f"Удалено {deleted_count} сетей")
                    
                    # Обновляем список
                    self._load_networks()
                    
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при удалении всех сетей: {str(e)}")
                    
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении списка сетей: {str(e)}")
    
    def _on_double_click(self, event):
        """Обработчик двойного клика по элементу списка"""
        self._load_selected_network()
    
    def _cancel(self):
        """Отменяет диалог"""
        self.result = {'action': 'cancel'}
        self.dialog.destroy()
    
    def show(self):
        """Показывает диалог и возвращает результат"""
        self.dialog.wait_window()
        return self.result
