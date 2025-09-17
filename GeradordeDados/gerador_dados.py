import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
import os
import unicodedata

# ... (A classe CustomDialog permanece a mesma) ...
class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title=None, prompts=None):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        self.prompts = prompts
        self.entries = {}
        body = ttk.Frame(self)
        self.initial_focus = self.create_widgets(body)
        body.pack(padx=10, pady=10)
        self.create_buttons()
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        if self.initial_focus:
            self.initial_focus.focus_set()
        self.grab_set()
        self.wait_window(self)
    def create_widgets(self, master):
        row = 0
        for key, config in self.prompts.items():
            label_text = config.get("label", key)
            default_val = config.get("default", "")
            label = ttk.Label(master, text=label_text)
            label.grid(row=row, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(master, width=30)
            entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
            entry.insert(0, default_val)
            self.entries[key] = entry
            row += 1
        return self.entries.get(list(self.prompts.keys())[0]) if self.prompts else None
    def create_buttons(self):
        box = ttk.Frame(self)
        ok_button = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        cancel_button = ttk.Button(box, text="Cancelar", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", lambda event: self.ok())
        self.bind("<Escape>", lambda event: self.cancel())
        box.pack()
    def ok(self):
        self.result = {}
        try:
            for key, entry in self.entries.items():
                prompt_config = self.prompts[key]
                value_type = prompt_config.get('type', str)
                self.result[key] = value_type(entry.get())
            self.withdraw()
            self.update_idletasks()
            self.parent.focus_set()
            self.destroy()
        except (ValueError, TypeError):
            messagebox.showerror("Erro de Entrada", "Por favor, insira um valor válido para cada campo.", parent=self)
    def cancel(self):
        self.parent.focus_set()
        self.destroy()

class DataGeneratorApp:
    # ... (__init__, create_main_widgets, create_field_widgets, _on_type_selected sem alterações) ...
    def __init__(self, root):
        self.root = root
        self.root.title("Cobra - Gerador de Dados para Testes")
        self.root.geometry("900x850")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=5, font=('Helvetica', 10, 'bold'))
        style.configure("TEntry", padding=5, font=('Helvetica', 10))
        style.configure("TCombobox", padding=5, font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'))
        self.field_widgets = []
        self.export_xlsx = tk.BooleanVar(value=False)
        self.export_csv = tk.BooleanVar(value=False)
        self.export_txt = tk.BooleanVar(value=False)
        self.export_sql = tk.BooleanVar(value=False)
        self.create_main_widgets()
    def create_main_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        setup_frame = ttk.LabelFrame(main_frame, text="1. Configuração da Tabela", padding="10")
        setup_frame.pack(fill=tk.X, pady=5)
        ttk.Label(setup_frame, text="Nome da Tabela:").grid(row=0, column=0, sticky=tk.W)
        self.table_name_entry = ttk.Entry(setup_frame, width=40)
        self.table_name_entry.grid(row=0, column=1, padx=5, sticky=tk.EW)
        ttk.Label(setup_frame, text="Quantidade de Campos:").grid(row=1, column=0, sticky=tk.W)
        self.num_fields_entry = ttk.Entry(setup_frame, width=10)
        self.num_fields_entry.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.create_fields_button = ttk.Button(setup_frame, text="Definir Campos", command=self.create_field_widgets)
        self.create_fields_button.grid(row=1, column=2, padx=10)
        self.fields_def_frame = ttk.LabelFrame(main_frame, text="2. Definição dos Campos", padding="10")
        self.fields_def_frame.pack(fill=tk.X, pady=5)
        self.fields_canvas = tk.Canvas(self.fields_def_frame, height=150)
        self.fields_frame_for_scroll = ttk.Frame(self.fields_canvas)
        self.scrollbar = ttk.Scrollbar(self.fields_def_frame, orient="vertical", command=self.fields_canvas.yview)
        self.fields_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.fields_canvas.pack(side="left", fill="both", expand=True)
        self.fields_canvas.create_window((0,0), window=self.fields_frame_for_scroll, anchor="nw")
        self.fields_frame_for_scroll.bind("<Configure>", lambda e: self.fields_canvas.configure(scrollregion=self.fields_canvas.bbox("all")))
        generation_frame = ttk.LabelFrame(main_frame, text="3. Geração e Exportação", padding="10")
        generation_frame.pack(fill=tk.X, pady=5)
        ttk.Label(generation_frame, text="Quantidade de Registros:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_records_entry = ttk.Entry(generation_frame, width=10)
        self.num_records_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        export_options_frame = ttk.Frame(generation_frame)
        export_options_frame.grid(row=1, column=0, columnspan=3, pady=10)
        ttk.Label(export_options_frame, text="Exportar para:").pack(side=tk.LEFT, padx=(0, 10))
        cb_xlsx = ttk.Checkbutton(export_options_frame, text="Excel (.xlsx)", variable=self.export_xlsx)
        cb_xlsx.pack(side=tk.LEFT, padx=5)
        cb_csv = ttk.Checkbutton(export_options_frame, text="CSV (.csv)", variable=self.export_csv)
        cb_csv.pack(side=tk.LEFT, padx=5)
        cb_txt = ttk.Checkbutton(export_options_frame, text="Texto (.txt)", variable=self.export_txt)
        cb_txt.pack(side=tk.LEFT, padx=5)
        cb_sql = ttk.Checkbutton(export_options_frame, text="SQL (.sql)", variable=self.export_sql)
        cb_sql.pack(side=tk.LEFT, padx=5)
        self.generate_button = ttk.Button(generation_frame, text="Gerar Dados", command=self.generate_data)
        self.generate_button.grid(row=2, column=0, columnspan=3, pady=(10,0))
        self.status_label = ttk.Label(generation_frame, text="", foreground="blue")
        self.status_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        output_frame = ttk.LabelFrame(main_frame, text="4. Query SQL de Inserção", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        self.sql_output_text = tk.Text(output_frame, height=20, wrap=tk.NONE, font=('Courier New', 9))
        self.sql_output_text.grid(row=0, column=0, sticky="nsew")
        v_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.sql_output_text.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.sql_output_text.config(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ttk.Scrollbar(output_frame, orient=tk.HORIZONTAL, command=self.sql_output_text.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.sql_output_text.config(xscrollcommand=h_scrollbar.set)
        self.copy_button = ttk.Button(output_frame, text="Copiar Código", command=self.copy_to_clipboard)
        self.copy_button.grid(row=2, column=0, columnspan=2, pady=10)
    def create_field_widgets(self):
        for widget in self.fields_frame_for_scroll.winfo_children():
            widget.destroy()
        self.field_widgets.clear()
        try:
            num_fields = int(self.num_fields_entry.get())
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número válido para a quantidade de campos.")
            return
        data_types = ["Autoincremento", "Numeros", "Nome", "Sobrenome", "Email", "Data", "Data/Hora", "Boolean", "Valor Fixo"]
        ttk.Label(self.fields_frame_for_scroll, text="Nome do Campo", font=('Helvetica', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.fields_frame_for_scroll, text="Tipo de Dado", font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.fields_frame_for_scroll, text="Opções", font=('Helvetica', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5)
        for i in range(num_fields):
            field_name_entry = ttk.Entry(self.fields_frame_for_scroll, width=30)
            field_name_entry.grid(row=i + 1, column=0, padx=5, pady=2, sticky=tk.W)
            data_type_combo = ttk.Combobox(self.fields_frame_for_scroll, values=data_types, state="readonly", width=20)
            data_type_combo.grid(row=i + 1, column=1, padx=5, pady=2, sticky=tk.W)
            options_button = ttk.Button(self.fields_frame_for_scroll, text="Configurar", command=lambda i=i: self.configure_field_options(i))
            options_button.grid(row=i + 1, column=2, padx=5, pady=2)
            options_button.config(state=tk.NORMAL)
            data_type_combo.bind("<<ComboboxSelected>>", lambda event, index=i: self._on_type_selected(event, index))
            self.field_widgets.append({'name_entry': field_name_entry, 'type_combo': data_type_combo, 'options': {},'options_button': options_button})
    def _on_type_selected(self, event, index):
        widget_info = self.field_widgets[index]
        button = widget_info['options_button']
        selected_type = widget_info['type_combo'].get()
        non_configurable_types = {"Sobrenome", "Email"}
        if selected_type in non_configurable_types:
            button.config(state=tk.DISABLED)
        else:
            button.config(state=tk.NORMAL)
    
    # --- FUNÇÃO configure_field_options MODIFICADA PARA DATAS ---
    def configure_field_options(self, index):
        widget_info = self.field_widgets[index]
        selected_type = widget_info['type_combo'].get()
        options = widget_info['options']

        if not selected_type:
            messagebox.showwarning("Aviso", "Selecione um tipo de dado primeiro.")
            return

        if selected_type == "Autoincremento":
            start_val = simpledialog.askinteger("Autoincremento", "Valor Inicial:", initialvalue=options.get('start', 1), parent=self.root)
            if start_val is not None: options.update({'type': 'autoincrement', 'start': start_val})
        
        elif selected_type == "Numeros":
            prompts = {'min': {'label': 'Valor Mínimo:', 'type': int, 'default': options.get('min', 0)},'max': {'label': 'Valor Máximo:', 'type': int, 'default': options.get('max', 1000)}}
            dialog = CustomDialog(self.root, title="Configurar Números Aleatórios", prompts=prompts)
            if dialog.result: options.update({'type': 'number', 'min': dialog.result['min'], 'max': dialog.result['max']})

        elif selected_type == "Nome":
            result = messagebox.askyesnocancel("Tipo de Nome", "Gerar nome e sobrenome juntos?", detail="Sim: 'João Silva'\nNão: 'João'")
            if result is not None: options.update({'type': 'name', 'together': result})

        # --- NOVA LÓGICA DE CONFIGURAÇÃO PARA DATAS ---
        elif selected_type in ["Data", "Data/Hora"]:
            if selected_type == "Data":
                title = "Configurar Intervalo de Data"
                prompts = {
                    'start': {'label': 'Data Inicial (dd/mm/AAAA):', 'type': str, 'default': options.get('start', '01/01/2020')},
                    'end': {'label': 'Data Final (dd/mm/AAAA):', 'type': str, 'default': options.get('end', f'{datetime.now().day:02d}/{datetime.now().month:02d}/{datetime.now().year}')}
                }
                date_format = '%d/%m/%Y'
            else: # Data/Hora
                title = "Configurar Intervalo de Data/Hora"
                prompts = {
                    'start': {'label': 'Início (dd/mm/AAAA HH:MM:SS):', 'type': str, 'default': options.get('start', '01/01/2020 00:00:00')},
                    'end': {'label': 'Final (dd/mm/AAAA HH:MM:SS):', 'type': str, 'default': options.get('end', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))}
                }
                date_format = '%d/%m/%Y %H:%M:%S'

            dialog = CustomDialog(self.root, title=title, prompts=prompts)
            if dialog.result:
                try:
                    # Valida os formatos antes de salvar
                    start_date = datetime.strptime(dialog.result['start'], date_format)
                    end_date = datetime.strptime(dialog.result['end'], date_format)

                    if start_date >= end_date:
                        messagebox.showerror("Erro de Lógica", "A data/hora inicial deve ser anterior à data/hora final.", parent=self.root)
                        return
                    
                    options.update({
                        'type': selected_type, 
                        'start': dialog.result['start'], 
                        'end': dialog.result['end']
                    })
                except ValueError:
                    messagebox.showerror("Erro de Formato", f"Formato de data inválido. Use {date_format.replace('%', '').upper()}", parent=self.root)

        elif selected_type == "Boolean":
            prompts = {'val1': {'label': 'Primeiro Valor:', 'type': str, 'default': options.get('values', ['True', 'False'])[0]},'val2': {'label': 'Segundo Valor:', 'type': str, 'default': options.get('values', ['True', 'False'])[1]}}
            dialog = CustomDialog(self.root, title="Configurar Valores Booleanos", prompts=prompts)
            if dialog.result: options.update({'type': 'boolean', 'values': [dialog.result['val1'], dialog.result['val2']]})

        elif selected_type == "Valor Fixo":
            fixed_value = simpledialog.askstring("Valor Fixo", "Digite o valor que será repetido em todos os registros.\nDeixe em branco para gerar NULL.", initialvalue=options.get('value', ''), parent=self.root)
            if fixed_value is not None: options.update({'type': 'fixed', 'value': fixed_value})
        
        self.field_widgets[index]['options'] = options

    # --- FUNÇÃO generate_data MODIFICADA PARA DATAS ---
    def generate_data(self):
        try:
            # ... (código de preparação e validação sem alterações) ...
            table_name = self.table_name_entry.get().strip()
            if not table_name: messagebox.showerror("Erro de Validação", "O nome da tabela é obrigatório."); return
            num_records = int(self.num_records_entry.get())
            columns, configs, email_configs = [], [], []
            name_col, surname_col = None, None
            for widget_info in self.field_widgets:
                field_name = widget_info['name_entry'].get().strip()
                field_type = widget_info['type_combo'].get()
                if not field_name or not field_type: messagebox.showerror("Erro de Validação", "Todos os campos devem ter um nome e um tipo selecionado."); return
                columns.append(field_name)
                current_config = {'name': field_name,'type': field_type,'options': widget_info['options']}
                if field_type == 'Email': email_configs.append(current_config)
                else: configs.append(current_config)
                if field_type == 'Nome' and not name_col: name_col = field_name
                if field_type == 'Sobrenome' and not surname_col: surname_col = field_name
            
            data = {col: [] for col in columns}
            autoincrement_counters = {}
            
            # Primeira Passada
            for i in range(num_records):
                for config in configs:
                    col_name, data_type, options = config['name'], config['type'], config['options']
                    value = None
                    if data_type == 'Autoincremento':
                        start = options.get('start', 1)
                        if col_name not in autoincrement_counters: autoincrement_counters[col_name] = start
                        value = autoincrement_counters[col_name]
                        autoincrement_counters[col_name] += 1
                    elif data_type == 'Numeros': value = random.randint(options.get('min', 0), options.get('max', 1000))
                    elif data_type == 'Nome': value = f"{fake.first_name()} {fake.last_name()}" if options.get('together', True) else fake.first_name()
                    elif data_type == 'Sobrenome': value = fake.last_name()
                    elif data_type == 'Valor Fixo': value = options.get('value', '') if options.get('value', '') else None
                    
                    # --- NOVA LÓGICA DE GERAÇÃO PARA DATAS ---
                    elif data_type in ['Data', 'Data/Hora']:
                        if data_type == 'Data':
                            fmt = '%d/%m/%Y'
                            start_str = options.get('start', '01/01/2020')
                            end_str = options.get('end', '31/12/2025')
                        else: # Data/Hora
                            fmt = '%d/%m/%Y %H:%M:%S'
                            start_str = options.get('start', '01/01/2020 00:00:00')
                            end_str = options.get('end', '31/12/2025 23:59:59')

                        start_date = datetime.strptime(start_str, fmt)
                        end_date = datetime.strptime(end_str, fmt)
                        
                        delta = end_date - start_date
                        random_seconds = random.uniform(0, delta.total_seconds())
                        random_date = start_date + timedelta(seconds=random_seconds)
                        
                        if data_type == 'Data':
                            value = random_date.strftime('%Y-%m-%d 00:00:00')
                        else:
                            value = random_date.strftime('%Y-%m-%d %H:%M:%S')

                    elif data_type == 'Boolean': value = random.choice(options.get('values', ['True', 'False']))
                    data[col_name].append(value)
            
            # ... (Segunda Passada e Lógica de Exportação sem alterações) ...
            for i in range(num_records):
                for config in email_configs:
                    col_name = config['name']
                    email_value = self._generate_contextual_email(i, data, name_col, surname_col)
                    data[col_name].append(email_value)
            df = pd.DataFrame(data, columns=columns)
            sql_query = self._generate_sql_string(table_name, columns, df)
            self.sql_output_text.delete(1.0, tk.END)
            self.sql_output_text.insert(1.0, sql_query)
            saved_files = []
            base_filename = f"{table_name}_dados"
            if self.export_xlsx.get():
                filename = f"{base_filename}.xlsx"
                df.to_excel(filename, index=False)
                saved_files.append(filename)
            if self.export_csv.get():
                filename = f"{base_filename}.csv"
                df.to_csv(filename, index=False, sep=',', encoding='utf-8')
                saved_files.append(filename)
            if self.export_txt.get():
                filename = f"{base_filename}.txt"
                df.to_csv(filename, index=False, sep='\t', encoding='utf-8')
                saved_files.append(filename)
            if self.export_sql.get():
                filename = f"{base_filename}.sql"
                with open(filename, 'w', encoding='utf-8') as f: f.write(sql_query)
                saved_files.append(filename)
            if saved_files: self.status_label.config(text=f"Sucesso! Arquivos salvos: {', '.join(saved_files)}", foreground="green")
            else: self.status_label.config(text="Sucesso! Query SQL gerada no painel abaixo.", foreground="green")
        except ValueError as e:
            if "time data" in str(e) and "does not match format" in str(e):
                 messagebox.showerror("Erro de Configuração", "Um campo de Data ou Data/Hora não foi configurado ou está com valores inválidos. Por favor, configure-o antes de gerar os dados.")
            else:
                messagebox.showerror("Erro", "A quantidade de registros deve ser um número inteiro.")
        except Exception as e: messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}")
    
    # ... (Restante do código sem alterações) ...
    def _sanitize_name_part(self, name_part):
        s = ''.join(c for c in unicodedata.normalize('NFD', name_part) if unicodedata.category(c) != 'Mn')
        return s.lower().replace(' ', '')
    def _generate_contextual_email(self, record_index, all_data, name_col, surname_col):
        nome = all_data.get(name_col, [None] * (record_index + 1))[record_index]
        sobrenome = all_data.get(surname_col, [None] * (record_index + 1))[record_index]
        domains = ["teste.com", "example.org", "mail.com.br", "empresa.net", "servico.com"]
        if nome and sobrenome:
            n_part = self._sanitize_name_part(nome.split(' ')[0])
            s_part = self._sanitize_name_part(sobrenome.split(' ')[-1])
            formats = [f"{n_part}.{s_part}", f"{n_part}{s_part}", f"{n_part[0]}{s_part}",f"{s_part}.{n_part}", f"{n_part}_{s_part}{random.randint(1,99)}"]
            username = random.choice(formats)
        elif nome:
            n_part = self._sanitize_name_part(nome.split(' ')[0])
            s_part = self._sanitize_name_part(fake.last_name())
            formats = [f"{n_part}.{s_part}", f"{n_part}{random.randint(1980,2023)}", f"{n_part}_{s_part}"]
            username = random.choice(formats)
        else:
            return fake.email()
        return f"{username}@{random.choice(domains)}"
    def _generate_sql_string(self, table_name, columns, df):
        sql_query = f"INSERT INTO `{table_name}` (`" + "`, `".join(columns) + "`) VALUES\n"
        value_rows = []
        for index, row in df.iterrows():
            values = []
            for col_name in columns:
                value = row[col_name]
                if pd.isna(value): values.append("NULL")
                elif isinstance(value, (int, float)) or str(value).lower() in ['true', 'false']: values.append(str(value))
                else:
                    value_str = str(value).replace("'", "''")
                    values.append(f"'{value_str}'")
            value_rows.append("(" + ", ".join(values) + ")")
        if not value_rows: return ""
        sql_query += ",\n".join(value_rows)
        sql_query += ";"
        return sql_query
    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        sql_code = self.sql_output_text.get(1.0, tk.END)
        self.root.clipboard_append(sql_code)
        self.status_label.config(text="Código SQL copiado para a área de transferência!", foreground="blue")


if __name__ == "__main__":
    fake = Faker('pt_BR')
    root = tk.Tk()
    app = DataGeneratorApp(root)
    root.mainloop()