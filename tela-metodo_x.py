from tkinter import * # Importa classes e funções do Tkinter
from tkinter import ttk                                                             # Importa o módulo ttk (widgets estilizados)

root = Tk()                                                                         # Cria a janela principal da aplicação

# --- Backend: Lógica de Negócio ---
class funcs():                                                                      # Define a classe para funções de backend
    def limpa_tela(self):                                                           # Método para limpar campos de entrada
        self.r_entry.delete(0,END)                                                  # Limpa o campo do raio do condutor
        self.h_entry.delete(0,END)                                                  # Limpa o campo da altura do condutor
        self.dab_entry.delete(0,END)                                                # Limpa o campo da distância entre A e B
        self.dac_entry.delete(0,END)                                                # Limpa o campo da distância entre A e C
        self.dbc_entry.delete(0,END)                                                # Limpa o campo da distância entre B e C

    def get_variaveis(self):                                                        # Método para obter valores das variáveis
        self.r = self.r_entry.get()                                                 # Obtém o valor do raio do condutor
        self.h = self.h_entry.get()                                                 # Obtém o valor da altura do condutor
        self.dab = self.dab_entry.get()                                             # Obtém o valor da distância entre A e B
        self.dac = self.dac_entry.get()                                             # Obtém o valor da distância entre A e C
        self.dbc = self.dbc_entry.get()                                             # Obtém o valor da distância entre B e C
    #def met_capacitancia_imagem():                                                 # (Comentado) Placeholder para método futuro

