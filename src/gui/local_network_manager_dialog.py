"""
Диалог для управления локальными сетями
LocalNetworkManagerDialog - интерфейс для работы с локальным хранилищем сетей
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Optional, Any
import os
from src.storage.network_storage import NetworkStorage
from src.gui.themes.blood_angels_theme import BloodAngelsTheme


class LocalNetworkManagerDialog:
    """
    Диалог для управления локальными сетями
    
    Позволяет:
    - Просматривать список сохраненных сетей
    - Загружать сети из локальных файлов
    - Сохранять текущую сеть в локальный файл
    - Удалять локальные сети
    - Экспортировать сети в текстовый формат
    """
    
    def __init__(self, parent, storage_dir: str = "networks"):
        """
        Инициализация диалога
        
        Args:
            parent: Родительское окно
            storage_dir: Директория для хранения сетей
        """
        self.parent = parent
        self.storage = NetworkStorage(storage_dir)
        self.theme = BloodAngelsTheme()
        self.result = None
        
        # Создание диалога
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Управление локальными сетями")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Центрирование диалога
        self._center_dialog()
        
        # Применение темы
        self._apply_theme()
        
        # Создание интерфейса
        self._create_widgets()
        
        # Загрузка списка сетей
        self._refresh_network_list()
        
        # Обработчики событий
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _center_dialog(self):
        """Центрирует диалог на экране"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _apply_theme(self):
        """Применяет тему Blood Angels"""
        self.dialog.configure(bg=self.theme.COLORS['bg_primary'])
    
    def _create_widgets(self):
        """Создает элементы интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ttk.Label(
            main_frame, 
            text="Управление локальными сетями",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Фрейм для списка сетей
        list_frame = ttk.LabelFrame(main_frame, text="Сохраненные сети")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Список сетей
        self.network_listbox = tk.Listbox(list_frame, height=15)
        self.network_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Скроллбар для списка
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.network_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.network_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Фрейм для информации о сети
        info_frame = ttk.LabelFrame(main_frame, text="Информация о сети")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=6, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Фрейм для кнопок управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки управления
        ttk.Button(
            button_frame, 
            text="Обновить список",
            command=self._refresh_network_list
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Загрузить сеть",
            command=self._load_selected_network
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Удалить сеть",
            command=self._delete_selected_network
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="Экспорт в текст",
            command=self._export_selected_network
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Фрейм для создания новой сети
        create_frame = ttk.LabelFrame(main_frame, text="Создать новую сеть")
        create_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Поле для имени сети
        name_frame = ttk.Frame(create_frame)
        name_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(name_frame, text="Имя сети:").pack(side=tk.LEFT)
        self.network_name_var = tk.StringVar()
        self.network_name_entry = ttk.Entry(name_frame, textvariable=self.network_name_var)
        self.network_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Кнопка создания
        ttk.Button(
            create_frame, 
            text="Создать сеть",
            command=self._create_network_dialog
        ).pack(padx=5, pady=5)
        
        # Фрейм для кнопок диалога
        dialog_frame = ttk.Frame(main_frame)
        dialog_frame.pack(fill=tk.X)
        
        # Кнопки диалога
        ttk.Button(
            dialog_frame, 
            text="Отмена",
            command=self._on_cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            dialog_frame, 
            text="ОК",
            command=self._on_ok
        ).pack(side=tk.RIGHT)
        
        # Обработчик выбора в списке
        self.network_listbox.bind('<<ListboxSelect>>', self._on_network_select)
    
    def _refresh_network_list(self):
        """Обновляет список сетей"""
        self.network_listbox.delete(0, tk.END)
        networks = self.storage.list_networks()
        
        for network_name in networks:
            self.network_listbox.insert(tk.END, network_name)
        
        # Очищаем информацию
        self._clear_info()
    
    def _on_network_select(self, event):
        """Обработчик выбора сети в списке"""
        selection = self.network_listbox.curselection()
        if selection:
            network_name = self.network_listbox.get(selection[0])
            self._show_network_info(network_name)
    
    def _show_network_info(self, network_name: str):
        """Показывает информацию о выбранной сети"""
        info = self.storage.get_network_info(network_name)
        if info:
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            
            info_text = f"""Имя сети: {info['name']}
