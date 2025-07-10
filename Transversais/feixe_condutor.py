import math
import numpy as np

def metodo_feixe_condutor_tran(
        ra_sub, rb_sub, rc_sub,  # Raios dos subcondutores das fases A, B, C
        na, nb, nc,  # Número de subcondutores por feixe para as fases A, B, C
        sa, sb, sc,  # Espaçamento entre subcondutores para as fases A, B, C
        xa, ha, xb, hb, xc, hc,  # Coordenadas X e H das Fases A, B, C
        rho, comprimento_total  # Resistividade do solo e comprimento total da linha
):
    """
    Calcula a matriz de capacitância de fase para uma linha de transmissão trifásica
    NÃO transposta, incluindo o efeito de condutores em feixe, e SEM cabos para-raios.

    Parâmetros:
    ra_sub, rb_sub, rc_sub (float): Raios físicos dos subcondutores das fases A, B e C (em metros).
    na, nb, nc (int): Número de subcondutores por feixe para as fases A, B e C.
                      Valores suportados: 1, 2, 3, 4.
    sa, sb, sc (float): Espaçamento entre os subcondutores do feixe para as fases A, B e C (em metros).
                        Ignorado se n=1.
    xa, ha (float): Coordenadas X e H da Fase A.
    xb, hb (float): Coordenadas X e H da Fase B.
    xc, hc (float): Coordenadas X e H da Fase C.
    rho (float): Resistividade do solo (em Ohm.m).
    comprimento_total (float): Comprimento total da linha (em metros).

    Retorna:
    numpy.ndarray: Matriz de capacitância de fase (3x3) da linha NÃO transposta (em Farads).

    Raises:
    ValueError: Para entradas inválidas (rho <= 0, alturas <= 0, número de subcondutores inválido, etc.).
    """

    # --- Constantes Físicas ---
    E = 8.854 * 10 ** (-12)  # Permissividade do vácuo (F/m)

    # --- Funções Auxiliares para RMG do Feixe ---
    def calcular_rmg_feixe(n, r_sub, s):
        """Calcula o Raio Médio Geométrico (RMG) equivalente para um condutor em feixe."""
        if n == 1:
            return r_sub
        elif n == 2:
            return math.sqrt(r_sub * s)
        elif n == 3:
            return math.pow(r_sub * s ** 2, 1 / 3)  # Raio do feixe triplo
        elif n == 4:
            # RMG de um feixe quádruplo:
            return math.pow(r_sub * s ** 3 * math.sqrt(2), 1 / 4)
        else:
            raise ValueError(
                f"Número de subcondutores ({n}) não suportado para o cálculo do RMG. Suportado: 1, 2, 3, 4.")

    # --- Validações de Entrada ---
    if rho <= 0:
        raise ValueError("ERRO! A resistividade do solo (rho) deve ser um valor positivo.")
    if ha <= 0 or hb <= 0 or hc <= 0:
        raise ValueError("ERRO! As alturas dos condutores (ha, hb, hc) devem ser maiores que zero.")
    if comprimento_total <= 0:
        raise ValueError("ERRO! O comprimento total da linha deve ser um valor positivo.")

    for n_val in [na, nb, nc]:
        if n_val not in [1, 2, 3, 4]:
            raise ValueError(f"ERRO! Número de subcondutores ({n_val}) inválido. Suportado: 1, 2, 3, 4.")

    for r_sub_val in [ra_sub, rb_sub, rc_sub]:
        if r_sub_val <= 0:
            raise ValueError("ERRO! O raio dos subcondutores (ra_sub, rb_sub, rc_sub) deve ser positivo.")

    for s_val in [sa, sb, sc]:
        if s_val < 0:
            raise ValueError("ERRO! O espaçamento entre subcondutores (sa, sb, sc) não pode ser negativo.")

    # --- Calcula o RMG equivalente para cada fase ---
    RMG_a = calcular_rmg_feixe(na, ra_sub, sa)
    RMG_b = calcular_rmg_feixe(nb, rb_sub, sb)
    RMG_c = calcular_rmg_feixe(nc, rc_sub, sc)

    # --- Coordenadas e RMGs dos condutores de fase ---
    cond_x = [xa, xb, xc]
    cond_h = [ha, hb, hc]
    cond_r = [RMG_a, RMG_b, RMG_c]

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

    # Cálculo da Matriz de Capacitância (por unidade de comprimento)
    C_matrix_per_m = np.linalg.inv(P_ff)

    # Capacitância total para o comprimento da linha
    C_total = C_matrix_per_m * comprimento_total

    return C_total  # Retorna a matriz de capacitância da linha (em Farads)

