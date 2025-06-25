from tkinter import * # Importa todas as classes e funções do módulo Tkinter (ex: Tk, Frame, Button, Label, StringVar)
from tkinter import ttk # Importa o módulo ttk do Tkinter, que oferece widgets mais modernos e estilizados (ex: ttk.Treeview)
from tkinter import messagebox # Importa o módulo messagebox para exibir caixas de diálogo e alertas ao usuário

import numpy as np
import math

root = Tk()                                                                             # Cria a janela principal da aplicação Tkinter; esta será a janela inicial visível

class funcs():                                                                          # Define uma classe para agrupar funções de lógica e comportamento (back-end do aplicativo)
    def selecionar_metodo(self):                                                        # MÉTODO: Chamado quando o usuário clica no botão "OK" para processar a seleção do método
        if self.metodo_select == "":                                                    # Verifica se a variável 'metodo_select' (que guarda a escolha do usuário) está vazia
            msg = "Selecione um método válido, \n"                                      # Constrói a primeira parte da mensagem de erro para o usuário
            msg += "na caixa de seleção de métodos"                                     # Adiciona a segunda parte da mensagem de erro
            messagebox.showinfo("Erro de seleção de método!!!", msg)                    # Exibe uma caixa de diálogo com o título e a mensagem de erro
        elif self.metodo_select == "Longitudinal Imagem":                               # Se um método foi selecionado, verifica se é "Longitudinal Imagem"
            self.root.destroy()                                                         # Fecha/destrói a janela principal atual (a primeira tela)
            self.janela_metodo_imagem()                                                 # Chama o método para abrir a nova janela, específica para o "Método Longitudinal Imagem"
        else:                                                                           # Se o método selecionado não for vazio e nem "Longitudinal Imagem"
            pass                                                                        # Não faz nada por enquanto (aqui poderia haver lógica para outros métodos)

