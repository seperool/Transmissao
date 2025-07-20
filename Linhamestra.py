# Bibliotecas

## Biblioteca gráfica/Janelas
from tkinter import * # Importa todas as classes e funções do módulo Tkinter (ex: Tk, Frame, Button, Label, StringVar)
from tkinter import ttk # Importa o módulo ttk do Tkinter, que oferece widgets mais modernos e estilizados (ex: ttk.Treeview)
from tkinter import messagebox # Importa o módulo messagebox para exibir caixas de diálogo e alertas ao usuário

## Bibliotecas dos cálculos
import numpy as np # Importa a biblioteca NumPy para operações com arrays e matrizes, especialmente úteis para números complexos
import math # Importa o módulo math para funções matemáticas como pi, sqrt e log
import cmath # Importa o módulo cmath para operações com números complexos (fasores).

# Importando Métodos de Cálculo

## Longitudinais
# Importa funções específicas para cálculos de impedância longitudinal,
# agrupadas por diferentes métodos e considerações.
from longitudinais.imagem import metodo_imagem_long
from longitudinais.Carson_correcao import Metodo_Carson_long
from longitudinais.Carson_pr import metodo_carson_para_raio
from longitudinais.Carson_transposicao import metodo_carson_transp
from longitudinais.feixes_de_condutores import calcular_rmg_feixe
from longitudinais.componentes_simetricas_sintese import comp_sim_sintese
from longitudinais.componentes_simetricas_analise import comp_sim_analise

## Transversais
# Importa funções específicas para cálculos de capacitância transversal,
# agrupadas por diferentes métodos e considerações.
from Transversais.imagem import metodo_imagem_tran
from Transversais.para_raio import metodo_para_raio_tran
from Transversais.transposicao import metodo_transposicao_tran
from Transversais.feixe_condutor import metodo_feixe_condutor_tran
from Transversais.capacitancia_de_sequencia import metodo_capacitancia_sequencia_tran

import numpy as np
from tkinter import Toplevel, Frame, Button, Label, Entry, END, CENTER, messagebox, Scrollbar # Importar Tkinter corretamente
from tkinter import ttk # Para Treeview

# Assumindo que 'metodo_imagem_long' está disponível (do seu módulo ou definido em outro lugar)
# from longitudinais.imagem import metodo_imagem_long

# --- Classe para a Tela de Cálculo do Método das Imagens Longitudinais ---
class LongitudinalImageCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window)
        
        # --- Novos: Valores padrão para os campos de entrada ---
        self._default_values = {
            'ra': 0.1,    # Ohm/km
            'rb': 0.1,    # Ohm/km
            'rc': 0.1,    # Ohm/km
            'R': 0.01,    # m
            'Rmg': '',    # Pode deixar vazio se R for o padrão
            'xa': 0.0,    # m
            'xb': 3.0,    # m
            'xc': 6.0,    # m
            'ha': 15.0,   # m
            'hb': 15.0,   # m
            'hc': 15.0,   # m
            'l': 10.0     # km
        }

        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()
        
        # Inicializa a Treeview com NaNs, como antes
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Impedância - Longitudinal Imagem")
        self.calc_window.geometry("700x500")
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify()

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.45)

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
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
        self.ra_entry.place(relx=.1, rely=.32, relwidth=0.08)
        self.ra_entry.insert(0, self._default_values['ra']) # Default Value

        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.44)
        self.rb_entry = Entry(self.frame_info)
        self.rb_entry.place(relx=.1, rely=.44, relwidth=0.08)
        self.rb_entry.insert(0, self._default_values['rb']) # Default Value

        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.56)
        self.rc_entry = Entry(self.frame_info)
        self.rc_entry.place(relx=.1, rely=.56, relwidth=0.08)
        self.rc_entry.insert(0, self._default_values['rc']) # Default Value

        # --- Labels e Entradas de Raio e RMG ---
        Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE').place(relx=0.01, rely=.68)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.2, rely=.68, relwidth=0.08)
        self.r_entry.insert(0, self._default_values['R']) # Default Value

        Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE').place(relx=0.01, rely=.80)
        self.rmg_entry = Entry(self.frame_info)
        self.rmg_entry.place(relx=.2, rely=.80, relwidth=0.08)
        self.rmg_entry.insert(0, self._default_values['Rmg']) # Default Value (vazio, pois R é o padrão)

        # --- Labels e Entradas de Coordenadas ---
        Label(self.frame_info, text='Coordenadas dos Cabos (m)', bg='#BEBEBE').place(relx=.4, rely=.2)

        Label(self.frame_info, text='Xa:', bg='#BEBEBE').place(relx=.4, rely=.32)
        self.xa_entry = Entry(self.frame_info)
        self.xa_entry.place(relx=.48, rely=.32, relwidth=0.08)
        self.xa_entry.insert(0, self._default_values['xa']) # Default Value

        Label(self.frame_info, text='Xb:', bg='#BEBEBE').place(relx=.4, rely=.44)
        self.xb_entry = Entry(self.frame_info)
        self.xb_entry.place(relx=.48, rely=.44, relwidth=0.08)
        self.xb_entry.insert(0, self._default_values['xb']) # Default Value

        Label(self.frame_info, text='Xc:', bg='#BEBEBE').place(relx=.4, rely=.56)
        self.xc_entry = Entry(self.frame_info)
        self.xc_entry.place(relx=.48, rely=.56, relwidth=0.08)
        self.xc_entry.insert(0, self._default_values['xc']) # Default Value

        Label(self.frame_info, text='Ha:', bg='#BEBEBE').place(relx=.6, rely=.32)
        self.ha_entry = Entry(self.frame_info)
        self.ha_entry.place(relx=.68, rely=.32, relwidth=0.08)
        self.ha_entry.insert(0, self._default_values['ha']) # Default Value

        Label(self.frame_info, text='Hb:', bg='#BEBEBE').place(relx=.6, rely=.44)
        self.hb_entry = Entry(self.frame_info)
        self.hb_entry.place(relx=.68, rely=.44, relwidth=0.08)
        self.hb_entry.insert(0, self._default_values['hb']) # Default Value

        Label(self.frame_info, text='Hc:', bg='#BEBEBE').place(relx=.6, rely=.56)
        self.hc_entry = Entry(self.frame_info)
        self.hc_entry.place(relx=.68, rely=.56, relwidth=0.08)
        self.hc_entry.insert(0, self._default_values['hc']) # Default Value

        Label(self.frame_info, text='Comp. da Linha (l) [km]:', bg='#BEBEBE').place(relx=.4, rely=.68)
        self.l_entry = Entry(self.frame_info)
        self.l_entry.place(relx=.68, rely=.68, relwidth=0.08)
        self.l_entry.insert(0, self._default_values['l']) # Default Value

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
        # Limpa os campos e insere os valores padrão novamente
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
        self.l_entry.delete(0,END)

        self.ra_entry.insert(0, self._default_values['ra'])
        self.rb_entry.insert(0, self._default_values['rb'])
        self.rc_entry.insert(0, self._default_values['rc'])
        self.r_entry.insert(0, self._default_values['R'])
        self.rmg_entry.insert(0, self._default_values['Rmg'])
        self.xa_entry.insert(0, self._default_values['xa'])
        self.xb_entry.insert(0, self._default_values['xb'])
        self.xc_entry.insert(0, self._default_values['xc'])
        self.ha_entry.insert(0, self._default_values['ha'])
        self.hb_entry.insert(0, self._default_values['hb'])
        self.hc_entry.insert(0, self._default_values['hc'])
        self.l_entry.insert(0, self._default_values['l'])
        
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
            
            # Novo: Comprimento da linha em quilômetros (input do usuário)
            l_km = float(self.l_entry.get()) if self.l_entry.get() else 0.0
            # Convertendo para metros, pois a função espera metros
            l_meters = l_km * 1000.0
            
            return {
                'ra': ra, 'rb': rb, 'rc': rc,
                'xa': xa, 'ha': ha,
                'xb': xb, 'hb': hb,
                'xc': xc, 'hc': hc,
                'l': l_meters,
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
            # Certifique-se que 'metodo_imagem_long' está importado ou acessível no seu projeto
            Z_matrix = metodo_imagem_long( # Chama a função específica para "Longitudinal Imagem"
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa=params['xa'], ha=params['ha'],
                xb=params['xb'], hb=params['hb'],
                xc=params['xc'], hc=params['hc'],
                l=params['l'],
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
        
        complex_format = "({:.6f} + j{:.6f})" # Formato para exibir números complexos
        row_labels = ["A", "B", "C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(Z_matrix.shape[1]):
                complex_num = Z_matrix[i, j]
                # Verifica se o número é NaN para exibir vazio
                if np.isnan(complex_num.real) and np.isnan(complex_num.imag):
                    formatted_value = ""
                else:
                    formatted_value = complex_format.format(complex_num.real, complex_num.imag)
                row_values.append(formatted_value)
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values))

# --- Classe para a Tela de Cálculo do Método de Carson com Correção Longitudinais ---
class CarsonLongitudinalCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.carson_window = Toplevel(master_window)
        
        # --- Valores padrão para os campos de entrada ---
        self._default_values = {
            'ra': 0.1,    # Ohm/km
            'rb': 0.1,    # Ohm/km
            'rc': 0.1,    # Ohm/km
            'R': 0.01,    # m
            'Rmg': '',    # Pode deixar vazio se R for o padrão
            'rho': 100.0, # Ohm-m
            'xa': 0.0,    # m
            'xb': 3.0,    # m
            'xc': 6.0,    # m
            'ha': 15.0,   # m
            'hb': 15.0,   # m
            'hc': 15.0,   # m
            'l': 10.0     # km
        }

        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()
        
        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _setup_window(self):
        self.carson_window.title("Cálculo de Impedância - Longitudinal Carson (Correção)")
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
        self.ra_entry.insert(0, self._default_values['ra']) # Default Value

        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.44)
        self.rb_entry = Entry(self.frame_info)
        self.rb_entry.place(relx=.25, rely=.44, relwidth=0.08)
        self.rb_entry.insert(0, self._default_values['rb']) # Default Value

        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.56)
        self.rc_entry = Entry(self.frame_info)
        self.rc_entry.place(relx=.25, rely=.56, relwidth=0.08)
        self.rc_entry.insert(0, self._default_values['rc']) # Default Value

        # --- Labels e Entradas de Raio e RMG ---
        Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE').place(relx=0.01, rely=.68)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.25, rely=.68, relwidth=0.08)
        self.r_entry.insert(0, self._default_values['R']) # Default Value

        Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE').place(relx=0.01, rely=.80)
        self.rmg_entry = Entry(self.frame_info)
        self.rmg_entry.place(relx=.25, rely=.80, relwidth=0.08)
        self.rmg_entry.insert(0, self._default_values['Rmg']) # Default Value (vazio)

        # --- Labels e Entradas de Resistividade do Solo ---
        Label(self.frame_info, text='Resistividade do Solo (ρ) [Ohm-m]', bg='#BEBEBE').place(relx=0.4, rely=.1)
        self.rho_entry = Entry(self.frame_info)
        self.rho_entry.place(relx=.7, rely=.1, relwidth=0.08) # Alinhado com as coordenadas X
        self.rho_entry.insert(0, self._default_values['rho']) # Default Value

        # --- Labels e Entradas de Coordenadas ---
        Label(self.frame_info, text='Coordenadas dos Cabos (m)', bg='#BEBEBE').place(relx=.4, rely=.2)

        Label(self.frame_info, text='Xa:', bg='#BEBEBE').place(relx=.4, rely=.32)
        self.xa_entry = Entry(self.frame_info)
        self.xa_entry.place(relx=.48, rely=.32, relwidth=0.08)
        self.xa_entry.insert(0, self._default_values['xa']) # Default Value

        Label(self.frame_info, text='Xb:', bg='#BEBEBE').place(relx=.4, rely=.44)
        self.xb_entry = Entry(self.frame_info)
        self.xb_entry.place(relx=.48, rely=.44, relwidth=0.08)
        self.xb_entry.insert(0, self._default_values['xb']) # Default Value

        Label(self.frame_info, text='Xc:', bg='#BEBEBE').place(relx=.4, rely=.56)
        self.xc_entry = Entry(self.frame_info)
        self.xc_entry.place(relx=.48, rely=.56, relwidth=0.08)
        self.xc_entry.insert(0, self._default_values['xc']) # Default Value

        Label(self.frame_info, text='Ha:', bg='#BEBEBE').place(relx=.62, rely=.32)
        self.ha_entry = Entry(self.frame_info)
        self.ha_entry.place(relx=.7, rely=.32, relwidth=0.08)
        self.ha_entry.insert(0, self._default_values['ha']) # Default Value

        Label(self.frame_info, text='Hb:', bg='#BEBEBE').place(relx=.62, rely=.44)
        self.hb_entry = Entry(self.frame_info)
        self.hb_entry.place(relx=.7, rely=.44, relwidth=0.08)
        self.hb_entry.insert(0, self._default_values['hb']) # Default Value

        Label(self.frame_info, text='Hc:', bg='#BEBEBE').place(relx=.62, rely=.56)
        self.hc_entry = Entry(self.frame_info)
        self.hc_entry.place(relx=.7, rely=.56, relwidth=0.08)
        self.hc_entry.insert(0, self._default_values['hc']) # Default Value

        # --- Labels e Entradas de Comprimento da Linha ---
        Label(self.frame_info, text='Comp. da Linha (l) [km]:', bg='#BEBEBE').place(relx=.4, rely=.68)
        self.l_entry = Entry(self.frame_info)
        self.l_entry.place(relx=.7, rely=.68, relwidth=0.08)
        self.l_entry.insert(0, self._default_values['l']) # Default Value

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
        # Limpa os campos e insere os valores padrão novamente
        self.ra_entry.delete(0,END)
        self.rb_entry.delete(0,END)
        self.rc_entry.delete(0,END)
        self.r_entry.delete(0,END)
        self.rmg_entry.delete(0,END)
        self.rho_entry.delete(0,END)
        self.xa_entry.delete(0,END)
        self.xb_entry.delete(0,END)
        self.xc_entry.delete(0,END)
        self.ha_entry.delete(0,END)
        self.hb_entry.delete(0,END)
        self.hc_entry.delete(0,END)
        self.l_entry.delete(0,END) 

        self.ra_entry.insert(0, self._default_values['ra'])
        self.rb_entry.insert(0, self._default_values['rb'])
        self.rc_entry.insert(0, self._default_values['rc'])
        self.r_entry.insert(0, self._default_values['R'])
        self.rmg_entry.insert(0, self._default_values['Rmg'])
        self.rho_entry.insert(0, self._default_values['rho'])
        self.xa_entry.insert(0, self._default_values['xa'])
        self.xb_entry.insert(0, self._default_values['xb'])
        self.xc_entry.insert(0, self._default_values['xc'])
        self.ha_entry.insert(0, self._default_values['ha'])
        self.hb_entry.insert(0, self._default_values['hb'])
        self.hc_entry.insert(0, self._default_values['hc'])
        self.l_entry.insert(0, self._default_values['l'])
        
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _get_input_values(self):
        try:
            # Resistências do condutor em Ohms/km (input do usuário)
            ra_km = float(self.ra_entry.get()) if self.ra_entry.get() else 0.0
            rb_km = float(self.rb_entry.get()) if self.rb_entry.get() else 0.0
            rc_km = float(self.rc_entry.get()) if self.rc_entry.get() else 0.0

            # Convertendo para Ohms/metro, pois a função `Metodo_Carson_long` espera Ohms/metro para Ra, Rb, Rc
            ra = ra_km / 1000.0
            rb = rb_km / 1000.0
            rc = rc_km / 1000.0

            R_val = float(self.r_entry.get()) if self.r_entry.get() else None
            Rmg_val = float(self.rmg_entry.get()) if self.rmg_entry.get() else None
            
            rho = float(self.rho_entry.get()) if self.rho_entry.get() else 0.0
            
            xa = float(self.xa_entry.get()) if self.xa_entry.get() else 0.0
            xb = float(self.xb_entry.get()) if self.xb_entry.get() else 0.0
            xc = float(self.xc_entry.get()) if self.xc_entry.get() else 0.0

            ha = float(self.ha_entry.get()) if self.ha_entry.get() else 0.0
            hb = float(self.hb_entry.get()) if self.hb_entry.get() else 0.0
            hc = float(self.hc_entry.get()) if self.hc_entry.get() else 0.0
            
            # Comprimento da linha em quilômetros (input do usuário)
            l_km = float(self.l_entry.get()) if self.l_entry.get() else 0.0
            
            return {
                'ra': ra, 'rb': rb, 'rc': rc, # Estes são em Ohms/metro agora
                'xa': xa, 'ha': ha,
                'xb': xb, 'hb': hb,
                'xc': xc, 'hc': hc,
                'rho': rho,
                'l_km': l_km, # Retornando 'l' em KM para uso direto no cálculo final
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
            # CHAMA A FUNÇÃO Metodo_Carson_long
            # A função Metodo_Carson_long agora retorna a impedância por Ohms/km
            Z_matrix_per_km = Metodo_Carson_long(
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa=params['xa'], ha=params['ha'],
                xb=params['xb'], hb=params['hb'],
                xc=params['xc'], hc=params['hc'],
                rho=params['rho'],
                # Não passamos 'l' para Metodo_Carson_long, pois ela calcula Ohms/km
                R=params['R'], Rmg_val=params['Rmg_val']
            )
            
            # Recupera o comprimento da linha em KM
            l_km = params['l_km']

            # Calcula a impedância TOTAL da linha (em Ohms)
            # Z_total = Z_por_km * comprimento_em_km
            Z_final_total_ohms = Z_matrix_per_km * l_km
            
            self._insert_data_to_treeview(Z_final_total_ohms)
            messagebox.showinfo("Cálculo Concluído", "A matriz de impedância total da linha foi calculada e exibida na tabela (Ohms).")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, Z_matrix):
        for i in self.lista_CAP.get_children():
            self.lista_CAP.delete(i)
        
        # Formato para exibir números complexos com 6 casas decimais
        complex_format = "({:.6f} + j{:.6f})" 
        row_labels = ["A", "B", "C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(Z_matrix.shape[1]):
                complex_num = Z_matrix[i, j]
                # Verifica se é NaN para exibir vazio, caso contrário formata
                if np.isnan(complex_num.real) and np.isnan(complex_num.imag):
                    formatted_value = "" 
                else:
                    formatted_value = complex_format.format(complex_num.real, complex_num.imag)
                row_values.append(formatted_value)
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values))

