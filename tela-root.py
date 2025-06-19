from tkinter import * # Importa classes e funções do Tkinter

root = Tk()                                                                             # Cria a janela principal da aplicação

class aplicativo():                                                                     # Define a classe principal do aplicativo
    def __init__(self):                                                                 # Construtor da classe
        self.root = root                                                                # Atribui a janela principal à instância da classe
        self.tela_root()                                                                # Configura a interface inicial da janela
        self.frames_da_tela()                                                           # Cria e posiciona os frames da interface
        self.widgets_frame_principal()                                                  # Cria e posiciona os widgets dentro do frame principal
        root.mainloop()                                                                 # Inicia o loop principal de eventos do Tkinter

    def tela_root(self):                                                                # Configurações da janela principal
        self.root.title("Métodos de linhas de Transmissão")                             # Define o título da janela
        self.root.geometry("700x500")                                                   # Define as dimensões iniciais da janela (largura x altura)
        self.root.resizable(False,False)                                                # Impede o redimensionamento da janela (largura, altura)
        self.root.maxsize(width=900, height=700)                                        # Define as dimensões máximas permitidas para a janela
        self.root.minsize(width=400, height=300)                                        # Define as dimensões mínimas permitidas para a janela

    def frames_da_tela(self):                                                           # Cria e organiza os frames na tela
        self.frame_principal = Frame(self.root, bd=4, bg='#BEBEBE',                    # Cria um frame principal para o conteúdo
                                     highlightbackground= 'black', highlightthickness=3 ) # Define borda e realce do frame
        self.frame_principal.place(relx= 0.02 , rely=0.02, relwidth= 0.96,relheight= 0.96) # Posiciona o frame principal na janela
    
    def widgets_frame_principal(self):                                                 # Cria e posiciona os widgets no frame principal
        self.botao_ok = Button(self.frame_principal, text='OK', bd=4,                  # Cria o botão "OK"
                                    font=('Arial',15))                                 # Define a fonte do botão
        self.botao_ok.place(relx=.8,rely=.85,relwidth=0.15,relheight=0.1)              # Posiciona o botão

aplicativo()                                                                           # Inicia o aplicativo, criando uma instância da classe