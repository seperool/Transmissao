import math
import numpy as np

def metodo_capacitancia_sequencia_tran(
        ra, rb, rc,  # Raios físicos dos condutores das fases A, B, C (em metros)
        xa, ha, xb, hb, xc, hc,  # Coordenadas X e H das Fases A, B, C
        rho, comprimento_total  # Resistividade do solo e comprimento total da linha
):
    """
    Calcula a matriz de capacitância de fase e as capacitâncias de sequência (C1 e C0)
    para uma linha de transmissão trifásica NÃO transposta, com CONDUTORES SIMPLES.

    Parâmetros:
    ra, rb, rc (float): Raios físicos dos condutores das fases A, B e C (em metros).
    xa, ha (float): Coordenadas X e H da Fase A.
    xb, hb (float): Coordenadas X e H da Fase B.
    xc, hc (float): Coordenadas X e H da Fase C.
    rho (float): Resistividade do solo (em Ohm.m).
    comprimento_total (float): Comprimento total da linha (em metros).

    Retorna:
    tuple: Uma tupla contendo (C_matrix_farads, C1_farads, C0_farads), onde:
           - C_matrix_farads (numpy.ndarray): Matriz de capacitância de fase (3x3) em Farads.
           - C1_farads (float): Capacitância de sequência positiva em Farads.
           - C0_farads (float): Capacitância de sequência zero em Farads.

    Raises:
    ValueError: Para entradas inválidas (rho <= 0, alturas <= 0, raios <= 0, etc.).
    """

    # --- Constantes Físicas ---
    E = 8.854 * 10 ** (-12)  # Permissividade do vácuo (F/m)

    # --- Validações de Entrada ---
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0:
        raise ValueError("ERRO! As alturas dos condutores (ha, hb, hc) devem ser maiores que zero.")
    if comprimento_total <= 0:
        raise ValueError("ERRO! O comprimento total da linha deve ser um valor positivo.")

    for r_val in [ra, rb, rc]:
        if r_val <= 0:
            raise ValueError("ERRO! O raio dos condutores (ra, rb, rc) deve ser positivo.")

    # --- Coordenadas e Raios dos condutores de fase ---
    cond_x = [xa, xb, xc]
    cond_h = [ha, hb, hc]
    cond_r = [ra, rb, rc]  # Agora, o raio é o próprio raio físico do condutor simples

    n_phases = 3  # Número de fases

    # --- Construção da Matriz de Potencial (P_ff) ---
    P_ff = np.zeros((n_phases, n_phases))
    for i in range(n_phases):
        for j in range(n_phases):
            xi, hi, ri = cond_x[i], cond_h[i], cond_r[i]
            xj, hj, rj = cond_x[j], cond_h[j], cond_r[j]

            if i == j:  # Elemento P_ii (auto-potencial)
                P_ff[i, j] = 1 / (2 * math.pi * E) * math.log((2 * hi) / ri)
            else:  # Elemento P_ij (potencial mútuo)
                d = np.sqrt(((xi - xj) ** 2) + ((hi - hj) ** 2))
                d_prime = np.sqrt(((xi - xj) ** 2) + ((hi + hj) ** 2))
                P_ff[i, j] = 1 / (2 * math.pi * E) * math.log(d_prime / d)

    # Cálculo da Matriz de Capacitância de fase (por unidade de comprimento)
    C_matrix_per_m = np.linalg.inv(P_ff)

    # Capacitância total da matriz de fase para o comprimento da linha
    C_matrix_farads = C_matrix_per_m * comprimento_total

    # --- Cálculo das Capacitâncias de Sequência C1 e C0 (aproximação para não transposta) ---
    # Usaremos os elementos da fase A (índices 0,0 e 0,1) da matriz de capacitância total.
    C_AA = C_matrix_farads[0, 0]
    C_AB = C_matrix_farads[0, 1]

    # C1 (Sequência Positiva) = C_self - C_mutual (onde C_mutual é um valor negativo)
    # Então, C_AA - C_AB se C_AB é negativo, significa C_AA + |C_AB|
    C1_farads = C_AA - C_AB

    # C0 (Sequência Zero) = C_self + 2 * C_mutual (onde C_mutual é um valor negativo)
    # Então, C_AA + 2 * C_AB se C_AB é negativo, significa C_AA - 2*|C_AB|
    C0_farads = C_AA + 2 * C_AB

    return C_matrix_farads, C1_farads, C0_farads