# --- A função 'metodo_carson_para_raio' deve ser importada ou definida em outro lugar acessível ---
class CarsonGroundWireCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window)
        
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()

        # Valor inicial vazio, indicando unidade por km (antes de multiplicar por L)
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex), unit="Ohm/km") 

    def _setup_window(self):
        self.calc_window.title("Cálculo de Impedância - Método de Carson com Cabo Para-Raio")
        self.calc_window.geometry("900x600") 
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify()

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.55)
        
        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.59, relwidth=0.96, relheight=0.39)

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
        self.ra_entry.insert(0, "0.1") # Valor default ajustado

        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.28)
        self.rb_entry = Entry(self.frame_info)
        self.rb_entry.place(relx=.08, rely=.28, relwidth=0.08)
        self.rb_entry.insert(0, "0.1") # Valor default ajustado

        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.36)
        self.rc_entry = Entry(self.frame_info)
        self.rc_entry.place(relx=.08, rely=.36, relwidth=0.08)
        self.rc_entry.insert(0, "0.1") # Valor default ajustado
        
        Label(self.frame_info, text='Rp:', bg='#BEBEBE').place(relx=0.01, rely=.44)
        self.rp_entry = Entry(self.frame_info)
        self.rp_entry.place(relx=.08, rely=.44, relwidth=0.08)
        self.rp_entry.insert(0, "0.15") # Valor default (para-raio)

        # --- Labels e Entradas de Raio e RMG ---
        Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE').place(relx=0.01, rely=.55)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.18, rely=.55, relwidth=0.08)
        self.r_entry.insert(0, "0.012") # Valor default (raio físico)

        Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE').place(relx=0.01, rely=.63)
        self.rmg_entry = Entry(self.frame_info)
        self.rmg_entry.place(relx=.18, rely=.63, relwidth=0.08)
        # self.rmg_entry.insert(0, "0.0096") # Valor default (descomente se preferir preencher RMG em vez de R)

        # --- Entrada de Resistividade do Solo ---
        Label(self.frame_info, text='Resistividade Solo (rho) [Ohm.m]', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=0.4, rely=.55)
        self.rho_entry = Entry(self.frame_info)
        self.rho_entry.place(relx=.68, rely=.55, relwidth=0.08)
        self.rho_entry.insert(0, "100") # Valor default

        # --- Campo: Distância (L) ---
        Label(self.frame_info, text='Distância (L) [km]', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=0.4, rely=.63)
        self.l_entry = Entry(self.frame_info)
        self.l_entry.place(relx=.68, rely=.63, relwidth=0.08)
        self.l_entry.insert(0, "10") # Valor default

        # --- Labels e Entradas de Coordenadas (X, H) para Fases e Para-Raio ---
        Label(self.frame_info, text='Coordenadas dos Condutores (m)', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=.4, rely=.12)

        # Fase A
        Label(self.frame_info, text='Xa:', bg='#BEBEBE').place(relx=.4, rely=.2)
        self.xa_entry = Entry(self.frame_info)
        self.xa_entry.place(relx=.48, rely=.2, relwidth=0.08)
        self.xa_entry.insert(0, "0.0") 
        Label(self.frame_info, text='Ha:', bg='#BEBEBE').place(relx=.6, rely=.2)
        self.ha_entry = Entry(self.frame_info)
        self.ha_entry.place(relx=.68, rely=.2, relwidth=0.08)
        self.ha_entry.insert(0, "15") 

        # Fase B
        Label(self.frame_info, text='Xb:', bg='#BEBEBE').place(relx=.4, rely=.28)
        self.xb_entry = Entry(self.frame_info)
        self.xb_entry.place(relx=.48, rely=.28, relwidth=0.08)
        self.xb_entry.insert(0, "1.5") 
        Label(self.frame_info, text='Hb:', bg='#BEBEBE').place(relx=.6, rely=.28)
        self.hb_entry = Entry(self.frame_info)
        self.hb_entry.place(relx=.68, rely=.28, relwidth=0.08)
        self.hb_entry.insert(0, "15") 

        # Fase C
        Label(self.frame_info, text='Xc:', bg='#BEBEBE').place(relx=.4, rely=.36)
        self.xc_entry = Entry(self.frame_info)
        self.xc_entry.place(relx=.48, rely=.36, relwidth=0.08)
        self.xc_entry.insert(0, "3.0") 
        Label(self.frame_info, text='Hc:', bg='#BEBEBE').place(relx=.6, rely=.36)
        self.hc_entry = Entry(self.frame_info)
        self.hc_entry.place(relx=.68, rely=.36, relwidth=0.08)
        self.hc_entry.insert(0, "15") 

        # Para-raio P
        Label(self.frame_info, text='Xp:', bg='#BEBEBE').place(relx=.4, rely=.44)
        self.xp_entry = Entry(self.frame_info)
        self.xp_entry.place(relx=.48, rely=.44, relwidth=0.08)
        self.xp_entry.insert(0, "1.5") 
        Label(self.frame_info, text='Hp:', bg='#BEBEBE').place(relx=.6, rely=.44)
        self.hp_entry = Entry(self.frame_info)
        self.hp_entry.place(relx=.68, rely=.44, relwidth=0.08)
        self.hp_entry.insert(0, "20") 
        
    def _setup_treeview(self):
        self.lista_impedancias = ttk.Treeview(self.frame_result, height=3,
                                             columns=('col1','col2','col3'))
        self.lista_impedancias.heading("#0", text="")
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
        # Limpa todos os campos e depois os preenche novamente com os valores default
        self.ra_entry.delete(0, END)
        self.rb_entry.delete(0, END)
        self.rc_entry.delete(0, END)
        self.rp_entry.delete(0, END)
        self.r_entry.delete(0, END)
        self.rmg_entry.delete(0, END)
        self.rho_entry.delete(0, END)
        self.l_entry.delete(0, END) 
        self.xa_entry.delete(0, END)
        self.xb_entry.delete(0, END)
        self.xc_entry.delete(0, END)
        self.xp_entry.delete(0, END)
        self.ha_entry.delete(0, END)
        self.hb_entry.delete(0, END)
        self.hc_entry.delete(0, END)
        self.hp_entry.delete(0, END)
        
        # Inserindo os valores default novamente após a limpeza
        self.ra_entry.insert(0, "0.1") # Ajustado
        self.rb_entry.insert(0, "0.1") # Ajustado
        self.rc_entry.insert(0, "0.1") # Ajustado
        self.rp_entry.insert(0, "0.15")
        self.r_entry.insert(0, "0.012")
        # self.rmg_entry.insert(0, "0.0096") # Se usar RMG default
        self.rho_entry.insert(0, "100")
        self.l_entry.insert(0, "10")
        self.xa_entry.insert(0, "0.0") 
        self.xb_entry.insert(0, "1.5") 
        self.xc_entry.insert(0, "3.0") 
        self.xp_entry.insert(0, "1.5") 
        self.ha_entry.insert(0, "15")
        self.hb_entry.insert(0, "15")
        self.hc_entry.insert(0, "15")
        self.hp_entry.insert(0, "20")

        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex), unit="Ohm/km") 

    def _get_input_values(self):
        try:
            ra_km = float(self.ra_entry.get()) if self.ra_entry.get() else 0.0
            rb_km = float(self.rb_entry.get()) if self.rb_entry.get() else 0.0
            rc_km = float(self.rc_entry.get()) if self.rc_entry.get() else 0.0
            rp_km = float(self.rp_entry.get()) if self.rp_entry.get() else 0.0

            ra = ra_km / 1000.0
            rb = rb_km / 1000.0
            rc = rc_km / 1000.0
            rp = rp_km / 1000.0

            R_val = float(self.r_entry.get()) if self.r_entry.get() else None
            Rmg_val = float(self.rmg_entry.get()) if self.rmg_entry.get() else None
            
            rho = float(self.rho_entry.get()) if self.rho_entry.get() else None
            L_val = float(self.l_entry.get()) if self.l_entry.get() else None 

            xa = float(self.xa_entry.get()) if self.xa_entry.get() else 0.0
            xb = float(self.xb_entry.get()) if self.xb_entry.get() else 0.0
            xc = float(self.xc_entry.get()) if self.xc_entry.get() else 0.0
            xp = float(self.xp_entry.get()) if self.xp_entry.get() else 0.0

            ha = float(self.ha_entry.get()) if self.ha_entry.get() else 0.0
            hb = float(self.hb_entry.get()) if self.hb_entry.get() else 0.0
            hc = float(self.hc_entry.get()) if self.hc_entry.get() else 0.0
            hp = float(self.hp_entry.get()) if self.hp_entry.get() else 0.0
            
            if rho is None:
                raise ValueError("A resistividade do solo (rho) é um campo obrigatório.")
            if L_val is None or L_val <= 0:
                raise ValueError("A distância (L) é um campo obrigatório e deve ser um valor positivo.")
            
            return {
                'ra': ra, 'rb': rb, 'rc': rc, 'rp': rp,
                'xa': xa, 'ha': ha,
                'xb': xb, 'hb': hb,
                'xc': xc, 'hc': hc,
                'xp': xp, 'hp': hp,
                'rho': rho,
                'R': R_val, 'Rmg_val': Rmg_val,
                'L': L_val 
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Detalhes: {e}")
            return None

    def _calculate_impedance(self):
        params = self._get_input_values()
        if params is None:
            return

        try:
            # Chama a função 'metodo_carson_para_raio' que deve ser definida ou importada
            Z_matrix_per_km = metodo_carson_para_raio(
                ra=params['ra'], rb=params['rb'], rc=params['rc'], rp=params['rp'],
                xa=params['xa'], ha=params['ha'],
                xb=params['xb'], hb=params['hb'],
                xc=params['xc'], hc=params['hc'],
                xp=params['xp'], hp=params['hp'],
                rho=params['rho'],
                R=params['R'], Rmg_val=params['Rmg_val']
            )
            
            # Multiplica a matriz Z (Ohm/km) pela distância L (km) para obter a impedância total (Ohm)
            L = params['L']
            Z_matrix_total = Z_matrix_per_km * L

            self._insert_data_to_treeview(Z_matrix_total, unit="Ohm") # Exibe a impedância total em Ohms
            messagebox.showinfo("Cálculo Concluído", f"A matriz de impedância total da linha ({L} km) foi calculada e exibida na tabela.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, Z_matrix, unit="Ohm"):
        for i in self.lista_impedancias.get_children():
            self.lista_impedancias.delete(i)
        
        # Atualiza os cabeçalhos da Treeview com a unidade correta
        self.lista_impedancias.heading("col1", text=f"Condutor A")
        self.lista_impedancias.heading("col2", text=f"Condutor B")
        self.lista_impedancias.heading("col3", text=f"Condutor C")

        complex_format = "({:.6f} + j{:.6f})"
        row_labels = ["Condutor A", "Condutor B", "Condutor C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(Z_matrix.shape[1]):
                complex_num = Z_matrix[i, j]
                if np.isnan(complex_num.real) and np.isnan(complex_num.imag):
                    formatted_value = ""
                else:
                    formatted_value = complex_format.format(complex_num.real, complex_num.imag)
                row_values.append(formatted_value)
            
            self.lista_impedancias.insert("", END, text=row_label, values=tuple(row_values))

# --- Classe para a Tela de Cálculo do Método de Carson com Transposição ---
class CarsonTransposedCalculator:
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
        self.calc_window.title("Cálculo de Impedância - Método de Carson Transposto") # Título da janela
        self.calc_window.geometry("850x550") # Dimensões da janela (semelhante à anterior)
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

        # --- Labels e Entradas de Resistências (Fases) ---
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
        
        # --- Labels e Entradas de Raio e RMG ---
        Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE').place(relx=0.01, rely=.47)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.18, rely=.47, relwidth=0.08)

        Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE').place(relx=0.01, rely=.55)
        self.rmg_entry = Entry(self.frame_info)
        self.rmg_entry.place(relx=.18, rely=.55, relwidth=0.08)

        # --- Entrada de Resistividade do Solo ---
        Label(self.frame_info, text='Resistividade Solo (rho) [Ohm.m]', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=0.01, rely=.66)
        self.rho_entry = Entry(self.frame_info)
        self.rho_entry.place(relx=.28, rely=.66, relwidth=0.08)

        # --- Labels e Entradas de Coordenadas (X, H) para Fases ---
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
        
        # --- Labels e Entradas de Comprimento das Seções de Transposição ---
        Label(self.frame_info, text='Comprimentos das Seções (m)', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=.4, rely=.47)
        Label(self.frame_info, text='L1:', bg='#BEBEBE').place(relx=.4, rely=.55)
        self.l1_entry = Entry(self.frame_info)
        self.l1_entry.place(relx=.48, rely=.55, relwidth=0.08)

        Label(self.frame_info, text='L2:', bg='#BEBEBE').place(relx=.4, rely=.63)
        self.l2_entry = Entry(self.frame_info)
        self.l2_entry.place(relx=.48, rely=.63, relwidth=0.08)

        Label(self.frame_info, text='L3:', bg='#BEBEBE').place(relx=.4, rely=.71)
        self.l3_entry = Entry(self.frame_info)
        self.l3_entry.place(relx=.48, rely=.71, relwidth=0.08)

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
        self.r_entry.delete(0, END)
        self.rmg_entry.delete(0, END)
        self.rho_entry.delete(0, END)
        self.xa_entry.delete(0, END)
        self.xb_entry.delete(0, END)
        self.xc_entry.delete(0, END)
        self.ha_entry.delete(0, END)
        self.hb_entry.delete(0, END)
        self.hc_entry.delete(0, END)
        self.l1_entry.delete(0, END) # Limpa l1
        self.l2_entry.delete(0, END) # Limpa l2
        self.l3_entry.delete(0, END) # Limpa l3
        
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

            # Convertendo para Ohms/metro, pois a função `metodo_carson_transp` espera Ohms/metro
            ra = ra_km / 1000.0
            rb = rb_km / 1000.0
            rc = rc_km / 1000.0

            R_val = float(self.r_entry.get()) if self.r_entry.get() else None
            Rmg_val = float(self.rmg_entry.get()) if self.rmg_entry.get() else None
            
            rho = float(self.rho_entry.get()) if self.rho_entry.get() else None # Resistividade do solo

            # Coordenadas X
            xa = float(self.xa_entry.get()) if self.xa_entry.get() else 0.0
            xb = float(self.xb_entry.get()) if self.xb_entry.get() else 0.0
            xc = float(self.xc_entry.get()) if self.xc_entry.get() else 0.0

            # Coordenadas H (altura)
            ha = float(self.ha_entry.get()) if self.ha_entry.get() else 0.0
            hb = float(self.hb_entry.get()) if self.hb_entry.get() else 0.0
            hc = float(self.hc_entry.get()) if self.hc_entry.get() else 0.0

            # Comprimentos das seções de transposição
            l1 = float(self.l1_entry.get()) if self.l1_entry.get() else 0.0
            l2 = float(self.l2_entry.get()) if self.l2_entry.get() else 0.0
            l3 = float(self.l3_entry.get()) if self.l3_entry.get() else 0.0
            
            # Validação específica para rho, pois a função espera um valor válido
            if rho is None:
                raise ValueError("A resistividade do solo (rho) é um campo obrigatório.")
            
            return {
                'ra': ra, 'rb': rb, 'rc': rc,
                'xa': xa, 'ha': ha,
                'xb': xb, 'hb': hb,
                'xc': xc, 'hc': hc,
                'rho': rho,
                'l1': l1, 'l2': l2, 'l3': l3, # Incluindo comprimentos
                'R': R_val, 'Rmg_val': Rmg_val
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Detalhes: {e}")
            return None

    def _calculate_impedance(self):
        """
        Coleta os inputs, chama a função de cálculo do Método de Carson com Transposição,
        e exibe os resultados na Treeview.
        """
        params = self._get_input_values()
        if params is None:
            return # Sai se houver erro na validação dos inputs

        try:
            # Chama a função específica para "Carson com Transposição"
            Z_matrix = metodo_carson_transp(
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa=params['xa'], ha=params['ha'],
                xb=params['xb'], hb=params['hb'],
                xc=params['xc'], hc=params['hc'],
                rho=params['rho'],
                l1=params['l1'], l2=params['l2'], l3=params['l3'], # Passa os comprimentos
                R=params['R'], Rmg_val=params['Rmg_val']
            )
            self._insert_data_to_treeview(Z_matrix)
            messagebox.showinfo("Cálculo Concluído", "A matriz de impedância Z transposta foi calculada e exibida na tabela.")
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
        row_labels = ["Z_A", "Z_B", "Z_C"] # Rótulos para as linhas da matriz

        for i, row_label in enumerate(row_labels):
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

# --- Classe para a Tela de Cálculo do RMG de Feixes de Condutores ---
class BundleConductorRMGCalculator:
    def __init__(self, master_window):
        self.master_window = master_window  # Armazena a janela principal para retornar
        self.calc_window = Toplevel(master_window)  # Cria uma nova janela Toplevel para este método
        
        self._setup_window()  # Configura propriedades da janela
        self._setup_frames()  # Cria e posiciona os frames
        self._setup_widgets() # Cria e posiciona os widgets de entrada e botões
        self._setup_treeview() # Configura a Treeview para exibir o resultado

        # Preenche a Treeview com um valor vazio/NaN ao iniciar
        self._insert_rmg_to_treeview(np.nan) # Usamos np.nan para indicar vazio inicialmente

    def _setup_window(self):
        self.calc_window.title("Cálculo de RMG de Feixe de Condutores") # Título da janela
        self.calc_window.geometry("550x350") # Dimensões da janela
        self.calc_window.configure(background='#2F4F4F') # Cor de fundo
        self.calc_window.resizable(False, False) # Impede redimensionamento
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing) # Gerencia fechamento da janela

    def _on_closing(self):
        self.calc_window.destroy()  # Destroi a janela de cálculo atual
        self.master_window.deiconify() # Reexibe a janela principal

    def _setup_frames(self):
        # Frame superior para entradas de dados
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.6)

        # Frame inferior para o resultado na Treeview
        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.65, relwidth=0.96, relheight=0.3)

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                   font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.18, relheight=0.12)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                   font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.80, rely=.01, relwidth=0.18, relheight=0.12)

        self.botao_calc = Button(self.frame_info, text='Calcular RMG', bd=4,
                                 font=('Arial',10), command=self._calculate_rmg)
        self.botao_calc.place(relx=.4, rely=.85, relwidth=0.2, relheight=0.12)

        # --- Labels e Entradas para Parâmetros do Feixe ---
        Label(self.frame_info, text='Número de subcondutores (n):', bg='#BEBEBE').place(relx=0.05, rely=.2)
        self.n_entry = Entry(self.frame_info)
        self.n_entry.place(relx=.5, rely=.2, relwidth=0.2)

        Label(self.frame_info, text='Distância entre subcondutores (d) [m]:', bg='#BEBEBE').place(relx=0.05, rely=.35)
        self.d_entry = Entry(self.frame_info)
        self.d_entry.place(relx=.5, rely=.35, relwidth=0.2)

        Label(self.frame_info, text='Raio físico do subcondutor (R) [m]:', bg='#BEBEBE').place(relx=0.05, rely=.5)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.5, rely=.5, relwidth=0.2)

        Label(self.frame_info, text='OU RMG do subcondutor (Rmg_val) [m]:', bg='#BEBEBE').place(relx=0.05, rely=.65)
        self.rmg_val_entry = Entry(self.frame_info)
        self.rmg_val_entry.place(relx=.5, rely=.65, relwidth=0.2)
        
    def _setup_treeview(self):
        # Configuração da Treeview para exibir o resultado de 1x1
        self.lista_rmg = ttk.Treeview(self.frame_result, height=1, columns=('col1'))
        self.lista_rmg.heading("#0", text="Resultado")
        self.lista_rmg.heading("col1", text="RMG do Feixe [m]")

        self.lista_rmg.column("#0", width=120, anchor=CENTER) # Para o título "Resultado"
        self.lista_rmg.column("col1", width=250, anchor=CENTER) # Para o valor do RMG

        self.lista_rmg.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.8) # Ajusta o tamanho da treeview no frame

        # Não é necessário scrollbar para uma Treeview de 1x1, mas pode ser adicionado se a altura for maior
        # self.scrollLista = Scrollbar(self.frame_result, orient='vertical')
        # self.lista_rmg.configure(yscrollcommand=self.scrollLista.set)
        # self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.8)

    def _clear_inputs(self):
        # Limpa todos os campos de entrada e o resultado na Treeview
        self.n_entry.delete(0, END)
        self.d_entry.delete(0, END)
        self.r_entry.delete(0, END)
        self.rmg_val_entry.delete(0, END)
        self._insert_rmg_to_treeview(np.nan) # Limpa a Treeview com NaN

    def _get_input_values(self):
        """
        Extrai e valida os valores de entrada dos campos da GUI.
        """
        try:
            n_val = int(self.n_entry.get()) if self.n_entry.get() else None
            d_val = float(self.d_entry.get()) if self.d_entry.get() else None
            R_val = float(self.r_entry.get()) if self.r_entry.get() else None
            Rmg_val_cond = float(self.rmg_val_entry.get()) if self.rmg_val_entry.get() else None
            
            # Validações básicas antes de passar para a função de cálculo
            if n_val not in [2, 3, 4]:
                raise ValueError("O número de subcondutores (n) deve ser 2, 3 ou 4.")
            if d_val is None or d_val <= 0:
                raise ValueError("A distância 'd' deve ser um valor numérico positivo.")
            if R_val is None and Rmg_val_cond is None:
                raise ValueError("É necessário fornecer o Raio físico (R) OU o RMG do subcondutor.")

            return {
                'n': n_val, 
                'd': d_val, 
                'R': R_val, 
                'Rmg_val': Rmg_val_cond
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores válidos: {e}")
            return None

    def _calculate_rmg(self):
        """
        Coleta os inputs, chama a função de cálculo do RMG do feixe,
        e exibe o resultado na Treeview.
        """
        params = self._get_input_values()
        if params is None:
            return # Sai se houver erro na validação dos inputs

        try:
            # Chama a função específica para calcular o RMG do feixe
            rmg_feixe_result = calcular_rmg_feixe(
                n=params['n'], 
                d=params['d'], 
                R=params['R'], 
                Rmg_val=params['Rmg_val']
            )
            self._insert_rmg_to_treeview(rmg_feixe_result)
            messagebox.showinfo("Cálculo Concluído", "O RMG do feixe foi calculado e exibido na tabela.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_rmg_to_treeview(self, rmg_value):
        """
        Limpa a Treeview e insere o valor do RMG do feixe.
        """
        # Limpa todas as entradas existentes na Treeview
        for i in self.lista_rmg.get_children():
            self.lista_rmg.delete(i)
        
        formatted_value = ""
        if not np.isnan(rmg_value):
            formatted_value = f"{rmg_value:.6f}" # Formata para 6 casas decimais
        
        # Insere o único valor na Treeview
        # O 'text' é a primeira coluna (referenciada por #0) e 'values' são as colunas nomeadas.
        self.lista_rmg.insert("", END, text="RMG Calculado", values=(formatted_value,))

# --- Classe para a Tela de Cálculo do Método de Síntese ---
class SymmetricalComponentSynthesizer:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window)
        
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()

        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 1), np.nan + 1j*np.nan, dtype=complex))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Tensão de Fase - Síntese de Componentes Simétricas")
        self.calc_window.geometry("700x450") # Ajustado para mais campos
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify()

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.6) # Maior para inputs

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.65, relwidth=0.96, relheight=0.33)

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                   font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.15, relheight=0.09)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                   font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.84, rely=.01, relwidth=0.15, relheight=0.09)

        self.botao_calc = Button(self.frame_info, text='Calcular Tensões de Fase', bd=4,
                                 font=('Arial',10), command=self._calculate_phase_voltages)
        self.botao_calc.place(relx=.4, rely=.88, relwidth=0.25, relheight=0.09)

        # --- Labels e Entradas para Componentes de Sequência ---
        Label(self.frame_info, text='Componentes de Sequência (Módulo e Ângulo em Graus)', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=0.05, rely=.12)

        # Van0 (Sequência Zero)
        Label(self.frame_info, text='Van0 Módulo:', bg='#BEBEBE').place(relx=0.05, rely=.2)
        self.van0_modulo_entry = Entry(self.frame_info)
        self.van0_modulo_entry.place(relx=.2, rely=.2, relwidth=0.2)
        Label(self.frame_info, text='Van0 Ângulo:', bg='#BEBEBE').place(relx=0.45, rely=.2)
        self.van0_angulo_entry = Entry(self.frame_info)
        self.van0_angulo_entry.place(relx=.6, rely=.2, relwidth=0.2)

        # Van1 (Sequência Positiva)
        Label(self.frame_info, text='Van1 Módulo:', bg='#BEBEBE').place(relx=0.05, rely=.35)
        self.van1_modulo_entry = Entry(self.frame_info)
        self.van1_modulo_entry.place(relx=.2, rely=.35, relwidth=0.2)
        Label(self.frame_info, text='Van1 Ângulo:', bg='#BEBEBE').place(relx=0.45, rely=.35)
        self.van1_angulo_entry = Entry(self.frame_info)
        self.van1_angulo_entry.place(relx=.6, rely=.35, relwidth=0.2)

        # Van2 (Sequência Negativa)
        Label(self.frame_info, text='Van2 Módulo:', bg='#BEBEBE').place(relx=0.05, rely=.5)
        self.van2_modulo_entry = Entry(self.frame_info)
        self.van2_modulo_entry.place(relx=.2, rely=.5, relwidth=0.2)
        Label(self.frame_info, text='Van2 Ângulo:', bg='#BEBEBE').place(relx=0.45, rely=.5)
        self.van2_angulo_entry = Entry(self.frame_info)
        self.van2_angulo_entry.place(relx=.6, rely=.5, relwidth=0.2)
        
    def _setup_treeview(self):
        # Configuração da Treeview para exibir as tensões de fase
        self.lista_tensoes = ttk.Treeview(self.frame_result, height=3,
                                          columns=('real_imag', 'mod_ang'))
        self.lista_tensoes.heading("#0", text="Tensão de Fase")
        self.lista_tensoes.heading("real_imag", text="Forma Retangular (Real + j Imaginária)")
        self.lista_tensoes.heading("mod_ang", text="Forma Polar (Módulo ∠ Ângulo)")

        self.lista_tensoes.column("#0", width=100, anchor=CENTER)
        self.lista_tensoes.column("real_imag", width=250, anchor=CENTER)
        self.lista_tensoes.column("mod_ang", width=250, anchor=CENTER)

        self.lista_tensoes.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')
        self.lista_tensoes.configure(yscrollcommand=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)

    def _clear_inputs(self):
        # Limpa todos os campos de entrada e a Treeview
        self.van0_modulo_entry.delete(0, END)
        self.van0_angulo_entry.delete(0, END)
        self.van1_modulo_entry.delete(0, END)
        self.van1_angulo_entry.delete(0, END)
        self.van2_modulo_entry.delete(0, END)
        self.van2_angulo_entry.delete(0, END)
        
        # Limpa a Treeview preenchendo com valores NaN (que serão exibidos como vazio)
        self._insert_data_to_treeview(np.full((3, 1), np.nan + 1j*np.nan, dtype=complex))

    def _get_input_values(self):
        """
        Extrai e valida os valores de entrada dos campos da GUI.
        """
        try:
            van0_m = float(self.van0_modulo_entry.get()) if self.van0_modulo_entry.get() else 0.0
            van0_a = float(self.van0_angulo_entry.get()) if self.van0_angulo_entry.get() else 0.0
            
            van1_m = float(self.van1_modulo_entry.get()) if self.van1_modulo_entry.get() else 0.0
            van1_a = float(self.van1_angulo_entry.get()) if self.van1_angulo_entry.get() else 0.0
            
            van2_m = float(self.van2_modulo_entry.get()) if self.van2_modulo_entry.get() else 0.0
            van2_a = float(self.van2_angulo_entry.get()) if self.van2_angulo_entry.get() else 0.0
            
            return {
                'Van0_modulo': van0_m, 'Van0_angulo': van0_a,
                'Van1_modulo': van1_m, 'Van1_angulo': van1_a,
                'Van2_modulo': van2_m, 'Van2_angulo': van2_a
            }
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos para módulos e ângulos.")
            return None

    def _calculate_phase_voltages(self):
        """
        Coleta os inputs, chama a função de cálculo da Síntese,
        e exibe os resultados na Treeview.
        """
        params = self._get_input_values()
        if params is None:
            return # Sai se houver erro na validação dos inputs

        try:
            # Chama a função específica para a Síntese
            Vabc_matrix = comp_sim_sintese(
                Van0_modulo=params['Van0_modulo'], Van0_angulo=params['Van0_angulo'],
                Van1_modulo=params['Van1_modulo'], Van1_angulo=params['Van1_angulo'],
                Van2_modulo=params['Van2_modulo'], Van2_angulo=params['Van2_angulo']
            )
            self._insert_data_to_treeview(Vabc_matrix)
            messagebox.showinfo("Cálculo Concluído", "As tensões de fase foram calculadas e exibidas na tabela.")
        except Exception as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")

    def _insert_data_to_treeview(self, Vabc_matrix):
        """
        Limpa a Treeview e insere os valores das tensões de fase.
        Formata números complexos para exibição em forma retangular e polar.
        """
        # Limpa todas as entradas existentes na Treeview
        for i in self.lista_tensoes.get_children():
            self.lista_tensoes.delete(i)
        
        # Rótulos para as linhas
        row_labels = ["Va", "Vb", "Vc"]
        
        # Formatos para exibição
        rect_format = "({:.4f} + j{:.4f})"
        polar_format = "{:.4f} ∠ {:.2f}°" # Módulo com 4 casas, Ângulo com 2 casas

        for i, row_label in enumerate(row_labels):
            complex_voltage = Vabc_matrix[i, 0] # A matriz Vabc é uma coluna

            formatted_rect = ""
            formatted_polar = ""

            # Verifica se o número é NaN (ocorre em entradas vazias iniciais)
            if not (np.isnan(complex_voltage.real) and np.isnan(complex_voltage.imag)):
                # Formata a forma retangular
                formatted_rect = rect_format.format(complex_voltage.real, complex_voltage.imag)
                
                # Formata a forma polar
                module = abs(complex_voltage)
                angle_deg = math.degrees(cmath.phase(complex_voltage))
                formatted_polar = polar_format.format(module, angle_deg)
            
            # Insere a linha na Treeview
            self.lista_tensoes.insert("", END, text=row_label, values=(formatted_rect, formatted_polar))

