from tkinter import * # Importa classes e funções do Tkinter
from tkinter import ttk

root = Tk()                                                                         # Cria a janela principal da aplicação

#Back-end
class funcs():
    def limpa_tela(self):
        self.r_entry.delete(0,END)
        self.h_entry.delete(0,END)
        self.dab_entry.delete(0,END)
        self.dac_entry.delete(0,END)
        self.dbc_entry.delete(0,END)
    def get_variaveis(self):
        self.r = self.r_entry.get()
        self.h = self.h_entry.get()
        self.dab = self.dab_entry.get()
        self.dac = self.dac_entry.get()
        self.dbc = self.dbc_entry.get()
    #def met_capacitancia_imagem():

#Front-end
class aplicativo(funcs):                                                            # Define a classe do aplicativo
    def __init__(self):                                                             # Construtor da classe
        self.root = root                                                            # Atribui a janela principal à instância da classe
        self.tela_metodo_X()                                                        # Configura a interface inicial da janela
        self.frames_da_tela()                                                       # Cria e posiciona os frames da interface
        self.widgets_frame_info()                                                   # Cria e posiciona os widgets dentro do frame de informações
        self.lista_frame_result()
        root.mainloop()                                                             # Inicia o loop principal de eventos do Tkinter
    def tela_metodo_X(self):                                                        # Configurações da janela principal
        self.root.title("Método x de linhas de Transmissão")                        # Define o título da janela
        self.root.geometry("700x500")                                               # Define as dimensões iniciais da janela (largura x altura)
        self.root.resizable(False,False)                                            # Impede o redimensionamento da janela (largura, altura)
        self.root.maxsize(width=900, height=700)                                    # Define as dimensões máximas permitidas para a janela
        self.root.minsize(width=400, height=300)                                    # Define as dimensões mínimas permitidas para a janela
    def frames_da_tela(self):                                                       # Cria e organiza os frames na tela
        self.frame_info = Frame(self.root, bd=4, bg='#BEBEBE',                      # Cria um frame para informações
                                 highlightbackground= 'black', highlightthickness=3 ) # Define borda com realce
        self.frame_info.place(relx= 0.02 , rely=0.02, relwidth= 0.96,relheight= 0.45) # Posiciona o frame na parte superior

        self.frame_result = Frame(self.root, bd=4, bg='#BEBEBE',                    # Cria um frame para resultados
                                 highlightbackground='black', highlightthickness=3)  # Define borda com realce
        self.frame_result.place(relx=0.02, rely=0.5, relwidth=0.96, relheight=0.45)  # Posiciona o frame na parte inferior
    def widgets_frame_info(self):                                                   # Cria e posiciona os widgets no frame de informações
        #Botões
        ##Botão para retornar ao seleção do método
        self.botao_return = Button(self.frame_info, text='Retornar',bd=4,           # Cria o botão "Retornar"
                                    font=('Arial',10))                              # Define a fonte do botão
        self.botao_return.place(relx=.01,rely=.01,relwidth=0.15,relheight=0.1)      # Posiciona o botão

        ##Botão para limpar tela de variáveis
        self.botao_limpar = Button(self.frame_info, text='Limpar',bd=4,             # Cria o botão "Limpar"
                                    font=('Arial',10), command=self.limpa_tela)     # Define a fonte do botão
        self.botao_limpar.place(relx=.80,rely=.01,relwidth=0.15,relheight=0.1)      # Posiciona o botão

        ##Botão para calcular o método
        self.botao_calc = Button(self.frame_info, text='Calcular',bd=4,             # Cria o botão "Calcular"
                                    font=('Arial',10))                              # Define a fonte do botão
        self.botao_calc.place(relx=.8,rely=.85,relwidth=0.15,relheight=0.1)         # Posiciona o botão

        #Labels e entradas
        ##Criação da label Variáveis
        self.lb_variaveis = Label(self.frame_info, text='Variáveis')                # Cria a label "Variáveis"
        self.lb_variaveis.place(relx=.3,rely=.1)                                    # Posiciona a label
        
        ##Labels das variáveis e entradas do código
        ###Variável Raio do contutor
        self.lb_r = Label(self.frame_info, text='Raio do condutor')                # Cria a label "Raio do condutor"
        self.lb_r.place(relx=.2,rely=.23)                                           # Posiciona a label
        self.r_entry = Entry(self.frame_info)                                       # Cria a entrada para o raio do condutor
        self.r_entry.place(relx=.5,rely=.23,relwidth=0.08)                          # Posiciona a entrada

        ###Variável Altura
        self.lb_h = Label(self.frame_info, text='Altura do condutor ao solo')       # Cria a label "Altura do condutor ao solo"
        self.lb_h.place(relx=.2,rely=.36)                                           # Posiciona a label
        self.h_entry = Entry(self.frame_info)                                       # Cria a entrada para a altura do condutor
        self.h_entry.place(relx=.5,rely=.36,relwidth=0.08)                          # Posiciona a entrada

        ##Criação da label Variáveis distâncias
        self.lb_distancias = Label(self.frame_info, text='Distâncias')              # Cria a label "Distâncias"
        self.lb_distancias.place(relx=.3,rely=.49)                                  # Posiciona a label

        ###Variável distancia entre A e B
        self.lb_dab = Label(self.frame_info, text='Distância entre os condutores A e B') # Cria a label "Distância entre A e B"
        self.lb_dab.place(relx=.2,rely=.62)                                         # Posiciona a label
        self.dab_entry = Entry(self.frame_info)                                     # Cria a entrada para a distância entre A e B
        self.dab_entry.place(relx=.5,rely=.62,relwidth=0.08)                        # Posiciona a entrada

        ###Variável distancia entre A e C
        self.lb_dac = Label(self.frame_info, text='Distância entre os condutores A e C') # Cria a label "Distância entre A e C"
        self.lb_dac.place(relx=.2,rely=.75)                                         # Posiciona a label
        self.dac_entry = Entry(self.frame_info)                                     # Cria a entrada para a distância entre A e C
        self.dac_entry.place(relx=.5,rely=.75,relwidth=0.08)                        # Posiciona a entrada

        ###Variável distancia entre B e C
        self.lb_dbc = Label(self.frame_info, text='Distância entre os condutores B e C') # Cria a label "Distância entre B e C"
        self.lb_dbc.place(relx=.2,rely=.88)                                         # Posiciona a label
        self.dbc_entry = Entry(self.frame_info)                                     # Cria a entrada para a distância entre B e C
        self.dbc_entry.place(relx=.5,rely=.88,relwidth=0.08)                        # Posiciona a entrada
    def lista_frame_result(self):
        
        self.lista_CAP = ttk.Treeview(self.frame_result, height=3, column=('col1','col2','col3'))
        self.lista_CAP.heading("#0", text="")
        self.lista_CAP.heading("#1", text="A")
        self.lista_CAP.heading("#2", text="B")
        self.lista_CAP.heading("#3", text="C")

        self.lista_CAP.column("#0", width=1)
        self.lista_CAP.column("#1", width=50)
        self.lista_CAP.column("#2", width=200)
        self.lista_CAP.column("#3", width=120)

        self.lista_CAP.place(relx=0.01, rely=0.1, relwidth=0.95, relheight=0.85)

        self.scrollLista = Scrollbar(self.frame_result, orient='vertical')
        self.lista_CAP.configure(yscroll=self.scrollLista.set)
        self.scrollLista.place(relx=0.96, rely=0.1, relwidth=0.02, relheight=0.85)

aplicativo()                                                                        # Inicia o aplicativo, criando uma instância da classe