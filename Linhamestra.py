from tkinter import *
from tkinter import ttk
from tkinter import messagebox

import numpy as np
import math

# --- Backend: Lógica de Negócio do Cálculo (Função Separada) ---
def metodo_imagem_long(ra, rb, rc, xa, ha, xb, hb, xc, hc, R=None, Rmg_val=None):
    """
    Calcula a matriz de impedância série por unidade de comprimento de uma linha de transmissão trifásica,
    utilizando o Método das Imagens para considerar o efeito do solo.
    """

    mi_0 = 4 * math.pi * (10**(-7))                                     # Permeabilidade magnética do vácuo
    f = 60                                                              # Frequência do sistema (Hertz)
    w = 2 * math.pi * f                                                 # Frequência angular

    Rmg = None                                                          # Inicializa o Raio Médio Geométrico (RMG)

    if Rmg_val is not None:                                             # Prioriza RMG_val se fornecido
        Rmg = Rmg_val
    elif R is not None:                                                 # Calcula RMG a partir de R se Rmg_val não estiver presente
        Rmg = R * math.exp(-1/4)
    
    if Rmg is None:                                                     # Erro se nenhum raio válido for dado
        raise ValueError("ERRO! É necessário fornecer o valor do raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:                                                        # Erro se RMG for não positivo
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")
    
    # --- Cálculo das Distâncias Geométricas ---
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2))                      # Distância entre condutores 'a' e 'b'
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2))                      # Distância entre condutores 'a' e 'c'
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2))                      # Distância entre condutores 'b' e 'c'
    
    dab_l = np.sqrt(((xa - xb)**2) + ((ha + hb)**2))                    # Distância entre 'a' e imagem de 'b'
    dac_l = np.sqrt(((xa - xc)**2) + ((ha + hc)**2))                    # Distância entre 'a' e imagem de 'c'
    dbc_l = np.sqrt(((xb - xc)**2) + ((hb + hc)**2))                    # Distância entre 'b' e imagem de 'c'
    
    # --- Cálculo das Impedâncias Série (por unidade de comprimento) ---
    Zaa = ra + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * ha) / Rmg)) # Impedância própria de 'a'
    Zbb = rb + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * hb) / Rmg)) # Impedância própria de 'b'
    Zcc = rc + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * hc) / Rmg)) # Impedância própria de 'c'
    
    Zab = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dab_l / dab))   # Impedância mútua 'ab'
    Zac = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dac_l / dac))   # Impedância mútua 'ac'
    Zbc = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dbc_l / dbc))   # Impedância mútua 'bc'
    
    Zba = Zab                                                           # Simetria: Zba = Zab
    Zca = Zac                                                           # Simetria: Zca = Zac
    Zcb = Zbc                                                           # Simetria: Zcb = Zbc
    
    # --- Montagem da Matriz de Impedância da Linha ---
    Z = np.array([                                                      # Cria a matriz de impedância (NumPy array)
        [Zaa, Zab, Zac],
        [Zba, Zbb, Zbc],
        [Zca, Zcb, Zcc]
    ])

    return Z                                                            # Retorna a matriz de impedância