# --- Classe para a Tela de Cálculo do Método de Análise ---
class SymmetricalComponentAnalyzer:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window)
        
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()

        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 1), np.nan + 1j*np.nan, dtype=complex))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Componentes de Sequência - Análise de Componentes Simétricas")
        self.calc_window.geometry("700x450") # Ajustado para campos de entrada
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify()

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.6) # Maior para inputs

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.65, relwidth=0.96, relheight=0.33)

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                   font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.15, relheight=0.09)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                   font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.84, rely=.01, relwidth=0.15, relheight=0.09)

        self.botao_calc = Button(self.frame_info, text='Calcular Componentes de Sequência', bd=4,
                                 font=('Arial',10), command=self._calculate_sequence_components)
        self.botao_calc.place(relx=.35, rely=.88, relwidth=0.35, relheight=0.09)

        # --- Labels e Entradas para Tensões de Fase ---
        Label(self.frame_info, text='Tensões de Fase (Módulo e Ângulo em Graus)', bg='#BEBEBE', font=('Arial', 9, 'bold')).place(relx=0.05, rely=.12)

        # Va
        Label(self.frame_info, text='Va Módulo:', bg='#BEBEBE').place(relx=0.05, rely=.2)
        self.va_modulo_entry = Entry(self.frame_info)
        self.va_modulo_entry.place(relx=.2, rely=.2, relwidth=0.2)
        Label(self.frame_info, text='Va Ângulo:', bg='#BEBEBE').place(relx=0.45, rely=.2)
        self.va_angulo_entry = Entry(self.frame_info)
        self.va_angulo_entry.place(relx=.6, rely=.2, relwidth=0.2)

        # Vb
        Label(self.frame_info, text='Vb Módulo:', bg='#BEBEBE').place(relx=0.05, rely=.35)
        self.vb_modulo_entry = Entry(self.frame_info)
        self.vb_modulo_entry.place(relx=.2, rely=.35, relwidth=0.2)
        Label(self.frame_info, text='Vb Ângulo:', bg='#BEBEBE').place(relx=0.45, rely=.35)
        self.vb_angulo_entry = Entry(self.frame_info)
        self.vb_angulo_entry.place(relx=.6, rely=.35, relwidth=0.2)

        # Vc
        Label(self.frame_info, text='Vc Módulo:', bg='#BEBEBE').place(relx=0.05, rely=.5)
        self.vc_modulo_entry = Entry(self.frame_info)
        self.vc_modulo_entry.place(relx=.2, rely=.5, relwidth=0.2)
        Label(self.frame_info, text='Vc Ângulo:', bg='#BEBEBE').place(relx=0.45, rely=.5)
        self.vc_angulo_entry = Entry(self.frame_info)
        self.vc_angulo_entry.place(relx=.6, rely=.5, relwidth=0.2)
        
    def _setup_treeview(self):
        # Configuração da Treeview para exibir as componentes de sequência
        self.lista_componentes = ttk.Treeview(self.frame_result, height=3,
                                              columns=('real_imag', 'mod_ang'))
        self.lista_componentes.heading("#0", text="Componente")
        self.lista_componentes.heading("real_imag", text="Forma Retangular (Real + j Imaginária)")
        self.lista_componentes.heading("mod_ang", text="Forma Polar (Módulo ∠ Ângulo)")

        self.lista_componentes.column("#0", width=100, anchor=CENTER)
        self.lista_componentes.column("real_imag", width=250, anchor=CENTER)
        self.lista_componentes.column("mod_ang", width=250, anchor=CENTER)

        self.lista_componentes.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')
        self.lista_componentes.configure(yscrollcommand=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)

    def _clear_inputs(self):
        # Limpa todos os campos de entrada e a Treeview
        self.va_modulo_entry.delete(0, END)
        self.va_angulo_entry.delete(0, END)
        self.vb_modulo_entry.delete(0, END)
        self.vb_angulo_entry.delete(0, END)
        self.vc_modulo_entry.delete(0, END)
        self.vc_angulo_entry.delete(0, END)
        
        # Limpa a Treeview preenchendo com valores NaN (que serão exibidos como vazio)
        self._insert_data_to_treeview(np.full((3, 1), np.nan + 1j*np.nan, dtype=complex))

    def _get_input_values(self):
        """
        Extrai e valida os valores de entrada dos campos da GUI.
        """
        try:
            va_m = float(self.va_modulo_entry.get()) if self.va_modulo_entry.get() else 0.0
            va_a = float(self.va_angulo_entry.get()) if self.va_angulo_entry.get() else 0.0
            
            vb_m = float(self.vb_modulo_entry.get()) if self.vb_modulo_entry.get() else 0.0
            vb_a = float(self.vb_angulo_entry.get()) if self.vb_angulo_entry.get() else 0.0
            
            vc_m = float(self.vc_modulo_entry.get()) if self.vc_modulo_entry.get() else 0.0
            vc_a = float(self.vc_angulo_entry.get()) if self.vc_angulo_entry.get() else 0.0
            
            return {
                'Va_modulo': va_m, 'Va_angulo': va_a,
                'Vb_modulo': vb_m, 'Vb_angulo': vb_a,
                'Vc_modulo': vc_m, 'Vc_angulo': vc_a
            }
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos para módulos e ângulos.")
            return None

    def _calculate_sequence_components(self):
        """
        Coleta os inputs, chama a função de cálculo da Análise,
        e exibe os resultados na Treeview.
        """
        params = self._get_input_values()
        if params is None:
            return # Sai se houver erro na validação dos inputs

        try:
            # Chama a função específica para a Análise
            V012_matrix = comp_sim_analise(
                Va_modulo=params['Va_modulo'], Va_angulo=params['Va_angulo'],
                Vb_modulo=params['Vb_modulo'], Vb_angulo=params['Vb_angulo'],
                Vc_modulo=params['Vc_modulo'], Vc_angulo=params['Vc_angulo']
            )
            self._insert_data_to_treeview(V012_matrix)
            messagebox.showinfo("Cálculo Concluído", "As componentes de sequência foram calculadas e exibidas na tabela.")
        except Exception as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")

    def _insert_data_to_treeview(self, V012_matrix):
        """
        Limpa a Treeview e insere os valores das componentes de sequência.
        Formata números complexos para exibição em forma retangular e polar.
        """
        # Limpa todas as entradas existentes na Treeview
        for i in self.lista_componentes.get_children():
            self.lista_componentes.delete(i)
        
        # Rótulos para as linhas
        row_labels = ["V0 (Zero)", "V1 (Positiva)", "V2 (Negativa)"]
        
        # Formatos para exibição
        rect_format = "({:.4f} + j{:.4f})"
        polar_format = "{:.4f} ∠ {:.2f}°" # Módulo com 4 casas, Ângulo com 2 casas

        for i, row_label in enumerate(row_labels):
            complex_component = V012_matrix[i, 0] # A matriz V012 é uma coluna

            formatted_rect = ""
            formatted_polar = ""

            # Verifica se o número é NaN (ocorre em entradas vazias iniciais)
            if not (np.isnan(complex_component.real) and np.isnan(complex_component.imag)):
                # Formata a forma retangular
                formatted_rect = rect_format.format(complex_component.real, complex_component.imag)
                
                # Formata a forma polar
                module = abs(complex_component)
                angle_deg = math.degrees(cmath.phase(complex_component))
                formatted_polar = polar_format.format(module, angle_deg)
            
            # Insere a linha na Treeview
            self.lista_componentes.insert("", END, text=row_label, values=(formatted_rect, formatted_polar))

