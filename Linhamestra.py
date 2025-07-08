from tkinter import * # Importa todas as classes e funções do módulo Tkinter (ex: Tk, Frame, Button, Label, StringVar)
from tkinter import ttk # Importa o módulo ttk do Tkinter, que oferece widgets mais modernos e estilizados (ex: ttk.Treeview)
from tkinter import messagebox # Importa o módulo messagebox para exibir caixas de diálogo e alertas ao usuário

import numpy as np # Importa a biblioteca NumPy para operações com arrays e matrizes, especialmente úteis para números complexos
import math # Importa o módulo math para funções matemáticas como pi, sqrt e log
import cmath # Importa o módulo cmath para operações com números complexos (fasores).

# Metodos
from longitudinais.imagem import metodo_imagem_long
from longitudinais.Carson_correcao import Metodo_Carson_long
from longitudinais.Carson_pr import metodo_carson_para_raio
#from longitudinais.Carson_transposicao import metodo_carson_transp
#from longitudinais.feixes_de_condutores import calcular_rmg_feixe
#from longitudinais.componentes_simetricas_sintese import comp_sim_sintese
#from longitudinais.componentes_simetricas_analise import comp_sim_analise

# --- Classe para a Tela de Cálculo do Método das Imagens Longitudinais (Mantida para o método "Longitudinal Imagem") ---
class LongitudinalImageCalculator:
    def __init__(self, master_window):
        self.master_window = master_window                              # Armazena a janela principal para retornar
        self.calc_window = Toplevel(master_window)                      # Cria uma nova janela Toplevel para este método
        self._setup_window()                                            # Configura propriedades da janela
        self._setup_frames()                                            # Cria e posiciona os frames
        self._setup_widgets()                                           # Cria e posiciona os widgets de entrada e botões
        self._setup_treeview()                                          # Configura a Treeview
        
        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Impedância - Longitudinal Imagem") # Título da janela de cálculo
        self.calc_window.geometry("700x500")                            # Dimensões da janela
        self.calc_window.configure(background='#2F4F4F')                # Cor de fundo
        self.calc_window.resizable(False, False)                        # Impede redimensionamento
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing) # Gerencia fechamento da janela

    def _on_closing(self):
        self.calc_window.destroy()                                      # Destroi a janela de cálculo
        self.master_window.deiconify()                                  # Reexibe a janela principal

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3) # Frame superior para entradas
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.45)

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3) # Frame inferior para resultados
        self.frame_result.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.45)

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                        font=('Arial',10), command=self._on_closing) # Botão "Retornar" com ação de fechamento
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.15, relheight=0.1)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                        font=('Arial',10), command=self._clear_inputs) # Botão "Limpar" com ação
        self.botao_limpar.place(relx=.80, rely=.01, relwidth=0.15, relheight=0.1)

        self.botao_calc = Button(self.frame_info, text='Calcular', bd=4,
                                     font=('Arial',10), command=self._calculate_impedance) # Botão "Calcular" com ação
        self.botao_calc.place(relx=.8, rely=.85, relwidth=0.15, relheight=0.1)

        # --- Labels e Entradas de Resistências ---
        Label(self.frame_info, text='Resistências (Ohm/km)', bg='#BEBEBE').place(relx=0.01, rely=.2)

        Label(self.frame_info, text='Ra:', bg='#BEBEBE').place(relx=0.01, rely=.32)
        self.ra_entry = Entry(self.frame_info)
        self.ra_entry.place(relx=.1, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.44)
        self.rb_entry = Entry(self.frame_info)
        self.rb_entry.place(relx=.1, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.56)
        self.rc_entry = Entry(self.frame_info)
        self.rc_entry.place(relx=.1, rely=.56, relwidth=0.08)

        # --- Labels e Entradas de Raio e RMG ---
        Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE').place(relx=0.01, rely=.68)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.2, rely=.68, relwidth=0.08)

        Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE').place(relx=0.01, rely=.80)
        self.rmg_entry = Entry(self.frame_info)
        self.rmg_entry.place(relx=.2, rely=.80, relwidth=0.08)

        # --- Labels e Entradas de Coordenadas ---
        Label(self.frame_info, text='Coordenadas dos Cabos (m)', bg='#BEBEBE').place(relx=.4, rely=.2)

        Label(self.frame_info, text='Xa:', bg='#BEBEBE').place(relx=.4, rely=.32)
        self.xa_entry = Entry(self.frame_info)
        self.xa_entry.place(relx=.48, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='Xb:', bg='#BEBEBE').place(relx=.4, rely=.44)
        self.xb_entry = Entry(self.frame_info)
        self.xb_entry.place(relx=.48, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='Xc:', bg='#BEBEBE').place(relx=.4, rely=.56)
        self.xc_entry = Entry(self.frame_info)
        self.xc_entry.place(relx=.48, rely=.56, relwidth=0.08)

        Label(self.frame_info, text='Ha:', bg='#BEBEBE').place(relx=.6, rely=.32)
        self.ha_entry = Entry(self.frame_info)
        self.ha_entry.place(relx=.68, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='Hb:', bg='#BEBEBE').place(relx=.6, rely=.44)
        self.hb_entry = Entry(self.frame_info)
        self.hb_entry.place(relx=.68, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='Hc:', bg='#BEBEBE').place(relx=.6, rely=.56)
        self.hc_entry = Entry(self.frame_info)
        self.hc_entry.place(relx=.68, rely=.56, relwidth=0.08)

    def _setup_treeview(self):
        self.lista_CAP = ttk.Treeview(self.frame_result, height=3,
                                          columns=('col1','col2','col3'))
        self.lista_CAP.heading("#0", text="Fase")
        self.lista_CAP.heading("col1", text="Condutor A")
        self.lista_CAP.heading("col2", text="Condutor B")
        self.lista_CAP.heading("col3", text="Condutor C")

        self.lista_CAP.column("#0", width=80, anchor=CENTER)
        self.lista_CAP.column("col1", width=180, anchor=CENTER)
        self.lista_CAP.column("col2", width=180, anchor=CENTER)
        self.lista_CAP.column("col3", width=180, anchor=CENTER)

        self.lista_CAP.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')
        self.lista_CAP.configure(yscrollcommand=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)

    def _clear_inputs(self):
        self.ra_entry.delete(0,END)
        self.rb_entry.delete(0,END)
        self.rc_entry.delete(0,END)
        self.r_entry.delete(0,END)
        self.rmg_entry.delete(0,END)
        self.xa_entry.delete(0,END)
        self.xb_entry.delete(0,END)
        self.xc_entry.delete(0,END)
        self.ha_entry.delete(0,END)
        self.hb_entry.delete(0,END)
        self.hc_entry.delete(0,END)
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _get_input_values(self):
        try:
            # Resistências do condutor em Ohms/km (assumindo input do usuário)
            ra_km = float(self.ra_entry.get()) if self.ra_entry.get() else 0.0
            rb_km = float(self.rb_entry.get()) if self.rb_entry.get() else 0.0
            rc_km = float(self.rc_entry.get()) if self.rc_entry.get() else 0.0

            # Convertendo para Ohms/metro, pois a função `metodo_imagem_long` espera Ohms/metro
            ra = ra_km / 1000.0
            rb = rb_km / 1000.0
            rc = rc_km / 1000.0

            R_val = float(self.r_entry.get()) if self.r_entry.get() else None
            Rmg_val = float(self.rmg_entry.get()) if self.rmg_entry.get() else None
            
            xa = float(self.xa_entry.get()) if self.xa_entry.get() else 0.0
            xb = float(self.xb_entry.get()) if self.xb_entry.get() else 0.0
            xc = float(self.xc_entry.get()) if self.xc_entry.get() else 0.0

            ha = float(self.ha_entry.get()) if self.ha_entry.get() else 0.0
            hb = float(self.hb_entry.get()) if self.hb_entry.get() else 0.0
            hc = float(self.hc_entry.get()) if self.hc_entry.get() else 0.0
            
            # Não há `rho` neste método
            
            return {
                'ra': ra, 'rb': rb, 'rc': rc,
                'xa': xa, 'ha': ha,
                'xb': xb, 'hb': hb,
                'xc': xc, 'hc': hc,
                'R': R_val, 'Rmg_val': Rmg_val
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Detalhes: {e}")
            return None

    def _calculate_impedance(self):
        params = self._get_input_values()
        if params is None:
            return

        try:
            Z_matrix = metodo_imagem_long( # Chama a função específica para "Longitudinal Imagem"
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa=params['xa'], ha=params['ha'],
                xb=params['xb'], hb=params['hb'],
                xc=params['xc'], hc=params['hc'],
                R=params['R'], Rmg_val=params['Rmg_val']
            )
            self._insert_data_to_treeview(Z_matrix)
            messagebox.showinfo("Cálculo Concluído", "A matriz de impedância foi calculada e exibida na tabela.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, Z_matrix):
        for i in self.lista_CAP.get_children():
            self.lista_CAP.delete(i)
        
        complex_format = "({:.6f} + j{:.6f})" # Formato para exibir números complexos com 6 casas decimais
        row_labels = ["A", "B", "C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(Z_matrix.shape[1]):
                complex_num = Z_matrix[i, j]
                if np.isnan(complex_num.real) and np.isnan(complex_num.imag):
                    formatted_value = "" # Exibe vazio se for NaN
                else:
                    formatted_value = complex_format.format(complex_num.real, complex_num.imag)
                row_values.append(formatted_value)
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values))


# --- Classe para a Tela de Cálculo do Método de Carson Longitudinal (COM CORREÇÃO DE SOLO) ---
class CarsonLongitudinalCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.carson_window = Toplevel(master_window)
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()
        
        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _setup_window(self):
        self.carson_window.title("Cálculo de Impedância - Longitudinal Carson (Correção)") # Título da janela de cálculo
        self.carson_window.geometry("700x500")
        self.carson_window.configure(background='#2F4F4F')
        self.carson_window.resizable(False, False)
        self.carson_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.carson_window.destroy()
        self.master_window.deiconify()

    def _setup_frames(self):
        self.frame_info = Frame(self.carson_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.45)

        self.frame_result = Frame(self.carson_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.45)

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                        font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.15, relheight=0.1)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                        font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.80, rely=.01, relwidth=0.15, relheight=0.1)

        self.botao_calc = Button(self.frame_info, text='Calcular', bd=4,
                                     font=('Arial',10), command=self._calculate_impedance)
        self.botao_calc.place(relx=.8, rely=.85, relwidth=0.15, relheight=0.1)

        # --- Labels e Entradas de Resistências ---
        Label(self.frame_info, text='Resistências (Ohm/km)', bg='#BEBEBE').place(relx=0.01, rely=.2)

        Label(self.frame_info, text='Ra:', bg='#BEBEBE').place(relx=0.01, rely=.32)
        self.ra_entry = Entry(self.frame_info)
        self.ra_entry.place(relx=.25, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.44)
        self.rb_entry = Entry(self.frame_info)
        self.rb_entry.place(relx=.25, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.56)
        self.rc_entry = Entry(self.frame_info)
        self.rc_entry.place(relx=.25, rely=.56, relwidth=0.08)

        # --- Labels e Entradas de Raio e RMG ---
        Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE').place(relx=0.01, rely=.68)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.25, rely=.68, relwidth=0.08) # Ajustado relx para alinhar com resistências

        Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE').place(relx=0.01, rely=.80)
        self.rmg_entry = Entry(self.frame_info)
        self.rmg_entry.place(relx=.25, rely=.80, relwidth=0.08) # Ajustado relx para alinhar com resistências

        # --- Labels e Entradas de Resistividade do Solo (NOVO) ---
        Label(self.frame_info, text='Resistividade do Solo (ρ) [Ohm-m]', bg='#BEBEBE').place(relx=0.01, rely=.1) # Nova posição para resistividade
        self.rho_entry = Entry(self.frame_info)
        self.rho_entry.place(relx=.3, rely=.1, relwidth=0.08) # Nova posição para o campo de entrada

        # --- Labels e Entradas de Coordenadas ---
        Label(self.frame_info, text='Coordenadas dos Cabos (m)', bg='#BEBEBE').place(relx=.4, rely=.2)

        Label(self.frame_info, text='Xa:', bg='#BEBEBE').place(relx=.4, rely=.32)
        self.xa_entry = Entry(self.frame_info)
        self.xa_entry.place(relx=.48, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='Xb:', bg='#BEBEBE').place(relx=.4, rely=.44)
        self.xb_entry = Entry(self.frame_info)
        self.xb_entry.place(relx=.48, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='Xc:', bg='#BEBEBE').place(relx=.4, rely=.56)
        self.xc_entry = Entry(self.frame_info)
        self.xc_entry.place(relx=.48, rely=.56, relwidth=0.08)

        Label(self.frame_info, text='Ha:', bg='#BEBEBE').place(relx=.6, rely=.32)
        self.ha_entry = Entry(self.frame_info)
        self.ha_entry.place(relx=.68, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='Hb:', bg='#BEBEBE').place(relx=.6, rely=.44)
        self.hb_entry = Entry(self.frame_info)
        self.hb_entry.place(relx=.68, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='Hc:', bg='#BEBEBE').place(relx=.6, rely=.56)
        self.hc_entry = Entry(self.frame_info)
        self.hc_entry.place(relx=.68, rely=.56, relwidth=0.08)

    def _setup_treeview(self):
        self.lista_CAP = ttk.Treeview(self.frame_result, height=3,
                                          columns=('col1','col2','col3'))
        self.lista_CAP.heading("#0", text="")
        self.lista_CAP.heading("col1", text="Condutor A")
        self.lista_CAP.heading("col2", text="Condutor B")
        self.lista_CAP.heading("col3", text="Condutor C")

        self.lista_CAP.column("#0", width=80, anchor=CENTER)
        self.lista_CAP.column("col1", width=180, anchor=CENTER)
        self.lista_CAP.column("col2", width=180, anchor=CENTER)
        self.lista_CAP.column("col3", width=180, anchor=CENTER)

        self.lista_CAP.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')
        self.lista_CAP.configure(yscrollcommand=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)

    def _clear_inputs(self):
        self.ra_entry.delete(0,END)
        self.rb_entry.delete(0,END)
        self.rc_entry.delete(0,END)
        self.r_entry.delete(0,END)
        self.rmg_entry.delete(0,END)
        self.rho_entry.delete(0,END) # Limpa o novo campo de resistividade
        self.xa_entry.delete(0,END)
        self.xb_entry.delete(0,END)
        self.xc_entry.delete(0,END)
        self.ha_entry.delete(0,END)
        self.hb_entry.delete(0,END)
        self.hc_entry.delete(0,END)
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _get_input_values(self):
        try:
            # Resistências do condutor em Ohms/km (assumindo input do usuário)
            ra_km = float(self.ra_entry.get()) if self.ra_entry.get() else 0.0
            rb_km = float(self.rb_entry.get()) if self.rb_entry.get() else 0.0
            rc_km = float(self.rc_entry.get()) if self.rc_entry.get() else 0.0

            # Convertendo para Ohms/metro, pois a função `Metodo_Carson_long` espera Ohms/metro
            ra = ra_km / 1000.0
            rb = rb_km / 1000.0
            rc = rc_km / 1000.0

            R_val = float(self.r_entry.get()) if self.r_entry.get() else None
            Rmg_val = float(self.rmg_entry.get()) if self.rmg_entry.get() else None
            
            # NOVO: Obtém e converte a resistividade do solo
            rho = float(self.rho_entry.get()) if self.rho_entry.get() else 0.0
            
            xa = float(self.xa_entry.get()) if self.xa_entry.get() else 0.0
            xb = float(self.xb_entry.get()) if self.xb_entry.get() else 0.0
            xc = float(self.xc_entry.get()) if self.xc_entry.get() else 0.0

            ha = float(self.ha_entry.get()) if self.ha_entry.get() else 0.0
            hb = float(self.hb_entry.get()) if self.hb_entry.get() else 0.0
            hc = float(self.hc_entry.get()) if self.hc_entry.get() else 0.0
            
            return {
                'ra': ra, 'rb': rb, 'rc': rc,
                'xa': xa, 'ha': ha,
                'xb': xb, 'hb': hb,
                'xc': xc, 'hc': hc,
                'R': R_val, 'Rmg_val': Rmg_val,
                'rho': rho # Adicionado o novo parâmetro
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Detalhes: {e}")
            return None

    def _calculate_impedance(self):
        params = self._get_input_values()
        if params is None:
            return

        try:
            # CHAMA A FUNÇÃO ESPECÍFICA DO MÉTODO DE CARSON, AGORA PASSANDO 'rho'
            Z_matrix = Metodo_Carson_long(
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa=params['xa'], ha=params['ha'],
                xb=params['xb'], hb=params['hb'],
                xc=params['xc'], hc=params['hc'],
                rho=params['rho'], # Passando a resistividade do solo
                R=params['R'], Rmg_val=params['Rmg_val']
            )
            self._insert_data_to_treeview(Z_matrix)
            messagebox.showinfo("Cálculo Concluído", "A matriz de impedância foi calculada e exibida na tabela.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, Z_matrix):
        for i in self.lista_CAP.get_children():
            self.lista_CAP.delete(i)
        
        complex_format = "({:.6f} + j{:.6f})" # Formato para exibir números complexos com 6 casas decimais
        row_labels = ["A", "B", "C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(Z_matrix.shape[1]):
                complex_num = Z_matrix[i, j]
                if np.isnan(complex_num.real) and np.isnan(complex_num.imag):
                    formatted_value = "" # Exibe vazio se for NaN
                else:
                    formatted_value = complex_format.format(complex_num.real, complex_num.imag)
                row_values.append(formatted_value)
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values))

# --- Classe para a Tela de Cálculo do Método de Carson com Cabo Para-Raio ---
class CarsonGroundWireCalculator:
    def __init__(self, master_window):
        self.master_window = master_window  # Armazena a janela principal para retornar
        self.calc_window = Toplevel(master_window)  # Cria uma nova janela Toplevel para este método
        
        self._setup_window()  # Configura propriedades da janela
        self._setup_frames()  # Cria e posiciona os frames
        self._setup_widgets() # Cria e posiciona os widgets de entrada e botões
        self._setup_treeview() # Configura a Treeview para exibir a matriz Z

        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Impedância - Método de Carson com Cabo Para-Raio") # Título da janela
        self.calc_window.geometry("850x550") # Dimensões da janela (um pouco maior para mais campos)
        self.calc_window.configure(background='#2F4F4F') # Cor de fundo
        self.calc_window.resizable(False, False) # Impede redimensionamento
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing) # Gerencia fechamento da janela

    def _on_closing(self):
        self.calc_window.destroy()  # Destroi a janela de cálculo atual
        self.master_window.deiconify() # Reexibe a janela principal

    def _setup_frames(self):
        # Frame superior para entradas de dados
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.5) # Um pouco maior

        # Frame inferior para os resultados (Treeview)
        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.54, relwidth=0.96, relheight=0.44) # Ajustado

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                   font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.12, relheight=0.08)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                   font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.87, rely=.01, relwidth=0.12, relheight=0.08)

        self.botao_calc = Button(self.frame_info, text='Calcular', bd=4,
                                 font=('Arial',10), command=self._calculate_impedance)
        self.botao_calc.place(relx=.87, rely=.89, relwidth=0.12, relheight=0.08)

        # --- Labels e Entradas de Resistências (Fases e Para-Raio) ---
        Label(self.frame_info, text='Resistências (Ohm/km)', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=0.01, rely=.12)

        Label(self.frame_info, text='Ra:', bg='#BEBEBE').place(relx=0.01, rely=.2)
        self.ra_entry = Entry(self.frame_info)
        self.ra_entry.place(relx=.08, rely=.2, relwidth=0.08)

        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.28)
        self.rb_entry = Entry(self.frame_info)
        self.rb_entry.place(relx=.08, rely=.28, relwidth=0.08)

        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.36)
        self.rc_entry = Entry(self.frame_info)
        self.rc_entry.place(relx=.08, rely=.36, relwidth=0.08)
        
        Label(self.frame_info, text='Rp:', bg='#BEBEBE').place(relx=0.01, rely=.44)
        self.rp_entry = Entry(self.frame_info)
        self.rp_entry.place(relx=.08, rely=.44, relwidth=0.08)


        # --- Labels e Entradas de Raio e RMG ---
        Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE').place(relx=0.01, rely=.55)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.18, rely=.55, relwidth=0.08)

        Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE').place(relx=0.01, rely=.63)
        self.rmg_entry = Entry(self.frame_info)
        self.rmg_entry.place(relx=.18, rely=.63, relwidth=0.08)

        # --- Entrada de Resistividade do Solo ---
        Label(self.frame_info, text='Resistividade Solo (rho) [Ohm.m]', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=0.01, rely=.75)
        self.rho_entry = Entry(self.frame_info)
        self.rho_entry.place(relx=.28, rely=.75, relwidth=0.08)


        # --- Labels e Entradas de Coordenadas (X, H) para Fases e Para-Raio ---
        Label(self.frame_info, text='Coordenadas dos Condutores (m)', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=.4, rely=.12)

        # Fase A
        Label(self.frame_info, text='Xa:', bg='#BEBEBE').place(relx=.4, rely=.2)
        self.xa_entry = Entry(self.frame_info)
        self.xa_entry.place(relx=.48, rely=.2, relwidth=0.08)
        Label(self.frame_info, text='Ha:', bg='#BEBEBE').place(relx=.6, rely=.2)
        self.ha_entry = Entry(self.frame_info)
        self.ha_entry.place(relx=.68, rely=.2, relwidth=0.08)

        # Fase B
        Label(self.frame_info, text='Xb:', bg='#BEBEBE').place(relx=.4, rely=.28)
        self.xb_entry = Entry(self.frame_info)
        self.xb_entry.place(relx=.48, rely=.28, relwidth=0.08)
        Label(self.frame_info, text='Hb:', bg='#BEBEBE').place(relx=.6, rely=.28)
        self.hb_entry = Entry(self.frame_info)
        self.hb_entry.place(relx=.68, rely=.28, relwidth=0.08)

        # Fase C
        Label(self.frame_info, text='Xc:', bg='#BEBEBE').place(relx=.4, rely=.36)
        self.xc_entry = Entry(self.frame_info)
        self.xc_entry.place(relx=.48, rely=.36, relwidth=0.08)
        Label(self.frame_info, text='Hc:', bg='#BEBEBE').place(relx=.6, rely=.36)
        self.hc_entry = Entry(self.frame_info)
        self.hc_entry.place(relx=.68, rely=.36, relwidth=0.08)

        # Para-raio P
        Label(self.frame_info, text='Xp:', bg='#BEBEBE').place(relx=.4, rely=.44)
        self.xp_entry = Entry(self.frame_info)
        self.xp_entry.place(relx=.48, rely=.44, relwidth=0.08)
        Label(self.frame_info, text='Hp:', bg='#BEBEBE').place(relx=.6, rely=.44)
        self.hp_entry = Entry(self.frame_info)
        self.hp_entry.place(relx=.68, rely=.44, relwidth=0.08)
        
    def _setup_treeview(self):
        # Configuração da Treeview para exibir a matriz de impedância (Z_matrix)
        self.lista_impedancias = ttk.Treeview(self.frame_result, height=3,
                                             columns=('col1','col2','col3'))
        self.lista_impedancias.heading("#0", text="Fase")
        self.lista_impedancias.heading("col1", text="Condutor A")
        self.lista_impedancias.heading("col2", text="Condutor B")
        self.lista_impedancias.heading("col3", text="Condutor C")

        self.lista_impedancias.column("#0", width=80, anchor=CENTER)
        self.lista_impedancias.column("col1", width=180, anchor=CENTER)
        self.lista_impedancias.column("col2", width=180, anchor=CENTER)
        self.lista_impedancias.column("col3", width=180, anchor=CENTER)

        self.lista_impedancias.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')
        self.lista_impedancias.configure(yscrollcommand=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)

    def _clear_inputs(self):
        # Limpa todos os campos de entrada e a Treeview
        self.ra_entry.delete(0, END)
        self.rb_entry.delete(0, END)
        self.rc_entry.delete(0, END)
        self.rp_entry.delete(0, END) # Novo campo para o para-raio
        self.r_entry.delete(0, END)
        self.rmg_entry.delete(0, END)
        self.rho_entry.delete(0, END) # Novo campo para resistividade
        self.xa_entry.delete(0, END)
        self.xb_entry.delete(0, END)
        self.xc_entry.delete(0, END)
        self.xp_entry.delete(0, END) # Novo campo para o para-raio
        self.ha_entry.delete(0, END)
        self.hb_entry.delete(0, END)
        self.hc_entry.delete(0, END)
        self.hp_entry.delete(0, END) # Novo campo para o para-raio
        
        # Limpa a Treeview preenchendo com valores NaN (que serão exibidos como vazio)
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _get_input_values(self):
        """
        Extrai e valida os valores de entrada dos campos da GUI.
        Converte resistências de Ohm/km para Ohm/m.
        """
        try:
            # Resistências do condutor em Ohms/km (assumindo input do usuário)
            ra_km = float(self.ra_entry.get()) if self.ra_entry.get() else 0.0
            rb_km = float(self.rb_entry.get()) if self.rb_entry.get() else 0.0
            rc_km = float(self.rc_entry.get()) if self.rc_entry.get() else 0.0
            rp_km = float(self.rp_entry.get()) if self.rp_entry.get() else 0.0 # Resistência do para-raio

            # Convertendo para Ohms/metro, pois a função `metodo_carson_para_raio` espera Ohms/metro
            ra = ra_km / 1000.0
            rb = rb_km / 1000.0
            rc = rc_km / 1000.0
            rp = rp_km / 1000.0 # Resistência do para-raio em Ohm/m

            R_val = float(self.r_entry.get()) if self.r_entry.get() else None
            Rmg_val = float(self.rmg_entry.get()) if self.rmg_entry.get() else None
            
            rho = float(self.rho_entry.get()) if self.rho_entry.get() else None # Resistividade do solo

            # Coordenadas X
            xa = float(self.xa_entry.get()) if self.xa_entry.get() else 0.0
            xb = float(self.xb_entry.get()) if self.xb_entry.get() else 0.0
            xc = float(self.xc_entry.get()) if self.xc_entry.get() else 0.0
            xp = float(self.xp_entry.get()) if self.xp_entry.get() else 0.0 # Coordenada X do para-raio

            # Coordenadas H (altura)
            ha = float(self.ha_entry.get()) if self.ha_entry.get() else 0.0
            hb = float(self.hb_entry.get()) if self.hb_entry.get() else 0.0
            hc = float(self.hc_entry.get()) if self.hc_entry.get() else 0.0
            hp = float(self.hp_entry.get()) if self.hp_entry.get() else 0.0 # Coordenada H do para-raio
            
            # Validação específica para rho, pois a função `metodo_carson_para_raio` espera um valor válido
            if rho is None:
                raise ValueError("A resistividade do solo (rho) é um campo obrigatório.")
            
            return {
                'ra': ra, 'rb': rb, 'rc': rc, 'rp': rp, # Incluindo rp
                'xa': xa, 'ha': ha,
                'xb': xb, 'hb': hb,
                'xc': xc, 'hc': hc,
                'xp': xp, 'hp': hp, # Incluindo coordenadas do para-raio
                'rho': rho, # Incluindo rho
                'R': R_val, 'Rmg_val': Rmg_val
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Detalhes: {e}")
            return None

    def _calculate_impedance(self):
        """
        Coleta os inputs, chama a função de cálculo do Método de Carson com Para-Raio,
        e exibe os resultados na Treeview.
        """
        params = self._get_input_values()
        if params is None:
            return # Sai se houver erro na validação dos inputs

        try:
            # Chama a função específica para "Carson com Cabo Para-Raio"
            Z_matrix = metodo_carson_para_raio(
                ra=params['ra'], rb=params['rb'], rc=params['rc'], rp=params['rp'],
                xa=params['xa'], ha=params['ha'],
                xb=params['xb'], hb=params['hb'],
                xc=params['xc'], hc=params['hc'],
                xp=params['xp'], hp=params['hp'], # Passa os parâmetros do para-raio
                rho=params['rho'], # Passa a resistividade do solo
                R=params['R'], Rmg_val=params['Rmg_val']
            )
            self._insert_data_to_treeview(Z_matrix)
            messagebox.showinfo("Cálculo Concluído", "A matriz de impedância Zp foi calculada e exibida na tabela.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, Z_matrix):
        """
        Limpa a Treeview e insere os valores da matriz de impedância.
        Formata números complexos para exibição.
        """
        # Limpa todas as entradas existentes na Treeview
        for i in self.lista_impedancias.get_children():
            self.lista_impedancias.delete(i)
        
        complex_format = "({:.6f} + j{:.6f})" # Formato para exibir números complexos com 6 casas decimais
        row_labels = ["Zaa", "Zbb", "Zcc"] # Rótulos para as linhas da matriz (fases)
        # Note que a matriz de saída do método de Kron é 3x3 (Zaa, Zbb, Zcc, Zab, etc.)
        # As linhas representam a primeira fase do termo (por exemplo, Z_linha_A)

        for i, row_label in enumerate(row_labels):
            # Obtém os valores da linha da matriz (Z_matrix[i, :])
            # e os formata como strings para exibição na Treeview.
            row_values = []
            for j in range(Z_matrix.shape[1]):
                complex_num = Z_matrix[i, j]
                # Verifica se o número é NaN (Not a Number), o que ocorre em entradas vazias iniciais
                if np.isnan(complex_num.real) and np.isnan(complex_num.imag):
                    formatted_value = "" # Exibe vazio se for NaN
                else:
                    formatted_value = complex_format.format(complex_num.real, complex_num.imag)
                row_values.append(formatted_value)
            
            # Insere a linha na Treeview
            self.lista_impedancias.insert("", END, text=row_label, values=tuple(row_values))


# --- Classe Principal da Aplicação (Tela de Seleção de Métodos) ---
class AppMain:
    def __init__(self, master):
        self.root = master                                              # Referência à janela principal
        self._setup_main_window()                                       # Configura a janela principal
        self._setup_main_frames()                                       # Cria frames na janela principal
        self._setup_main_widgets()                                      # Cria widgets na janela principal
        self.root.mainloop()                                            # Inicia o loop principal do Tkinter

    def _setup_main_window(self):
        self.root.title("LinhaMestre - Seleção de Método")              # Título da janela principal
        self.root.geometry("700x500")                                   # Dimensões da janela
        self.root.configure(background='#2F4F4F')                       # Cor de fundo
        self.root.resizable(False, False)                               # Impede redimensionamento
        self.root.maxsize(width=900, height=700)                        # Tamanho máximo
        self.root.minsize(width=400, height=300)                        # Tamanho mínimo

    def _setup_main_frames(self):
        self.frame_principal = Frame(self.root, bd=4, bg="gray",
                                     highlightbackground='black', highlightthickness=3)
        self.frame_principal.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)

    def _setup_main_widgets(self):
        self.botao_ok = Button(self.frame_principal, text='OK', bd=4,
                               font=('Arial',15), command=self._select_method)
        self.botao_ok.place(relx=.8, rely=.85, relwidth=0.15, relheight=0.1)

        Label(self.frame_principal, text='Selecione o método:', bg='gray', fg='black', font=('Arial', 12)).place(relx=.05, rely=.32)

        self.metodo_select = StringVar(self.root)
        self.metodo_options = ("Longitudinal Imagem", "Longitudinal Carson (Correção)", # Adicionado o novo método aqui
                               "Longitudinal Carson transposição",
                               "Longitudinal Carson para-raio", "Longitudinal Carson feixe de condutor",
                               "Longitudinal Carson impedância de sequência", "Transversal imagem",
                               "Transversal transposição", "Transversal para-raio",
                               "Transversal feixe de condutor", "Transversal capacitância de sequências")
        self.metodo_select.set(self.metodo_options[0]) # Define o valor inicial

        self.popupMenu = OptionMenu(self.frame_principal, self.metodo_select, *self.metodo_options)
        self.popupMenu.place(relx=.4, rely=.3, relwidth=0.5, relheight=0.08)
        
    def _select_method(self):
        selected_method = self.metodo_select.get()
        if selected_method == "":
            messagebox.showinfo("Erro de seleção de método!!!", "Selecione um método válido, \nna caixa de seleção de métodos")
        elif selected_method == "Longitudinal Imagem":
            self.root.withdraw() # Esconde a janela principal
            LongitudinalImageCalculator(self.root) # Passa a referência da janela principal
        elif selected_method == "Longitudinal Carson (Correção)": # Nova condição para o método de Carson
            self.root.withdraw() # Esconde a janela principal
            CarsonLongitudinalCalculator(self.root) # Instancia a nova janela de Carson
        elif selected_method == "Longitudinal Carson para-raio": # Nova condição para o método de Carson
            self.root.withdraw() # Esconde a janela principal
            CarsonGroundWireCalculator(self.root) # Instancia a nova janela de Carson
        else:
            messagebox.showinfo("Método Não Implementado", f"O método '{selected_method}' ainda não foi implementado. Por favor, selecione 'Longitudinal Imagem' ou 'Longitudinal Carson (Correção)'.")

# --- Inicialização ---
if __name__ == "__main__":
    root = Tk()
    app = AppMain(root)