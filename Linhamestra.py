from tkinter import * # Importa todas as classes e funções do módulo Tkinter (ex: Tk, Frame, Button, Label, StringVar)
from tkinter import ttk # Importa o módulo ttk do Tkinter, que oferece widgets mais modernos e estilizados (ex: ttk.Treeview)
from tkinter import messagebox # Importa o módulo messagebox para exibir caixas de diálogo e alertas ao usuário

import numpy as np # Importa a biblioteca NumPy para operações com arrays e matrizes, especialmente úteis para números complexos
import math # Importa o módulo math para funções matemáticas como pi, sqrt e log

# Metodos
#from imagem import metodo_imagem_long
#from Carson_correcao import Metodo_Carson_long
#from Carson_pr import metodo_carson_para_raio
#from Carson_transposicao import metodo_carson_transp
#from feixes_de_condutores import calcular_rmg_feixe
#from componentes_simetricas_sintese
#from componentes_simetricas_analise

# --- Backend: Lógica de Negócio do Cálculo (Funções Separadas) ---

# Função para o Método Longitudinal Imagem (SEM correção de Carson com rho explícito)
def metodo_imagem_long(ra, rb, rc, xa, ha, xb, hb, xc, hc, R=None, Rmg_val=None):
    """
    Calcula a matriz de impedância série por unidade de comprimento de uma linha de transmissão trifásica,
    utilizando o Método das Imagens para considerar o efeito do solo.
    Esta versão NÃO usa a resistividade do solo (rho) diretamente como parâmetro.
    """

    mi_0 = 4 * math.pi * (10**(-7))                                     # Permeabilidade magnética do vácuo (H/m)
    f = 60                                                              # Frequência do sistema (Hertz)
    w = 2 * math.pi * f                                                 # Frequência angular (rad/s)

    Rmg = None                                                          # Inicializa o Raio Médio Geométrico (RMG)

    if Rmg_val is not None:                                             # Prioriza RMG_val se fornecido
        Rmg = Rmg_val
    elif R is not None:                                                 # Calcula RMG a partir de R se Rmg_val não estiver presente
        Rmg = R * math.exp(-1/4)
    
    if Rmg is None:                                                     # Erro se nenhum raio válido for dado
        raise ValueError("ERRO! É necessário fornecer o valor do raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:                                                        # Erro se RMG for não positivo
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0:                                   # Valida alturas positivas para o método da imagem
        raise ValueError("ERRO! As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero para o Método da Imagem.")
    
    # --- Cálculo das Distâncias Geométricas ---
    # Distâncias entre condutores reais
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2))
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2))
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2))
    
    # Distâncias entre condutor real e imagem do outro condutor
    dab_l = np.sqrt(((xa - xb)**2) + ((ha + hb)**2))
    dac_l = np.sqrt(((xa - xc)**2) + ((ha + hc)**2))
    dbc_l = np.sqrt(((xb - xc)**2) + ((hb + hc)**2))
    
    # --- Cálculo das Impedâncias Série (por unidade de comprimento em Ohms/metro) ---
    # As resistências ra, rb, rc são consideradas Ohms/metro se o resultado for Ohms/metro
    Zaa_m = ra + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * ha) / Rmg))
    Zbb_m = rb + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * hb) / Rmg))
    Zcc_m = rc + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * hc) / Rmg))
    
    Zab_m = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dab_l / dab))
    Zac_m = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dac_l / dac))
    Zbc_m = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dbc_l / dbc))
    
    Zba_m = Zab_m
    Zca_m = Zac_m
    Zcb_m = Zbc_m
    
    # --- Montagem da Matriz de Impedância da Linha ---
    # Retorna a matriz em Ohms/km
    Z = np.array([
        [Zaa_m, Zab_m, Zac_m],
        [Zba_m, Zbb_m, Zbc_m],
        [Zca_m, Zcb_m, Zcc_m]
    ]) * 1000 # Converte Ohms/metro para Ohms/km

    return Z