# --- Classe da janela para cálculo de capacitância imagem ---
class CapacitanceImageCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window) # Cria uma nova janela Toplevel
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()

        # Preenche a Treeview com campos vazios ao iniciar a janela
        # A matriz de capacitância é real, então usamos float.
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=float))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Capacitância - Método da Imagem") # Título ajustado
        self.calc_window.geometry("700x500")
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify() # Reexibe a janela principal

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.45)

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
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
                                 font=('Arial',10), command=self._calculate_capacitance) # Ação de cálculo de capacitância
        self.botao_calc.place(relx=.8, rely=.85, relwidth=0.15, relheight=0.1)

        # --- Labels e Entradas de Coordenadas e Raio ---
        Label(self.frame_info, text='Coordenadas dos Condutores (m)', bg='#BEBEBE').place(relx=.01, rely=.2)

        # Coordenadas X
        Label(self.frame_info, text='X_A:', bg='#BEBEBE').place(relx=.01, rely=.32)
        self.xa_entry = Entry(self.frame_info)
        self.xa_entry.place(relx=.1, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='X_B:', bg='#BEBEBE').place(relx=.01, rely=.44)
        self.xb_entry = Entry(self.frame_info)
        self.xb_entry.place(relx=.1, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='X_C:', bg='#BEBEBE').place(relx=.01, rely=.56)
        self.xc_entry = Entry(self.frame_info)
        self.xc_entry.place(relx=.1, rely=.56, relwidth=0.08)

        # Alturas H
        Label(self.frame_info, text='H_A:', bg='#BEBEBE').place(relx=.25, rely=.32)
        self.ha_entry = Entry(self.frame_info)
        self.ha_entry.place(relx=.34, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='H_B:', bg='#BEBEBE').place(relx=.25, rely=.44)
        self.hb_entry = Entry(self.frame_info)
        self.hb_entry.place(relx=.34, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='H_C:', bg='#BEBEBE').place(relx=.25, rely=.56)
        self.hc_entry = Entry(self.frame_info)
        self.hc_entry.place(relx=.34, rely=.56, relwidth=0.08)

        # Raio
        Label(self.frame_info, text='Raio Condutor (R) [m]:', bg='#BEBEBE').place(relx=0.01, rely=.68)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.2, rely=.68, relwidth=0.08)

        # As entradas de Ra, Rb, Rc e RMG foram removidas por não serem relevantes para capacitância.

    def _setup_treeview(self):
        # A Treeview será usada para exibir a matriz de capacitância (similar à de impedância)
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
        # Limpa apenas os campos de entrada relevantes para capacitância
        self.xa_entry.delete(0, END)
        self.xb_entry.delete(0, END)
        self.xc_entry.delete(0, END)
        self.ha_entry.delete(0, END)
        self.hb_entry.delete(0, END)
        self.hc_entry.delete(0, END)
        self.r_entry.delete(0, END)
        
        # Limpa a Treeview e a preenche com NaN
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=float))

    def _get_input_values(self):
        try:
            # Obtém e valida as coordenadas e o raio
            xa = float(self.xa_entry.get())
            xb = float(self.xb_entry.get())
            xc = float(self.xc_entry.get())

            ha = float(self.ha_entry.get())
            hb = float(self.hb_entry.get())
            hc = float(self.hc_entry.get())

            R = float(self.r_entry.get())

            return {
                'xa': xa, 'xb': xb, 'xc': xc,
                'ha': ha, 'hb': hb, 'hc': hc,
                'R': R
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Detalhes: {e}")
            return None

    def _calculate_capacitance(self):
        params = self._get_input_values()
        if params is None:
            return

        try:
            # Chama a função de cálculo da capacitância
            C_matrix_F_per_m = metodo_imagem_tran(
                xa=params['xa'], xb=params['xb'], xc=params['xc'],
                ha=params['ha'], hb=params['hb'], hc=params['hc'],
                R=params['R']
            )

            # Convertendo para nF/km (nanofarads por quilômetro) para melhor visualização
            C_matrix_nF_per_km = C_matrix_F_per_m * 1e9 * 1e3 # 1e9 para nF, 1e3 para km

            self._insert_data_to_treeview(C_matrix_nF_per_km)
            messagebox.showinfo("Cálculo Concluído", "A matriz de capacitância foi calculada e exibida na tabela.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, C_matrix):
        for i in self.lista_CAP.get_children():
            self.lista_CAP.delete(i)

        # A matriz de capacitância é real, não complexa.
        float_format = "{:.6f}" # Formato para exibir números reais com 6 casas decimais
        row_labels = ["A", "B", "C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(C_matrix.shape[1]):
                value = C_matrix[i, j]
                if np.isnan(value):
                    formatted_value = "" # Exibe vazio se for NaN
                else:
                    formatted_value = float_format.format(value)
                row_values.append(formatted_value)
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values))

# --- CLASSE DA JANELA PARA CÁLCULO DE CAPACITÂNCIA TRANSPOSTA ---
class TransposedCapacitanceCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window) # Cria uma nova janela Toplevel
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()

        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=float))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Capacitância - Transposição")
        self.calc_window.geometry("850x650") # Aumenta o tamanho para acomodar mais campos
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify() # Reexibe a janela principal

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.55) # Aumenta a altura para os campos de entrada

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.6, relwidth=0.96, relheight=0.37) # Ajusta a posição e altura

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                   font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.15, relheight=0.08)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                   font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.80, rely=.01, relwidth=0.15, relheight=0.08)

        self.botao_calc = Button(self.frame_info, text='Calcular', bd=4,
                                 font=('Arial',10), command=self._calculate_transposed_capacitance)
        self.botao_calc.place(relx=.8, rely=.9, relwidth=0.15, relheight=0.08) # Posição ajustada

        # --- Labels e Entradas de Raios dos Condutores ---
        Label(self.frame_info, text='Raios dos Condutores (m)', bg='#BEBEBE').place(relx=0.01, rely=.12)

        Label(self.frame_info, text='Ra:', bg='#BEBEBE').place(relx=0.01, rely=.2)
        self.ra_entry = Entry(self.frame_info)
        self.ra_entry.place(relx=.08, rely=.2, relwidth=0.08)

        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.28)
        self.rb_entry = Entry(self.frame_info)
        self.rb_entry.place(relx=.08, rely=.28, relwidth=0.08)

        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.36)
        self.rc_entry = Entry(self.frame_info)
        self.rc_entry.place(relx=.08, rely=.36, relwidth=0.08)

        # --- Labels e Entradas de Coordenadas para Posição 1 ---
        Label(self.frame_info, text='Posição Física 1 (m)', bg='#BEBEBE').place(relx=.2, rely=.12)

        Label(self.frame_info, text='X_Pos1:', bg='#BEBEBE').place(relx=.2, rely=.2)
        self.xa_pos1_entry = Entry(self.frame_info)
        self.xa_pos1_entry.place(relx=.28, rely=.2, relwidth=0.08)

        Label(self.frame_info, text='H_Pos1:', bg='#BEBEBE').place(relx=.2, rely=.28)
        self.ha_pos1_entry = Entry(self.frame_info)
        self.ha_pos1_entry.place(relx=.28, rely=.28, relwidth=0.08)

        # --- Labels e Entradas de Coordenadas para Posição 2 ---
        Label(self.frame_info, text='Posição Física 2 (m)', bg='#BEBEBE').place(relx=.4, rely=.12)

        Label(self.frame_info, text='X_Pos2:', bg='#BEBEBE').place(relx=.4, rely=.2)
        self.xb_pos2_entry = Entry(self.frame_info)
        self.xb_pos2_entry.place(relx=.48, rely=.2, relwidth=0.08)

        Label(self.frame_info, text='H_Pos2:', bg='#BEBEBE').place(relx=.4, rely=.28)
        self.hb_pos2_entry = Entry(self.frame_info)
        self.hb_pos2_entry.place(relx=.48, rely=.28, relwidth=0.08)

        # --- Labels e Entradas de Coordenadas para Posição 3 ---
        Label(self.frame_info, text='Posição Física 3 (m)', bg='#BEBEBE').place(relx=.6, rely=.12)

        Label(self.frame_info, text='X_Pos3:', bg='#BEBEBE').place(relx=.6, rely=.2)
        self.xc_pos3_entry = Entry(self.frame_info)
        self.xc_pos3_entry.place(relx=.68, rely=.2, relwidth=0.08)

        Label(self.frame_info, text='H_Pos3:', bg='#BEBEBE').place(relx=.6, rely=.28)
        self.hc_pos3_entry = Entry(self.frame_info)
        self.hc_pos3_entry.place(relx=.68, rely=.28, relwidth=0.08)

        # --- Entrada de Resistividade do Solo ---
        Label(self.frame_info, text='Resistividade Solo (rho) [Ohm.m]:', bg='#BEBEBE').place(relx=0.01, rely=.45)
        self.rho_entry = Entry(self.frame_info)
        self.rho_entry.place(relx=.25, rely=.45, relwidth=0.08)

        # --- Entradas de Comprimentos das Seções ---
        Label(self.frame_info, text='Comprimentos das Seções (m)', bg='#BEBEBE').place(relx=0.01, rely=.55)

        Label(self.frame_info, text='L1 (m):', bg='#BEBEBE').place(relx=.01, rely=.63)
        self.l1_entry = Entry(self.frame_info)
        self.l1_entry.place(relx=.08, rely=.63, relwidth=0.08)

        Label(self.frame_info, text='L2 (m):', bg='#BEBEBE').place(relx=.01, rely=.71)
        self.l2_entry = Entry(self.frame_info)
        self.l2_entry.place(relx=.08, rely=.71, relwidth=0.08)

        Label(self.frame_info, text='L3 (m):', bg='#BEBEBE').place(relx=.01, rely=.79)
        self.l3_entry = Entry(self.frame_info)
        self.l3_entry.place(relx=.08, rely=.79, relwidth=0.08)

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
        # Limpa todos os campos de entrada
        self.ra_entry.delete(0, END)
        self.rb_entry.delete(0, END)
        self.rc_entry.delete(0, END)
        self.xa_pos1_entry.delete(0, END)
        self.ha_pos1_entry.delete(0, END)
        self.xb_pos2_entry.delete(0, END)
        self.hb_pos2_entry.delete(0, END)
        self.xc_pos3_entry.delete(0, END)
        self.hc_pos3_entry.delete(0, END)
        self.rho_entry.delete(0, END)
        self.l1_entry.delete(0, END)
        self.l2_entry.delete(0, END)
        self.l3_entry.delete(0, END)

        # Limpa a Treeview e a preenche com NaN
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=float))

    def _get_input_values(self):
        try:
            # Raios dos condutores
            ra = float(self.ra_entry.get())
            rb = float(self.rb_entry.get())
            rc = float(self.rc_entry.get())

            # Coordenadas das Posições Físicas
            xa_pos1 = float(self.xa_pos1_entry.get())
            ha_pos1 = float(self.ha_pos1_entry.get())
            xb_pos2 = float(self.xb_pos2_entry.get())
            hb_pos2 = float(self.hb_pos2_entry.get())
            xc_pos3 = float(self.xc_pos3_entry.get())
            hc_pos3 = float(self.hc_pos3_entry.get())

            # Resistividade do solo
            rho = float(self.rho_entry.get())

            # Comprimentos das seções
            l1 = float(self.l1_entry.get())
            l2 = float(self.l2_entry.get())
            l3 = float(self.l3_entry.get())

            return {
                'ra': ra, 'rb': rb, 'rc': rc,
                'xa_pos1': xa_pos1, 'ha_pos1': ha_pos1,
                'xb_pos2': xb_pos2, 'hb_pos2': hb_pos2,
                'xc_pos3': xc_pos3, 'hc_pos3': hc_pos3,
                'rho': rho,
                'l1': l1, 'l2': l2, 'l3': l3
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Detalhes: {e}")
            return None
        except Exception as e:
            messagebox.showerror("Erro", f"Um erro inesperado ocorreu ao obter os valores: {e}")
            return None


    def _calculate_transposed_capacitance(self):
        params = self._get_input_values()
        if params is None:
            return

        try:
            # Chama a função de cálculo da capacitância transposta
            # Certifique-se de que 'metodo_transposicao_tran' esteja acessível aqui (importada ou definida globalmente)
            C_matrix_total = metodo_transposicao_tran(
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa_pos1=params['xa_pos1'], ha_pos1=params['ha_pos1'],
                xb_pos2=params['xb_pos2'], hb_pos2=params['hb_pos2'],
                xc_pos3=params['xc_pos3'], hc_pos3=params['hc_pos3'],
                rho=params['rho'],
                l1=params['l1'], l2=params['l2'], l3=params['l3']
            )

            # Convertendo para nF (nanofarads) para melhor visualização
            C_matrix_nF = C_matrix_total * 1e9 # Farads -> nanofarads

            self._insert_data_to_treeview(C_matrix_nF)
            messagebox.showinfo("Cálculo Concluído", "A matriz de capacitância transposta foi calculada e exibida na tabela.")
        except NameError:
            messagebox.showerror("Erro de Função", "A função 'metodo_transposicao_tran' não foi encontrada. Certifique-se de que está definida ou importada.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, C_matrix):
        for i in self.lista_CAP.get_children():
            self.lista_CAP.delete(i)

        float_format = "{:.6e}" # Formato para exibir números reais em notação científica para valores pequenos
        row_labels = ["A", "B", "C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(C_matrix.shape[1]):
                value = C_matrix[i, j]
                if np.isnan(value):
                    formatted_value = "" # Exibe vazio se for NaN
                else:
                    formatted_value = float_format.format(value)
                row_values.append(formatted_value)
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values))

# --- CLASSE DA JANELA PARA CÁLCULO DE CAPACITÂNCIA COM CABO PARA-RAIO ---
class CapacitanceGroundWireCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window)
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()

        # Adiciona campos de entrada dinâmicos para os para-raios
        self.num_pr_entries = [] # Para armazenar as Entries para X e H de cada para-raio
        self.r_pr_entries = []   # Para armazenar as Entries para os raios de cada para-raio
        self.add_pr_fields(1) # Começa com 1 cabo para-raio por padrão

        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=float))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Capacitância - Com Cabo Para-Raio")
        self.calc_window.geometry("1000x750") # Aumenta bastante para acomodar todos os campos
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify() # Reexibe a janela principal

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.6) # Mais alto

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.64, relwidth=0.96, relheight=0.34) # Ajusta posição e altura

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                   font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.1, relheight=0.05)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                   font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.9, rely=.01, relwidth=0.08, relheight=0.05)

        self.botao_calc = Button(self.frame_info, text='Calcular', bd=4,
                                 font=('Arial',10), command=self._calculate_capacitance_ground_wire)
        self.botao_calc.place(relx=.9, rely=.92, relwidth=0.08, relheight=0.05)

        # --- Seção para Raios dos Condutores de Fase ---
        Label(self.frame_info, text='Raios Condutores Fase (m)', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.08)
        Label(self.frame_info, text='Ra:', bg='#BEBEBE').place(relx=0.01, rely=.12)
        self.ra_entry = Entry(self.frame_info, width=8)
        self.ra_entry.place(relx=.05, rely=.12)
        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.16)
        self.rb_entry = Entry(self.frame_info, width=8)
        self.rb_entry.place(relx=.05, rely=.16)
        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.20)
        self.rc_entry = Entry(self.frame_info, width=8)
        self.rc_entry.place(relx=.05, rely=.20)

        # --- Seção para Posições Físicas das Fases ---
        Label(self.frame_info, text='Posições Físicas das Fases (m)', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=.2, rely=.08)

        Label(self.frame_info, text='Posição 1 (X, H)', bg='#BEBEBE').place(relx=.2, rely=.12)
        self.xa_pos1_entry = Entry(self.frame_info, width=8)
        self.xa_pos1_entry.place(relx=.32, rely=.12)
        self.ha_pos1_entry = Entry(self.frame_info, width=8)
        self.ha_pos1_entry.place(relx=.38, rely=.12)

        Label(self.frame_info, text='Posição 2 (X, H)', bg='#BEBEBE').place(relx=.2, rely=.16)
        self.xb_pos2_entry = Entry(self.frame_info, width=8)
        self.xb_pos2_entry.place(relx=.32, rely=.16)
        self.hb_pos2_entry = Entry(self.frame_info, width=8)
        self.hb_pos2_entry.place(relx=.38, rely=.16)

        Label(self.frame_info, text='Posição 3 (X, H)', bg='#BEBEBE').place(relx=.2, rely=.20)
        self.xc_pos3_entry = Entry(self.frame_info, width=8)
        self.xc_pos3_entry.place(relx=.32, rely=.20)
        self.hc_pos3_entry = Entry(self.frame_info, width=8)
        self.hc_pos3_entry.place(relx=.38, rely=.20)

        # --- Seção para Resistividade do Solo ---
        Label(self.frame_info, text='Resistividade Solo (rho) [Ohm.m]:', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.28)
        self.rho_entry = Entry(self.frame_info, width=8)
        self.rho_entry.place(relx=.25, rely=.28)

        # --- Seção para Comprimentos das Seções ---
        Label(self.frame_info, text='Comprimentos das Seções (m)', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.35)
        Label(self.frame_info, text='L1 (m):', bg='#BEBEBE').place(relx=.01, rely=.39)
        self.l1_entry = Entry(self.frame_info, width=8)
        self.l1_entry.place(relx=.08, rely=.39)

        Label(self.frame_info, text='L2 (m):', bg='#BEBEBE').place(relx=.01, rely=.43)
        self.l2_entry = Entry(self.frame_info, width=8)
        self.l2_entry.place(relx=.08, rely=.43)

        Label(self.frame_info, text='L3 (m):', bg='#BEBEBE').place(relx=.01, rely=.47)
        self.l3_entry = Entry(self.frame_info, width=8)
        self.l3_entry.place(relx=.08, rely=.47)

        # --- Seção para Cabos Para-Raios (Dinâmica) ---
        Label(self.frame_info, text='Cabos Para-Raios (Raio, Posição 1 X, Posição 1 H, ...)', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.55)

        self.pr_frame = Frame(self.frame_info, bg='#BEBEBE')
        self.pr_frame.place(relx=0.01, rely=0.6, relwidth=0.98, relheight=0.3) # Dedica espaço para os para-raios

        self.add_pr_button = Button(self.frame_info, text='Adicionar Para-Raio', command=self.add_pr_fields)
        self.add_pr_button.place(relx=0.01, rely=0.92, relwidth=0.15, relheight=0.05)

        self.remove_pr_button = Button(self.frame_info, text='Remover Último Para-Raio', command=self.remove_pr_fields)
        self.remove_pr_button.place(relx=0.17, rely=0.92, relwidth=0.2, relheight=0.05)


    def add_pr_fields(self, num_to_add=1):
        for _ in range(num_to_add):
            current_row = len(self.num_pr_entries) # Determina a linha atual
            
            # Raio do para-raio
            Label(self.pr_frame, text=f'R_PR{current_row+1}:', bg='#BEBEBE').grid(row=current_row, column=0, padx=2, pady=2, sticky='w')
            r_entry = Entry(self.pr_frame, width=8)
            r_entry.grid(row=current_row, column=1, padx=2, pady=2, sticky='w')
            self.r_pr_entries.append(r_entry)

            # Posição 1
            Label(self.pr_frame, text=f'Pos1 X/H:', bg='#BEBEBE').grid(row=current_row, column=2, padx=2, pady=2, sticky='w')
            x_pos1_entry = Entry(self.pr_frame, width=8)
            x_pos1_entry.grid(row=current_row, column=3, padx=2, pady=2, sticky='w')
            h_pos1_entry = Entry(self.pr_frame, width=8)
            h_pos1_entry.grid(row=current_row, column=4, padx=2, pady=2, sticky='w')

            # Posição 2
            Label(self.pr_frame, text=f'Pos2 X/H:', bg='#BEBEBE').grid(row=current_row, column=5, padx=2, pady=2, sticky='w')
            x_pos2_entry = Entry(self.pr_frame, width=8)
            x_pos2_entry.grid(row=current_row, column=6, padx=2, pady=2, sticky='w')
            h_pos2_entry = Entry(self.pr_frame, width=8)
            h_pos2_entry.grid(row=current_row, column=7, padx=2, pady=2, sticky='w')

            # Posição 3
            Label(self.pr_frame, text=f'Pos3 X/H:', bg='#BEBEBE').grid(row=current_row, column=8, padx=2, pady=2, sticky='w')
            x_pos3_entry = Entry(self.pr_frame, width=8)
            x_pos3_entry.grid(row=current_row, column=9, padx=2, pady=2, sticky='w')
            h_pos3_entry = Entry(self.pr_frame, width=8)
            h_pos3_entry.grid(row=current_row, column=10, padx=2, pady=2, sticky='w')
            
            # Armazena todas as entries dessa linha
            self.num_pr_entries.append({
                'r': r_entry,
                'x_pos1': x_pos1_entry, 'h_pos1': h_pos1_entry,
                'x_pos2': x_pos2_entry, 'h_pos2': h_pos2_entry,
                'x_pos3': x_pos3_entry, 'h_pos3': h_pos3_entry
            })
        self.pr_frame.update_idletasks() # Atualiza o layout do frame

    def remove_pr_fields(self):
        if not self.num_pr_entries:
            messagebox.showinfo("Aviso", "Não há cabos para-raios para remover.")
            return

        last_pr_set = self.num_pr_entries.pop()
        
        # Destruir os widgets associados a este conjunto de entradas
        last_pr_set['r'].destroy()
        last_pr_set['x_pos1'].destroy()
        last_pr_set['h_pos1'].destroy()
        last_pr_set['x_pos2'].destroy()
        last_pr_set['h_pos2'].destroy()
        last_pr_set['x_pos3'].destroy()
        last_pr_set['h_pos3'].destroy()

        # Também remover o Label do raio
        for widget in self.pr_frame.winfo_children():
            if isinstance(widget, Label) and f'R_PR{len(self.num_pr_entries)+1}:' in widget.cget("text"):
                widget.destroy()
                break
        
        # Remover os labels de Posição 1 X/H, Posição 2 X/H, Posição 3 X/H
        # Isso é um pouco mais complexo pois os labels são genéricos.
        # Precisamos de uma forma de identificar os labels da linha removida.
        # Uma abordagem mais robusta seria associar os labels diretamente no dicionário
        # self.num_pr_entries ou usar um layout que gerencie isso melhor (como Frame aninhados).
        # Por simplicidade, vamos apenas limpar e redesenhar se muitos forem removidos.
        # Uma solução mais simples para agora é apenas remover os entries.

        # Alternativamente, para garantir que os labels sejam removidos corretamente:
        # Percorrer o grid e destruir os widgets da última linha
        for col in range(11): # 0 a 10 colunas no grid
            widget = self.pr_frame.grid_slaves(row=len(self.num_pr_entries), column=col)
            if widget:
                widget[0].destroy() # Destrói o widget se ele existir
        
        # Redesenhar todos os widgets restantes para evitar lacunas (opcional, mas bom para limpeza)
        self._redraw_pr_fields()
        self.pr_frame.update_idletasks()

    def _redraw_pr_fields(self):
        # Limpa o frame de para-raios e redesenha tudo
        for widget in self.pr_frame.winfo_children():
            widget.destroy()
        
        # Zera as listas de entries e as reconstrói com os dados atuais
        self.r_pr_entries = []
        temp_pr_entries = list(self.num_pr_entries) # Faz uma cópia
        self.num_pr_entries = [] # Zera a lista original

        for i, pr_set in enumerate(temp_pr_entries):
            # Recria os widgets e as associações
            Label(self.pr_frame, text=f'R_PR{i+1}:', bg='#BEBEBE').grid(row=i, column=0, padx=2, pady=2, sticky='w')
            r_entry = Entry(self.pr_frame, width=8)
            r_entry.grid(row=i, column=1, padx=2, pady=2, sticky='w')
            r_entry.insert(0, pr_set['r'].get()) # Preserva o valor
            self.r_pr_entries.append(r_entry)

            Label(self.pr_frame, text=f'Pos1 X/H:', bg='#BEBEBE').grid(row=i, column=2, padx=2, pady=2, sticky='w')
            x_pos1_entry = Entry(self.pr_frame, width=8)
            x_pos1_entry.grid(row=i, column=3, padx=2, pady=2, sticky='w')
            x_pos1_entry.insert(0, pr_set['x_pos1'].get())
            h_pos1_entry = Entry(self.pr_frame, width=8)
            h_pos1_entry.grid(row=i, column=4, padx=2, pady=2, sticky='w')
            h_pos1_entry.insert(0, pr_set['h_pos1'].get())

            Label(self.pr_frame, text=f'Pos2 X/H:', bg='#BEBEBE').grid(row=i, column=5, padx=2, pady=2, sticky='w')
            x_pos2_entry = Entry(self.pr_frame, width=8)
            x_pos2_entry.grid(row=i, column=6, padx=2, pady=2, sticky='w')
            x_pos2_entry.insert(0, pr_set['x_pos2'].get())
            h_pos2_entry = Entry(self.pr_frame, width=8)
            h_pos2_entry.grid(row=i, column=7, padx=2, pady=2, sticky='w')
            h_pos2_entry.insert(0, pr_set['h_pos2'].get())

            Label(self.pr_frame, text=f'Pos3 X/H:', bg='#BEBEBE').grid(row=i, column=8, padx=2, pady=2, sticky='w')
            x_pos3_entry = Entry(self.pr_frame, width=8)
            x_pos3_entry.grid(row=i, column=9, padx=2, pady=2, sticky='w')
            x_pos3_entry.insert(0, pr_set['x_pos3'].get())
            h_pos3_entry = Entry(self.pr_frame, width=8)
            h_pos3_entry.grid(row=i, column=10, padx=2, pady=2, sticky='w')
            h_pos3_entry.insert(0, pr_set['h_pos3'].get())

            self.num_pr_entries.append({
                'r': r_entry,
                'x_pos1': x_pos1_entry, 'h_pos1': h_pos1_entry,
                'x_pos2': x_pos2_entry, 'h_pos2': h_pos2_entry,
                'x_pos3': x_pos3_entry, 'h_pos3': h_pos3_entry
            })


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
        # Limpa os campos de entrada das fases e comprimentos
        self.ra_entry.delete(0, END)
        self.rb_entry.delete(0, END)
        self.rc_entry.delete(0, END)
        self.xa_pos1_entry.delete(0, END)
        self.ha_pos1_entry.delete(0, END)
        self.xb_pos2_entry.delete(0, END)
        self.hb_pos2_entry.delete(0, END)
        self.xc_pos3_entry.delete(0, END)
        self.hc_pos3_entry.delete(0, END)
        self.rho_entry.delete(0, END)
        self.l1_entry.delete(0, END)
        self.l2_entry.delete(0, END)
        self.l3_entry.delete(0, END)
        
        # Limpa e remove todos os campos de para-raios
        while self.num_pr_entries:
            self.remove_pr_fields()
        self.add_pr_fields(1) # Adiciona um campo de para-raio vazio novamente

        # Limpa a Treeview e a preenche com NaN
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=float))

    def _get_input_values(self):
        try:
            # Raios dos condutores de fase
            ra = float(self.ra_entry.get())
            rb = float(self.rb_entry.get())
            rc = float(self.rc_entry.get())

            # Coordenadas das Posições Físicas das fases
            xa_pos1 = float(self.xa_pos1_entry.get())
            ha_pos1 = float(self.ha_pos1_entry.get())
            xb_pos2 = float(self.xb_pos2_entry.get())
            hb_pos2 = float(self.hb_pos2_entry.get())
            xc_pos3 = float(self.xc_pos3_entry.get())
            hc_pos3 = float(self.hc_pos3_entry.get())

            # Resistividade do solo
            rho = float(self.rho_entry.get())

            # Comprimentos das seções
            l1 = float(self.l1_entry.get())
            l2 = float(self.l2_entry.get())
            l3 = float(self.l3_entry.get())

            # Coleta os dados dos cabos para-raios
            r_pr_list = []
            x_pr_pos1_list = []
            h_pr_pos1_list = []
            x_pr_pos2_list = []
            h_pr_pos2_list = []
            x_pr_pos3_list = []
            h_pr_pos3_list = []

            for pr_set in self.num_pr_entries:
                r_pr_list.append(float(pr_set['r'].get()))
                x_pr_pos1_list.append(float(pr_set['x_pos1'].get()))
                h_pr_pos1_list.append(float(pr_set['h_pos1'].get()))
                x_pr_pos2_list.append(float(pr_set['x_pos2'].get()))
                h_pr_pos2_list.append(float(pr_set['h_pos2'].get()))
                x_pr_pos3_list.append(float(pr_set['x_pos3'].get()))
                h_pr_pos3_list.append(float(pr_set['h_pos3'].get()))

            return {
                'ra': ra, 'rb': rb, 'rc': rc,
                'xa_pos1': xa_pos1, 'ha_pos1': ha_pos1,
                'xb_pos2': xb_pos2, 'hb_pos2': hb_pos2,
                'xc_pos3': xc_pos3, 'hc_pos3': hc_pos3,
                'r_pr': r_pr_list,
                'x_pr_pos1': x_pr_pos1_list, 'h_pr_pos1': h_pr_pos1_list,
                'x_pr_pos2': x_pr_pos2_list, 'h_pr_pos2': h_pr_pos2_list,
                'x_pr_pos3': x_pr_pos3_list, 'h_pr_pos3': h_pr_pos3_list,
                'rho': rho,
                'l1': l1, 'l2': l2, 'l3': l3
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos em todos os campos. Detalhes: {e}")
            return None
        except Exception as e:
            messagebox.showerror("Erro", f"Um erro inesperado ocorreu ao obter os valores: {e}")
            return None

    def _calculate_capacitance_ground_wire(self):
        params = self._get_input_values()
        if params is None:
            return

        try:
            # Chama a função de cálculo da capacitância com cabo para-raio
            # Certifique-se de que 'metodo_para_raio_tran' esteja acessível aqui (importada ou definida globalmente)
            C_matrix_total = metodo_para_raio_tran(
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa_pos1=params['xa_pos1'], ha_pos1=params['ha_pos1'],
                xb_pos2=params['xb_pos2'], hb_pos2=params['hb_pos2'],
                xc_pos3=params['xc_pos3'], hc_pos3=params['hc_pos3'],
                r_pr=params['r_pr'],
                x_pr_pos1=params['x_pr_pos1'], h_pr_pos1=params['h_pr_pos1'],
                x_pr_pos2=params['x_pr_pos2'], h_pr_pos2=params['h_pr_pos2'],
                x_pr_pos3=params['x_pr_pos3'], h_pr_pos3=params['h_pr_pos3'],
                rho=params['rho'],
                l1=params['l1'], l2=params['l2'], l3=params['l3']
            )

            # Convertendo para nF (nanofarads) para melhor visualização
            C_matrix_nF = C_matrix_total * 1e9 # Farads -> nanofarads

            self._insert_data_to_treeview(C_matrix_nF)
            messagebox.showinfo("Cálculo Concluído", "A matriz de capacitância (com para-raios) foi calculada e exibida na tabela.")
        except NameError:
            messagebox.showerror("Erro de Função", "A função 'metodo_para_raio_tran' não foi encontrada. Certifique-se de que está definida ou importada.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, C_matrix):
        for i in self.lista_CAP.get_children():
            self.lista_CAP.delete(i)

        float_format = "{:.6e}" # Notação científica para valores pequenos
        row_labels = ["A", "B", "C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(C_matrix.shape[1]):
                value = C_matrix[i, j]
                if np.isnan(value):
                    formatted_value = "" # Exibe vazio se for NaN
                else:
                    formatted_value = float_format.format(value)
                row_values.append(formatted_value)
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values))

# --- CLASSE DA JANELA PARA CÁLCULO DE CAPACITÂNCIA COM FEIXE CONDUTOR ---
class BundledCapacitanceCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window)
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()

        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=float))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Capacitância - Feixe Condutor")
        self.calc_window.geometry("800x600") # Tamanho ajustado para os campos
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify() # Reexibe a janela principal

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.55)

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.6, relwidth=0.96, relheight=0.37)

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                   font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.15, relheight=0.08)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                   font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.80, rely=.01, relwidth=0.15, relheight=0.08)

        self.botao_calc = Button(self.frame_info, text='Calcular', bd=4,
                                 font=('Arial',10), command=self._calculate_bundled_capacitance)
        self.botao_calc.place(relx=.8, rely=.88, relwidth=0.15, relheight=0.08)

        # --- Labels e Entradas de Raios dos Subcondutores ---
        Label(self.frame_info, text='Raios dos Subcondutores (m)', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.12)

        Label(self.frame_info, text='Ra_sub:', bg='#BEBEBE').place(relx=0.01, rely=.18)
        self.ra_sub_entry = Entry(self.frame_info, width=10)
        self.ra_sub_entry.place(relx=.08, rely=.18)

        Label(self.frame_info, text='Rb_sub:', bg='#BEBEBE').place(relx=0.01, rely=.23)
        self.rb_sub_entry = Entry(self.frame_info, width=10)
        self.rb_sub_entry.place(relx=.08, rely=.23)

        Label(self.frame_info, text='Rc_sub:', bg='#BEBEBE').place(relx=0.01, rely=.28)
        self.rc_sub_entry = Entry(self.frame_info, width=10)
        self.rc_sub_entry.place(relx=.08, rely=.28)

        # --- Labels e Entradas de Número de Subcondutores ---
        Label(self.frame_info, text='Nº Subcondutores (1,2,3,4)', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.25, rely=.12)

        Label(self.frame_info, text='Na:', bg='#BEBEBE').place(relx=.25, rely=.18)
        self.na_entry = Entry(self.frame_info, width=5)
        self.na_entry.place(relx=.30, rely=.18)

        Label(self.frame_info, text='Nb:', bg='#BEBEBE').place(relx=.25, rely=.23)
        self.nb_entry = Entry(self.frame_info, width=5)
        self.nb_entry.place(relx=.30, rely=.23)

        Label(self.frame_info, text='Nc:', bg='#BEBEBE').place(relx=.25, rely=.28)
        self.nc_entry = Entry(self.frame_info, width=5)
        self.nc_entry.place(relx=.30, rely=.28)

        # --- Labels e Entradas de Espaçamento entre Subcondutores ---
        Label(self.frame_info, text='Espaçamento Subcondutores (m)', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.45, rely=.12)

        Label(self.frame_info, text='Sa:', bg='#BEBEBE').place(relx=.45, rely=.18)
        self.sa_entry = Entry(self.frame_info, width=10)
        self.sa_entry.place(relx=.50, rely=.18)

        Label(self.frame_info, text='Sb:', bg='#BEBEBE').place(relx=.45, rely=.23)
        self.sb_entry = Entry(self.frame_info, width=10)
        self.sb_entry.place(relx=.50, rely=.23)

        Label(self.frame_info, text='Sc:', bg='#BEBEBE').place(relx=.45, rely=.28)
        self.sc_entry = Entry(self.frame_info, width=10)
        self.sc_entry.place(relx=.50, rely=.28)

        # --- Labels e Entradas de Coordenadas X e H das Fases ---
        Label(self.frame_info, text='Coordenadas Fases (X, H) [m]', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.7, rely=.12)

        Label(self.frame_info, text='Fase A (X, H):', bg='#BEBEBE').place(relx=.7, rely=.18)
        self.xa_entry = Entry(self.frame_info, width=8)
        self.xa_entry.place(relx=.82, rely=.18)
        self.ha_entry = Entry(self.frame_info, width=8)
        self.ha_entry.place(relx=.88, rely=.18)

        Label(self.frame_info, text='Fase B (X, H):', bg='#BEBEBE').place(relx=.7, rely=.23)
        self.xb_entry = Entry(self.frame_info, width=8)
        self.xb_entry.place(relx=.82, rely=.23)
        self.hb_entry = Entry(self.frame_info, width=8)
        self.hb_entry.place(relx=.88, rely=.23)

        Label(self.frame_info, text='Fase C (X, H):', bg='#BEBEBE').place(relx=.7, rely=.28)
        self.xc_entry = Entry(self.frame_info, width=8)
        self.xc_entry.place(relx=.82, rely=.28)
        self.hc_entry = Entry(self.frame_info, width=8)
        self.hc_entry.place(relx=.88, rely=.28)

        # --- Entrada de Resistividade do Solo ---
        Label(self.frame_info, text='Resistividade Solo (rho) [Ohm.m]:', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.4)
        self.rho_entry = Entry(self.frame_info, width=10)
        self.rho_entry.place(relx=.25, rely=.4)

        # --- Entrada de Comprimento Total da Linha ---
        Label(self.frame_info, text='Comprimento Total da Linha (m):', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.5)
        self.comprimento_total_entry = Entry(self.frame_info, width=10)
        self.comprimento_total_entry.place(relx=.25, rely=.5)

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
        # Limpa todos os campos de entrada
        self.ra_sub_entry.delete(0, END)
        self.rb_sub_entry.delete(0, END)
        self.rc_sub_entry.delete(0, END)
        self.na_entry.delete(0, END)
        self.nb_entry.delete(0, END)
        self.nc_entry.delete(0, END)
        self.sa_entry.delete(0, END)
        self.sb_entry.delete(0, END)
        self.sc_entry.delete(0, END)
        self.xa_entry.delete(0, END)
        self.ha_entry.delete(0, END)
        self.xb_entry.delete(0, END)
        self.hb_entry.delete(0, END)
        self.xc_entry.delete(0, END)
        self.hc_entry.delete(0, END)
        self.rho_entry.delete(0, END)
        self.comprimento_total_entry.delete(0, END)

        # Limpa a Treeview e a preenche com NaN
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=float))

    def _get_input_values(self):
        try:
            # Raios dos subcondutores
            ra_sub = float(self.ra_sub_entry.get())
            rb_sub = float(self.rb_sub_entry.get())
            rc_sub = float(self.rc_sub_entry.get())

            # Número de subcondutores
            na = int(self.na_entry.get())
            nb = int(self.nb_entry.get())
            nc = int(self.nc_entry.get())

            # Espaçamento entre subcondutores
            sa = float(self.sa_entry.get())
            sb = float(self.sb_entry.get())
            sc = float(self.sc_entry.get())

            # Coordenadas X e H das Fases
            xa = float(self.xa_entry.get())
            ha = float(self.ha_entry.get())
            xb = float(self.xb_entry.get())
            hb = float(self.hb_entry.get())
            xc = float(self.xc_entry.get())
            hc = float(self.hc_entry.get())

            # Resistividade do solo
            rho = float(self.rho_entry.get())

            # Comprimento total da linha
            comprimento_total = float(self.comprimento_total_entry.get())

            return {
                'ra_sub': ra_sub, 'rb_sub': rb_sub, 'rc_sub': rc_sub,
                'na': na, 'nb': nb, 'nc': nc,
                'sa': sa, 'sb': sb, 'sc': sc,
                'xa': xa, 'ha': ha, 'xb': xb, 'hb': hb, 'xc': xc, 'hc': hc,
                'rho': rho, 'comprimento_total': comprimento_total
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Verifique todos os campos. Detalhes: {e}")
            return None
        except Exception as e:
            messagebox.showerror("Erro", f"Um erro inesperado ocorreu ao obter os valores: {e}")
            return None

    def _calculate_bundled_capacitance(self):
        params = self._get_input_values()
        if params is None:
            return

        try:
            # Chama a função de cálculo da capacitância com feixe condutor
            # Certifique-se de que 'metodo_feixe_condutor_tran' esteja acessível aqui (importada ou definida globalmente)
            C_matrix = metodo_feixe_condutor_tran(
                ra_sub=params['ra_sub'], rb_sub=params['rb_sub'], rc_sub=params['rc_sub'],
                na=params['na'], nb=params['nb'], nc=params['nc'],
                sa=params['sa'], sb=params['sb'], sc=params['sc'],
                xa=params['xa'], ha=params['ha'], xb=params['xb'], hb=params['hb'], xc=params['xc'], hc=params['hc'],
                rho=params['rho'], comprimento_total=params['comprimento_total']
            )

            # Convertendo para nF (nanofarads) para melhor visualização
            C_matrix_nF = C_matrix * 1e9 # Farads -> nanofarads

            self._insert_data_to_treeview(C_matrix_nF)
            messagebox.showinfo("Cálculo Concluído", "A matriz de capacitância (feixe condutor) foi calculada e exibida na tabela.")
        except NameError:
            messagebox.showerror("Erro de Função", "A função 'metodo_feixe_condutor_tran' não foi encontrada. Certifique-se de que está definida ou importada.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, C_matrix):
        for i in self.lista_CAP.get_children():
            self.lista_CAP.delete(i)

        float_format = "{:.6e}" # Formato para exibir números reais em notação científica para valores pequenos
        row_labels = ["A", "B", "C"]

        for i, row_label in enumerate(row_labels):
            row_values = []
            for j in range(C_matrix.shape[1]):
                value = C_matrix[i, j]
                if np.isnan(value):
                    formatted_value = "" # Exibe vazio se for NaN
                else:
                    formatted_value = float_format.format(value)
                row_values.append(formatted_value)
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values))

