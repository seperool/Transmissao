import math
import numpy as np

def metodo_imagem_tran(xa, xb, xc, ha, hb, hc, R):
    """
    Calcula a matriz de capacitância de uma linha de transmissão trifásica
    usando o Método da Imagem, considerando o efeito do solo.

    Parâmetros:
    xa, xb, xc (float): Coordenadas horizontais (eixo x) dos condutores A, B e C em metros.
    ha, hb, hc (float): Alturas dos condutores A, B e C acima do solo em metros.
    R (float): Raio dos condutores (assumido o mesmo para todos) em metros.

    Retorna:
    numpy.ndarray: A matriz de capacitância 3x3 da linha em Farads por metro (F/m).

    Raises:
    ValueError: Se alguma altura (ha, hb, hc) for <= 0 ou se o raio (R) for <= 0.
    """
    # Constantes físicas
    # Permissividade do vácuo (F/m). 'E' é um bom nome para isso em alguns contextos de engenharia.
    E = 8.854187817 * 10**(-12)

    # --- Validação de Entradas ---
    if ha <= 0 or hb <= 0 or hc <= 0:
        # A mensagem de erro agora usa os nomes exatos das variáveis para maior clareza.
        raise ValueError("ERRO! As alturas dos condutores (ha, hb, hc) devem ser maiores que zero.")
    if R <= 0:
        raise ValueError("ERRO! O raio dos condutores (R) deve ser maior que zero.")

    # --- Cálculo das Distâncias ---
    # Distâncias diretas entre condutores
    dab = np.sqrt(((xa - xb)**2) + ((ha - hb)**2))
    dac = np.sqrt(((xa - xc)**2) + ((ha - hc)**2))
    dbc = np.sqrt(((xb - xc)**2) + ((hb - hc)**2))

    # Distâncias entre condutores e suas imagens (d_ij')
    dab_l = np.sqrt(((xa - xb)**2) + ((ha + hb)**2))
    dac_l = np.sqrt(((xa - xc)**2) + ((ha + hc)**2))
    dbc_l = np.sqrt(((xb - xc)**2) + ((hb + hc)**2))

    # --- Construção da Matriz de Potencial (P) ---
    # Os elementos da matriz P são dados por P_ij = 1/(2*pi*epsilon_0) * ln(d_ij'/d_ij).
    # Para os termos diagonais (P_ii), d_ii é o raio do condutor (R) e d_ii' é 2*h_i.

    # Elementos diagonais (auto-potenciais)
    Paa = 1/(2 * math.pi * E) * math.log((2 * ha)/R)
    Pbb = 1/(2 * math.pi * E) * math.log((2 * hb)/R)
    Pcc = 1/(2 * math.pi * E) * math.log((2 * hc)/R)

    # Elementos fora da diagonal (potenciais mútuos)
    Pab = 1/(2 * math.pi * E) * math.log(dab_l/dab)
    Pba = Pab # Devido à simetria, Pba é igual a Pab
    Pac = 1/(2 * math.pi * E) * math.log(dac_l/dac)
    Pca = Pac # Devido à simetria, Pca é igual a Pac
    Pbc = 1/(2 * math.pi * E) * math.log(dbc_l/dbc)
    Pcb = Pbc # Devido à simetria, Pcb é igual a Pbc

    # Monta a matriz de potencial P
    P = np.array([[Paa, Pab, Pac],
                  [Pba, Pbb, Pbc],
                  [Pca, Pcb, Pcc]])

    # --- Cálculo da Matriz de Capacitância (C) ---
    # A matriz de capacitância é a inversa da matriz de potencial.
    C = np.linalg.inv(P)

    return C # Retorna a matriz de capacitância em F/m