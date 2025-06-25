from tkinter import * # Importa classes e funções do Tkinter
from tkinter import ttk                                                             # Importa o módulo ttk (widgets estilizados)
from tkinter import messagebox                                                      # Importa messagebox para exibir mensagens de erro/informação

import numpy as np                                                                  # Importa NumPy para operações matriciais
import math                                                                         # Importa math para funções matemáticas

root = Tk()                                                                         # Cria a janela principal do Tkinter

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

# --- Backend: Lógica de Interação da UI ---
class funcs():                                                          # Define a classe para funções de backend
    def limpa_tela(self):                                               # Método para limpar campos de entrada e Treeview
        self.ra_entry.delete(0,END)                                     # Limpa resistência A
        self.rb_entry.delete(0,END)                                     # Limpa resistência B
        self.rc_entry.delete(0,END)                                     # Limpa resistência C
        self.r_entry.delete(0,END)                                      # Limpa raio do condutor
        self.rmg_entry.delete(0,END)                                    # Limpa RMG
        self.xa_entry.delete(0,END)                                     # Limpa coordenada X de A
        self.xb_entry.delete(0,END)                                     # Limpa coordenada X de B
        self.xc_entry.delete(0,END)                                     # Limpa coordenada X de C
        self.ha_entry.delete(0,END)                                     # Limpa altura H de A
        self.hb_entry.delete(0,END)                                     # Limpa altura H de B
        self.hc_entry.delete(0,END)                                     # Limpa altura H de C
        
        for i in self.lista_CAP.get_children():                         # Itera e deleta itens na Treeview
            self.lista_CAP.delete(i)
        
        self.inserir_dados_tabela(np.full((3, 3), np.nan, dtype=complex)) # Preenche Treeview com campos vazios

    def get_variaveis(self):                                            # Obtém e converte valores dos campos
        try:
            ra = float(self.ra_entry.get()) if self.ra_entry.get() else 0.0 # Converte Ra ou 0.0
            rb = float(self.rb_entry.get()) if self.rb_entry.get() else 0.0 # Converte Rb ou 0.0
            rc = float(self.rc_entry.get()) if self.rc_entry.get() else 0.0 # Converte Rc ou 0.0

            R_val = float(self.r_entry.get()) if self.r_entry.get() else None # Converte R ou None
            Rmg_val = float(self.rmg_entry.get()) if self.rmg_entry.get() else None # Converte RMG ou None
            
            xa = float(self.xa_entry.get()) if self.xa_entry.get() else 0.0 # Converte Xa ou 0.0
            xb = float(self.xb_entry.get()) if self.xb_entry.get() else 0.0 # Converte Xb ou 0.0
            xc = float(self.xc_entry.get()) if self.xc_entry.get() else 0.0 # Converte Xc ou 0.0

            ha = float(self.ha_entry.get()) if self.ha_entry.get() else 0.0 # Converte Ha ou 0.0
            hb = float(self.hb_entry.get()) if self.hb_entry.get() else 0.0 # Converte Hb ou 0.0
            hc = float(self.hc_entry.get()) if self.hc_entry.get() else 0.0 # Converte Hc ou 0.0

            if ha <= 0 or hb <= 0 or hc <= 0:                           # Valida alturas positivas
                raise ValueError("As alturas dos condutores (Ha, Hb, Hc) devem ser maiores que zero.")

            return {                                                    # Retorna dicionário de parâmetros
                'ra': ra, 'rb': rb, 'rc': rc,
                'xa': xa, 'ha': ha,
                'xb': xb, 'hb': hb,
                'xc': xc, 'hc': hc,
                'R': R_val, 'Rmg_val': Rmg_val
            }
        except ValueError as e:                                         # Captura erros de conversão
            messagebox.showerror("Erro de Entrada", f"Por favor, insira valores numéricos válidos. Detalhes: {e}")
            return None                                                 # Retorna None em caso de erro

    def calcular(self):                                                 # Orquestra o cálculo e exibição
        params = self.get_variaveis()                                   # Obtém os parâmetros de entrada
        if params is None:                                              # Sai se houver erro nos parâmetros
            return

        try:
            Z_matrix = metodo_imagem_long(                              # Chama a função de cálculo
                ra=params['ra'], rb=params['rb'], rc=params['rc'],
                xa=params['xa'], ha=params['ha'],
                xb=params['xb'], hb=params['hb'],
                xc=params['xc'], hc=params['hc'],
                R=params['R'], Rmg_val=params['Rmg_val']
            )
            self.inserir_dados_tabela(Z_matrix)                         # Atualiza a tabela com o resultado
            messagebox.showinfo("Cálculo Concluído", "A matriz de impedância foi calculada e exibida na tabela.") # Mensagem de sucesso
        except ValueError as e:                                         # Captura erros específicos de cálculo
            messagebox.showerror("Erro de Cálculo", f"Ocorreu um erro durante o cálculo: {e}")
        except Exception as e:                                          # Captura erros inesperados
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro inesperado: {e}")

    def inserir_dados_tabela(self, Z_matrix):                           # Insere dados na Treeview
        for i in self.lista_CAP.get_children():                         # Limpa dados existentes
            self.lista_CAP.delete(i)
        
        # --- MODIFICAÇÃO AQUI: Altera de {:.3f} para {:.6f} ---
        complex_format = "({:.6f} + j{:.6f})"                           # Formato de exibição para números complexos (6 casas decimais)

        row_labels = ["A", "B", "C"]                                    # Rótulos das linhas (Fases)

        for i, row_label in enumerate(row_labels):                      # Itera pelas linhas da matriz
            row_values = []
            for j in range(Z_matrix.shape[1]):                          # Itera pelas colunas
                complex_num = Z_matrix[i, j]
                if np.isnan(complex_num.real) and np.isnan(complex_num.imag): # Se for NaN, exibe vazio
                    formatted_value = ""
                else:                                                   # Caso contrário, formata o número
                    formatted_value = complex_format.format(complex_num.real, complex_num.imag)
                row_values.append(formatted_value)
            
            self.lista_CAP.insert("", END, text=row_label, values=tuple(row_values)) # Insere a linha na Treeview