# --- CLASSE DA JANELA PARA CÁLCULO DE CAPACITÂNCIA DE SEQUÊNCIA ---
class SequenceCapacitanceCalculator:
    def __init__(self, master_window):
        self.master_window = master_window
        self.calc_window = Toplevel(master_window)
        self._setup_window()
        self._setup_frames()
        self._setup_widgets()
        self._setup_treeview()

        # Preenche a Treeview com campos vazios ao iniciar a janela
        self._insert_data_to_treeview(np.full((3, 3), np.nan + 0j, dtype=complex))

    def _setup_window(self):
        self.calc_window.title("Cálculo de Capacitância de Sequência")
        self.calc_window.geometry("750x550") # Tamanho ajustado
        self.calc_window.configure(background='#2F4F4F')
        self.calc_window.resizable(False, False)
        self.calc_window.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.calc_window.destroy()
        self.master_window.deiconify() # Reexibe a janela principal

    def _setup_frames(self):
        self.frame_info = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_info.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.45) # Ajusta altura

        self.frame_result = Frame(self.calc_window, bd=4, bg='#BEBEBE', highlightthickness=3)
        self.frame_result.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.48) # Ajusta posição e altura

    def _setup_widgets(self):
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar', bd=4,
                                   font=('Arial',10), command=self._on_closing)
        self.botao_return.place(relx=.01, rely=.01, relwidth=0.15, relheight=0.1)

        self.botao_limpar = Button(self.frame_info, text='Limpar', bd=4,
                                   font=('Arial',10), command=self._clear_inputs)
        self.botao_limpar.place(relx=.80, rely=.01, relwidth=0.15, relheight=0.1)

        self.botao_calc = Button(self.frame_info, text='Calcular', bd=4,
                                 font=('Arial',10), command=self._calculate_sequence_capacitance)
        self.botao_calc.place(relx=.8, rely=.85, relwidth=0.15, relheight=0.1)

        # --- Labels e Entradas de Raios dos Condutores ---
        Label(self.frame_info, text='Raios dos Condutores (m)', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.15)

        Label(self.frame_info, text='Ra:', bg='#BEBEBE').place(relx=0.01, rely=.25)
        self.ra_entry = Entry(self.frame_info, width=10)
        self.ra_entry.place(relx=.08, rely=.25)

        Label(self.frame_info, text='Rb:', bg='#BEBEBE').place(relx=0.01, rely=.35)
        self.rb_entry = Entry(self.frame_info, width=10)
        self.rb_entry.place(relx=.08, rely=.35)

        Label(self.frame_info, text='Rc:', bg='#BEBEBE').place(relx=0.01, rely=.45)
        self.rc_entry = Entry(self.frame_info, width=10)
        self.rc_entry.place(relx=.08, rely=.45)

        # --- Labels e Entradas de Coordenadas X dos Condutores ---
        Label(self.frame_info, text='Coordenadas Horizontais (X) [m]', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.3, rely=.15)

        Label(self.frame_info, text='Xa:', bg='#BEBEBE').place(relx=.3, rely=.25)
        self.xa_entry = Entry(self.frame_info, width=10)
        self.xa_entry.place(relx=.37, rely=.25)

        Label(self.frame_info, text='Xb:', bg='#BEBEBE').place(relx=.3, rely=.35)
        self.xb_entry = Entry(self.frame_info, width=10)
        self.xb_entry.place(relx=.37, rely=.35)

        Label(self.frame_info, text='Xc:', bg='#BEBEBE').place(relx=.3, rely=.45)
        self.xc_entry = Entry(self.frame_info, width=10)
        self.xc_entry.place(relx=.37, rely=.45)

        # --- Labels e Entradas de Alturas dos Condutores ---
        Label(self.frame_info, text='Alturas (H) acima do solo [m]', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.6, rely=.15)

        Label(self.frame_info, text='Ha:', bg='#BEBEBE').place(relx=.6, rely=.25)
        self.ha_entry = Entry(self.frame_info, width=10)
        self.ha_entry.place(relx=.67, rely=.25)

        Label(self.frame_info, text='Hb:', bg='#BEBEBE').place(relx=.6, rely=.35)
        self.hb_entry = Entry(self.frame_info, width=10)
        self.hb_entry.place(relx=.67, rely=.35)

        Label(self.frame_info, text='Hc:', bg='#BEBEBE').place(relx=.6, rely=.45)
        self.hc_entry = Entry(self.frame_info, width=10)
        self.hc_entry.place(relx=.67, rely=.45)

        # --- Entrada de Resistividade do Solo ---
        Label(self.frame_info, text='Resistividade Solo (rho) [Ohm.m]:', bg='#BEBEBE', font=('Arial', 10, 'bold')).place(relx=0.01, rely=.6)
        self.rho_entry = Entry(self.frame_info, width=10)
        self.rho_entry.place(relx=.25, rely=.6)

    def _setup_treeview(self):
        # A Treeview para Capacitância de Sequência precisa de 3 colunas (0, 1, 2)
        # e deve exibir partes real e imaginária.
        self.lista_CAP_SEQ = ttk.Treeview(self.frame_result, height=3,
                                          columns=('col0','col1','col2'))
        self.lista_CAP_SEQ.heading("#0", text="Componente")
        self.lista_CAP_SEQ.heading("col0", text="Seq. 0")
        self.lista_CAP_SEQ.heading("col1", text="Seq. 1")
        self.lista_CAP_SEQ.heading("col2", text="Seq. 2")

        self.lista_CAP_SEQ.column("#0", width=120, anchor=CENTER)
        self.lista_CAP_SEQ.column("col0", width=180, anchor=CENTER)
        self.lista_CAP_SEQ.column("col1", width=180, anchor=CENTER)
        self.lista_CAP_SEQ.column("col2", width=180, anchor=CENTER)

        self.lista_CAP_SEQ.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')
        self.lista_CAP_SEQ.configure(yscrollcommand=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)

    def _clear_inputs(self):
        # Limpa todos os campos de entrada
        self.ra_entry.delete(0, END)
        self.rb_entry.delete(0, END)
        self.rc_entry.delete(0, END)
        self.xa_entry.delete(0, END)
        self.xb_entry.delete(0, END)
        self.xc_entry.delete(0, END)
        self.ha_entry.delete(0, END)
        self.hb_entry.delete(0, END)
        self.hc_entry.delete(0, END)
        self.rho_entry.delete(0, END)

        # Limpa a Treeview e a preenche com NaN
        self._insert_data_to_treeview(np.full((3, 3), np.nan + 0j, dtype=complex))

    def _get_input_values(self):
        try:
            # Raios dos condutores
            ra = float(self.ra_entry.get())
            rb = float(self.rb_entry.get())
            rc = float(self.rc_entry.get())

            # Coordenadas X
            xa = float(self.xa_entry.get())
            xb = float(self.xb_entry.get())
            xc = float(self.xc_entry.get())

            # Alturas H
            ha = float(self.ha_entry.get())
            hb = float(self.hb_entry.get())
            hc = float(self.hc_entry.get())

            # Resistividade do solo
            rho = float(self.rho_entry.get())

            return {
                'ra': ra, 'rb': rb, 'rc': rc,
                'xa': xa, 'xb': xb, 'xc': xc,
                'ha': ha, 'hb': hb, 'hc': hc,
                'rho': rho
            }
        except ValueError as e:
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Verifique todos os campos. Detalhes: {e}")
            return None
        except Exception as e:
            messagebox.showerror("Erro", f"Um erro inesperado ocorreu ao obter os valores: {e}")
            return None

    def _calculate_sequence_capacitance(self):
        params = self._get_input_values()
        if params is None:
            return

        try:
            # Chama a função de cálculo da capacitância de sequência
            # Certifique-se de que 'metodo_capacitancia_sequencia_tran' esteja acessível aqui
            C_seq_matrix = metodo_capacitancia_sequencia_tran(
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa=params['xa'], xb=params['xb'], xc=params['xc'],
                ha=params['ha'], hb=params['hb'], hc=params['hc'],
                rho=params['rho']
            )

            # Para exibição, podemos converter para pF/m (picofarads por metro) ou nF/m
            # C_seq_matrix_pF_per_m = C_seq_matrix * 1e12 # Farads/m -> pF/m
            # Vamos exibir em nF/m para consistência com outras janelas
            C_seq_matrix_nF_per_m = C_seq_matrix * 1e9 # Farads/m -> nF/m

            self._insert_data_to_treeview(C_seq_matrix_nF_per_m)
            messagebox.showinfo("Cálculo Concluído", "A matriz de capacitância de sequência foi calculada e exibida na tabela (nF/m).")
        except NameError:
            messagebox.showerror("Erro de Função", "A função 'metodo_capacitancia_sequencia_tran' não foi encontrada. Certifique-se de que está definida ou importada.")
        except ValueError as e:
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def _insert_data_to_treeview(self, C_seq_matrix):
        for i in self.lista_CAP_SEQ.get_children():
            self.lista_CAP_SEQ.delete(i)

        # Formato para exibir números complexos (parte real + parte imaginária)
        # Usando '{:.4e}' para notação científica com 4 casas decimais para cada parte.
        complex_format = "{:.4e} + j{:.4e}"
        
        # Inserir a parte real
        real_values = []
        for j in range(C_seq_matrix.shape[1]):
            value = C_seq_matrix[0, j].real # Capacitância de Sequência Zero
            if np.isnan(value):
                real_values.append("")
            else:
                real_values.append(f"{value:.4e}")
        self.lista_CAP_SEQ.insert("", END, text="Real (0)", values=tuple(real_values))

        real_values = []
        for j in range(C_seq_matrix.shape[1]):
            value = C_seq_matrix[1, j].real # Capacitância de Sequência Positiva
            if np.isnan(value):
                real_values.append("")
            else:
                real_values.append(f"{value:.4e}")
        self.lista_CAP_SEQ.insert("", END, text="Real (1)", values=tuple(real_values))

        real_values = []
        for j in range(C_seq_matrix.shape[1]):
            value = C_seq_matrix[2, j].real # Capacitância de Sequência Negativa
            if np.isnan(value):
                real_values.append("")
            else:
                real_values.append(f"{value:.4e}")
        self.lista_CAP_SEQ.insert("", END, text="Real (2)", values=tuple(real_values))

        # Inserir a parte imaginária
        imag_values = []
        for j in range(C_seq_matrix.shape[1]):
            value = C_seq_matrix[0, j].imag # Capacitância de Sequência Zero Imaginária
            if np.isnan(value):
                imag_values.append("")
            else:
                imag_values.append(f"{value:.4e}")
        self.lista_CAP_SEQ.insert("", END, text="Imaginário (0)", values=tuple(imag_values))

        imag_values = []
        for j in range(C_seq_matrix.shape[1]):
            value = C_seq_matrix[1, j].imag # Capacitância de Sequência Positiva Imaginária
            if np.isnan(value):
                imag_values.append("")
            else:
                imag_values.append(f"{value:.4e}")
        self.lista_CAP_SEQ.insert("", END, text="Imaginário (1)", values=tuple(imag_values))
        
        imag_values = []
        for j in range(C_seq_matrix.shape[1]):
            value = C_seq_matrix[2, j].imag # Capacitância de Sequência Negativa Imaginária
            if np.isnan(value):
                imag_values.append("")
            else:
                imag_values.append(f"{value:.4e}")
        self.lista_CAP_SEQ.insert("", END, text="Imaginário (2)", values=tuple(imag_values))

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
        self.metodo_options = ("Longitudinal Imagem", 
                               "Longitudinal Carson (Correção)",
                               "Longitudinal Carson com Para-Raio",
                               "Longitudinal Carson transposição", 
                               "Longitudinal Carson feixe de condutor",
                               "Longitudinal Síntese de Componentes Simétricas", 
                               "Longitudinal Análise de Componentes Simétricas",
                               "Transversal imagem",
                               "Transversal transposição",
                               "Transversal para-raio",
                               "Transversal feixe de condutor",
                               "Transversal capacitância de sequências")
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
        elif selected_method == "Longitudinal Carson (Correção)":
            self.root.withdraw() # Esconde a janela principal
            CarsonLongitudinalCalculator(self.root) # Instancia a nova janela de Carson com correção
        elif selected_method == "Longitudinal Carson com Para-Raio": # Nova condição para o método de Carson
            self.root.withdraw() # Esconde a janela principal
            CarsonGroundWireCalculator(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Longitudinal Carson transposição": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    CarsonTransposedCalculator(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Longitudinal Carson feixe de condutor": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    BundleConductorRMGCalculator(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Longitudinal Síntese de Componentes Simétricas": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    SymmetricalComponentSynthesizer(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Longitudinal Análise de Componentes Simétricas": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    SymmetricalComponentAnalyzer(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Transversal imagem": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    CapacitanceImageCalculator(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Transversal transposição": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    TransposedCapacitanceCalculator(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Transversal para-raio": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    CapacitanceGroundWireCalculator(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Transversal feixe de condutor": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    BundledCapacitanceCalculator(self.root) # Instancia a nova janela de Carson
        #elif selected_method == "Transversal capacitância de sequências": # Nova condição para o método de Carson
        #    self.root.withdraw() # Esconde a janela principal
        #    SequenceCapacitanceCalculator(self.root) # Instancia a nova janela de Carson
        else:
            messagebox.showinfo("Método Não Implementado", f"O método '{selected_method}' ainda não foi implementado. Por favor, selecione 'Longitudinal Imagem' ou 'Longitudinal Carson (Correção)'.")

# --- Inicialização ---
if __name__ == "__main__":
    root = Tk()
    app = AppMain(root)