class aplicativo(funcs):                                                                # Define a classe principal da aplicação, herdando as funções de 'funcs'
    def __init__(self):                                                                 # O construtor da classe; é a primeira coisa executada ao iniciar o 'aplicativo'
        # --- Variáveis de Instância (Atributos) ---
        self.root = root                                                                # VARIÁVEL: Armazena a referência para a janela principal do Tkinter, permitindo manipulá-la
        self.metodo_select = ""                                                         # VARIÁVEL: Inicializa uma string vazia para armazenar o método selecionado pelo usuário.
                                                                                        # Essencial para evitar 'AttributeError' se acessada antes de uma seleção.
        
        # --- Chamadas de Métodos ---
        self.tela_root()                                                                # MÉTODO: Configura as propriedades visuais da janela principal (título, tamanho, cor de fundo)
        self.frames_da_tela()                                                           # MÉTODO: Cria e posiciona os contêineres visuais (frames) na janela principal
        self.widgets_frame_principal()                                                  # MÉTODO: Adiciona e posiciona todos os elementos interativos (botões, rótulos, menus) no frame principal
        root.mainloop()                                                                 # MÉTODO: Inicia o "loop infinito" do Tkinter, mantendo a janela aberta e respondendo a eventos do usuário

    def tela_root(self):                                                                # Método para configurar a aparência e o comportamento da janela principal
        self.root.title("LinhaMestre")                                                  # Define o texto que aparece na barra de título da janela
        self.root.configure(background='#2F4F4F')                                       # Define a cor de fundo da janela usando um código hexadecimal (um tom de azul/cinza escuro)
        self.root.geometry("700x500")                                                   # Define o tamanho inicial da janela em pixels (largura x altura)
        self.root.resizable(False,False)                                                # Impede que o usuário possa redimensionar a janela manualmente (largura e altura fixas)
        self.root.maxsize(width=900, height=700)                                        # Define o tamanho máximo que a janela pode assumir (útil se 'resizable' fosse True)
        self.root.minsize(width=400, height=300)                                        # Define o tamanho mínimo que a janela pode assumir (útil se 'resizable' fosse True)

    def frames_da_tela(self):                                                           # Método para criar e organizar os "quadros" (frames) que servem como contêineres para outros widgets
        self.frame_principal = Frame(self.root, bd=4, bg="gray",                        # Cria um 'Frame' dentro da janela principal, com borda de 4px e fundo cinza
                                     highlightbackground= 'black', highlightthickness=3 ) # Adiciona uma borda de destaque preta com 3px de espessura ao frame
        self.frame_principal.place(relx= 0.02 , rely=0.02, relwidth= 0.96,relheight= 0.96) # Posiciona o frame principal usando coordenadas relativas à janela (2% de margem, 96% de preenchimento)
    
    def widgets_frame_principal(self):                                                  # Método para criar e posicionar os elementos interativos (widgets) no 'frame_principal'
        # --- Botão de OK ---
        self.botao_ok = Button(self.frame_principal, text='OK', bd=4,                  # Cria um botão com o texto "OK" e borda de 4 pixels
                                     font=('Arial',15), command=self.selecionar_metodo)# Define a fonte do texto do botão e associa o clique ao método 'selecionar_metodo'
        self.botao_ok.place(relx=.8,rely=.85,relwidth=0.15,relheight=0.1)               # Posiciona o botão no frame principal, perto do canto inferior direito

        # --- Label de seleção de método ---
        self.lb_variaveis = Label(self.frame_principal, text='Selecione o método:')    # Cria um rótulo de texto para guiar o usuário na seleção do método
        self.lb_variaveis.place(relx=.05,rely=.32)                                      # Posiciona o rótulo no frame principal

        # --- Lista de seleção dos métodos (Dropdown/OptionMenu) ---
        self.Tipvar = StringVar()                                                       # Cria uma variável especial do Tkinter (StringVar) que pode ser ligada a widgets para capturar e atualizar valores de texto
        self.TipV = ("Longitudinal Imagem", "Longitudinal Carson transposição",         # Define uma tupla (lista de opções) com todos os nomes dos métodos disponíveis para seleção
                      "Longitudinal Carson para-raio", "Longitudinal Carson feixe de condutor",
                      "Longitudinal Carson impedância de sequência", "Transversal imagem",
                      "Transversal transposição", "Transversal para-raio",
                      "Transversal feixe de condutor", "Transversal capacitância de sequências")
        self.Tipvar.set("Longitudinal Imagem")                                          # Define a opção "Longitudinal Imagem" como o valor inicial que aparece no menu dropdown
        self.popupMenu = OptionMenu(self.frame_principal,self.Tipvar, *self.TipV)      # Cria o widget de menu dropdown, ligando-o ao frame principal, à variável 'Tipvar' e às opções de 'TipV'
        self.popupMenu.place(relx=.25,rely=.3,relwidth=0.5,relheight=0.08)              # Posiciona o menu dropdown no frame principal
        self.Tipvar.trace_add("write", self.atualizar_metodo_selecionado)               # Configura um "monitor": sempre que o valor de 'Tipvar' mudar, chama o método 'atualizar_metodo_selecionado'

    # --- Método para atualizar o valor selecionado ---
    def atualizar_metodo_selecionado(self, *args):                                      # Método callback: é chamado automaticamente quando o valor da 'Tipvar' muda
        self.metodo_select = self.Tipvar.get()                                          # Atualiza a variável de instância 'metodo_select' com o valor mais recente do menu dropdown
        print(f"Método selecionado: {self.metodo_select}")                              # Imprime no console qual método foi selecionado (útil para depuração)

    def janela_metodo_imagem(self):                                                          # Método para criar e configurar uma nova janela específica para o "Método Longitudinal Imagem"
        self.root2 = Tk()                                                               # Cria uma NOVA janela principal do Tkinter para substituir a anterior
        self.root2.title("Método x de LinhaMestre")                                     # Define o título desta nova janela
        self.root2.geometry("700x500")                                                  # Define o tamanho inicial da nova janela
        self.root2.configure(background='#2F4F4F')                                      # Define a cor de fundo da nova janela
        self.root2.resizable(False,False)                                               # Impede que a nova janela seja redimensionada pelo usuário
        self.root2.maxsize(width=900, height=700)                                       # Define o tamanho máximo da nova janela
        self.root2.minsize(width=400, height=300)                                       # Define o tamanho mínimo da nova janela

aplicativo()                                                                            # Cria uma instância da classe 'aplicativo', o que dá início à execução do programa da interface gráfica