# --- Frontend: Interface Gráfica ---
class aplicativo(funcs):                                                # Define a classe do aplicativo, herda de funcs
    def __init__(self):                                                 # Construtor da classe
        self.root = root                                                # Atribui a janela principal
        self.tela_metodo_X()                                            # Configura a janela
        self.frames_da_tela()                                           # Cria e posiciona frames
        self.widgets_frame_info()                                       # Cria widgets no frame de informações
        self.lista_frame_result()                                       # Cria Treeview no frame de resultados
        
        # Esta linha é crucial: ela preenche o Treeview com NaNs que são exibidos como vazios.
        self.inserir_dados_tabela(np.full((3, 3), np.nan, dtype=complex)) # Inicia o Treeview vazio

        root.mainloop()                                                 # Inicia o loop principal do Tkinter

    def tela_metodo_X(self):                                            # Configurações da janela
        self.root.title("Cálculo de Impedância - Método das Imagens")   # Título da janela
        self.root.geometry("700x500")                                   # Dimensões da janela
        self.root.configure(background='#2F4F4F')                       # Cor de fundo da janela
        self.root.resizable(False,False)                                # Impede redimensionamento
        self.root.maxsize(width=900, height=700)                        # Tamanho máximo
        self.root.minsize(width=400, height=300)                        # Tamanho mínimo

    def frames_da_tela(self):                                           # Cria e organiza os frames
        self.frame_info = Frame(self.root, bd=4, bg='#BEBEBE', highlightthickness=3) # Frame superior para entradas
        self.frame_info.place(relx= 0.02 , rely=0.02, relwidth= 0.96,relheight= 0.45) # Posiciona frame superior

        self.frame_result = Frame(self.root, bd=4, bg='#BEBEBE', highlightthickness=3) # Frame inferior para resultados
        self.frame_result.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.45)  # Posiciona frame inferior

    def widgets_frame_info(self):                                       # Cria widgets no frame de informações
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar',bd=4,          # Botão "Retornar"
                                        font=('Arial',10))                          # Fonte do botão
        self.botao_return.place(relx=.01,rely=.01,relwidth=0.15,relheight=0.1)      # Posiciona botão "Retornar"

        self.botao_limpar = Button(self.frame_info, text='Limpar',bd=4,            # Botão "Limpar"
                                        font=('Arial',10), command=self.limpa_tela) # Ação de limpar campos
        self.botao_limpar.place(relx=.80,rely=.01,relwidth=0.15,relheight=0.1)      # Posiciona botão "Limpar"

        self.botao_calc = Button(self.frame_info, text='Calcular',bd=4,            # Botão "Calcular"
                                     font=('Arial',10), command=self.calcular)      # Ação de calcular
        self.botao_calc.place(relx=.8,rely=.85,relwidth=0.15,relheight=0.1)         # Posiciona botão "Calcular"

        # --- Labels e Entradas de Resistências ---
        Label(self.frame_info, text='Resistências', bg='#BEBEBE').place(relx=0.01,rely=.2) # Label "Resistências"

        self.lb_ra = Label(self.frame_info, text='Ra (Ohm/unidade)', bg='#BEBEBE') # Label Ra
        self.lb_ra.place(relx=0.01,rely=.32)
        self.ra_entry = Entry(self.frame_info)                                      # Campo de entrada Ra
        self.ra_entry.place(relx=.2,rely=.32,relwidth=0.08)

        self.lb_rb = Label(self.frame_info, text='Rb (Ohm/unidade)', bg='#BEBEBE') # Label Rb
        self.lb_rb.place(relx=0.01,rely=.44)
        self.rb_entry = Entry(self.frame_info)                                      # Campo de entrada Rb
        self.rb_entry.place(relx=.2,rely=.44,relwidth=0.08)

        self.lb_rc = Label(self.frame_info, text='Rc (Ohm/unidade)', bg='#BEBEBE') # Label Rc
        self.lb_rc.place(relx=0.01,rely=.56)
        self.rc_entry = Entry(self.frame_info)                                      # Campo de entrada Rc
        self.rc_entry.place(relx=.2,rely=.56,relwidth=0.08)

        # --- Labels e Entradas de Raio e RMG ---
        self.lb_r = Label(self.frame_info, text='Raio Condutor (R) [m]', bg='#BEBEBE') # Label Raio Condutor
        self.lb_r.place(relx=0.01,rely=.68)
        self.r_entry = Entry(self.frame_info)                                       # Campo de entrada Raio
        self.r_entry.place(relx=.2,rely=.68,relwidth=0.08)

        self.lb_rmg = Label(self.frame_info, text='OU RMG [m]', bg='#BEBEBE')       # Label RMG
        self.lb_rmg.place(relx=0.01,rely=.80)
        self.rmg_entry = Entry(self.frame_info)                                     # Campo de entrada RMG
        self.rmg_entry.place(relx=.2,rely=.80,relwidth=0.08)

        # --- Labels e Entradas de Coordenadas ---
        Label(self.frame_info, text='Coordenadas dos Cabos', bg='#BEBEBE').place(relx=.4,rely=.2) # Label Coordenadas

        self.lb_xa = Label(self.frame_info, text='X_a (m)', bg='#BEBEBE')          # Label Xa
        self.lb_xa.place(relx=.4,rely=.32)
        self.xa_entry = Entry(self.frame_info)                                      # Campo de entrada Xa
        self.xa_entry.place(relx=.48,rely=.32,relwidth=0.08)

        self.lb_xb = Label(self.frame_info, text='X_b (m)', bg='#BEBEBE')          # Label Xb
        self.lb_xb.place(relx=.4,rely=.44)
        self.xb_entry = Entry(self.frame_info)                                      # Campo de entrada Xb
        self.xb_entry.place(relx=.48,rely=.44,relwidth=0.08)

        self.lb_xc = Label(self.frame_info, text='X_c (m)', bg='#BEBEBE')          # Label Xc
        self.lb_xc.place(relx=.4,rely=.56)
        self.xc_entry = Entry(self.frame_info)                                      # Campo de entrada Xc
        self.xc_entry.place(relx=.48,rely=.56,relwidth=0.08)

        self.lb_ha = Label(self.frame_info, text='H_a (m)', bg='#BEBEBE')          # Label Ha
        self.lb_ha.place(relx=.6,rely=.32)
        self.ha_entry = Entry(self.frame_info)                                      # Campo de entrada Ha
        self.ha_entry.place(relx=.68,rely=.32,relwidth=0.08)

        self.lb_hb = Label(self.frame_info, text='H_b (m)', bg='#BEBEBE')          # Label Hb
        self.lb_hb.place(relx=.6,rely=.44)
        self.hb_entry = Entry(self.frame_info)                                      # Campo de entrada Hb
        self.hb_entry.place(relx=.68,rely=.44,relwidth=0.08)

        self.lb_hc = Label(self.frame_info, text='H_c (m)', bg='#BEBEBE')          # Label Hc
        self.lb_hc.place(relx=.6,rely=.56)
        self.hc_entry = Entry(self.frame_info)                                      # Campo de entrada Hc
        self.hc_entry.place(relx=.68,rely=.56,relwidth=0.08)

    def lista_frame_result(self):                                       # Cria e configura a Treeview
        self.lista_CAP = ttk.Treeview(self.frame_result, height=3,                  # Cria a Treeview
                                          columns=('col1','col2','col3'))           # Define as colunas
        self.lista_CAP.heading("#0", text="Fase")                                   # Cabeçalho da coluna "Fase"
        self.lista_CAP.heading("col1", text="Condutor A")                           # Cabeçalho da coluna 1
        self.lista_CAP.heading("col2", text="Condutor B")                           # Cabeçalho da coluna 2
        self.lista_CAP.heading("col3", text="Condutor C")                           # Cabeçalho da coluna 3

        self.lista_CAP.column("#0", width=80, anchor=CENTER)                        # Configura coluna "Fase"
        self.lista_CAP.column("col1", width=180, anchor=CENTER)                     # Configura coluna 1
        self.lista_CAP.column("col2", width=180, anchor=CENTER)                     # Configura coluna 2
        self.lista_CAP.column("col3", width=180, anchor=CENTER)                     # Configura coluna 3

        self.lista_CAP.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)     # Posiciona a Treeview

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')          # Cria barra de rolagem
        self.lista_CAP.configure(yscrollcommand=self.scrollLista.set)               # Associa barra à Treeview
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)   # Posiciona a barra

# --- Inicialização ---
aplicativo()                                                                        # Inicia o aplicativo