Размер файла: {info['file_size']} байт
Количество узлов: {info['node_count']}
Количество связей: {info['connection_count']}
Путь к файлу: {info['file_path']}"""
            
            self.info_text.insert(1.0, info_text)
            self.info_text.config(state=tk.DISABLED)
    
    def _clear_info(self):
        """Очищает информацию о сети"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state=tk.DISABLED)
    
    def _load_selected_network(self):
        """Загружает выбранную сеть"""
        selection = self.network_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сеть для загрузки")
            return
        
        network_name = self.network_listbox.get(selection[0])
        network_data = self.storage.load_network(network_name)
        
        if network_data:
            self.result = {
                'action': 'load',
                'network_name': network_name,
                'network_data': network_data
            }
            self.dialog.destroy()
        else:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сеть '{network_name}'")
    
    def _delete_selected_network(self):
        """Удаляет выбранную сеть"""
        selection = self.network_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сеть для удаления")
            return
        
        network_name = self.network_listbox.get(selection[0])
        
        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение", f"Удалить сеть '{network_name}'?"):
            if self.storage.delete_network(network_name):
                messagebox.showinfo("Успех", f"Сеть '{network_name}' удалена")
                self._refresh_network_list()
            else:
                messagebox.showerror("Ошибка", f"Не удалось удалить сеть '{network_name}'")
    
    def _export_selected_network(self):
        """Экспортирует выбранную сеть в текстовый файл"""
        selection = self.network_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите сеть для экспорта")
            return
        
        network_name = self.network_listbox.get(selection[0])
        
        # Выбор файла для сохранения
        filename = filedialog.asksaveasfilename(
            title="Сохранить сеть как текст",
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if filename:
            if self.storage.export_network_to_text(network_name, filename):
                messagebox.showinfo("Успех", f"Сеть '{network_name}' экспортирована в {filename}")
            else:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать сеть '{network_name}'")
    
    def _create_network_dialog(self):
        """Открывает диалог создания новой сети"""
        network_name = self.network_name_var.get().strip()
        if not network_name:
            messagebox.showwarning("Предупреждение", "Введите имя сети")
            return
        
        # Проверяем, не существует ли уже сеть с таким именем
        if self.storage.network_exists(network_name):
            if not messagebox.askyesno("Подтверждение", f"Сеть '{network_name}' уже существует. Перезаписать?"):
                return
        
        # Открываем диалог создания сети
        from src.gui.network_dialog import NetworkDialog
        dialog = NetworkDialog(self.dialog, self.storage)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            # Сохраняем созданную сеть
            network_data = dialog.result.get('network_data')
            if network_data:
                # Конвертируем данные сети в нужный формат
                converted_data = self._convert_network_data(network_data)
                if self.storage.save_network(network_name, converted_data):
                    messagebox.showinfo("Успех", f"Сеть '{network_name}' создана и сохранена")
                    self._refresh_network_list()
                else:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить сеть '{network_name}'")
    
    def _convert_network_data(self, network_data) -> Dict[str, List[str]]:
        """
        Конвертирует данные сети в формат словаря
        
        Args:
            network_data: Данные сети из NetworkDialog
            
        Returns:
            Dict[str, List[str]]: Конвертированные данные
        """
        # Здесь нужно реализовать конвертацию из формата NetworkModel в словарь
        # Пока возвращаем простую структуру для примера
        converted = {}
        
        if hasattr(network_data, 'nodes') and hasattr(network_data, 'links'):
            # Создаем словарь узлов
            for node in network_data.nodes:
                converted[str(node.id)] = []
            
            # Добавляем связи
            for link in network_data.links:
                source = str(link.source)
                target = str(link.target)
                if source in converted:
                    converted[source].append(target)
        
        return converted
    
    def _on_ok(self):
        """Обработчик кнопки ОК"""
        self.result = {'action': 'ok'}
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Обработчик кнопки Отмена"""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """Показывает диалог и возвращает результат"""
        self.dialog.wait_window()
        return self.result


# Пример использования
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Скрываем главное окно
    
    dialog = LocalNetworkManagerDialog(root)
    result = dialog.show()
    
    if result:
        print(f"Результат: {result}")
    
    root.destroy()