# Função para o Método de Carson Longitudinal (COM correção de resistividade do solo)
def Metodo_Carson_long(ra, rb, rc, xa, xb, xc, ha, hb, hc, rho, R=None, Rmg_val=None):
    """
    Método de Carson com correção para cálculo de impedâncias longitudinais
    em linhas de transmissão trifásicas, sem cabo para-raio.

    Parâmetros:
    ra, rb, rc (float): Resistência ôhmica por unidade de comprimento dos condutores A, B, C (Ohms/metro).
                        É crucial que estas resistências estejam em Ohms por metro para consistência com as constantes.
    xa, xb, xc (float): Coordenadas horizontais (X) dos condutores A, B, C (metros).
    ha, hb, hc (float): Coordenadas verticais (altura H) dos condutores A, B, C (metros).
    rho (float): Resistividade do solo (Ohms-metro). Variável de entrada crucial para a correção de Carson.
    R (float, opcional): Raio físico do condutor (metros). Usado para calcular o RMG se Rmg_val não for fornecido.
    Rmg_val (float, opcional): Raio Médio Geométrico (RMG) do condutor (metros). Se fornecido, R é ignorado,
                                pois o RMG é mais preciso para cabos trançados.

    Retorna:
    numpy.ndarray: Matriz de impedância 3x3 complexa (Ohms/km).

    Raises:
    ValueError: Se nem R nem Rmg_val forem fornecidos, ou se RMG, rho, ou qualquer altura for não positivo.
    """

    # --- Constantes Físicas e Elétricas ---
    f = 60                                          # Frequência do sistema (Hz). Padrão no Brasil e em outras regiões.
    mi_0 = 4 * math.pi * (10**(-7))                 # Permeabilidade magnética do vácuo (H/m). Constante física fundamental.
    w = 2 * math.pi * f                             # Frequência angular (rad/s). Usada nos cálculos de reatância indutiva.

    # --- Termos de Correção do Método de Carson para o Solo ---
    # rd: Termo de resistência de Carson (Ohms/m) que representa a parcela de resistência adicionada
    # devido ao retorno da corrente pelo solo com resistividade finita. É um termo constante.
    rd = 9.869 * (10**(-7)) * f                     # Ohms/m. Esta é uma aproximação amplamente usada para 50/60 Hz.

    # De: Distância de retorno equivalente do solo (metros).
    # É uma profundidade fictícia do plano de retorno da corrente no solo,
    # que encapsula o efeito da resistividade finita do solo.
    # A constante 659 é apropriada para rho em Ohm-m e f em Hz, resultando em De em metros.
    De = 659 * (math.sqrt(rho / f))                 # Metros

    # --- Cálculo do Raio Médio Geométrico (RMG) ---
    Rmg = None # Inicializa RMG como None para verificar se foi calculado ou fornecido
    if Rmg_val is not None:
        Rmg = Rmg_val # Se o RMG já foi fornecido, usa-o diretamente
    elif R is not None:
        # Se o raio físico (R) foi fornecido, calcula o RMG.
        # Para condutores sólidos ou simples, RMG = R * e^(-1/4).
        # Para condutores trançados (como ACSR), o RMG geralmente é um valor tabelado pelo fabricante.
        Rmg = R * math.exp(-1/4)
    
    # --- Validações de Entrada ---
    # Estas verificações garantem que os valores de entrada são válidos para o cálculo.
    if Rmg is None:
        raise ValueError("ERRO! É necessário fornecer o raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0:
        # As alturas devem ser positivas para o uso do logaritmo (ln(De/H)) no cálculo da impedância própria.
        raise ValueError("ERRO! As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.")

    # --- Cálculo das Distâncias Geométricas entre os condutores ---
    # As distâncias entre os centros dos condutores reais são calculadas usando a fórmula da distância euclidiana 2D.
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2)) # Distância entre condutores A e B
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2)) # Distância entre condutores A e C
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2)) # Distância entre condutores B e C

    # --- Cálculo das Impedâncias Próprias e Mútuas (por metro) ---
    # As fórmulas de Carson geralmente resultam em impedâncias por metro.
    # Impedâncias Próprias (Zii): Representam a impedância de um condutor em relação ao retorno pelo solo.
    # Zii = Ri_condutor + R_terra_Carson + j * X_terra_propria_Carson
    # R_terra_Carson é o termo 'rd'. X_terra_propria_Carson é a parte logarítmica com De/RMG.
    Zaa = ra + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zbb = rb + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)
    Zcc = rc + rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / Rmg)

    # Impedâncias Mútuas (Zij): Representam o acoplamento eletromagnético entre dois condutores,
    # considerando o retorno pelo solo.
    # Zij = R_terra_Carson + j * X_terra_mutua_Carson
    # R_terra_Carson é o termo 'rd'. X_terra_mutua_Carson é a parte logarítmica com De/dij.
    Zab = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dab) # Impedância mútua entre A e B
    Zac = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dac) # Impedância mútua entre A e C
    Zbc = rd + ((1j * w * mi_0) / (2 * math.pi)) * math.log(De / dbc) # Impedância mútua entre B e C

    # As impedâncias mútuas são simétricas na matriz de impedância de fase (Zij = Zji).
    Zba = Zab
    Zca = Zac
    Zcb = Zbc

    # --- Construção da Matriz de Impedância ---
    # Monta a matriz 3x3 de impedâncias de fase.
    # Cada elemento [i, j] da matriz representa a impedância entre a fase i e a fase j.
    # Multiplica a matriz inteira por 1000 para converter de Ohms/metro para Ohms/km.
    Z = np.array([
        [Zaa, Zab, Zac],
        [Zba, Zbb, Zbc],
        [Zca, Zcb, Zcc]
    ]) * 1000 # Converter para Ohms/km

    return Z # Retorna a matriz de impedância longitudinal da linha


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
        else:
            messagebox.showinfo("Método Não Implementado", f"O método '{selected_method}' ainda não foi implementado. Por favor, selecione 'Longitudinal Imagem' ou 'Longitudinal Carson (Correção)'.")

# --- Inicialização ---
if __name__ == "__main__":
    root = Tk()
    app = AppMain(root)