# --- Frontend: Interface Gráfica ---
class aplicativo(funcs):                                                            # Define a classe do aplicativo, herdando funções
    def __init__(self):                                                             # Construtor da classe
        self.root = root                                                            # Atribui a janela principal à instância da classe
        self.tela_metodo_X()                                                        # Configura a interface inicial da janela
        self.frames_da_tela()                                                       # Cria e posiciona os frames da interface
        self.widgets_frame_info()                                                   # Cria e posiciona os widgets no frame de informações
        self.lista_frame_result()                                                   # Cria e posiciona a Treeview no frame de resultados
        self.inserir_dados_tabela()
        root.mainloop()                                                             # Inicia o loop principal de eventos do Tkinter

    def tela_metodo_X(self):                                                        # Configurações da janela principal
        self.root.title("Método x de LinhaMestre")                                  # Define o título da janela
        self.root.geometry("700x500")                                               # Define as dimensões iniciais da janela (largura x altura)
        self.root.configure(background='#2F4F4F')
        self.root.resizable(False,False)                                            # Impede o redimensionamento da janela (largura, altura)
        self.root.maxsize(width=900, height=700)                                    # Define as dimensões máximas permitidas para a janela
        self.root.minsize(width=400, height=300)                                    # Define as dimensões mínimas permitidas para a janela

    def frames_da_tela(self):                                                         # Cria e organiza os frames na tela
        self.frame_info = Frame(self.root, bd=4, bg='#BEBEBE',                      # Cria um frame para informações
                                 highlightbackground= 'black', highlightthickness=3 ) # Define borda com realce
        self.frame_info.place(relx= 0.02 , rely=0.02, relwidth= 0.96,relheight= 0.45) # Posiciona o frame na parte superior

        self.frame_result = Frame(self.root, bd=4, bg='#BEBEBE',                  # Cria um frame para resultados
                                 highlightbackground='black', highlightthickness=3) # Define borda com realce
        self.frame_result.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.45) # Posiciona o frame na parte inferior

    def widgets_frame_info(self):                                                   # Cria e posiciona os widgets no frame de informações
        # --- Botões ---
        self.botao_return = Button(self.frame_info, text='Retornar',bd=4,           # Cria o botão "Retornar"
                                     font=('Arial',10))                             # Define a fonte do botão
        self.botao_return.place(relx=.01,rely=.01,relwidth=0.15,relheight=0.1)      # Posiciona o botão

        self.botao_limpar = Button(self.frame_info, text='Limpar',bd=4,             # Cria o botão "Limpar"
                                     font=('Arial',10), command=self.limpa_tela)    # Define fonte e ação de limpeza
        self.botao_limpar.place(relx=.80,rely=.01,relwidth=0.15,relheight=0.1)      # Posiciona o botão

        self.botao_calc = Button(self.frame_info, text='Calcular',bd=4,             # Cria o botão "Calcular"
                                    font=('Arial',10))                             # Define a fonte do botão
        self.botao_calc.place(relx=.8,rely=.85,relwidth=0.15,relheight=0.1)         # Posiciona o botão

        # --- Labels e Entradas ---
        self.lb_variaveis = Label(self.frame_info, text='Variáveis')                # Cria a label "Variáveis"
        self.lb_variaveis.place(relx=.3,rely=.1)                                    # Posiciona a label
        
        # Variável Raio do condutor
        self.lb_r = Label(self.frame_info, text='Raio do condutor')                 # Cria a label "Raio do condutor"
        self.lb_r.place(relx=.2,rely=.23)                                           # Posiciona a label
        self.r_entry = Entry(self.frame_info)                                       # Cria a entrada para o raio do condutor
        self.r_entry.place(relx=.5,rely=.23,relwidth=0.08)                          # Posiciona a entrada

        # Variável Altura
        self.lb_h = Label(self.frame_info, text='Altura do condutor ao solo')       # Cria a label "Altura do condutor ao solo"
        self.lb_h.place(relx=.2,rely=.36)                                           # Posiciona a label
        self.h_entry = Entry(self.frame_info)                                       # Cria a entrada para a altura do condutor
        self.h_entry.place(relx=.5,rely=.36,relwidth=0.08)                          # Posiciona a entrada

        # Criação da label Variáveis distâncias
        self.lb_distancias = Label(self.frame_info, text='Distâncias')             # Cria a label "Distâncias"
        self.lb_distancias.place(relx=.3,rely=.49)                                  # Posiciona a label

        # Variável distancia entre A e B
        self.lb_dab = Label(self.frame_info, text='Distância entre os condutores A e B') # Cria a label "Distância entre A e B"
        self.lb_dab.place(relx=.2,rely=.62)                                         # Posiciona a label
        self.dab_entry = Entry(self.frame_info)                                     # Cria a entrada para a distância entre A e B
        self.dab_entry.place(relx=.5,rely=.62,relwidth=0.08)                        # Posiciona a entrada

        # Variável distancia entre A e C
        self.lb_dac = Label(self.frame_info, text='Distância entre os condutores A e C') # Cria a label "Distância entre A e C"
        self.lb_dac.place(relx=.2,rely=.75)                                         # Posiciona a label
        self.dac_entry = Entry(self.frame_info)                                     # Cria a entrada para a distância entre A e C
        self.dac_entry.place(relx=.5,rely=.75,relwidth=0.08)                        # Posiciona a entrada

        # Variável distancia entre B e C
        self.lb_dbc = Label(self.frame_info, text='Distância entre os condutores B e C') # Cria a label "Distância entre B e C"
        self.lb_dbc.place(relx=.2,rely=.88)                                         # Posiciona a label
        self.dbc_entry = Entry(self.frame_info)                                     # Cria a entrada para a distância entre B e C
        self.dbc_entry.place(relx=.5,rely=.88,relwidth=0.08)                        # Posiciona a entrada

    def lista_frame_result(self):                                                   # Cria e configura a lista de resultados (Treeview)
        self.lista_CAP = ttk.Treeview(self.frame_result, height=3,                  # Cria o widget Treeview para resultados
                                      column=('col1','col2','col3'))                # Define as colunas
        self.lista_CAP.heading("#0", text="")                                       # Define o cabeçalho da coluna oculta
        self.lista_CAP.heading("#1", text="A")                                      # Define o cabeçalho da coluna 1
        self.lista_CAP.heading("#2", text="B")                                      # Define o cabeçalho da coluna 2
        self.lista_CAP.heading("#3", text="C")                                      # Define o cabeçalho da coluna 3

        self.lista_CAP.column("#0", width=1)                                        # Define a largura da coluna oculta
        self.lista_CAP.column("#1", width=50)                                       # Define a largura da coluna 1
        self.lista_CAP.column("#2", width=200)                                      # Define a largura da coluna 2
        self.lista_CAP.column("#3", width=120)                                      # Define a largura da coluna 3

        self.lista_CAP.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)    # Posiciona a Treeview

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')          # Cria uma barra de rolagem vertical
        self.lista_CAP.configure(yscroll=self.scrollLista.set)                      # Associa a barra de rolagem à Treeview
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)  # Posiciona a barra de rolagem

    def inserir_dados_tabela(self):                                                 # Método para inserir dados na tabela Treeview
        # Limpa qualquer dado existente na Treeview (útil para atualizações)
        for i in self.lista_CAP.get_children():                                     # Itera sobre todos os itens
            self.lista_CAP.delete(i)                                                # Deleta cada item

        # Inserindo os dados conforme solicitado
        # A primeira coluna "" é para o identificador interno do Treeview.
        # Os valores da primeira coluna visível ('A') vão para o 'text' do item.
        # Os valores das colunas seguintes ('B', 'C') vão para o 'values'.
        self.lista_CAP.insert("", END, text="A", values=("", "", ""))                # Insere linha para 'A'
        self.lista_CAP.insert("", END, text="B", values=("", "", ""))                # Insere linha para 'B'
        self.lista_CAP.insert("", END, text="C", values=("", "", ""))                # Insere linha para 'C'

# --- Inicialização ---
aplicativo()                                                                         # Inicia o aplicativo, criando uma instância da classe