from tkinter import * # Importa todas as classes e funções do módulo Tkinter
from tkinter import ttk # Importa o módulo ttk do Tkinter, que oferece widgets mais modernos e estilizados
from tkinter import messagebox # Importa o módulo messagebox para exibir caixas de diálogo

root = Tk()                                                                             # Cria a janela principal da aplicação, que será a base da interface gráfica

class funcs():                                                                          # Define uma classe para conter funções de lógica de negócio e validação
    def selecionar_metodo(self):                                                        # MÉTODO: Chamado, por exemplo, ao clicar no botão "OK". Ele valida a seleção.
        if self.metodo_select == "":                                                    # Verifica se a variável 'metodo_select' está vazia
            msg = "Selecione um método válido, \n"                                      # Constrói a primeira parte da mensagem de erro
            msg += "na caixa de seleção de métodos"                                     # Adiciona a segunda parte da mensagem
            messagebox.showinfo("Erro de seleção de método!!!", msg)                    # Exibe uma caixa de diálogo informativa com a mensagem de erro
        else:                                                                           # Se um método foi selecionado (não está vazio)
            pass                                                                        # Não faz nada por enquanto (placeholder para futura lógica de processamento)

class aplicativo(funcs):                                                                # Define a classe principal do aplicativo, herdando funções da classe 'funcs'
    def __init__(self):                                                                 # O construtor da classe, chamado quando um objeto 'aplicativo' é criado
        # --- Variáveis de Instância (Atributos) ---
        self.root = root                                                                # VARIÁVEL: Armazena a referência para a janela principal do Tkinter.
        self.metodo_select = ""                                                         # VARIÁVEL: Inicializa esta variável que vai guardar o método selecionado pelo usuário.
                                                                                        # É importante inicializá-la para evitar erros caso seja acessada antes da seleção.
        
        # --- Chamadas de Métodos ---
        self.tela_root()                                                                # MÉTODO: Chama a função para configurar a janela principal (título, tamanho, etc.).
        self.frames_da_tela()                                                           # MÉTODO: Chama a função para criar e organizar os "quadros" (áreas) na janela.
        self.widgets_frame_principal()                                                  # MÉTODO: Chama a função para adicionar os elementos interativos (botões, menus) ao quadro principal.
        root.mainloop()                                                                 # MÉTODO: Inicia o loop principal de eventos do Tkinter; ele mantém a janela aberta e responsiva.

    def tela_root(self):                                                                # Método para configurar propriedades da janela principal
        self.root.title("LinhaMestre")                                                  # Define o texto que aparece na barra de título da janela como "LinhaMestre"
        self.root.configure(background='#2F4F4F')                                       # Define a cor de fundo da janela usando um código hexadecimal (azul/cinza escuro)
        self.root.geometry("700x500")                                                   # Define o tamanho inicial da janela: 700 pixels de largura por 500 de altura
        self.root.resizable(False,False)                                                # Impede que o usuário redimensione a janela (largura e altura fixas)
        self.root.maxsize(width=900, height=700)                                        # Define o tamanho máximo que a janela pode ter (se fosse redimensionável)
        self.root.minsize(width=400, height=300)                                        # Define o tamanho mínimo que a janela pode ter (se fosse redimensionável)

    def frames_da_tela(self):                                                           # Método para criar e organizar as áreas (frames) dentro da janela
        self.frame_principal = Frame(self.root, bd=4, bg="gray",                        # Cria um 'Frame' (um contêiner retangular) dentro da janela principal, com borda, cor cinza
                                     highlightbackground= 'black', highlightthickness=3 ) # Define uma borda de destaque preta com 3 pixels de espessura para o frame
        self.frame_principal.place(relx= 0.02 , rely=0.02, relwidth= 0.96,relheight= 0.96) # Posiciona o frame principal usando coordenadas relativas (2% da borda, 96% da largura/altura)
    
    def widgets_frame_principal(self):                                                  # Método para adicionar elementos interativos (widgets) ao frame principal
        # --- Botão de OK ---
        self.botao_ok = Button(self.frame_principal, text='OK', bd=4,                  # Cria um botão com o texto "OK" e borda de 4 pixels
                                     font=('Arial',15), command=self.selecionar_metodo)# Define a fonte e o tamanho do texto do botão, e associa o clique ao método 'selecionar_metodo'
        self.botao_ok.place(relx=.8,rely=.85,relwidth=0.15,relheight=0.1)               # Posiciona o botão no canto inferior direito do frame principal (80% da largura, 85% da altura)

        # --- Label de seleção de método ---
        self.lb_variaveis = Label(self.frame_principal, text='Selecione o método:')    # Cria um rótulo de texto para instruir o usuário a selecionar um método
        self.lb_variaveis.place(relx=.05,rely=.32)                                      # Posiciona o rótulo no frame principal

        # --- Lista de seleção dos métodos (Dropdown/OptionMenu) ---
        self.Tipvar = StringVar()                                                       # Cria uma variável especial do Tkinter (StringVar) para guardar o texto selecionado do menu
        self.TipV = ("Longitudinal Imagem", "Longitudinal Carson transposição",         # Define uma tupla (lista imutável) com todas as opções de método para o menu dropdown
                      "Longitudinal Carson para-raio", "Longitudinal Carson feixe de condutor",
                      "Longitudinal Carson impedância de sequência", "Transversal imagem",
                      "Transversal transposição", "Transversal para-raio",
                      "Transversal feixe de condutor", "Transversal capacitância de sequências")
        self.Tipvar.set("Longitudinal Imagem")                                          # Define a opção "Longitudinal Imagem" como o valor inicial padrão do menu dropdown
        self.popupMenu = OptionMenu(self.frame_principal,self.Tipvar, *self.TipV)      # Cria o menu dropdown (OptionMenu), associando-o ao frame principal, à variável Tipvar e às opções em TipV
        self.popupMenu.place(relx=.25,rely=.3,relwidth=0.5,relheight=0.08)              # Posiciona o menu dropdown no frame principal
        self.Tipvar.trace_add("write", self.atualizar_metodo_selecionado)               # Configura um "monitor" para a variável Tipvar: quando seu valor mudar (for escrito), chama o método 'atualizar_metodo_selecionado'

    # --- Método para atualizar o valor selecionado ---
    def atualizar_metodo_selecionado(self, *args):                                      # Método chamado automaticamente quando o valor de 'Tipvar' é alterado (por causa do 'trace_add')
        self.metodo_select = self.Tipvar.get()                                          # Atualiza a variável 'metodo_select' da instância com o valor atual da seleção do menu
        print(f"Método selecionado: {self.metodo_select}")                              # Imprime o método selecionado no console para fins de depuração

aplicativo()                                                                            # Cria uma instância da classe 'aplicativo', o que inicia todo o programa da interface gráfica