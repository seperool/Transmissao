import numpy as np  # Importa a biblioteca NumPy para operações numéricas e matriciais eficientes
import math         # Importa a biblioteca math para funções matemáticas como pi, log e exp

def metodo_imagem_long(ra, rb, rc, xa, ha, xb, hb, xc, hc, R=None, Rmg_val=None):
    """
    Calcula a matriz de impedância série por unidade de comprimento de uma linha de transmissão trifásica,
    utilizando o Método das Imagens para considerar o efeito do solo.

    A função considera 3 condutores (a, b, c) e suas resistências, coordenadas horizontais (x),
    e alturas (h) acima do solo. Permite entrada do raio físico (R) ou do Raio Médio Geométrico (Rmg_val).

    Parâmetros:
    -----------
    ra, rb, rc : float
        Resistências de fase dos condutores a, b, c por unidade de comprimento (Ohm/unidade de comprimento).
    xa, xb, xc : float
        Coordenadas horizontais (eixo X) dos condutores a, b, c (em metros).
        Assumem-se posições relativas, ex: x=0 para o primeiro condutor.
    ha, hb, hc : float
        Alturas verticais (eixo Y) dos condutores a, b, c acima do solo (em metros).
    R : float, opcional
        Raio físico do condutor (em metros). Se fornecido, o RMG será calculado (R * e^(-1/4)).
        Deve ser fornecido se Rmg_val não for. Padrão: None.
    Rmg_val : float, opcional
        Raio Médio Geométrico (RMG) do condutor (em metros).
        Se fornecido, tem prioridade sobre o cálculo via 'R'. Deve ser fornecido se R não for. Padrão: None.

    Retorna:
    --------
    numpy.ndarray
        A matriz de impedância série 3x3 complexa (Ohm/unidade de comprimento).

    Raises:
    -------
    ValueError
        Se nem o Raio (R) nem o Raio Médio Geométrico (Rmg_val) forem fornecidos,
        ou se ambos forem inválidos (por exemplo, negativos).
    """

    # --- Variáveis Físicas e Constantes ---
    mi_0 = 4 * math.pi * (10**(-7))                                     # Permeabilidade magnética do vácuo (Henry/metro)
    f = 60                                                              # Frequência do sistema elétrico (Hertz)
    w = 2 * math.pi * f                                                 # Frequência angular (radianos/segundo)

    # --- Tratamento e Validação do Raio Médio Geométrico (RMG) ---
    Rmg = None                                                          # Inicializa Rmg para controle de fluxo e validação

    if Rmg_val is not None:
        Rmg = Rmg_val
    elif R is not None:
        # Se o raio físico (R) é fornecido, calcula o RMG para condutores sólidos.
        # Para condutores trançados, o RMG é tipicamente um valor dado diretamente.
        Rmg = R * math.exp(-1/4)
    
    # Verifica se Rmg foi definido (seja diretamente ou calculado)
    if Rmg is None:
        raise ValueError("ERRO! É necessário fornecer o valor do raio do condutor (R) OU o Raio Médio Geométrico (Rmg_val).")
    if Rmg <= 0:
        raise ValueError("ERRO! O Raio Médio Geométrico (RMG) deve ser um valor positivo.")
    
    # print(f"Parâmetros de cálculo: mi_0={mi_0}, w={w}, RMG={Rmg}") # Exemplo de depuração

    # --- Cálculo das Distâncias Geométricas ---
    # As distâncias são calculadas usando a fórmula da distância euclidiana 2D (sqrt(dx^2 + dy^2)).

    # Distâncias entre os condutores reais (d_ij)
    # dx = |x_i - x_j|, dy = |h_i - h_j|
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2))
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2))
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2))
    
    # Distâncias entre os condutores e as imagens dos outros condutores (d_i,j')
    # No método das imagens, a altura da imagem de um condutor 'h_j' é '-h_j'.
    # A distância vertical entre condutor 'i' (h_i) e imagem de 'j' (-h_j) é (h_i - (-h_j)) = h_i + h_j.
    # dx = |x_i - x_j|, dy = |h_i + h_j|
    dab_l = np.sqrt(((xa - xb)**2) + ((ha + hb)**2))                    # Distância entre 'a' e a imagem de 'b'
    dac_l = np.sqrt(((xa - xc)**2) + ((ha + hc)**2))                    # Distância entre 'a' e a imagem de 'c'
    dbc_l = np.sqrt(((xb - xc)**2) + ((hb + hc)**2))                    # Distância entre 'b' e a imagem de 'c'
    
    # Nota: Não precisamos declarar dba, dca, dcb, dba_l, dca_l, dcb_l explicitamente,
    # pois a simetria (d_ij = d_ji e d_i,j' = d_j,i') será usada diretamente na construção da matriz Z.

    # --- Cálculo das Impedâncias Série (por unidade de comprimento) ---
    # As fórmulas são baseadas no Método das Imagens, derivado de Carson.
    # Z_ij = R_ij + j * X_ij
    # Z_ii = R_i + j * (w * mi0 / (2 * pi)) * ln((2 * h_i) / RMG_i)
    # Z_ij = j * (w * mi0 / (2 * pi)) * ln(d_i,j' / d_ij)

    # Impedâncias Próprias (Elementos da diagonal da Matriz Z: Zaa, Zbb, Zcc)
    # Representam a impedância de um condutor consigo mesmo, considerando seu retorno através do solo.
    # A parte real é a resistência interna do condutor. A parte imaginária é a reatância indutiva própria.
    Zaa = ra + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * ha) / Rmg))
    Zbb = rb + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * hb) / Rmg))
    Zcc = rc + (((1j * mi_0 * w) / (2 * math.pi)) * math.log((2 * hc) / Rmg))
    
    # print(f"Zaa: {Zaa}, Zbb: {Zbb}, Zcc: {Zcc}") # Exemplo de depuração

    # Impedâncias Mútuas (Elementos fora da diagonal da Matriz Z: Zab, Zac, Zbc)
    # Representam o acoplamento eletromagnético entre dois condutores devido aos campos que eles geram.
    # Assume-se que a parte resistiva mútua (devido ao solo) é zero nesta formulação simplificada.
    Zab = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dab_l / dab))
    Zac = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dac_l / dac))
    Zbc = ((1j * w * mi_0) / (2 * math.pi)) * (math.log(dbc_l / dbc))
    
    # Pela simetria da linha, as impedâncias mútuas são iguais (Z_ij = Z_ji).
    Zba = Zab
    Zca = Zac
    Zcb = Zbc
    
    # --- Montagem da Matriz de Impedância da Linha ---
    # A matriz de impedância (Z_abc) é uma matriz 3x3 que relaciona as quedas de tensão
    # nos condutores com as correntes que fluem neles e nos outros condutores.
    Z = np.matrix([
        [Zaa, Zab, Zac],
        [Zba, Zbb, Zbc],
        [Zca, Zcb, Zcc]
    ])

    return Z # A função retorna a matriz de impedância calculada