# --- Classe para a Tela de Cálculo do Método das Imagens Longitudinais ---
class LongitudinalImageCalculator:
    def __init__(self, master_window):
        self.master_window = master_window                              # Armazena a janela principal para retornar
        self.calc_window = Toplevel(master_window)                      # Cria uma nova janela Toplevel
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
        Label(self.frame_info, text='Resistências', bg='#BEBEBE').place(relx=0.01, rely=.2)

        Label(self.frame_info, text='Ra (Ohm/unidade)', bg='#BEBEBE').place(relx=0.01, rely=.32)
        self.ra_entry = Entry(self.frame_info)
        self.ra_entry.place(relx=.2, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='Rb (Ohm/unidade)', bg='#BEBEBE').place(relx=0.01, rely=.44)
        self.rb_entry = Entry(self.frame_info)
        self.rb_entry.place(relx=.2, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='Rc (Ohm/unidade)', bg='#BEBEBE').place(relx=0.01, rely=.56)
        self.rc_entry = Entry(self.frame_info)
        self.rc_entry.place(relx=.2, rely=.56, relwidth=0.08)

        # --- Labels e Entradas de Raio e RMG ---
        Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE').place(relx=0.01, rely=.68)
        self.r_entry = Entry(self.frame_info)
        self.r_entry.place(relx=.2, rely=.68, relwidth=0.08)

        Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE').place(relx=0.01, rely=.80)
        self.rmg_entry = Entry(self.frame_info)
        self.rmg_entry.place(relx=.2, rely=.80, relwidth=0.08)

        # --- Labels e Entradas de Coordenadas ---
        Label(self.frame_info, text='Coordenadas dos Cabos', bg='#BEBEBE').place(relx=.4, rely=.2)

        Label(self.frame_info, text='X_a (m)', bg='#BEBEBE').place(relx=.4, rely=.32)
        self.xa_entry = Entry(self.frame_info)
        self.xa_entry.place(relx=.48, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='X_b (m)', bg='#BEBEBE').place(relx=.4, rely=.44)
        self.xb_entry = Entry(self.frame_info)
        self.xb_entry.place(relx=.48, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='X_c (m)', bg='#BEBEBE').place(relx=.4, rely=.56)
        self.xc_entry = Entry(self.frame_info)
        self.xc_entry.place(relx=.48, rely=.56, relwidth=0.08)

        Label(self.frame_info, text='H_a (m)', bg='#BEBEBE').place(relx=.6, rely=.32)
        self.ha_entry = Entry(self.frame_info)
        self.ha_entry.place(relx=.68, rely=.32, relwidth=0.08)

        Label(self.frame_info, text='H_b (m)', bg='#BEBEBE').place(relx=.6, rely=.44)
        self.hb_entry = Entry(self.frame_info)
        self.hb_entry.place(relx=.68, rely=.44, relwidth=0.08)

        Label(self.frame_info, text='H_c (m)', bg='#BEBEBE').place(relx=.6, rely=.56)
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
        # Limpa todos os campos de entrada
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
        
        # Limpa os dados existentes na Treeview e reinicia com vazios
        self._insert_data_to_treeview(np.full((3, 3), np.nan, dtype=complex))

    def _get_input_values(self):
        try:
            # Obtém e converte as resistências. Usa 0.0 se o campo estiver vazio.
            ra = float(self.ra_entry.get()) if self.ra_entry.get() else 0.0
            rb = float(self.rb_entry.get()) if self.rb_entry.get() else 0.0
            rc = float(self.rc_entry.get()) if self.rc_entry.get() else 0.0

            # Tenta obter R ou RMG. Prioriza RMG_val se ambos forem fornecidos.
            R_val = float(self.r_entry.get()) if self.r_entry.get() else None
            Rmg_val = float(self.rmg_entry.get()) if self.rmg_entry.get() else None
            
            # Obtém e converte as coordenadas X. Usa 0.0 se o campo estiver vazio.
            xa = float(self.xa_entry.get()) if self.xa_entry.get() else 0.0
            xb = float(self.xb_entry.get()) if self.xb_entry.get() else 0.0
            xc = float(self.xc_entry.get()) if self.xc_entry.get() else 0.0

            # Obtém e converte as alturas H. Usa 0.0 se o campo estiver vazio.
            ha = float(self.ha_entry.get()) if self.ha_entry.get() else 0.0
            hb = float(self.hb_entry.get()) if self.hb_entry.get() else 0.0
            hc = float(self.hc_entry.get()) if self.hc_entry.get() else 0.0

            # Valida que as alturas são positivas para evitar problemas com logaritmos
            if ha <= 0 or hb <= 0 or hc <= 0:
                raise ValueError("As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.")

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
            Z_matrix = metodo_imagem_long(
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
        
        # Formato para exibir números complexos com 6 casas decimais
        complex_format = "({:.6f} + j{:.6f})"

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

# --- Classe Principal da Aplicação (Tela de Seleção de Métodos) ---
class AppMain:
    def __init__(self, master):
        self.root = master                                              # Referência à janela principal
        self._setup_main_window()                                       # Configura a janela principal
        self._setup_main_frames()                                       # Cria frames na janela principal
        self._setup_main_widgets()                                      # Cria widgets na janela principal
        # O self.root.withdraw() e self.root.deiconify() foram movidos para dentro
        # da inicialização para garantir que a janela só apareça depois de totalmente configurada.
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
        self.metodo_options = ("Longitudinal Imagem", "Longitudinal Carson transposição",
                               "Longitudinal Carson para-raio", "Longitudinal Carson feixe de condutor",
                               "Longitudinal Carson impedância de sequência", "Transversal imagem",
                               "Transversal transposição", "Transversal para-raio",
                               "Transversal feixe de condutor", "Transversal capacitância de sequências")
        self.metodo_select.set(self.metodo_options[0]) # Define o valor inicial

        self.popupMenu = OptionMenu(self.frame_principal, self.metodo_select, *self.metodo_options)
        self.popupMenu.place(relx=.4, rely=.3, relwidth=0.5, relheight=0.08)
        
        # O trace_add não é estritamente necessário aqui, já que a ação é no botão OK.
        # Mas se você quiser um feedback imediato da seleção, pode manter.
        # self.metodo_select.trace_add("write", lambda *args: print(f"Método selecionado: {self.metodo_select.get()}"))

    def _select_method(self):
        selected_method = self.metodo_select.get()
        if selected_method == "":
            messagebox.showinfo("Erro de seleção de método!!!", "Selecione um método válido, \nna caixa de seleção de métodos")
        elif selected_method == "Longitudinal Imagem":
            self.root.withdraw() # Esconde a janela principal
            LongitudinalImageCalculator(self.root) # Passa a referência da janela principal
        else:
            messagebox.showinfo("Método Não Implementado", f"O método '{selected_method}' ainda não foi implementado. Por favor, selecione 'Longitudinal Imagem'.")

# --- Inicialização ---
if __name__ == "__main__":
    root = Tk() # AQUI ESTÁ A CORREÇÃO: Cria a instância de Tk() antes de usá-la
    app = AppMain(root)