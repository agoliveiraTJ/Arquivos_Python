import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
import queue
from ttkbootstrap import Style


class GeradorEXEApp:
    PLACEHOLDER_COLOR = "gray70"
    TEXT_COLOR = "black"
    PLACEHOLDER_ICONE = "Opcional: Selecione o arquivo de ícone, se não tiver deixe em branco"
    PLACEHOLDER_MODULOS = "Opcional: ex: 'pandas,numpy, se não tiver deixe em branco'"

    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Executável (.exe) v2.6 by Andcooper")
        self.root.geometry("700x800")
        self.style = Style(theme="cosmo")
        self.entries = {}
        self.var_arquivo = tk.StringVar()
        self.var_saida = tk.StringVar()
        self.var_nome = tk.StringVar(value="programa")
        self.var_icone = tk.StringVar()
        self.var_console = tk.BooleanVar(value=True)
        self.var_modulos = tk.StringVar()
        self.lista_extras = []
        self.var_extras_display = tk.StringVar(
            value="Nenhum arquivo ou pasta selecionada")
        self.criar_widgets()

    def criar_widgets(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill="both", expand=True)

        basic_group = ttk.Labelframe(
            main_frame, text="Configurações Básicas", padding=10)
        basic_group.pack(fill="x", expand=True, pady=5)
        self.add_field(basic_group, "Arquivo .py:", self.var_arquivo, 0,
                       self.procurar_arquivo, "Selecione o arquivo Python principal")
        self.add_field(basic_group, "Pasta de saída:", self.var_saida, 1,
                       self.procurar_pasta, "Selecione a pasta onde o .exe será salvo")
        self.add_field(basic_group, "Nome do executável:", self.var_nome, 2)

        advanced_group = ttk.Labelframe(
            main_frame, text="Opções Avançadas", padding=10)
        advanced_group.pack(fill="x", expand=True, pady=5)
        self.add_field(advanced_group, "Ícone (.ico):", self.var_icone,
                       0, self.procurar_icone, self.PLACEHOLDER_ICONE)
        self.add_field(advanced_group, "Arquivos/Pastas extras:",
                       self.var_extras_display, 1, self.procurar_extras, "", readonly=True)

        # NOVO: Aplica a cor de placeholder manualmente ao campo readonly.
        self.entries["Arquivos/Pastas extras:"].config(
            foreground=self.PLACEHOLDER_COLOR)

        self.add_field(advanced_group, "Módulos ocultos:",
                       self.var_modulos, 2, placeholder=self.PLACEHOLDER_MODULOS)

        ttk.Checkbutton(advanced_group, text="Exibir console (janela de comando)",
                        variable=self.var_console).grid(row=3, column=0, columnspan=3, sticky="w", pady=5)

        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=5)

        log_frame = ttk.Labelframe(
            main_frame, text="Log da Compilação", padding=10)
        log_frame.pack(fill="both", expand=True, pady=5)
        self.log_area = scrolledtext.ScrolledText(
            log_frame, height=10, state="disabled", bg="black", fg="white", font=("Courier New", 9))
        self.log_area.pack(fill="both", expand=True)

        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", expand=False, pady=(10, 0))
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        self.btn_gerar = ttk.Button(
            action_frame, text="Gerar Executável", command=self.iniciar_geracao, style='success.TButton')
        self.btn_gerar.grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=5)
        exit_button = ttk.Button(
            action_frame, text="Sair", command=self.root.destroy, style='secondary.TButton')
        exit_button.grid(row=0, column=1, sticky="ew", padx=(5, 0), ipady=5)

    def add_field(self, parent, label_text, variable, row, command=None, placeholder="", readonly=False):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=0, sticky="w", pady=5, padx=5)
        entry_state = "readonly" if readonly else "normal"
        entry = ttk.Entry(parent, textvariable=variable,
                          width=50, state=entry_state)
        entry.grid(row=row, column=1, sticky="ew", pady=5, padx=5)
        self.entries[label_text] = entry
        if placeholder and not readonly and not variable.get():
            entry.insert(0, placeholder)
            entry.config(foreground=self.PLACEHOLDER_COLOR)

            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(foreground=self.TEXT_COLOR)

            def on_focus_out(event):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.config(foreground=self.PLACEHOLDER_COLOR)
            entry.bind("<FocusIn>", on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)
        if command:
            btn = ttk.Button(parent, text="Procurar...", command=command)
            btn.grid(row=row, column=2, sticky="ew", pady=5, padx=5)
        parent.columnconfigure(1, weight=1)

    # ... (O resto do código permanece o mesmo)
    def procurar_arquivo(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py")])
        if caminho:
            self.var_arquivo.set(caminho)
            self.entries["Arquivo .py:"].config(foreground=self.TEXT_COLOR)

    def procurar_pasta(self):
        caminho = filedialog.askdirectory()
        if caminho:
            self.var_saida.set(caminho)
            self.entries["Pasta de saída:"].config(foreground=self.TEXT_COLOR)

    def procurar_icone(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Icon files", "*.ico")])
        if caminho:
            if self.var_icone.get() == self.PLACEHOLDER_ICONE:
                self.entries["Ícone (.ico):"].delete(0, tk.END)
            self.var_icone.set(caminho)
            self.entries["Ícone (.ico):"].config(foreground=self.TEXT_COLOR)

    def procurar_extras(self):
        caminhos = filedialog.askopenfilenames()
        pasta = filedialog.askdirectory(
            title="Selecione uma pasta para adicionar se precisar (Opcional)")
        if caminhos:
            self.lista_extras.extend(caminhos)
        if pasta:
            self.lista_extras.append(pasta)
        if self.lista_extras:
            self.var_extras_display.set(
                f"{len(self.lista_extras)} itens selecionados")
            self.entries["Arquivos/Pastas extras:"].config(
                foreground=self.TEXT_COLOR)

    def iniciar_geracao(self):
        if not self.var_arquivo.get() or not self.var_saida.get():
            messagebox.showerror(
                "Erro", "Arquivo .py e pasta de saída são obrigatórios!")
            return
        self.btn_gerar.config(state="disabled")
        self.progress_bar.start()
        self.log_area.config(state="normal")
        self.log_area.delete(1.0, tk.END)
        self.log_area.insert(tk.END, "Iniciando processo de compilação...\n\n")
        self.log_area.config(state="disabled")
        self.log_queue = queue.Queue()
        threading.Thread(target=self.gerar_exe_thread, daemon=True).start()
        self.root.after(100, self.processar_fila_log)

    def gerar_exe_thread(self):
        try:
            arquivo = self.var_arquivo.get()
            saida = self.var_saida.get()
            nome = self.var_nome.get()
            icone = self.var_icone.get()
            modulos = self.var_modulos.get()
            comando = ["pyinstaller", "--onefile", "--clean",
                       "--noconfirm", "--distpath", saida, "--name", nome, arquivo]
            if not self.var_console.get():
                comando.append("--noconsole")
            if icone and icone != self.PLACEHOLDER_ICONE and os.path.exists(icone):
                comando.extend(["--icon", icone])
            if modulos and modulos != self.PLACEHOLDER_MODULOS:
                for modulo in modulos.split(','):
                    comando.extend(["--hidden-import", modulo.strip()])
            for item in self.lista_extras:
                nome_base = os.path.basename(item)
                comando.extend(
                    ["--add-data", f"{item}{os.pathsep}{nome_base}"])
            self.log_queue.put(f"Comando executado: {' '.join(comando)}\n\n")
            processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            for linha in iter(processo.stdout.readline, ''):
                self.log_queue.put(linha)
            processo.wait()
            if processo.returncode == 0:
                self.log_queue.put(
                    f"\nSUCESSO! Executável gerado em: {os.path.join(saida, f'{nome}.exe')}")
            else:
                self.log_queue.put(
                    f"\nERRO! A compilação falhou. Verifique o log acima para detalhes.")
        except Exception as e:
            self.log_queue.put(f"\nERRO CRÍTICO: {e}")
        finally:
            self.log_queue.put(None)

    def processar_fila_log(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                if msg is None:
                    self.finalizar_geracao()
                    return
                self.log_area.config(state="normal")
                self.log_area.insert(tk.END, msg)
                self.log_area.see(tk.END)
                self.log_area.config(state="disabled")
        except queue.Empty:
            self.root.after(100, self.processar_fila_log)

    def finalizar_geracao(self):
        self.btn_gerar.config(state="normal")
        self.progress_bar.stop()
        messagebox.showinfo(
            "Concluído", "Processo de geração finalizado. Verifique o log para detalhes.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GeradorEXEApp(root)
    root.mainloop()
